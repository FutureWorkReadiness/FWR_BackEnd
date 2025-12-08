"""
gemini_version/quiz_generator_gemini_v3.py

Sector-based quiz bank generator using Google Gemini (v3)
- Sectors: technology, finance, health_social_care, education, construction
- Internally generates 40 questions per career per level, but saves 20 shuffled questions
- 5 levels per career
- Deduplication of questions by text
- Separate soft skills block with 20 questions total
- LLMOps:
    * Pydantic schema enforcement
    * Agentic workflow: generator + critic pass
    * Shuffle logic before saving
    * More robust JSON cleaning and retry logic

Setup:
  pip install google-genai pydantic

Set your API key:
  export GEMINI_API_KEY="your_gemini_key_here"
"""

import os
import json
import logging
import random
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel, model_validator, ValidationError
from google import genai  # pip install google-genai
from google.genai import types

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file in the project root."""
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load .env file at module import
load_env_file()

# -------------------------
# CONFIG
# -------------------------

# TECHNOLOGY TRACKS (flattened)
TECHNOLOGY_TRACKS = [
    "FRONTEND_DEVELOPER",
    "BACKEND_DEVELOPER",
    "IOS_DEVELOPER",
    "ANDROID_DEVELOPER",
    "MOBILE_DEVELOPMENT_CROSS_PLATFORM",
    "DATA_SCIENTIST",
    "DATA_ANALYST",
    "DATA_ENGINEER",
    "AI_ML_ENGINEER",
    "CYBERSECURITY_ANALYST",
    "QA_AUTOMATION_ENGINEER_SET",
    "DEVOPS_ENGINEER",
    "CLOUD_ENGINEER",
    "DATABASE_ADMINISTRATOR_DBA",
    "NETWORK_ENGINEER",
    "SYSTEMS_ADMINISTRATOR",
    "UX_UI_DESIGNER",
    "TECHNICAL_PRODUCT_MANAGER",
    "TECHNICAL_PROJECT_MANAGER_SCRUM_MASTER",
]

SECTOR_TRACKS: Dict[str, list] = {
    "technology": TECHNOLOGY_TRACKS,
    "finance": [
        "investment_banker", "financial_analyst", "accountant", "risk_manager", "portfolio_manager",
        "tax_consultant", "auditor", "compliance_officer", "trader", "fund_manager",
        "financial_planner", "credit_analyst", "insurance_underwriter", "budget_analyst", "wealth_manager"
    ],
    "health_social_care": [
        "nurse", "midwife", "care_worker", "social_worker",
        "occupational_therapist", "physiotherapist", "healthcare_assistant",
        "mental_health_counselor", "public_health_officer"
    ],
    "education": [
        "teacher", "special_need_educator"
    ],
    "construction": [
        "civil_engineer", "site_manager", "quantity_surveyor",
        "architect", "construction_worker", "project_manager", "structural_engineer"
    ],
}

# Create outputs directory path
OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

DEFAULT_OUTPUT_FILE = str(OUTPUTS_DIR / "sector_quiz_bank_gemini_v3.json")
RAW_OUTPUT_DIR = str(OUTPUTS_DIR / "raw_responses_gemini_v3")
CLEAN_OUTPUT_DIR = str(OUTPUTS_DIR / "clean_quiz_chunks_gemini_v3")

QUESTIONS_INTERNAL = 20   # Reduced to fit within token limits
QUESTIONS_SAVED = 20      # what we actually keep
SOFT_SKILLS_COUNT = 20

MODEL_NAME_JUNIOR = os.getenv("GEMINI_MODEL_JUNIOR", "gemini-2.0-flash")
MODEL_NAME_SENIOR = os.getenv("GEMINI_MODEL_SENIOR", "gemini-2.5-pro")

TEMP_JUNIOR = 0.6
TEMP_SENIOR = 0.4
TEMP_CRITIC = 0.3

# Tuned ranges (slightly looser for more variation)
QUESTION_WORD_MIN = 12
QUESTION_WORD_MAX = 28
OPTION_WORD_MIN = 10
OPTION_WORD_MAX = 24
RATIONALE_WORD_MAX = 30

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")


# -------------------------
# Utility
# -------------------------

def word_count(s: str) -> int:
    return len(s.strip().split())


def ensure_dirs():
    os.makedirs(RAW_OUTPUT_DIR, exist_ok=True)
    os.makedirs(CLEAN_OUTPUT_DIR, exist_ok=True)


def normalise_question_text(text: str) -> str:
    """Normalise question text for deduplication."""
    return re.sub(r"\s+", " ", text.strip().lower())


# -------------------------
# Pydantic schema (LLMOps)
# -------------------------

class OptionModel(BaseModel):
    key: str
    text: str
    is_correct: bool
    rationale: str

    @model_validator(mode='after')
    def validate_lengths(self):
        text = self.text
        rationale = self.rationale
        tw = word_count(text)
        rw = word_count(rationale)
        if tw < OPTION_WORD_MIN or tw > OPTION_WORD_MAX:
            raise ValueError(
                f"Option text word count {tw} out of range "
                f"[{OPTION_WORD_MIN}, {OPTION_WORD_MAX}]."
            )
        if rw > RATIONALE_WORD_MAX:
            raise ValueError(
                f"Rationale word count {rw} exceeds max {RATIONALE_WORD_MAX}."
            )
        if self.key not in ("A", "B", "C", "D", "E"):
            raise ValueError("Option key must be one of 'A', 'B', 'C', 'D', 'E'.")
        return self


class QuestionModel(BaseModel):
    id: int
    question: str
    options: List[OptionModel]

    @model_validator(mode='after')
    def validate_question(self):
        q = self.question
        opts = self.options
        qw = word_count(q)
        if qw < QUESTION_WORD_MIN or qw > QUESTION_WORD_MAX:
            raise ValueError(
                f"Question word count {qw} out of range "
                f"[{QUESTION_WORD_MIN}, {QUESTION_WORD_MAX}]."
            )
        if len(opts) != 5:
            raise ValueError("There must be exactly 5 options.")
        correct_count = sum(1 for o in opts if o.is_correct)
        if correct_count != 1:
            raise ValueError("There must be exactly one correct option.")
        return self


class QuizPoolModel(BaseModel):
    quiz_pool: List[QuestionModel]

    @model_validator(mode='after')
    def validate_pool(self):
        pool = self.quiz_pool
        if not pool:
            raise ValueError("quiz_pool must not be empty.")
        return self


# -------------------------
# Gemini client
# -------------------------

def init_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set in environment.")
    client = genai.Client(api_key=api_key)
    return client


# -------------------------
# System prompts
# -------------------------

SYS_PROMPT_GENERATOR = """
You are a precise Subject Matter Expert and Lead Interviewer for the role {career} within the {sector} sector.

TASK:
- Generate EXACTLY {count} unique multiple-choice questions (A-E) for interview Level {level}.

Constraints (strict):
- Output: ONLY a single valid JSON object, nothing else.
- Schema: {{ "quiz_pool": [ {{ "id":int, "question":str,
              "options":[{{"key":"A"-"E","text":str,"is_correct":bool,"rationale":str}}] }} ] }}
- Count: EXACTLY {count} items.
- Question length: {qmin}-{qmax} words.
- Each option length: {omin}-{omax} words.
- Exactly one option must have is_correct=true; all others false.
- Options must be plausible, distinct, and of similar length.
- Do NOT include commentary, markdown, code fences, or extra text outside the JSON.
- Do NOT invent non-existent tools, standards, or regulations.
- Rationale for each option <= {rationale_max} words.

Return ONLY the JSON object.
""".strip()

SYS_PROMPT_CRITIC_TEMPLATE = """
You are an expert QA Reviewer (Critic) for technical and sector-based interview questions.

You are given a JSON object containing a quiz_pool of multiple-choice questions (A-E).
Each question must follow this schema:
{{ "quiz_pool": [ {{ "id":int, "question":str,
  "options":[{{"key":"A"-"E","text":str,"is_correct":bool,"rationale":str}}] }} ] }}

Your job:
- Fix any structural issues (missing fields, wrong types, invalid booleans).
- Ensure there are exactly 5 options per question, with exactly one is_correct=true.
- Ensure question and options length constraints (words) are respected:
  - question: {qmin}-{qmax} words
  - options: {omin}-{omax} words
  - rationale: <= {rationale_max} words
- Remove or correct any obviously unrealistic or impossible content.
- Preserve the original intent and difficulty of the questions.
- Keep the same number of questions.

Constraints:
- Output ONLY a single valid JSON object following the same schema.
- Do NOT add commentary, markdown, or text outside the JSON object.
"""

SYS_PROMPT_CRITIC = SYS_PROMPT_CRITIC_TEMPLATE.format(
    qmin=QUESTION_WORD_MIN,
    qmax=QUESTION_WORD_MAX,
    omin=OPTION_WORD_MIN,
    omax=OPTION_WORD_MAX,
    rationale_max=RATIONALE_WORD_MAX,
).strip()

SOFT_SKILLS_SYS_PROMPT_TEMPLATE = """
You are an expert behavioural interviewer for early-career candidates across technology, finance, health and social care, education, and construction sectors.

Generate EXACTLY 20 unique multiple-choice questions that assess soft skills such as:
- communication
- teamwork
- problem solving
- time management
- adaptability
- leadership
- handling feedback
- dealing with conflict
- professionalism
- ethical judgment

Constraints (strict):
- Output: ONLY a single valid JSON object.
- Schema: {{ "quiz_pool": [ {{ "id":int, "question":str,
           "options":[{{"key":"A"-"E","text":str,"is_correct":bool,"rationale":str}}] }} ] }}
- Count: EXACTLY 20 items.
- Question length: {qmin}-{qmax} words.
- Each option length: {omin}-{omax} words.
- Each question should describe a realistic scenario or situation.
- Exactly one option is correct; the others are plausible but flawed.
- Rationale for each option must be <= {rationale_max} words and clearly state why it is correct or incorrect.
- Do NOT include commentary, markdown, code fences, or text outside the JSON object.
Return ONLY the JSON object.
"""

SOFT_SKILLS_SYS_PROMPT = SOFT_SKILLS_SYS_PROMPT_TEMPLATE.format(
    qmin=QUESTION_WORD_MIN,
    qmax=QUESTION_WORD_MAX,
    omin=OPTION_WORD_MIN,
    omax=OPTION_WORD_MAX,
    rationale_max=RATIONALE_WORD_MAX,
).strip()


# -------------------------
# JSON helper
# -------------------------

JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json_text(raw_text: str) -> Optional[str]:
    """
    Try to extract a JSON object from the raw text.
    Handles cases where the model wraps output in ```json ... ``` fences or adds commentary.
    """
    if not raw_text:
        logging.debug("extract_json_text: raw_text is empty")
        return None

    logging.debug(f"extract_json_text: Processing text of length {len(raw_text)}")
    logging.debug(f"extract_json_text: First 200 chars: {raw_text[:200]}")

    # Strip code fences if present
    raw = raw_text.strip()
    if raw.startswith("```"):
        logging.debug("extract_json_text: Detected markdown code fence")
        # Remove leading and trailing fences
        raw = re.sub(r"^```(?:json)?", "", raw, flags=re.IGNORECASE).strip()
        raw = re.sub(r"```$", "", raw).strip()

    # If it parses directly, great
    try:
        json.loads(raw)
        logging.debug(f"extract_json_text: Successfully parsed raw text directly (length: {len(raw)})")
        return raw
    except Exception as e:
        logging.debug(f"extract_json_text: Direct parsing failed: {e}")
        pass

    # Fallback: extract first JSON object-ish substring
    logging.debug("extract_json_text: Attempting regex extraction")
    match = JSON_OBJECT_RE.search(raw)
    if match:
        candidate = match.group(0)
        logging.debug(f"extract_json_text: Regex matched {len(candidate)} chars")
        try:
            json.loads(candidate)
            logging.debug("extract_json_text: Successfully parsed regex-extracted JSON")
            return candidate
        except Exception as e:
            logging.debug(f"extract_json_text: Regex candidate parsing failed: {e}")
            return None

    logging.debug("extract_json_text: No valid JSON found")
    return None


def clean_json_text(raw_text: str) -> Optional[dict]:
    json_str = extract_json_text(raw_text)
    if not json_str:
        logging.debug("extract_json_text returned None")
        return None
    try:
        parsed = json.loads(json_str)
        logging.debug(f"Successfully parsed JSON with {len(str(parsed))} chars")
        return parsed
    except Exception as e:
        logging.error(f"JSON parsing failed: {e}")
        logging.debug(f"Failed JSON string (first 1000 chars): {json_str[:1000]}")
        return None


# -------------------------
# Gemini generator with critic + shuffle
# -------------------------

@dataclass
class GeminiQuizGeneratorV3:
    model_junior: str = MODEL_NAME_JUNIOR
    model_senior: str = MODEL_NAME_SENIOR
    temp_junior: float = TEMP_JUNIOR
    temp_senior: float = TEMP_SENIOR
    temp_critic: float = TEMP_CRITIC
    results_bank: Dict[str, Any] = field(default_factory=dict)
    client: genai.Client = field(default=None)
    raw_dir: Path = field(default=None)
    clean_dir: Path = field(default=None)

    def __post_init__(self):
        if self.client is None:
            self.client = init_gemini_client()
        if self.raw_dir is None:
            self.raw_dir = Path(RAW_OUTPUT_DIR)
            self.raw_dir.mkdir(parents=True, exist_ok=True)
        if self.clean_dir is None:
            self.clean_dir = Path(CLEAN_OUTPUT_DIR)
            self.clean_dir.mkdir(parents=True, exist_ok=True)

    def pick_model_for_level(self, level: int) -> Tuple[str, float]:
        return (
            (self.model_junior, self.temp_junior)
            if level in (1, 2)
            else (self.model_senior, self.temp_senior)
        )

    def _call_gemini_json(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        label: str,
        max_attempts: int = 2,
    ) -> Optional[dict]:
        """
        Call Gemini up to max_attempts times, trying to get valid JSON.
        """
        for attempt in range(1, max_attempts + 1):
            logging.info(
                "Gemini call (%s) attempt %d/%d using model=%s",
                label,
                attempt,
                max_attempts,
                model,
            )
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        temperature=temperature,
                        max_output_tokens=32768,  # Increased to handle large quiz responses
                    ),
                )
                
                # Extract text from response - handle potential truncation
                raw_text = None
                if hasattr(response, 'candidates') and response.candidates:
                    # Get all parts from the first candidate
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        parts = candidate.content.parts
                        raw_text = ''.join(part.text for part in parts if hasattr(part, 'text'))
                        logging.debug(f"Extracted {len(raw_text)} chars from {len(parts)} parts")
                
                # Fallback to response.text if candidates not available
                if not raw_text:
                    raw_text = getattr(response, "text", None)
                    
                if not raw_text:
                    logging.error("Empty response.text from Gemini for %s", label)
                    continue
                
                # Save raw response for debugging
                try:
                    raw_file = self.raw_dir / f"{label}_attempt{attempt}.txt"
                    raw_file.write_text(raw_text, encoding="utf-8")
                    logging.info(f"Saved raw response to {raw_file}")
                except Exception as save_err:
                    logging.warning(f"Could not save raw response: {save_err}")
                    
            except Exception as e:
                logging.error("Gemini API error for %s: %s", label, e)
                continue

            result = clean_json_text(raw_text)
            if result is not None:
                return result
            else:
                logging.warning("Failed to parse JSON for %s (attempt %d). Raw text length: %d", 
                              label, attempt, len(raw_text))
                logging.debug("First 500 chars of raw text: %s", raw_text[:500])

        logging.error("All attempts failed for %s. Returning None.", label)
        return None

    def generate_raw_quiz(self, sector: str, career: str, level: int) -> Optional[dict]:
        model, temp = self.pick_model_for_level(level)
        system_prompt = SYS_PROMPT_GENERATOR.format(
            sector=sector.replace("_", " "),
            career=career.replace("_", " "),
            count=QUESTIONS_INTERNAL,
            level=level,
            qmin=QUESTION_WORD_MIN,
            qmax=QUESTION_WORD_MAX,
            omin=OPTION_WORD_MIN,
            omax=OPTION_WORD_MAX,
            rationale_max=RATIONALE_WORD_MAX,
        )
        user_prompt = (
            f"Generate {QUESTIONS_INTERNAL} Level {level} interview questions for the role: "
            f"{career} in the {sector} sector."
        )
        key = f"{sector}_{career}_lvl{level}_raw"
        label = f"generator:{key}"
        logging.info("Gemini generator: %s", key)

        ensure_dirs()
        result = self._call_gemini_json(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temp,
            label=label,
            max_attempts=2,
        )
        if result is None:
            logging.error("Generator failed to produce JSON for %s.", key)
            return None

        raw_path = os.path.join(RAW_OUTPUT_DIR, f"{key}.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return result

    def critic_review_quiz(
        self,
        raw_quiz: dict,
        sector: str,
        career: str,
        level: int,
    ) -> Optional[QuizPoolModel]:
        model, _ = self.pick_model_for_level(level)  # reuse same model
        system_prompt = SYS_PROMPT_CRITIC
        user_prompt = (
            "Here is the JSON object you must review and fix:\n\n"
            + json.dumps(raw_quiz, ensure_ascii=False)
        )
        key = f"{sector}_{career}_lvl{level}_critic"
        label = f"critic:{key}"
        logging.info("Gemini critic: %s", key)

        # Try critic up to 2 times if pydantic validation fails.
        for attempt in range(1, 3):
            result = self._call_gemini_json(
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=self.temp_critic,
                label=f"{label}_attempt{attempt}",
                max_attempts=1,
            )
            if result is None:
                logging.error("Critic call failed for %s (attempt %d).", key, attempt)
                continue

            clean_path = os.path.join(
                CLEAN_OUTPUT_DIR, f"{key}_attempt{attempt}.json"
            )
            with open(clean_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            try:
                qp = QuizPoolModel.parse_obj(result)
                return qp
            except ValidationError as e:
                logging.warning(
                    "Pydantic validation failed for %s (attempt %d): %s",
                    key,
                    attempt,
                    e,
                )

        logging.error("Critic could not produce valid QuizPoolModel for %s.", key)
        return None

    def _deduplicate_questions(self, questions: List[QuestionModel]) -> List[QuestionModel]:
        """Deduplicate by normalised question text."""
        seen = set()
        unique_questions: List[QuestionModel] = []
        for q in questions:
            norm = normalise_question_text(q.question)
            if norm in seen:
                continue
            seen.add(norm)
            unique_questions.append(q)
        return unique_questions

    def generate_for_career_level(self, sector: str, career: str, level: int):
        raw_quiz = self.generate_raw_quiz(sector, career, level)
        if raw_quiz is None:
            logging.error("Skipping %s/%s level %d (no raw quiz).", sector, career, level)
            return

        qp_model = self.critic_review_quiz(raw_quiz, sector, career, level)
        if qp_model is None:
            logging.error("Skipping %s/%s level %d (critic failed).", sector, career, level)
            return

        questions = qp_model.quiz_pool
        logging.info(
            "Received %d questions for %s/%s level %d before dedup.",
            len(questions),
            sector,
            career,
            level,
        )

        # Deduplicate
        questions = self._deduplicate_questions(questions)
        logging.info(
            "Retained %d unique questions for %s/%s level %d after dedup.",
            len(questions),
            sector,
            career,
            level,
        )

        if len(questions) < QUESTIONS_SAVED:
            logging.warning(
                "Got only %d unique questions for %s/%s level %d; expected at least %d.",
                len(questions),
                sector,
                career,
                level,
                QUESTIONS_SAVED,
            )

        if not questions:
            logging.error(
                "No valid questions remain for %s/%s level %d after dedup. Skipping.",
                sector,
                career,
                level,
            )
            return

        # Shuffle logic: random 20 out of available (or fewer if not enough)
        random.shuffle(questions)
        selected = questions[:QUESTIONS_SAVED]

        # Renumber IDs from 1..N for clarity
        for idx, q in enumerate(selected, start=1):
            q.id = idx

        # Convert back to dicts
        quiz_pool_dicts = [json.loads(q.json()) for q in selected]

        self.results_bank.setdefault(sector, {}).setdefault(career, {})[
            f"level_{level}"
        ] = {"quiz_pool": quiz_pool_dicts}

    def generate_soft_skills_block(self):
        model = self.model_junior
        temp = 0.5
        logging.info(
            "Gemini generating soft skills block (%d questions) with model=%s",
            SOFT_SKILLS_COUNT,
            model,
        )

        result = self._call_gemini_json(
            model=model,
            system_prompt=SOFT_SKILLS_SYS_PROMPT,
            user_prompt="Generate the 20 soft skills questions as specified.",
            temperature=temp,
            label="soft_skills",
            max_attempts=2,
        )
        if result is None:
            logging.error("Soft skills (Gemini): failed to get JSON.")
            return

        ensure_dirs()
        raw_path = os.path.join(RAW_OUTPUT_DIR, "soft_skills_raw_gemini_v3.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        try:
            qp = QuizPoolModel.parse_obj(result)
        except ValidationError as e:
            logging.error("Soft skills (Gemini) validation failed: %s", e)
            return

        # No dedup / shuffle here; it's already 20
        self.results_bank["soft_skills"] = json.loads(qp.json())

        clean_path = os.path.join(CLEAN_OUTPUT_DIR, "soft_skills_clean_gemini_v3.json")
        with open(clean_path, "w", encoding="utf-8") as f:
            json.dump(self.results_bank["soft_skills"], f, indent=2, ensure_ascii=False)

    def generate_all(self):
        for sector, careers in SECTOR_TRACKS.items():
            for career in careers:
                for level in range(1, 6):
                    logging.info(
                        "=== Gemini v3 generating %s / %s (level %d) ===",
                        sector,
                        career,
                        level,
                    )
                    self.generate_for_career_level(sector, career, level)

        self.generate_soft_skills_block()

        with open(DEFAULT_OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(self.results_bank, f, indent=2, ensure_ascii=False)
        logging.info("Saved Gemini v3 quiz bank to %s", DEFAULT_OUTPUT_FILE)


# -------------------------
# Entrypoint
# -------------------------

if __name__ == "__main__":
    ensure_dirs()
    generator = GeminiQuizGeneratorV3()
    generator.generate_all()




# ====== Mini test for only Data Science===

# -------------------------
# Integrated Entrypoint + Mini Test Runner (Levels 1–5)
# -------------------------

import argparse

def run_mini_test():
    """
    MINI TEST MODE — runs:
    - Sector: technology
    - Career: DATA_SCIENTIST
    - Levels: 1 to 5
    """

    ensure_dirs()
    gen = GeminiQuizGeneratorV3()

    TEST_SECTOR = "technology"
    TEST_CAREER = "DATA_SCIENTIST"
    TEST_LEVELS = [1, 2, 3, 4, 5]
    OUTPUT_FILE = "test_quiz_output.json"

    print("\n===============================")
    print("       MINI TEST MODE")
    print("===============================")

    test_results = {TEST_SECTOR: {TEST_CAREER: {}}}

    for level in TEST_LEVELS:
        print(f"\n--- Generating TEST level {level} ---")

        gen.generate_for_career_level(TEST_SECTOR, TEST_CAREER, level)

        level_key = f"level_{level}"

        # Save if successful
        if (
            TEST_SECTOR in gen.results_bank
            and TEST_CAREER in gen.results_bank[TEST_SECTOR]
            and level_key in gen.results_bank[TEST_SECTOR][TEST_CAREER]
        ):
            test_results[TEST_SECTOR][TEST_CAREER][level_key] = (
                gen.results_bank[TEST_SECTOR][TEST_CAREER][level_key]
            )
            print(f"✓ Level {level} generated successfully.")
        else:
            print(f"✗ Level {level} FAILED.")

    # Soft skills generation
    print("\n--- Soft Skills Block ---")
    gen.generate_soft_skills_block()

    if "soft_skills" in gen.results_bank:
        test_results["soft_skills"] = gen.results_bank["soft_skills"]
        print("✓ Soft skills generated.")
    else:
        print("✗ Soft skills generation FAILED.")

    # Save the test results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)

    # Analyze logs
    # summary = analyze_logs(gen.log_events)
    # save_summary_report(summary)

    print("\n===============================")
    print(" MINI TEST COMPLETE")
    print(" Output saved to:", OUTPUT_FILE)
    print(" Summary saved to: test_summary_report.json")
    print("===============================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run mini test mode (Data Scientist Levels 1–5)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full quiz generation for all sectors/careers/levels",
    )

    args = parser.parse_args()

    ensure_dirs()

    if args.test:
        run_mini_test()
    elif args.full:
        generator = GeminiQuizGeneratorV3()
        generator.generate_all()
    else:
        print("\nNo mode selected. Use:\n")
        print("  python quiz_generator_gemini_v3.py --test")
        print("  python quiz_generator_gemini_v3.py --full\n")

