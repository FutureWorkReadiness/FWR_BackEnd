# Gemini Quiz Generator V4

A Python-based automated prompt-generation system that uses the Google Gemini API to generate structured multiple-choice interview questions in batches.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Installation](#installation)
- [Virtual Environment](#virtual-environment)
- [Usage](#usage)
- [Configuration](#configuration)
- [V4 Improvements Summary](#v4-improvements-summary)
- [Detailed File Changes](#detailed-file-changes)
  - [settings.py](#1-settingspy---enhanced-configuration--utilities)
  - [system_prompts.py](#2-system_promptspy---stronger-word-count-enforcement)
  - [json_utils.py](#3-json_utilspy---robust-json-handling)
  - [generator.py](#4-generatorpy---major-rewrite-v4)
  - [main.py](#5-mainpy---enhanced-cli)
- [Error Handling](#error-handling)
- [Troubleshooting](#troubleshooting)

---

## Overview

This system generates interview questions for various sectors (technology, finance, healthcare, etc.) and career tracks. Questions are generated in chunks, validated against strict schemas, and repaired automatically if they fail validation.

### Key Features

- **Chunked Generation**: Questions are generated in batches of 5, with checkpointing for resume capability
- **Critic Repair Pipeline**: Failed validations are sent to a "critic" model for automatic repair
- **Graceful Shutdown**: Ctrl+C saves progress instead of crashing
- **Adaptive Throttling**: Automatically adjusts request pacing based on API errors
- **Comprehensive Diagnostics**: All failures are logged with detailed error information

---

## Quick Start

Here's a complete step-by-step guide to get the script running after cloning:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd geminiGenerator
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

**macOS / Linux:**

```bash
source venv/bin/activate
```

**Windows (Command Prompt):**

```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**

```powershell
venv\Scripts\Activate.ps1
```

> ✅ When activated, you'll see `(venv)` at the beginning of your terminal prompt.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Your API Key

```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

Or create a `.env` file manually and add:

```
GEMINI_API_KEY=your_api_key_here
```

### 6. Run the Script

**Test mode (recommended first):**

```bash
python -m app.main --test --sector technology --career FRONTEND_DEVELOPER --level 1
```

**Full generation:**

```bash
python -m app.main
```

### 7. Deactivate the Virtual Environment (When Done)

```bash
deactivate
```

---

## Architecture

```
geminiGenerator/
├── app/
│   ├── config/
│   │   └── settings.py          # Configuration, constants, utilities
│   ├── prompts/
│   │   └── system_prompts.py    # LLM system prompts
│   ├── schema/
│   │   ├── models.py            # Pydantic validation models
│   │   └── json_utils.py        # JSON extraction and cleaning
│   ├── services/
│   │   └── generator.py         # Core generation engine
│   └── main.py                  # Entry point
├── raw_responses_gemini_v2.5/   # Raw API outputs (created at runtime)
├── clean_quiz_chunks_gemini_v2.5/ # Validated outputs (created at runtime)
├── requirements.txt
└── README.md
```

---

## Installation

1. **Clone the repository**

2. **Create and activate virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

---

## Virtual Environment

### What is a Virtual Environment?

A virtual environment is an isolated Python environment that keeps project dependencies separate from your system Python. This prevents version conflicts between projects.

### Activating the Virtual Environment

You must activate the virtual environment **every time** you open a new terminal session to work on this project.

**macOS / Linux:**

```bash
source venv/bin/activate
```

**Windows (Command Prompt):**

```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**

```powershell
venv\Scripts\Activate.ps1
```

> 💡 **Tip:** You'll know the virtual environment is active when you see `(venv)` at the start of your terminal prompt:
>
> ```
> (venv) user@computer:~/geminiGenerator$
> ```

### Deactivating the Virtual Environment

When you're finished working on the project, deactivate the virtual environment:

```bash
deactivate
```

The `(venv)` prefix will disappear from your prompt.

### Common Virtual Environment Issues

| Issue                       | Solution                                                                    |
| --------------------------- | --------------------------------------------------------------------------- |
| `command not found: python` | Use `python3` instead of `python`                                           |
| `No module named 'google'`  | You forgot to activate the venv. Run `source venv/bin/activate`             |
| Packages not installing     | Make sure venv is activated (check for `(venv)` prefix)                     |
| PowerShell script blocked   | Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |

### Recreating the Virtual Environment

If your virtual environment becomes corrupted:

```bash
# Remove the old venv
rm -rf venv

# Create a fresh one
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Usage

### Run Full Generation

```bash
python -m app.main
```

### Test Mode (Single Career/Level)

```bash
python -m app.main --test --sector technology --career FRONTEND_DEVELOPER --level 1
```

### Test soft skills questions

```bash
python -m app.main --test --soft-skills
```

### Check Progress Status

```bash
python -m app.main --status
```

### Verbose Logging

```bash
python -m app.main --verbose
```

### CLI Options

| Option            | Description                                        |
| ----------------- | -------------------------------------------------- |
| `--test`          | Run single career/level instead of full generation |
| `--sector`        | Sector for test mode (default: technology)         |
| `--career`        | Career for test mode (default: FRONTEND_DEVELOPER) |
| `--level`         | Level 1-5 for test mode (default: 1)               |
| `--verbose`, `-v` | Enable debug logging                               |
| `--status`        | Show checkpoint progress and exit                  |

---

## Configuration

### Environment Variables

| Variable              | Default                   | Description                |
| --------------------- | ------------------------- | -------------------------- |
| `GEMINI_API_KEY`      | (required)                | Your Google Gemini API key |
| `GEMINI_MODEL_JUNIOR` | `models/gemini-2.5-flash` | Model for levels 1-2       |
| `GEMINI_MODEL_SENIOR` | `models/gemini-2.5-pro`   | Model for levels 3-5       |
| `GEMINI_MODEL_CRITIC` | `models/gemini-2.5-pro`   | Model for critic repairs   |

### Key Constants (in `settings.py`)

| Constant             | Value | Description                            |
| -------------------- | ----- | -------------------------------------- |
| `QUESTIONS_INTERNAL` | 20    | Questions to generate per career/level |
| `CHUNK_SIZE`         | 5     | Questions per API call                 |
| `QUESTION_WORD_MIN`  | 12    | Minimum words in question text         |
| `QUESTION_WORD_MAX`  | 28    | Maximum words in question text         |
| `OPTION_WORD_MIN`    | 10    | Minimum words in option text           |
| `OPTION_WORD_MAX`    | 24    | Maximum words in option text           |
| `MAX_API_ATTEMPTS`   | 3     | Retries per API call                   |
| `MAX_CHUNK_RETRIES`  | 3     | Retries per chunk generation           |
| `BACKOFF_MAX_SLEEP`  | 60    | Maximum backoff sleep (seconds)        |

---

## V4 Improvements Summary

### Problems Solved

| Issue                                | Solution                                                 |
| ------------------------------------ | -------------------------------------------------------- |
| **503 UNAVAILABLE errors**           | Better error classification + longer adaptive backoff    |
| **429 RESOURCE_EXHAUSTED**           | Quota-specific backoff (30-60 seconds)                   |
| **Short option word counts**         | Strengthened prompts + pre-validation + critic awareness |
| **ValueError not JSON serializable** | Safe recursive error serialization                       |
| **KeyboardInterrupt crashes**        | Graceful shutdown handler saves progress                 |
| **Critic failures**                  | Multi-attempt critic + fallback simple prompt            |

### New Features

- ✅ Error type classification (rate limit vs quota vs unavailable)
- ✅ Adaptive sleep based on consecutive errors
- ✅ Pre-validation word count checking
- ✅ Automatic word count truncation for long text
- ✅ Validation errors passed to critic for targeted fixes
- ✅ Fallback critic prompt for simpler repairs
- ✅ Dedicated word-count fixer as last resort
- ✅ Partial progress saving during generation
- ✅ CLI with test mode, status, and verbose options

---

## Detailed File Changes

### 1. `settings.py` — Enhanced Configuration & Utilities

**Location**: `app/config/settings.py`

#### New Constants Added

```python
# Dedicated critic model (can be different from generator)
MODEL_NAME_CRITIC = os.getenv("GEMINI_MODEL_CRITIC", "models/gemini-2.5-pro")

# Retry settings
MAX_API_ATTEMPTS = 3      # Per API call
MAX_CHUNK_RETRIES = 3     # Per chunk generation
MAX_CRITIC_RETRIES = 2    # Per critic repair

# Backoff settings
BACKOFF_BASE = 2.0        # Exponential base
BACKOFF_MAX_SLEEP = 60    # Max sleep (increased from 10)
BACKOFF_JITTER = 2.0      # Random jitter

# Throttle pacing
SLEEP_BETWEEN_CHUNKS = 2.0
SLEEP_AFTER_SUCCESS = 1.0
SLEEP_AFTER_ERROR = 3.0

# New files
PARTIAL_POOL_FILE = os.path.join(RAW_OUTPUT_DIR, "partial_pool.json")
```

#### New Functions

| Function                                          | Purpose                                                                                                           |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `backoff(attempt, error_type)`                    | Exponential backoff with error-type awareness. Quota exhaustion gets 30-60s sleep.                                |
| `adaptive_sleep(base, errors)`                    | Increases sleep time based on consecutive error count                                                             |
| `serialize_validation_errors(errors)`             | **Fixes "ValueError not JSON serializable"** — recursively converts all Pydantic error objects to JSON-safe types |
| `format_validation_errors_for_critic(errors)`     | Formats errors as human-readable text for critic prompts                                                          |
| `save_partial_pool(data)` / `load_partial_pool()` | Save/restore partial progress during interrupts                                                                   |

#### New Class: `GracefulShutdown`

```python
class GracefulShutdown:
    """
    Context manager that catches SIGINT (Ctrl+C) and SIGTERM.
    Sets a flag instead of crashing, allowing clean exit.
    """
```

**Usage**:

```python
with GracefulShutdown() as handler:
    while not handler.check():
        # do work
        pass
    # cleanup and save progress
```

---

### 2. `system_prompts.py` — Stronger Word-Count Enforcement

**Location**: `app/prompts/system_prompts.py`

#### Changes to `SYS_PROMPT_GENERATOR`

**Before**: Word counts mentioned once in a list  
**After**: Multiple reinforcement strategies

1. **Visual Warning Block**

   ```
   ════════════════════════════════════════════════════════════════════════════════
   ⚠️ CRITICAL WORD COUNT REQUIREMENTS — READ CAREFULLY ⚠️
   ════════════════════════════════════════════════════════════════════════════════
   ```

2. **Explicit Rejection Warning**

   ```
   IMPORTANT: Options that are only 5-8 words will be REJECTED.
   Each option MUST be a complete, detailed sentence of at least {omin} words.
   ```

3. **Self-Check Instruction**

   ```
   BEFORE OUTPUTTING, mentally verify:
   ✓ Is each option at least {omin} words? Count them.
   ✓ Is each question at least {qmin} words?
   ```

4. **Improved Few-Shot Example**
   - Each option is now 15-20 words (previously shorter)
   - Added notice: "Each option above is 15-20 words. Your options must also be this length!"

#### Changes to `SYS_PROMPT_CRITIC`

**Before**: Generic "fix the JSON" instruction  
**After**: Targeted repair instructions

1. **Explicit Fix Instructions**

   ```
   HOW TO FIX SHORT OPTIONS:
   If an option like "Load balancers distribute traffic" (only 4 words) is too short:
   → Expand it to: "Load balancers distribute incoming network traffic evenly
      across multiple backend servers to prevent overload" (15 words)
   ```

2. **Self-Check Before Output**
   ```
   BEFORE OUTPUTTING, verify:
   ✓ Every option has at least {omin} words (count them!)
   ```

#### New Prompts Added

| Prompt                       | Purpose                                                                            |
| ---------------------------- | ---------------------------------------------------------------------------------- |
| `SYS_PROMPT_CRITIC_SIMPLE`   | Fallback prompt when main critic fails. Simpler instructions focused on structure. |
| `SYS_PROMPT_WORDCOUNT_FIXER` | Dedicated prompt for expanding short options as a last resort.                     |

---

### 3. `json_utils.py` — Robust JSON Handling

**Location**: `app/schema/json_utils.py`

#### Improved `extract_json_text()`

**Before**: Simple regex extraction  
**After**: Multi-stage extraction

````python
# 1. Remove code fences (```json ... ```)
# 2. Try direct parse
# 3. Find first { to last } and clean
# 4. Fallback: regex search for any JSON object
````

#### New Function: `_clean_json_string()`

```python
def _clean_json_string(text: str) -> str:
    # Remove trailing commas before } or ]
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    # Remove control characters
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text
```

#### New Pre-Validation Functions

| Function                           | Purpose                                                                               |
| ---------------------------------- | ------------------------------------------------------------------------------------- |
| `check_word_counts(data)`          | Returns `(is_valid, issues_list)` — checks all word counts before Pydantic validation |
| `format_word_count_issues(issues)` | Human-readable formatting for logging                                                 |
| `attempt_word_count_fix(data)`     | Auto-truncates overly long text (cannot expand short text without LLM)                |
| `get_short_option_summary(data)`   | Formatted summary of short options for critic prompt                                  |

**Example Output of `format_word_count_issues()`**:

```
Word count violations found:
  • quiz_pool[0].options[A].text: 6 words (TOO SHORT, need 10-24)
    Text: "Load balancers distribute traffic evenly"
  • quiz_pool[1].options[C].text: 5 words (TOO SHORT, need 10-24)
    Text: "Caching improves response times"
```

---

### 4. `generator.py` — Major Rewrite (V4)

**Location**: `app/services/generator.py`

#### New: Error Classification System

```python
class APIErrorType(Enum):
    RATE_LIMIT = "rate_limit"           # 429 - standard backoff
    QUOTA_EXHAUSTED = "quota_exhausted" # 429 + "quota" - long backoff (30-60s)
    UNAVAILABLE = "unavailable"         # 503 - retry with backoff
    TIMEOUT = "timeout"                 # Request timeout - retry
    PERMANENT = "permanent"             # 400/401/403 - don't retry
    UNKNOWN = "unknown"                 # Cautious retry

def classify_api_error(exception: Exception) -> APIErrorType:
    """Analyzes exception string to determine error type."""
```

**Why This Matters**: Different errors need different handling:

- `429 QUOTA_EXHAUSTED` → Sleep 30-60 seconds
- `503 UNAVAILABLE` → Standard exponential backoff
- `401 UNAUTHORIZED` → Don't retry (permanent error)

#### Improved `_call_gemini_json()`

| Change             | Before              | After                            |
| ------------------ | ------------------- | -------------------------------- |
| Max attempts       | 2                   | 3 (configurable)                 |
| Backoff strategy   | Same for all errors | Error-type specific              |
| Shutdown check     | None                | Checks `is_shutdown_requested()` |
| Consecutive errors | Not tracked         | Tracked for adaptive sleep       |

#### New: `_write_diagnostic_file()`

**Before**: Direct `json.dump()` which failed on `ValueError` objects  
**After**: Safe serialization

```python
def _write_diagnostic_file(self, filepath: str, data: Dict) -> bool:
    safe_data = {}
    for key, value in data.items():
        if key in ("validation_errors", "critic_validation_errors"):
            safe_data[key] = serialize_validation_errors(value)  # Safe conversion
        else:
            try:
                json.dumps(value)
                safe_data[key] = value
            except (TypeError, ValueError):
                safe_data[key] = str(value)  # Fallback to string
```

#### Improved Critic Pipeline: `_run_critic_repair()`

**Before**:

- Single critic attempt
- No error context passed
- Same prompt always

**After**:

```python
def _run_critic_repair(self, failed_json, validation_errors, key_base, model, attempt):
    # 1. Check word counts specifically
    _, word_issues = check_word_counts(failed_json)

    # 2. Format errors for critic
    error_summary = format_validation_errors_for_critic(validation_errors)

    # 3. Build prompt with error context
    critic_user_prompt = f"""
    The following JSON failed validation. Fix all issues.

    === VALIDATION ERRORS ===
    {error_summary}

    === WORD COUNT ISSUES ===
    {word_issue_summary}

    === JSON TO FIX ===
    {json.dumps(failed_json)}
    """

    # 4. Try main critic prompt, then fallback to simple prompt
    for critic_attempt in range(1, MAX_CRITIC_RETRIES + 1):
        prompt = SYS_PROMPT_CRITIC if critic_attempt == 1 else SYS_PROMPT_CRITIC_SIMPLE
        # ... call API and validate

    # 5. Last resort: dedicated word-count fixer
    return self._try_wordcount_fixer(critic_output, key_base)
```

#### Graceful Shutdown Integration

**Before**: Ctrl+C crashes immediately, losing all progress

**After**:

```python
def generate_all(self):
    with self.shutdown_handler:
        try:
            for sector, careers in SECTOR_TRACKS.items():
                for career in careers:
                    for level in range(1, 6):
                        if is_shutdown_requested():
                            break
                        self.generate_for_career_level(sector, career, level)
        finally:
            # Always saves progress
            if self.results_bank:
                json.dump(self.results_bank, f)

            if is_shutdown_requested():
                print("""
                🛑 Generation interrupted. Progress saved.
                   To resume, run the script again.
                   Checkpoint file: raw_responses_gemini_v2.5/generation_checkpoint.json
                """)
```

#### Chunk Recovery System

```python
def _save_chunk(self, key_base: str, questions: List[QuestionModel]):
    """Save successful chunk for potential recovery."""

def _load_chunk_to_pool(self, key_base: str, pool: List[QuestionModel]):
    """Load previously saved chunk into the pool."""

def _save_partial_progress(self, pool, job_key, checkpoint):
    """Save partial progress for recovery."""
```

---

### 5. `main.py` — Enhanced CLI

**Location**: `app/main.py`

#### New Features

| Feature            | Description                                     |
| ------------------ | ----------------------------------------------- |
| **argparse CLI**   | Proper command-line interface with help         |
| **Test mode**      | `--test` runs single career/level for debugging |
| **Status command** | `--status` shows checkpoint progress            |
| **Verbose mode**   | `--verbose` enables debug logging               |
| **File logging**   | Logs to `generation.log` in addition to console |
| **Reduced noise**  | HTTP libraries set to WARNING level             |

#### Usage Examples

```bash
# Full generation
python -m app.main

# Test single career
python -m app.main --test --sector technology --career DATA_SCIENTIST --level 3

# Check what's been completed
python -m app.main --status

# Debug mode
python -m app.main --test --verbose
```

---

## Error Handling

### API Errors

| Error                    | Handling                                 |
| ------------------------ | ---------------------------------------- |
| `429 RESOURCE_EXHAUSTED` | 30-60 second backoff, then retry         |
| `503 UNAVAILABLE`        | Exponential backoff (2^attempt + jitter) |
| `500/502/504`            | Retry with backoff                       |
| `400/401/403`            | Don't retry (permanent error)            |
| Timeout                  | Retry with backoff                       |

### Validation Errors

1. **Pre-validation**: Check word counts before Pydantic
2. **Auto-fix**: Truncate overly long text
3. **Critic repair**: Send to critic with error context
4. **Fallback critic**: Try simpler prompt
5. **Word-count fixer**: Dedicated expansion prompt
6. **Skip chunk**: Move to next chunk after all retries exhausted

### Interrupt Handling

- **First Ctrl+C**: Sets shutdown flag, finishes current operation, saves progress
- **Second Ctrl+C**: Force exit

---

## Troubleshooting

### "GEMINI_API_KEY not set"

```bash
# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env
```

### "429 RESOURCE_EXHAUSTED" repeatedly

- You've exceeded your API quota
- Wait 1-2 minutes or check your Google Cloud quotas
- The system will auto-retry with 30-60s backoff

### "503 UNAVAILABLE" / "Model is overloaded"

- Gemini servers are busy
- System will auto-retry with exponential backoff
- If persistent, try again later

### Short option word counts failing

- V4 has stronger prompt enforcement
- Critic now receives specific error details
- Word-count fixer tries to expand short options
- Check `raw_responses_gemini_v2.5/` for diagnostic files

### Resume after interruption

```bash
# Check what's completed
python -m app.main --status

# Resume (automatically skips completed chunks)
python -m app.main
```

---

## Output Files

| Directory/File                      | Contents                                          |
| ----------------------------------- | ------------------------------------------------- |
| `raw_responses_gemini_v2.5/`        | Raw API responses, error diagnostics, checkpoints |
| `clean_quiz_chunks_gemini_v2.5/`    | Validated/repaired chunks, critic outputs         |
| `sector_quiz_bank_gemini_v2.5.json` | Final combined output                             |
| `generation.log`                    | Full generation log                               |
| `generation_checkpoint.json`        | Resume checkpoint                                 |

---

## License

See [LICENSE](LICENSE) file.
