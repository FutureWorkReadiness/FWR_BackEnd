import os
import re
import logging
import time
import random
import json
import signal
from typing import Any, Dict, List, Optional

# ------------------------------
# Project root detection
# ------------------------------
# When installed as a package, we need to find the project root
# The package is at: {PROJECT_ROOT}/geminiGenerator/gemini_pkg/
# This file is at: {PROJECT_ROOT}/geminiGenerator/gemini_pkg/config/settings.py
# So project root is 4 levels up from this file

_PACKAGE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
_PROJECT_ROOT = os.path.dirname(
    _PACKAGE_DIR
)  # Go up from geminiGenerator to project root

# Allow override via environment variable (useful for Docker/testing)
PROJECT_ROOT = os.getenv("FWR_PROJECT_ROOT", _PROJECT_ROOT)

# ------------------------------
# Output directories (v2 - organized by sector)
# ------------------------------

# Base results directory (inside geminiGenerator for intermediate files)
RESULTS_BASE_DIR = os.path.join(_PACKAGE_DIR, "results")

# Subdirectories for intermediate/debug output
RESULTS_BY_SECTOR_DIR = os.path.join(RESULTS_BASE_DIR, "by_sector")
RESULTS_COMBINED_DIR = os.path.join(RESULTS_BASE_DIR, "combined")
RESULTS_LOGS_DIR = os.path.join(RESULTS_BASE_DIR, "logs")

# Legacy paths (for backwards compatibility - inside geminiGenerator)
RAW_OUTPUT_DIR = os.path.join(_PACKAGE_DIR, "raw_responses_gemini_v2.5")
CLEAN_OUTPUT_DIR = os.path.join(_PACKAGE_DIR, "clean_quiz_chunks_gemini_v2.5")

# Main output files (intermediate)
DEFAULT_OUTPUT_FILE = os.path.join(RESULTS_COMBINED_DIR, "all_sectors_quiz_bank.json")
CHECKPOINT_FILE = os.path.join(RESULTS_LOGS_DIR, "generation_checkpoint.json")
PARTIAL_POOL_FILE = os.path.join(RESULTS_LOGS_DIR, "partial_pool.json")

# ------------------------------
# Production data output (new schema format)
# Points to the root project's data directory
# ------------------------------
DATA_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data")
DATA_SECTORS_DIR = os.path.join(DATA_OUTPUT_DIR, "generated_sectors")

# ------------------------------
# Difficulty level metadata (fixed rules)
# ------------------------------
DIFFICULTY_METADATA = {
    1: {"time_limit_minutes": 30, "passing_score": 70.0},
    2: {"time_limit_minutes": 40, "passing_score": 70.0},
    3: {"time_limit_minutes": 50, "passing_score": 75.0},
    4: {"time_limit_minutes": 50, "passing_score": 75.0},
    5: {"time_limit_minutes": 60, "passing_score": 80.0},
}


def get_difficulty_metadata(level: int) -> Dict[str, Any]:
    """Get time limit and passing score for a difficulty level."""
    return DIFFICULTY_METADATA.get(
        level, {"time_limit_minutes": 30, "passing_score": 70.0}
    )


def get_sector_data_output_path(sector: str) -> str:
    """Get the path for the production data output of a sector."""
    os.makedirs(DATA_SECTORS_DIR, exist_ok=True)
    return os.path.join(DATA_SECTORS_DIR, f"{sector}.json")


def get_sector_dir(sector: str) -> str:
    """Get the directory for a specific sector."""
    return os.path.join(RESULTS_BY_SECTOR_DIR, sector)


def get_career_dir(sector: str, career: str) -> str:
    """Get the directory for a specific career within a sector."""
    return os.path.join(get_sector_dir(sector), career)


def get_career_subdir(sector: str, career: str, subdir: str) -> str:
    """
    Get a subdirectory within a career folder.

    Subdirs: 'raw', 'validated', 'final', 'diagnostics'
    """
    return os.path.join(get_career_dir(sector, career), subdir)


def get_level_output_path(sector: str, career: str, level: int) -> str:
    """Get the path for the final output of a specific level."""
    final_dir = get_career_subdir(sector, career, "final")
    os.makedirs(final_dir, exist_ok=True)
    return os.path.join(final_dir, f"level_{level}_final.json")


def get_sector_complete_path(sector: str) -> str:
    """Get the path for the complete sector output (all careers combined)."""
    sector_dir = get_sector_dir(sector)
    os.makedirs(sector_dir, exist_ok=True)
    return os.path.join(sector_dir, f"_{sector}_complete.json")


def get_soft_skills_output_path() -> str:
    """Get the path for soft skills final output."""
    soft_skills_dir = os.path.join(RESULTS_BY_SECTOR_DIR, "soft_skills", "final")
    os.makedirs(soft_skills_dir, exist_ok=True)
    return os.path.join(soft_skills_dir, "soft_skills_final.json")


# ------------------------------
# Question generation constants
# ------------------------------

QUESTIONS_INTERNAL = 20
QUESTIONS_SAVED = 20
CHUNK_SIZE = 5
SOFT_SKILLS_COUNT = 20

# Word limits
QUESTION_WORD_MIN = 12
QUESTION_WORD_MAX = 28
OPTION_WORD_MIN = 10
OPTION_WORD_MAX = 24
RATIONALE_WORD_MAX = 30
EXPLANATION_WORD_MIN = 15
EXPLANATION_WORD_MAX = 50

# Model settings
MODEL_NAME_JUNIOR = os.getenv("GEMINI_MODEL_JUNIOR", "models/gemini-2.5-flash")
MODEL_NAME_SENIOR = os.getenv("GEMINI_MODEL_SENIOR", "models/gemini-2.5-pro")
MODEL_NAME_CRITIC = os.getenv(
    "GEMINI_MODEL_CRITIC", "models/gemini-2.5-pro"
)  # Separate critic model

TEMP_JUNIOR = 0.6
TEMP_SENIOR = 0.4
TEMP_CRITIC = 0.3

# ------------------------------
# Retry / Backoff settings
# ------------------------------

# Max retry attempts for different scenarios
MAX_API_ATTEMPTS = 3  # Per API call
MAX_CHUNK_RETRIES = 3  # Per chunk generation
MAX_CRITIC_RETRIES = 2  # Per critic repair

# Backoff settings
BACKOFF_BASE = 2.0  # Exponential base
BACKOFF_MAX_SLEEP = 60  # Max sleep for quota exhaustion (increased from 10)
BACKOFF_JITTER = 2.0  # Random jitter to add

# Throttle pacing
SLEEP_BETWEEN_CHUNKS = 2.0  # Increased from 1.5
SLEEP_AFTER_SUCCESS = 1.0  # After successful chunk
SLEEP_AFTER_ERROR = 3.0  # After error before retry

# API timeout (seconds) - prevents hanging on slow/stuck requests
API_TIMEOUT = 180  # 3 minutes per API call

# ------------------------------
# Sector data
# ------------------------------

# Legacy flat list for backwards compatibility
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

# Sector tracks organized by branches
SECTOR_TRACKS = {
    "technology": {
        "Software Development": [
            "FRONTEND_DEVELOPER",
            "BACKEND_DEVELOPER",
        ],
        "Mobile Development": [
            "IOS_DEVELOPER",
            "ANDROID_DEVELOPER",
            "MOBILE_DEVELOPMENT_CROSS_PLATFORM",
        ],
        "Data Science & AI": [
            "DATA_SCIENTIST",
            "DATA_ANALYST",
            "DATA_ENGINEER",
            "AI_ML_ENGINEER",
        ],
        "Infrastructure & Cloud Operations": [
            "DEVOPS_ENGINEER",
            "CLOUD_ENGINEER",
            "DATABASE_ADMINISTRATOR_DBA",
            "NETWORK_ENGINEER",
            "SYSTEMS_ADMINISTRATOR",
        ],
        "Cybersecurity": [
            "CYBERSECURITY_ANALYST",
        ],
        "Quality Assurance": [
            "QA_AUTOMATION_ENGINEER_SET",
        ],
        "Product & Design": [
            "UX_UI_DESIGNER",
            "TECHNICAL_PRODUCT_MANAGER",
            "TECHNICAL_PROJECT_MANAGER_SCRUM_MASTER",
        ],
    },
    "finance": {
        "Investment Banking & Asset Management": [
            "investment_banker",
            "portfolio_manager",
            "trader",
            "fund_manager",
            "wealth_manager",
        ],
        "Financial Analysis & Planning": [
            "financial_analyst",
            "financial_planner",
            "budget_analyst",
        ],
        "Accounting & Auditing": [
            "accountant",
            "tax_consultant",
            "auditor",
        ],
        "Risk Management & Compliance": [
            "risk_manager",
            "compliance_officer",
            "credit_analyst",
            "insurance_underwriter",
        ],
    },
    "health_social_care": {
        "Nursing & Midwifery": [
            "nurse",
            "midwife",
        ],
        "Allied Health & Therapy": [
            "occupational_therapist",
            "physiotherapist",
            "mental_health_counselor",
        ],
        "Social Care & Support": [
            "care_worker",
            "social_worker",
            "healthcare_assistant",
        ],
        "Public Health": [
            "public_health_officer",
        ],
    },
    "education": {
        "Teaching & Instruction": [
            "teacher",
            "special_need_educator",
        ],
    },
    "construction": {
        "Engineering & Design": [
            "civil_engineer",
            "architect",
            "structural_engineer",
        ],
        "Construction Management & Cost": [
            "site_manager",
            "quantity_surveyor",
            "project_manager",
        ],
        "Trades & Labour": [
            "construction_worker",
        ],
    },
}


def get_all_careers_for_sector(sector: str) -> List[str]:
    """Get a flat list of all careers for a sector (across all branches)."""
    if sector not in SECTOR_TRACKS:
        return []
    branches = SECTOR_TRACKS[sector]
    careers = []
    for branch_careers in branches.values():
        careers.extend(branch_careers)
    return careers


def get_all_careers() -> List[str]:
    """Get a flat list of all careers across all sectors."""
    all_careers = []
    for sector in SECTOR_TRACKS:
        all_careers.extend(get_all_careers_for_sector(sector))
    return all_careers


def get_branches_for_sector(sector: str) -> List[str]:
    """Get list of branch names for a sector."""
    if sector not in SECTOR_TRACKS:
        return []
    return list(SECTOR_TRACKS[sector].keys())


def get_careers_for_branch(sector: str, branch: str) -> List[str]:
    """Get list of careers for a specific branch within a sector."""
    if sector not in SECTOR_TRACKS:
        return []
    branches = SECTOR_TRACKS[sector]
    return branches.get(branch, [])


# ------------------------------
# Sector Metadata (loaded from FULL_TRACKS.json)
# ------------------------------

# Path to the taxonomy JSON file (single source of truth)
# Located at: {geminiGenerator}/FULL_TRACKS.json
FULL_TRACKS_JSON_PATH = os.path.join(_PACKAGE_DIR, "FULL_TRACKS.json")


def _load_sector_metadata() -> Dict[str, Any]:
    """
    Load and transform FULL_TRACKS.json into the SECTOR_METADATA format.

    Transforms the JSON array structure into a dictionary structure:
    - sectors array → dict keyed by sector name
    - branches array → dict keyed by branch name
    - specializations array → dict keyed by specialization name

    Returns:
        Dict with structure: {sector: {description, branches: {branch: {description, specializations: {name: desc}}}}}
    """
    try:
        with open(FULL_TRACKS_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning(f"Failed to load FULL_TRACKS.json: {e}. Using empty metadata.")
        return {}

    metadata = {}

    for sector in data.get("sectors", []):
        sector_name = sector.get("name", "")
        if not sector_name:
            continue

        sector_data = {"description": sector.get("description", ""), "branches": {}}

        for branch in sector.get("branches", []):
            branch_name = branch.get("name", "")
            if not branch_name:
                continue

            branch_data = {
                "description": branch.get("description", ""),
                "specializations": {},
            }

            for spec in branch.get("specializations", []):
                spec_name = spec.get("name", "")
                spec_desc = spec.get("description", "")
                if spec_name:
                    branch_data["specializations"][spec_name] = spec_desc

            sector_data["branches"][branch_name] = branch_data

        metadata[sector_name] = sector_data

    return metadata


# Load metadata from JSON file at module import time
SECTOR_METADATA: Dict[str, Any] = _load_sector_metadata()


# ------------------------------
# Description Lookup Functions
# ------------------------------


def get_sector_description(sector: str) -> str:
    """Get the description for a sector."""
    if sector not in SECTOR_METADATA:
        return ""
    return SECTOR_METADATA[sector].get("description", "")


def get_branch_for_career(sector: str, career: str) -> str:
    """Find which branch a career belongs to within a sector."""
    if sector not in SECTOR_METADATA:
        return ""
    branches = SECTOR_METADATA[sector].get("branches", {})
    for branch_name, branch_data in branches.items():
        specializations = branch_data.get("specializations", {})
        if career in specializations:
            return branch_name
    return ""


def get_branch_description(sector: str, branch: str) -> str:
    """Get the description for a branch within a sector."""
    if sector not in SECTOR_METADATA:
        return ""
    branches = SECTOR_METADATA[sector].get("branches", {})
    if branch not in branches:
        return ""
    return branches[branch].get("description", "")


def get_career_description(sector: str, career: str) -> str:
    """Get the description for a career/specialization."""
    if sector not in SECTOR_METADATA:
        return ""
    branches = SECTOR_METADATA[sector].get("branches", {})
    for branch_data in branches.values():
        specializations = branch_data.get("specializations", {})
        if career in specializations:
            return specializations[career]
    return ""


def get_role_context(sector: str, career: str) -> Dict[str, str]:
    """
    Get complete role context for a sector/career combination.

    Returns a dict with:
        - sector_description
        - branch
        - branch_description
        - career_description
    """
    return {
        "sector_description": get_sector_description(sector),
        "branch": get_branch_for_career(sector, career),
        "branch_description": get_branch_description(
            sector, get_branch_for_career(sector, career)
        ),
        "career_description": get_career_description(sector, career),
    }


# ------------------------------
# Utility functions
# ------------------------------


def word_count(text: str) -> int:
    """Count words in a text string."""
    if not text:
        return 0
    return len(text.strip().split())


def ensure_dirs():
    """Create output directories if they don't exist."""
    # New organized structure
    os.makedirs(RESULTS_BY_SECTOR_DIR, exist_ok=True)
    os.makedirs(RESULTS_COMBINED_DIR, exist_ok=True)
    os.makedirs(RESULTS_LOGS_DIR, exist_ok=True)

    # Legacy directories (for backwards compatibility)
    os.makedirs(RAW_OUTPUT_DIR, exist_ok=True)
    os.makedirs(CLEAN_OUTPUT_DIR, exist_ok=True)


def ensure_career_dirs(sector: str, career: str):
    """Create all subdirectories for a career."""
    for subdir in ["raw", "validated", "final", "diagnostics"]:
        os.makedirs(get_career_subdir(sector, career, subdir), exist_ok=True)


def normalise_question_text(text: str) -> str:
    """Normalize question text for deduplication."""
    return re.sub(r"\s+", " ", text.strip().lower())


def backoff(attempt: int, error_type: str = "rate_limit"):
    """
    Exponential backoff with jitter for API errors.

    Args:
        attempt: Current attempt number (1-based)
        error_type: Type of error ('rate_limit', 'unavailable', 'quota_exhausted')

    For quota exhaustion (429), sleep longer.
    For temporary unavailable (503), use standard backoff.
    """
    if error_type == "quota_exhausted":
        # Longer sleep for quota - wait 30-60 seconds
        base_sleep = min(BACKOFF_MAX_SLEEP, 30 + (attempt * 10))
    else:
        # Standard exponential backoff
        base_sleep = min(BACKOFF_MAX_SLEEP, (BACKOFF_BASE**attempt))

    jitter = random.uniform(0, BACKOFF_JITTER)
    sleep_time = base_sleep + jitter

    logging.warning(
        f"⏳ Backoff sleeping {sleep_time:.2f}s (attempt {attempt}, type={error_type})..."
    )
    time.sleep(sleep_time)


def adaptive_sleep(base_sleep: float, consecutive_errors: int = 0):
    """
    Adaptive sleep that increases with consecutive errors.

    Args:
        base_sleep: Base sleep time
        consecutive_errors: Number of consecutive errors encountered
    """
    multiplier = 1 + (consecutive_errors * 0.5)  # Increase by 50% per error
    sleep_time = base_sleep * multiplier
    time.sleep(sleep_time)


# ------------------------------
# Checkpoint management
# ------------------------------


def load_checkpoint() -> Dict[str, Any]:
    """Load checkpoint from file, returning empty dict if not found."""
    if not os.path.exists(CHECKPOINT_FILE):
        return {}
    try:
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logging.warning(f"Failed to load checkpoint: {e}")
        return {}


def save_checkpoint(checkpoint: Dict[str, Any]):
    """Save checkpoint to file."""
    ensure_dirs()
    try:
        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
    except IOError as e:
        logging.error(f"Failed to save checkpoint: {e}")


def save_partial_pool(pool_data: Dict[str, Any]):
    """Save partial pool data for recovery."""
    ensure_dirs()
    try:
        with open(PARTIAL_POOL_FILE, "w", encoding="utf-8") as f:
            json.dump(pool_data, f, indent=2, ensure_ascii=False)
        logging.info(f"💾 Partial pool saved to {PARTIAL_POOL_FILE}")
    except IOError as e:
        logging.error(f"Failed to save partial pool: {e}")


def load_partial_pool() -> Optional[Dict[str, Any]]:
    """Load partial pool data for recovery."""
    if not os.path.exists(PARTIAL_POOL_FILE):
        return None
    try:
        with open(PARTIAL_POOL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logging.warning(f"Failed to load partial pool: {e}")
        return None


# ------------------------------
# Safe serialization for diagnostics
# ------------------------------


def serialize_validation_errors(errors: Any) -> Any:
    """
    Safely serialize Pydantic validation errors for JSON output.

    Handles:
    - Pydantic v2 error dicts with nested ValueError objects
    - Plain strings
    - Lists of errors
    - Any other non-serializable objects
    """
    if errors is None:
        return None

    if isinstance(errors, str):
        return errors

    if isinstance(errors, (int, float, bool)):
        return errors

    if isinstance(errors, Exception):
        return {
            "error_type": type(errors).__name__,
            "error_message": str(errors),
        }

    if isinstance(errors, list):
        return [serialize_validation_errors(e) for e in errors]

    if isinstance(errors, dict):
        result = {}
        for key, value in errors.items():
            # Handle special 'ctx' dict that may contain ValueError objects
            if key == "ctx" and isinstance(value, dict):
                result[key] = {
                    k: serialize_validation_errors(v) for k, v in value.items()
                }
            else:
                result[key] = serialize_validation_errors(value)
        return result

    # Fallback: convert to string
    try:
        # Try JSON serialization first
        json.dumps(errors)
        return errors
    except (TypeError, ValueError):
        return str(errors)


def format_validation_errors_for_critic(errors: Any) -> str:
    """
    Format validation errors into a human-readable string for the critic.

    This helps the critic understand exactly what needs to be fixed.
    """
    if not errors:
        return "Unknown validation error"

    lines = []
    serialized = serialize_validation_errors(errors)

    if isinstance(serialized, list):
        for i, err in enumerate(serialized, 1):
            if isinstance(err, dict):
                loc = err.get("loc", [])
                msg = err.get("msg", "Unknown error")
                err_type = err.get("type", "unknown")

                # Format location path
                loc_str = " → ".join(str(x) for x in loc) if loc else "root"
                lines.append(f"  {i}. [{loc_str}] {msg} (type: {err_type})")
            else:
                lines.append(f"  {i}. {err}")
    else:
        lines.append(f"  {serialized}")

    return "\n".join(lines)


# ------------------------------
# Graceful shutdown handling
# ------------------------------


class GracefulShutdown:
    """
    Context manager for graceful shutdown handling.

    Catches SIGINT (Ctrl+C) and SIGTERM, sets a flag, and allows
    the generator to save state before exiting.
    """

    def __init__(self):
        self.shutdown_requested = False
        self._original_sigint = None
        self._original_sigterm = None

    def __enter__(self):
        self._original_sigint = signal.getsignal(signal.SIGINT)
        self._original_sigterm = signal.getsignal(signal.SIGTERM)

        signal.signal(signal.SIGINT, self._handler)
        signal.signal(signal.SIGTERM, self._handler)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.signal(signal.SIGINT, self._original_sigint)
        signal.signal(signal.SIGTERM, self._original_sigterm)

    def _handler(self, signum, frame):
        if self.shutdown_requested:
            # Second signal - force exit
            logging.warning("\n⚠️  Force shutdown requested. Exiting immediately...")
            raise SystemExit(1)

        self.shutdown_requested = True
        logging.warning(
            "\n\n🛑 Shutdown requested (Ctrl+C). Finishing current operation...\n"
            "   Press Ctrl+C again to force exit.\n"
        )

    def check(self) -> bool:
        """Check if shutdown was requested."""
        return self.shutdown_requested


# Global shutdown handler instance
_shutdown_handler: Optional[GracefulShutdown] = None


def get_shutdown_handler() -> GracefulShutdown:
    """Get or create the global shutdown handler."""
    global _shutdown_handler
    if _shutdown_handler is None:
        _shutdown_handler = GracefulShutdown()
    return _shutdown_handler


def is_shutdown_requested() -> bool:
    """Check if shutdown was requested."""
    if _shutdown_handler is None:
        return False
    return _shutdown_handler.check()
