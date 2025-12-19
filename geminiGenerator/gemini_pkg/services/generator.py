"""
Gemini Quiz Generator Service - V4

Improvements over V3:
- Enhanced API retry logic with better error classification
- Graceful shutdown handling (Ctrl+C saves progress)
- Improved critic pipeline with validation error awareness
- Word-count pre-validation and targeted fixing
- Safe diagnostic serialization (no more ValueError JSON errors)
- Adaptive throttling based on error frequency
- Partial progress saving
- Better logging and diagnostics
"""

import os
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from google import genai
from google.genai import types
from pydantic import ValidationError

from gemini_pkg.config.settings import (
    MODEL_NAME_JUNIOR,
    MODEL_NAME_SENIOR,
    MODEL_NAME_CRITIC,
    TEMP_JUNIOR,
    TEMP_SENIOR,
    TEMP_CRITIC,
    RAW_OUTPUT_DIR,
    CLEAN_OUTPUT_DIR,
    QUESTIONS_INTERNAL,
    QUESTIONS_SAVED,
    CHUNK_SIZE,
    SOFT_SKILLS_COUNT,
    SECTOR_TRACKS,
    get_all_careers_for_sector,
    get_role_context,
    DEFAULT_OUTPUT_FILE,
    ensure_dirs,
    ensure_career_dirs,
    normalise_question_text,
    backoff,
    adaptive_sleep,
    load_checkpoint,
    save_checkpoint,
    save_partial_pool,
    load_partial_pool,
    QUESTION_WORD_MIN,
    QUESTION_WORD_MAX,
    OPTION_WORD_MIN,
    OPTION_WORD_MAX,
    RATIONALE_WORD_MAX,
    EXPLANATION_WORD_MIN,
    EXPLANATION_WORD_MAX,
    MAX_API_ATTEMPTS,
    MAX_CHUNK_RETRIES,
    MAX_CRITIC_RETRIES,
    SLEEP_BETWEEN_CHUNKS,
    SLEEP_AFTER_SUCCESS,
    SLEEP_AFTER_ERROR,
    serialize_validation_errors,
    format_validation_errors_for_critic,
    GracefulShutdown,
    get_shutdown_handler,
    is_shutdown_requested,
    # New organized output paths
    get_career_subdir,
    get_level_output_path,
    get_sector_complete_path,
    get_soft_skills_output_path,
    RESULTS_LOGS_DIR,
    # Production data output
    DATA_SECTORS_DIR,
    get_sector_data_output_path,
    get_difficulty_metadata,
)

from gemini_pkg.schema.models import QuestionModel, QuizPoolModel
from gemini_pkg.prompts.system_prompts import (
    SYS_PROMPT_GENERATOR,
    SYS_PROMPT_CRITIC,
    SYS_PROMPT_CRITIC_SIMPLE,
    SYS_PROMPT_WORDCOUNT_FIXER,
    SOFT_SKILLS_SYS_PROMPT,
)

from gemini_pkg.schema.json_utils import (
    clean_json_text,
    check_word_counts,
    format_word_count_issues,
    attempt_word_count_fix,
    get_short_option_summary,
)


# =============================================================================
# ERROR CLASSIFICATION
# =============================================================================


class APIErrorType(Enum):
    """Classification of API errors for appropriate handling."""

    RATE_LIMIT = "rate_limit"  # 429 - back off and retry
    QUOTA_EXHAUSTED = "quota_exhausted"  # 429 with specific message - long backoff
    UNAVAILABLE = "unavailable"  # 503 - retry with backoff
    TIMEOUT = "timeout"  # Request timeout - retry
    PERMANENT = "permanent"  # Don't retry (bad request, auth error)
    UNKNOWN = "unknown"  # Unknown error - cautious retry


def classify_api_error(exception: Exception) -> APIErrorType:
    """
    Classify an API exception to determine retry strategy.
    """
    error_str = str(exception).lower()
    exception_type = type(exception).__name__.lower()

    # Check for timeout-related exceptions (httpx, requests, etc.)
    if "timeout" in exception_type or "timedout" in exception_type:
        return APIErrorType.TIMEOUT

    if "429" in error_str:
        if "quota" in error_str or "resource_exhausted" in error_str:
            return APIErrorType.QUOTA_EXHAUSTED
        return APIErrorType.RATE_LIMIT

    if "503" in error_str or "unavailable" in error_str or "overloaded" in error_str:
        return APIErrorType.UNAVAILABLE

    if (
        "timeout" in error_str
        or "timed out" in error_str
        or "read timeout" in error_str
    ):
        return APIErrorType.TIMEOUT

    if "400" in error_str or "401" in error_str or "403" in error_str:
        return APIErrorType.PERMANENT

    if "500" in error_str or "502" in error_str or "504" in error_str:
        return APIErrorType.UNAVAILABLE

    # Connection errors should be retried
    if "connection" in error_str or "connect" in exception_type:
        return APIErrorType.UNAVAILABLE

    return APIErrorType.UNKNOWN


def should_retry_error(error_type: APIErrorType) -> bool:
    """Determine if an error type should be retried."""
    return error_type not in (APIErrorType.PERMANENT,)


# =============================================================================
# GEMINI QUIZ GENERATOR SERVICE
# =============================================================================


@dataclass
class GeminiQuizGeneratorV4:
    """
    Enhanced Gemini Quiz Generator with improved reliability.

    Features:
    - Chunked generation with checkpointing
    - Critic repair pipeline with validation awareness
    - Graceful shutdown handling
    - Adaptive throttling
    - Comprehensive diagnostics
    """

    model_junior: str = MODEL_NAME_JUNIOR
    model_senior: str = MODEL_NAME_SENIOR
    model_critic: str = MODEL_NAME_CRITIC
    temp_junior: float = TEMP_JUNIOR
    temp_senior: float = TEMP_SENIOR
    temp_critic: float = TEMP_CRITIC

    results_bank: Dict[str, Any] = field(default_factory=dict)
    client: genai.Client = field(default=None)

    # Track consecutive errors for adaptive throttling
    consecutive_errors: int = field(default=0)

    # Shutdown handler
    shutdown_handler: GracefulShutdown = field(default=None)

    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    def __post_init__(self):
        if self.client is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise EnvironmentError("GEMINI_API_KEY not set in environment.")
            # Initialize client (no custom timeout - use library defaults)
            self.client = genai.Client(api_key=api_key)

        if self.shutdown_handler is None:
            # Use global handler so is_shutdown_requested() works correctly
            self.shutdown_handler = get_shutdown_handler()

        # Load existing results to merge with (allows running sectors separately)
        self._load_existing_results()

    def _load_existing_results(self):
        """
        Load existing combined results file if it exists.
        This allows running sectors separately without losing previous data.
        """
        if os.path.exists(DEFAULT_OUTPUT_FILE):
            try:
                with open(DEFAULT_OUTPUT_FILE, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                if isinstance(existing, dict):
                    self.results_bank = existing
                    sectors = [k for k in existing.keys() if k != "soft_skills"]
                    logging.info(
                        f"📂 Loaded existing results: {len(sectors)} sectors, "
                        f"soft_skills={'yes' if 'soft_skills' in existing else 'no'}"
                    )
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"⚠️ Could not load existing results: {e}")
                # Start fresh if file is corrupted
                self.results_bank = {}

    # =========================================================================
    # MODEL SELECTION
    # =========================================================================

    def pick_model_for_level(self, level: int) -> Tuple[str, float]:
        """Select model and temperature based on question level."""
        if level in (1, 2):
            return (self.model_junior, self.temp_junior)
        return (self.model_senior, self.temp_senior)

    # =========================================================================
    # CORE GEMINI API CALL
    # =========================================================================

    def _call_gemini_json(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        label: str,
        max_attempts: int = MAX_API_ATTEMPTS,
    ) -> Optional[dict]:
        """
        Make a Gemini API call with retry logic and JSON extraction.

        Args:
            model: Model name to use
            system_prompt: System instruction
            user_prompt: User message
            temperature: Generation temperature
            label: Label for logging
            max_attempts: Maximum retry attempts

        Returns:
            Parsed JSON dict, or None if all attempts fail
        """
        last_error = None

        for attempt in range(1, max_attempts + 1):
            # Check for shutdown request
            if is_shutdown_requested():
                logging.warning(f"Shutdown requested, aborting API call: {label}")
                return None

            try:
                logging.info(
                    f"🔄 Gemini call ({label}) attempt {attempt}/{max_attempts} "
                    f"[model={model}, temp={temperature}]"
                )

                response = self.client.models.generate_content(
                    model=model,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=temperature,
                        response_mime_type="application/json",
                    ),
                )

                raw_text = getattr(response, "text", None)
                if not raw_text:
                    logging.warning(f"⚠️ Empty response for {label} (attempt {attempt})")
                    self.consecutive_errors += 1
                    adaptive_sleep(SLEEP_AFTER_ERROR, self.consecutive_errors)
                    continue

                # Reset consecutive errors on successful response
                self.consecutive_errors = 0

                # Extract and parse JSON
                parsed = clean_json_text(raw_text)
                if parsed is not None:
                    logging.info(f"✅ Successfully parsed JSON for {label}")
                    return parsed

                logging.warning(
                    f"⚠️ Failed to parse JSON for {label} (attempt {attempt}). "
                    f"Raw text length: {len(raw_text)}"
                )
                last_error = "JSON parse failure"

            except Exception as e:
                last_error = e
                error_type = classify_api_error(e)
                logging.error(
                    f"❌ Gemini API error for {label}: {e} "
                    f"(type={error_type.value}, attempt={attempt})"
                )

                self.consecutive_errors += 1

                if not should_retry_error(error_type):
                    logging.error(f"🚫 Permanent error for {label}, not retrying")
                    return None

                # Apply appropriate backoff
                if error_type == APIErrorType.QUOTA_EXHAUSTED:
                    backoff(attempt, "quota_exhausted")
                elif error_type == APIErrorType.RATE_LIMIT:
                    backoff(attempt, "rate_limit")
                elif error_type == APIErrorType.UNAVAILABLE:
                    backoff(attempt, "unavailable")
                else:
                    adaptive_sleep(SLEEP_AFTER_ERROR, self.consecutive_errors)

        logging.error(
            f"❌ All {max_attempts} attempts failed for {label}: {last_error}"
        )
        return None

    # =========================================================================
    # DIAGNOSTIC FILE WRITING
    # =========================================================================

    def _write_diagnostic_file(
        self,
        filepath: str,
        data: Dict[str, Any],
    ) -> bool:
        """
        Safely write a diagnostic file with proper error serialization.

        Args:
            filepath: Path to write to
            data: Data dict to write (may contain non-serializable items)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Safely serialize all data
            safe_data = {}
            for key, value in data.items():
                if key in ("validation_errors", "critic_validation_errors"):
                    safe_data[key] = serialize_validation_errors(value)
                else:
                    try:
                        json.dumps(value)
                        safe_data[key] = value
                    except (TypeError, ValueError):
                        safe_data[key] = str(value)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(safe_data, f, indent=2, ensure_ascii=False)

            logging.debug(f"📝 Wrote diagnostic: {filepath}")
            return True

        except Exception as e:
            logging.error(f"Failed to write diagnostic file {filepath}: {e}")
            return False

    # =========================================================================
    # CRITIC PIPELINE
    # =========================================================================

    def _run_critic_repair(
        self,
        failed_json: dict,
        validation_errors: Any,
        key_base: str,
        model: str,
        attempt: int,
    ) -> Optional[dict]:
        """
        Run the critic repair pipeline on failed JSON.

        Improvements:
        - Passes validation errors to critic
        - Multiple critic attempts
        - Fallback to simpler critic prompt

        Args:
            failed_json: The JSON that failed validation
            validation_errors: Pydantic validation errors
            key_base: Base key for file naming
            model: Model to use for critic
            attempt: Current attempt number

        Returns:
            Repaired and validated dict, or None if repair fails
        """
        # Check word counts specifically to give critic targeted feedback
        _, word_issues = check_word_counts(failed_json)
        word_issue_summary = (
            format_word_count_issues(word_issues) if word_issues else ""
        )

        # Format validation errors for critic
        error_summary = format_validation_errors_for_critic(validation_errors)

        # Build critic user prompt with error context
        critic_user_prompt = (
            "The following JSON failed validation. Fix all issues.\n\n"
            f"=== VALIDATION ERRORS ===\n{error_summary}\n\n"
        )

        if word_issue_summary:
            critic_user_prompt += f"=== WORD COUNT ISSUES ===\n{word_issue_summary}\n\n"

        critic_user_prompt += (
            f"=== JSON TO FIX ===\n{json.dumps(failed_json, ensure_ascii=False)}"
        )

        # Try main critic prompt
        for critic_attempt in range(1, MAX_CRITIC_RETRIES + 1):
            if is_shutdown_requested():
                return None

            # Use simpler prompt on second attempt
            critic_prompt = (
                SYS_PROMPT_CRITIC if critic_attempt == 1 else SYS_PROMPT_CRITIC_SIMPLE
            )
            critic_label = (
                f"critic:{key_base}:gen_attempt{attempt}:critic_attempt{critic_attempt}"
            )

            logging.info(
                f"🔧 Running critic repair: {critic_label} "
                f"(using {'main' if critic_attempt == 1 else 'simple'} prompt)"
            )

            critic_output = self._call_gemini_json(
                model=self.model_critic,  # Use dedicated critic model
                system_prompt=critic_prompt,
                user_prompt=critic_user_prompt,
                temperature=self.temp_critic,
                label=critic_label,
                max_attempts=2,  # 2 API attempts per critic call
            )

            timestamp = int(time.time())
            critic_output_path = os.path.join(
                CLEAN_OUTPUT_DIR,
                f"{key_base}_critic_fixed_attempt{attempt}_c{critic_attempt}_ts-{timestamp}.json",
            )

            if critic_output is None:
                logging.warning(f"Critic returned no output for {critic_label}")
                self._write_diagnostic_file(
                    critic_output_path,
                    {
                        "error": "critic_no_response",
                        "critic_attempt": critic_attempt,
                        "timestamp": timestamp,
                    },
                )
                continue

            # Save critic output
            with open(critic_output_path, "w", encoding="utf-8") as f:
                json.dump(critic_output, f, indent=2, ensure_ascii=False)

            # Try to fix any remaining word count issues automatically
            critic_output = attempt_word_count_fix(critic_output)

            # Validate critic output
            try:
                validated = QuizPoolModel.model_validate(critic_output)
                logging.info(
                    f"✅ Critic repaired {key_base} successfully (attempt {critic_attempt})"
                )
                return {"quiz_pool": [q.model_dump() for q in validated.quiz_pool]}

            except ValidationError as e:
                logging.warning(
                    f"Critic output still invalid for {critic_label}: "
                    f"{serialize_validation_errors(e.errors())[:200]}..."
                )

                # Save critic validation diagnostic
                self._write_diagnostic_file(
                    critic_output_path.replace(".json", "_validation_error.json"),
                    {
                        "critic_validation_errors": e.errors(),
                        "critic_output": critic_output,
                        "critic_attempt": critic_attempt,
                        "timestamp": timestamp,
                    },
                )

                # On last attempt, try word count fixer as last resort
                if critic_attempt == MAX_CRITIC_RETRIES:
                    fixed = self._try_wordcount_fixer(critic_output, key_base)
                    if fixed:
                        return fixed

        return None

    def _try_wordcount_fixer(
        self,
        data: dict,
        key_base: str,
    ) -> Optional[dict]:
        """
        Last resort: use dedicated word count fixer prompt.
        """
        short_summary = get_short_option_summary(data)
        if not short_summary:
            return None  # No short options to fix

        logging.info(f"🔧 Trying word count fixer for {key_base}")

        user_prompt = (
            f"{short_summary}\n\n"
            f"=== JSON TO FIX ===\n{json.dumps(data, ensure_ascii=False)}"
        )

        fixed_output = self._call_gemini_json(
            model=self.model_critic,
            system_prompt=SYS_PROMPT_WORDCOUNT_FIXER,
            user_prompt=user_prompt,
            temperature=0.3,
            label=f"wordcount_fixer:{key_base}",
            max_attempts=1,
        )

        if fixed_output is None:
            return None

        try:
            validated = QuizPoolModel.model_validate(fixed_output)
            logging.info(f"✅ Word count fixer succeeded for {key_base}")
            return {"quiz_pool": [q.model_dump() for q in validated.quiz_pool]}
        except ValidationError:
            return None

    # =========================================================================
    # CHUNKED GENERATION
    # =========================================================================

    def generate_raw_quiz(
        self,
        sector: str,
        career: str,
        level: int,
    ) -> Optional[dict]:
        """
        Generate questions in chunks with validation and repair.

        Features:
        - Checkpoint-based resume
        - Per-chunk retry with critic repair
        - Graceful shutdown handling
        - Partial progress saving

        Args:
            sector: Industry sector
            career: Career/role name
            level: Difficulty level (1-5)

        Returns:
            Combined quiz pool dict, or None if generation fails
        """
        model, temp = self.pick_model_for_level(level)
        combined_pool: List[QuestionModel] = []

        ensure_dirs()

        num_chunks = QUESTIONS_INTERNAL // CHUNK_SIZE
        checkpoint = load_checkpoint()

        # Track progress for this job
        job_key = f"{sector}_{career}_lvl{level}"

        for chunk_index in range(num_chunks):
            # Check for shutdown
            if is_shutdown_requested():
                logging.warning(
                    f"🛑 Shutdown requested. Saving progress for {job_key}..."
                )
                self._save_partial_progress(combined_pool, job_key, checkpoint)
                return None

            # Anti-throttle delay between chunks
            adaptive_sleep(SLEEP_BETWEEN_CHUNKS, self.consecutive_errors)

            key_base = f"{sector}_{career}_lvl{level}_chunk{chunk_index + 1}"
            logging.info(
                f"\n{'='*60}\n"
                f"📦 Generating chunk {chunk_index + 1}/{num_chunks}: {key_base}\n"
                f"{'='*60}"
            )

            # Skip if already completed
            if checkpoint.get(key_base) == "done":
                logging.info(f"⏭️ Skipping completed chunk: {key_base}")
                # Load previously saved chunk if available
                self._load_chunk_to_pool(key_base, combined_pool)
                continue

            chunk_success = False

            for retry_count in range(1, MAX_CHUNK_RETRIES + 1):
                if is_shutdown_requested():
                    break

                logging.info(f"🔄 Chunk attempt {retry_count}/{MAX_CHUNK_RETRIES}")

                # Get role context for enhanced prompts
                role_ctx = get_role_context(sector, career)

                # Build prompts with full context
                system_prompt = SYS_PROMPT_GENERATOR.format(
                    sector=sector.replace("_", " "),
                    sector_description=role_ctx["sector_description"],
                    branch=role_ctx["branch"] or "General",
                    branch_description=role_ctx["branch_description"],
                    career=career.replace("_", " "),
                    career_description=role_ctx["career_description"],
                    count=CHUNK_SIZE,
                    level=level,
                    qmin=QUESTION_WORD_MIN,
                    qmax=QUESTION_WORD_MAX,
                    exp_min=EXPLANATION_WORD_MIN,
                    exp_max=EXPLANATION_WORD_MAX,
                    omin=OPTION_WORD_MIN,
                    omax=OPTION_WORD_MAX,
                    rationale_max=RATIONALE_WORD_MAX,
                )

                # Calculate the starting ID for this chunk
                start_id = chunk_index * CHUNK_SIZE + 1
                end_id = start_id + CHUNK_SIZE - 1

                user_prompt = (
                    f"Generate {CHUNK_SIZE} Level {level} interview questions for the role "
                    f"'{career.replace('_', ' ')}' in the '{sector.replace('_', ' ')}' sector.\n"
                    f"This is chunk {chunk_index + 1} of {num_chunks}.\n"
                    f"IMPORTANT: Question IDs must start at {start_id} and go to {end_id}.\n"
                    f"REMEMBER: Each option text MUST be {OPTION_WORD_MIN}-{OPTION_WORD_MAX} words!\n"
                    f"REMEMBER: Each question MUST have an explanation ({EXPLANATION_WORD_MIN}-{EXPLANATION_WORD_MAX} words)!"
                )

                label = f"generator:{key_base}:attempt{retry_count}"

                result = self._call_gemini_json(
                    model=model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temp,
                    label=label,
                    max_attempts=MAX_API_ATTEMPTS,
                )

                timestamp = int(time.time())
                raw_chunk_path = os.path.join(
                    RAW_OUTPUT_DIR,
                    f"{key_base}_raw_attempt{retry_count}_ts-{timestamp}.json",
                )

                if result is None:
                    logging.error(f"❌ Generator returned no JSON for {key_base}")
                    self._write_diagnostic_file(
                        raw_chunk_path,
                        {
                            "error": "no_response",
                            "sector": sector,
                            "career": career,
                            "level": level,
                            "chunk": chunk_index + 1,
                            "attempt": retry_count,
                            "model": model,
                            "temperature": temp,
                            "timestamp": timestamp,
                        },
                    )
                    adaptive_sleep(SLEEP_AFTER_ERROR, self.consecutive_errors)
                    continue

                # Save raw output
                with open(raw_chunk_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)

                # Pre-check word counts
                is_valid_wc, wc_issues = check_word_counts(result)
                if not is_valid_wc:
                    logging.warning(
                        f"⚠️ Word count issues detected:\n{format_word_count_issues(wc_issues)}"
                    )
                    # Try automatic fix for truncation issues
                    result = attempt_word_count_fix(result)

                # Validate with Pydantic
                try:
                    chunk_pool = QuizPoolModel.model_validate(result)
                    combined_pool.extend(chunk_pool.quiz_pool)
                    chunk_success = True

                    logging.info(
                        f"✅ Chunk {key_base} validated successfully "
                        f"({len(chunk_pool.quiz_pool)} questions)"
                    )

                    # Save checkpoint
                    checkpoint[key_base] = "done"
                    save_checkpoint(checkpoint)

                    # Save successful chunk for recovery
                    self._save_chunk(key_base, chunk_pool.quiz_pool)

                    adaptive_sleep(SLEEP_AFTER_SUCCESS, 0)
                    break

                except ValidationError as e:
                    logging.warning(
                        f"⚠️ Validation failed for {key_base}:\n"
                        f"{format_validation_errors_for_critic(e.errors())}"
                    )

                    # Save validation diagnostic
                    self._write_diagnostic_file(
                        raw_chunk_path.replace(".json", "_validation_error.json"),
                        {
                            "validation_errors": e.errors(),
                            "raw_response": result,
                            "model": model,
                            "temperature": temp,
                            "sector": sector,
                            "career": career,
                            "level": level,
                            "chunk": chunk_index + 1,
                            "attempt": retry_count,
                            "timestamp": timestamp,
                        },
                    )

                    # Run critic repair
                    repaired = self._run_critic_repair(
                        failed_json=result,
                        validation_errors=e.errors(),
                        key_base=key_base,
                        model=model,
                        attempt=retry_count,
                    )

                    if repaired:
                        try:
                            repaired_pool = QuizPoolModel.model_validate(repaired)
                            combined_pool.extend(repaired_pool.quiz_pool)
                            chunk_success = True

                            logging.info(
                                f"✅ Chunk {key_base} repaired successfully "
                                f"({len(repaired_pool.quiz_pool)} questions)"
                            )

                            checkpoint[key_base] = "done"
                            save_checkpoint(checkpoint)
                            self._save_chunk(key_base, repaired_pool.quiz_pool)

                            adaptive_sleep(SLEEP_AFTER_SUCCESS, 0)
                            break
                        except ValidationError as e2:
                            logging.error(f"❌ Repaired JSON still invalid: {e2}")

                    adaptive_sleep(SLEEP_AFTER_ERROR, self.consecutive_errors)

            if not chunk_success:
                logging.error(
                    f"❌ Chunk {key_base} failed after {MAX_CHUNK_RETRIES} attempts. "
                    f"Moving to next chunk."
                )
                # Save partial progress periodically
                if chunk_index % 2 == 0:
                    self._save_partial_progress(combined_pool, job_key, checkpoint)

        # Final check
        if not combined_pool:
            logging.error(
                f"❌ No valid questions produced for {sector}/{career} level {level}"
            )
            return None

        # Build final output
        final_raw = {"quiz_pool": [q.model_dump() for q in combined_pool]}

        # Save combined raw
        raw_path = os.path.join(
            RAW_OUTPUT_DIR,
            f"{sector}_{career}_lvl{level}_raw_combined.json",
        )
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(final_raw, f, indent=2, ensure_ascii=False)

        logging.info(
            f"✅ Generated {len(combined_pool)} questions for {sector}/{career} L{level}"
        )
        return final_raw

    def _save_chunk(self, key_base: str, questions: List[QuestionModel]):
        """Save a successful chunk for potential recovery."""
        chunk_path = os.path.join(
            CLEAN_OUTPUT_DIR,
            f"{key_base}_validated.json",
        )
        with open(chunk_path, "w", encoding="utf-8") as f:
            json.dump(
                {"quiz_pool": [q.model_dump() for q in questions]},
                f,
                indent=2,
                ensure_ascii=False,
            )

    def _load_chunk_to_pool(
        self,
        key_base: str,
        pool: List[QuestionModel],
    ):
        """Load a previously saved chunk into the pool."""
        chunk_path = os.path.join(
            CLEAN_OUTPUT_DIR,
            f"{key_base}_validated.json",
        )
        if os.path.exists(chunk_path):
            try:
                with open(chunk_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                validated = QuizPoolModel.model_validate(data)
                pool.extend(validated.quiz_pool)
                logging.info(
                    f"📂 Loaded {len(validated.quiz_pool)} questions from {key_base}"
                )
            except Exception as e:
                logging.warning(f"Failed to load chunk {key_base}: {e}")

    def _save_partial_progress(
        self,
        pool: List[QuestionModel],
        job_key: str,
        checkpoint: Dict[str, Any],
    ):
        """Save partial progress for recovery."""
        if pool:
            save_partial_pool(
                {
                    "job_key": job_key,
                    "question_count": len(pool),
                    "quiz_pool": [q.model_dump() for q in pool],
                }
            )
        save_checkpoint(checkpoint)
        logging.info(f"💾 Saved partial progress: {len(pool)} questions for {job_key}")

    # =========================================================================
    # FULL CRITIC REVIEW (POST-GENERATION)
    # =========================================================================

    def critic_review_quiz(
        self,
        raw_quiz: dict,
        sector: str,
        career: str,
        level: int,
    ) -> Optional[QuizPoolModel]:
        """
        Run final critic review on combined quiz.
        """
        model, _ = self.pick_model_for_level(level)

        user_prompt = (
            "Review and correct this quiz JSON. Ensure all word counts are valid.\n\n"
            + json.dumps(raw_quiz, ensure_ascii=False)
        )

        key = f"{sector}_{career}_lvl{level}_critic"

        for attempt in range(1, 3):
            if is_shutdown_requested():
                return None

            result = self._call_gemini_json(
                model=self.model_critic,
                system_prompt=SYS_PROMPT_CRITIC,
                user_prompt=user_prompt,
                temperature=self.temp_critic,
                label=f"final_critic:{key}_attempt{attempt}",
                max_attempts=2,
            )

            if result is None:
                logging.error(f"Final critic failed for {key} (attempt {attempt})")
                continue

            # Save critic output
            clean_path = os.path.join(CLEAN_OUTPUT_DIR, f"{key}_attempt{attempt}.json")
            with open(clean_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            # Apply automatic fixes
            result = attempt_word_count_fix(result)

            try:
                return QuizPoolModel.model_validate(result)
            except ValidationError as e:
                # Extract first error for clear logging
                errors = e.errors()
                first_error = errors[0] if errors else {}
                error_type = first_error.get("type", "unknown")
                error_msg = first_error.get("msg", "Unknown validation error")
                error_loc = ".".join(str(x) for x in first_error.get("loc", []))

                logging.warning(
                    f"❌ Final critic validation failed ({key} attempt {attempt}):\n"
                    f"   Error type: {error_type}\n"
                    f"   Message: {error_msg}\n"
                    f"   Location: {error_loc or 'root'}\n"
                    f"   Total errors: {len(errors)}"
                )
                self._write_diagnostic_file(
                    clean_path.replace(".json", "_validation_error.json"),
                    {"validation_errors": e.errors(), "result": result},
                )

        logging.error(f"❌ Final critic failed for {key} after all attempts")
        return None

    # =========================================================================
    # DEDUPLICATION
    # =========================================================================

    def _deduplicate_questions(
        self,
        questions: List[QuestionModel],
    ) -> List[QuestionModel]:
        """Remove duplicate questions based on normalized text."""
        seen = set()
        unique: List[QuestionModel] = []

        for q in questions:
            norm = normalise_question_text(q.question)
            if norm not in seen:
                seen.add(norm)
                unique.append(q)

        return unique

    # =========================================================================
    # FULL PIPELINE PER CAREER/LEVEL
    # =========================================================================

    def generate_for_career_level(
        self,
        sector: str,
        career: str,
        level: int,
    ):
        """
        Complete generation pipeline for one sector/career/level combination.
        """
        if is_shutdown_requested():
            return

        # Ensure career directories exist
        ensure_career_dirs(sector, career)

        raw = self.generate_raw_quiz(sector, career, level)
        if raw is None:
            logging.error(f"❌ Skipping due to raw failure: {sector}/{career}/L{level}")
            return

        if is_shutdown_requested():
            return

        reviewed = self.critic_review_quiz(raw, sector, career, level)
        if reviewed is None:
            # Fallback: use raw if critic fails
            logging.warning(
                f"⚠️ Critic failed, using raw output for {sector}/{career}/L{level}"
            )
            try:
                reviewed = QuizPoolModel.model_validate(raw)
            except ValidationError:
                logging.error(f"❌ Cannot use raw output either")
                return

        questions = reviewed.quiz_pool

        logging.info(
            f"📊 Before dedup: {len(questions)} questions for {sector}/{career} L{level}"
        )

        questions = self._deduplicate_questions(questions)

        logging.info(
            f"📊 After dedup: {len(questions)} questions for {sector}/{career} L{level}"
        )

        if len(questions) < QUESTIONS_SAVED:
            logging.warning(
                f"⚠️ Got only {len(questions)} questions (expected {QUESTIONS_SAVED})"
            )

        if not questions:
            logging.error(
                f"❌ No valid questions after dedup: {sector}/{career} L{level}"
            )
            return

        selected = questions[:QUESTIONS_SAVED]

        # Reassign sequential IDs
        for i, q in enumerate(selected, start=1):
            q.id = i

        # Convert to dicts using Pydantic v2 method
        quiz_pool_dicts = [q.model_dump() for q in selected]
        level_data = {"quiz_pool": quiz_pool_dicts}

        # Save to results bank (for combined output)
        self.results_bank.setdefault(sector, {}).setdefault(career, {})[
            f"level_{level}"
        ] = level_data

        # Save to organized folder structure
        level_output_path = get_level_output_path(sector, career, level)
        with open(level_output_path, "w", encoding="utf-8") as f:
            json.dump(level_data, f, indent=2, ensure_ascii=False)
        logging.info(f"📁 Saved level output: {level_output_path}")

    # =========================================================================
    # SOFT SKILLS BLOCK
    # =========================================================================

    def generate_soft_skills_block(self):
        """Generate soft skills questions block with full pipeline (critic + dedup)."""
        if is_shutdown_requested():
            return

        logging.info(
            f"\n{'='*60}\n"
            f"🧠 Generating soft skills questions ({SOFT_SKILLS_COUNT})\n"
            f"{'='*60}"
        )

        # Step 1: Generate raw questions
        result = self._call_gemini_json(
            model=self.model_junior,
            system_prompt=SOFT_SKILLS_SYS_PROMPT,
            user_prompt=(
                f"Generate {SOFT_SKILLS_COUNT} soft skills interview questions.\n"
                f"REMEMBER: Each option text MUST be {OPTION_WORD_MIN}-{OPTION_WORD_MAX} words!"
            ),
            temperature=0.5,
            label="soft_skills_generator",
            max_attempts=3,
        )

        if result is None:
            logging.error("❌ Soft skills generation failed")
            return

        # Save raw
        raw_path = os.path.join(RAW_OUTPUT_DIR, "soft_skills_raw.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logging.info(f"📄 Saved raw response: {raw_path}")

        # Apply automatic word count fixes (truncate long text)
        result = attempt_word_count_fix(result)

        # Initial validation check
        try:
            qp = QuizPoolModel.model_validate(result)
            logging.info(
                f"✅ Initial validation passed ({len(qp.quiz_pool)} questions)"
            )
        except ValidationError as e:
            logging.warning(f"⚠️ Initial validation failed, sending to critic repair")
            # Try critic repair
            repaired = self._run_critic_repair(
                failed_json=result,
                validation_errors=e.errors(),
                key_base="soft_skills",
                model=self.model_junior,
                attempt=1,
            )
            if repaired:
                try:
                    qp = QuizPoolModel.model_validate(repaired)
                    result = repaired
                except ValidationError:
                    logging.error("❌ Soft skills repair also failed")
                    return
            else:
                return

        if is_shutdown_requested():
            return

        # Step 2: Final critic review (always runs, like career questions)
        logging.info("🔍 Running final critic review for soft skills...")
        reviewed = self._critic_review_soft_skills(result)

        if reviewed is None:
            logging.warning("⚠️ Critic review failed, using pre-critic output")
            # Fallback to pre-critic validated output
            reviewed = qp
        else:
            logging.info("✅ Final critic review completed")

        questions = reviewed.quiz_pool

        # Step 3: Deduplication
        logging.info(f"📊 Before dedup: {len(questions)} soft skills questions")
        questions = self._deduplicate_questions(questions)
        logging.info(f"📊 After dedup: {len(questions)} soft skills questions")

        if not questions:
            logging.error("❌ No valid questions after dedup")
            return

        # Reassign sequential IDs
        for i, q in enumerate(questions, start=1):
            q.id = i

        # Convert to dicts
        quiz_pool_dicts = [q.model_dump() for q in questions]
        soft_skills_data = {"quiz_pool": quiz_pool_dicts}

        # Save to results bank
        self.results_bank["soft_skills"] = soft_skills_data

        # Save to organized folder structure
        soft_skills_path = get_soft_skills_output_path()
        with open(soft_skills_path, "w", encoding="utf-8") as f:
            json.dump(soft_skills_data, f, indent=2, ensure_ascii=False)
        logging.info(f"📁 Saved soft skills: {soft_skills_path}")

        # Also save to legacy location (backwards compatibility)
        legacy_path = os.path.join(
            CLEAN_OUTPUT_DIR, "soft_skills_clean_gemini_v2.5.json"
        )
        with open(legacy_path, "w", encoding="utf-8") as f:
            json.dump(soft_skills_data, f, indent=2, ensure_ascii=False)

        logging.info(
            f"✅ Generated {len(questions)} soft skills questions (after critic + dedup)"
        )

    def _critic_review_soft_skills(self, raw_quiz: dict) -> Optional[QuizPoolModel]:
        """
        Run final critic review on soft skills quiz.
        Similar to critic_review_quiz but for soft skills.
        """
        user_prompt = (
            "Review and correct this soft skills quiz JSON.\n"
            "Ensure all word counts are valid and content is accurate.\n"
            "Check for any hallucinated or fictional content.\n\n"
            + json.dumps(raw_quiz, ensure_ascii=False)
        )

        key = "soft_skills_critic"

        for attempt in range(1, 3):
            if is_shutdown_requested():
                return None

            result = self._call_gemini_json(
                model=self.model_critic,
                system_prompt=SYS_PROMPT_CRITIC,
                user_prompt=user_prompt,
                temperature=self.temp_critic,
                label=f"final_critic:{key}_attempt{attempt}",
                max_attempts=2,
            )

            if result is None:
                logging.error(f"Final critic failed for {key} (attempt {attempt})")
                continue

            # Save critic output
            clean_path = os.path.join(CLEAN_OUTPUT_DIR, f"{key}_attempt{attempt}.json")
            with open(clean_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logging.info(f"📄 Saved critic attempt {attempt}: {clean_path}")

            # Apply automatic fixes
            result = attempt_word_count_fix(result)

            try:
                return QuizPoolModel.model_validate(result)
            except ValidationError as e:
                # Extract first error for clear logging
                errors = e.errors()
                first_error = errors[0] if errors else {}
                error_type = first_error.get("type", "unknown")
                error_msg = first_error.get("msg", "Unknown validation error")
                error_loc = ".".join(str(x) for x in first_error.get("loc", []))

                logging.warning(
                    f"❌ Soft skills critic validation failed (attempt {attempt}):\n"
                    f"   Error type: {error_type}\n"
                    f"   Message: {error_msg}\n"
                    f"   Location: {error_loc or 'root'}\n"
                    f"   Total errors: {len(errors)}"
                )
                self._write_diagnostic_file(
                    clean_path.replace(".json", "_validation_error.json"),
                    {"validation_errors": e.errors(), "result": result},
                )

        logging.error(f"❌ Final critic review failed for soft skills")
        return None

    # =========================================================================
    # MASTER PIPELINE
    # =========================================================================

    def generate_sector(self, sector: str):
        """
        Generate all questions for a single sector (all careers, all levels).

        Args:
            sector: Sector name (e.g., 'technology', 'finance', 'health_social_care', 'education')
        """
        ensure_dirs()

        if sector not in SECTOR_TRACKS:
            available = ", ".join(SECTOR_TRACKS.keys())
            logging.error(f"❌ Unknown sector: {sector}")
            logging.error(f"   Available sectors: {available}")
            return

        careers = get_all_careers_for_sector(sector)
        total_careers = len(careers)

        logging.info(
            f"\n{'='*60}\n"
            f"🏭 Generating sector: {sector}\n"
            f"   Careers: {total_careers}\n"
            f"   Levels per career: 5\n"
            f"   Total generations: {total_careers * 5}\n"
            f"{'='*60}"
        )

        with self.shutdown_handler:
            try:
                for career_idx, career in enumerate(careers, 1):
                    for level in range(1, 6):
                        if is_shutdown_requested():
                            break

                        logging.info(
                            f"\n{'#'*60}\n"
                            f"### [{career_idx}/{total_careers}] {sector} / {career} (Level {level}) ###\n"
                            f"{'#'*60}"
                        )

                        self.generate_for_career_level(sector, career, level)

                    if is_shutdown_requested():
                        break

                # Save sector-complete file
                if sector in self.results_bank and not is_shutdown_requested():
                    self._save_sector_complete(sector)

            except Exception as e:
                logging.error(f"❌ Unexpected error in generate_sector: {e}")

            finally:
                # Save progress
                if self.results_bank:
                    os.makedirs(os.path.dirname(DEFAULT_OUTPUT_FILE), exist_ok=True)
                    with open(DEFAULT_OUTPUT_FILE, "w", encoding="utf-8") as f:
                        json.dump(self.results_bank, f, indent=2, ensure_ascii=False)
                    logging.info(f"\n💾 Saved progress to {DEFAULT_OUTPUT_FILE}")

                if is_shutdown_requested():
                    logging.info(
                        f"\n{'='*60}\n"
                        f"🛑 Generation interrupted. Progress saved.\n"
                        f"{'='*60}"
                    )

    def generate_all(self):
        """
        Generate all questions for all sectors, careers, and levels.

        Uses graceful shutdown handler for Ctrl+C handling.
        """
        ensure_dirs()

        with self.shutdown_handler:
            try:
                for sector in SECTOR_TRACKS.keys():
                    careers = get_all_careers_for_sector(sector)
                    sector_start = len(self.results_bank.get(sector, {}))

                    for career in careers:
                        for level in range(1, 6):
                            if is_shutdown_requested():
                                break

                            logging.info(
                                f"\n{'#'*60}\n"
                                f"### {sector} / {career} (Level {level}) ###\n"
                                f"{'#'*60}"
                            )

                            self.generate_for_career_level(sector, career, level)

                        if is_shutdown_requested():
                            break

                    # Save sector-complete file after each sector
                    if sector in self.results_bank and not is_shutdown_requested():
                        self._save_sector_complete(sector)

                    if is_shutdown_requested():
                        break

                if not is_shutdown_requested():
                    self.generate_soft_skills_block()

            except Exception as e:
                logging.error(f"❌ Unexpected error in generate_all: {e}")

            finally:
                # Always save final combined output
                if self.results_bank:
                    # Ensure combined directory exists
                    os.makedirs(os.path.dirname(DEFAULT_OUTPUT_FILE), exist_ok=True)
                    with open(DEFAULT_OUTPUT_FILE, "w", encoding="utf-8") as f:
                        json.dump(self.results_bank, f, indent=2, ensure_ascii=False)
                    logging.info(
                        f"\n💾 Saved combined quiz bank: {DEFAULT_OUTPUT_FILE}"
                    )

                if is_shutdown_requested():
                    logging.info(
                        f"\n"
                        f"{'='*60}\n"
                        f"🛑 Generation interrupted. Progress saved.\n"
                        f"   To resume, run the script again.\n"
                        f"   Checkpoint file: {os.path.abspath(RESULTS_LOGS_DIR)}/generation_checkpoint.json\n"
                        f"{'='*60}"
                    )

    def _save_sector_complete(self, sector: str):
        """Save the complete output for a sector (all careers combined)."""
        if sector not in self.results_bank:
            return

        sector_data = self.results_bank[sector]
        sector_path = get_sector_complete_path(sector)

        with open(sector_path, "w", encoding="utf-8") as f:
            json.dump(sector_data, f, indent=2, ensure_ascii=False)

        # Count total questions in sector
        total_questions = 0
        for career_data in sector_data.values():
            for level_data in career_data.values():
                if isinstance(level_data, dict) and "quiz_pool" in level_data:
                    total_questions += len(level_data["quiz_pool"])

        logging.info(
            f"📁 Saved sector complete: {sector_path} ({total_questions} questions)"
        )

        # =====================================================================
        # PRODUCTION DATA OUTPUT: Transform and save to data/sectors/{sector}.json
        # =====================================================================
        self._save_sector_production_data(sector)

    def _transform_question_to_production_schema(
        self,
        question: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Transform a question from internal format to production schema format.

        Internal format:
        {
            "id": 1,
            "question": "...",
            "explanation": "...",
            "options": [
                {"key": "A", "text": "...", "is_correct": true, "rationale": "..."},
                ...
            ]
        }

        Production format (preserves all 5 options with key and rationale):
        {
            "question_text": "...",
            "question_type": "multiple_choice",
            "points": 1,
            "explanation": "...",
            "options": [
                {"key": "A", "text": "...", "is_correct": true, "rationale": "..."},
                ...
            ]
        }
        """
        # Preserve all 5 options with their keys and rationales
        production_options = [
            {
                "key": opt.get("key", ""),
                "text": opt.get("text", ""),
                "is_correct": opt.get("is_correct", False),
                "rationale": opt.get("rationale", ""),
            }
            for opt in question.get("options", [])
        ]

        return {
            "question_text": question.get("question", ""),
            "question_type": "multiple_choice",  # Always multiple_choice
            "points": 1,  # Always 1
            "explanation": question.get("explanation", ""),
            "options": production_options,
        }

    def _transform_to_production_quiz(
        self,
        career: str,
        level: int,
        quiz_pool: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Transform a career/level quiz_pool into production quiz format.

        Production schema:
        {
            "title": "...",
            "description": "...",
            "specialization": "...",
            "difficulty_level": 1,
            "time_limit_minutes": 30,
            "passing_score": 70.0,
            "questions": [...]
        }
        """
        # Get difficulty metadata (time limit, passing score)
        difficulty_meta = get_difficulty_metadata(level)

        # Build quiz title and description
        career_display = career.replace("_", " ").title()
        title = f"{career_display} Interview - Level {level}"
        description = f"Level {level} assessment questions for {career_display} role"

        # Transform all questions
        production_questions = [
            self._transform_question_to_production_schema(q) for q in quiz_pool
        ]

        return {
            "title": title,
            "description": description,
            "specialization": career,  # Use exact career name from database
            "difficulty_level": level,
            "time_limit_minutes": difficulty_meta["time_limit_minutes"],
            "passing_score": difficulty_meta["passing_score"],
            "questions": production_questions,
        }

    def _save_sector_production_data(self, sector: str):
        """
        Transform and save sector data to production format in data/sectors/{sector}.json

        Production schema:
        {
            "quizzes": [
                {
                    "title": "...",
                    "description": "...",
                    "specialization": "...",
                    "difficulty_level": 1,
                    "time_limit_minutes": 30,
                    "passing_score": 70.0,
                    "questions": [...]
                },
                ...
            ]
        }
        """
        if sector not in self.results_bank:
            return

        sector_data = self.results_bank[sector]
        production_quizzes = []

        # Iterate through all careers and levels
        for career, career_data in sector_data.items():
            if not isinstance(career_data, dict):
                continue

            for level_key, level_data in career_data.items():
                # level_key is like "level_1", "level_2", etc.
                if not isinstance(level_data, dict) or "quiz_pool" not in level_data:
                    continue

                # Extract level number from key
                try:
                    level = int(level_key.replace("level_", ""))
                except ValueError:
                    continue

                quiz_pool = level_data["quiz_pool"]
                if not quiz_pool:
                    continue

                # Transform to production format
                production_quiz = self._transform_to_production_quiz(
                    career=career,
                    level=level,
                    quiz_pool=quiz_pool,
                )
                production_quizzes.append(production_quiz)

        # Sort quizzes by specialization, then by difficulty level
        production_quizzes.sort(
            key=lambda q: (q["specialization"], q["difficulty_level"])
        )

        # Build final production output
        production_output = {"quizzes": production_quizzes}

        # Ensure output directory exists and save
        output_path = get_sector_data_output_path(sector)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(production_output, f, indent=2, ensure_ascii=False)

        # Count total questions
        total_questions = sum(len(q["questions"]) for q in production_quizzes)

        logging.info(
            f"📦 Saved production data: {output_path} "
            f"({len(production_quizzes)} quizzes, {total_questions} questions)"
        )


# =============================================================================
# BACKWARDS COMPATIBILITY ALIAS
# =============================================================================

# Alias for backwards compatibility
GeminiQuizGeneratorV3 = GeminiQuizGeneratorV4
