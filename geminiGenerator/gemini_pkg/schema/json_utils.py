"""
JSON Utilities for cleaning and extracting JSON from Gemini responses.

Improvements:
- Better handling of nested JSON objects
- More robust code fence removal
- Handles common Gemini quirks (trailing text, embedded markdown)
- Pre-validation word count checking
"""

import json
import re
import logging
from typing import Optional, List, Dict, Any, Tuple

from gemini_pkg.config.settings import (
    word_count,
    QUESTION_WORD_MIN,
    QUESTION_WORD_MAX,
    OPTION_WORD_MIN,
    OPTION_WORD_MAX,
    RATIONALE_WORD_MAX,
    EXPLANATION_WORD_MIN,
    EXPLANATION_WORD_MAX,
)


# Regex to find JSON object - improved to handle nested structures
JSON_OBJECT_RE = re.compile(r"\{[\s\S]*\}", re.MULTILINE)


def extract_json_text(raw_text: str) -> Optional[str]:
    """
    Extract valid JSON from raw text that may contain markdown, code fences, etc.

    Args:
        raw_text: Raw text response from Gemini

    Returns:
        Cleaned JSON string, or None if extraction fails
    """
    if not raw_text:
        return None

    raw = raw_text.strip()

    # Remove code fences (```json ... ``` or ``` ... ```)
    if raw.startswith("```"):
        # Remove opening fence with optional language tag
        raw = re.sub(r"^```(?:json|JSON)?\s*\n?", "", raw, flags=re.IGNORECASE)
        # Remove closing fence
        raw = re.sub(r"\n?```\s*$", "", raw)
        raw = raw.strip()

    # Remove any trailing backticks that might remain
    raw = raw.rstrip("`").strip()

    # Try direct parse first
    try:
        json.loads(raw)
        return raw
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in the text
    # First, find the first { and the matching last }
    first_brace = raw.find("{")
    if first_brace == -1:
        return None

    last_brace = raw.rfind("}")
    if last_brace == -1 or last_brace <= first_brace:
        return None

    candidate = raw[first_brace : last_brace + 1]

    # Clean up common issues
    candidate = _clean_json_string(candidate)

    # Try to parse the cleaned candidate
    try:
        json.loads(candidate)
        return candidate
    except json.JSONDecodeError as e:
        logging.debug(f"JSON parse error after cleaning: {e}")
        pass

    # Last resort: try to find any valid JSON object
    match = JSON_OBJECT_RE.search(raw)
    if match:
        candidate = match.group(0)
        candidate = _clean_json_string(candidate)
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass

    return None


def _clean_json_string(text: str) -> str:
    """
    Clean common JSON issues from text.

    Fixes:
    - Trailing commas before } or ]
    - Control characters
    - Invalid escape sequences
    """
    # Remove trailing commas before } or ]
    text = re.sub(r",(\s*[}\]])", r"\1", text)

    # Remove control characters except newlines and tabs
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Fix common escape issues (unescaped quotes in strings)
    # This is tricky - we need to be careful not to break valid JSON

    return text


def clean_json_text(raw_text: str) -> Optional[dict]:
    """
    Extract and parse JSON from raw text.

    Args:
        raw_text: Raw text response from Gemini

    Returns:
        Parsed JSON as dict, or None if parsing fails
    """
    json_str = extract_json_text(raw_text)
    if not json_str:
        return None
    try:
        result = json.loads(json_str)
        # Handle case where Gemini returns array instead of object
        result = _unwrap_array_if_needed(result)
        return result
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        return None


def _unwrap_array_if_needed(data: Any) -> Any:
    """
    If Gemini returns [{"quiz_pool": [...]}] instead of {"quiz_pool": [...]},
    unwrap the outer array automatically.

    This is a common Gemini quirk where it wraps the response in an array.
    """
    if isinstance(data, list):
        if len(data) == 1 and isinstance(data[0], dict):
            # Single-element array containing a dict - unwrap it
            logging.warning(
                "⚠️ Auto-unwrapped array response from Gemini (was [{{...}}], now {{...}})"
            )
            return data[0]
        elif len(data) > 1:
            # Multiple elements - check if they all have quiz_pool and merge
            if all(isinstance(item, dict) and "quiz_pool" in item for item in data):
                logging.warning(
                    f"⚠️ Merging {len(data)} quiz_pool arrays from Gemini response"
                )
                merged_pool = []
                for item in data:
                    merged_pool.extend(item.get("quiz_pool", []))
                return {"quiz_pool": merged_pool}
    return data


# =============================================================================
# PRE-VALIDATION WORD COUNT CHECKING
# =============================================================================


def check_word_counts(data: dict) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Pre-validate word counts before Pydantic validation.

    Returns:
        Tuple of (is_valid, list_of_issues)
        Each issue is a dict with: location, current_count, required_range, text_preview
    """
    issues = []

    if not isinstance(data, dict):
        return False, [{"error": "Data is not a dict"}]

    quiz_pool = data.get("quiz_pool", [])
    if not isinstance(quiz_pool, list):
        return False, [{"error": "quiz_pool is not a list"}]

    for q_idx, question in enumerate(quiz_pool):
        if not isinstance(question, dict):
            issues.append(
                {"location": f"quiz_pool[{q_idx}]", "error": "Question is not a dict"}
            )
            continue

        # Check question text
        q_text = question.get("question", "")
        q_words = word_count(q_text)
        if not (QUESTION_WORD_MIN <= q_words <= QUESTION_WORD_MAX):
            issues.append(
                {
                    "location": f"quiz_pool[{q_idx}].question",
                    "current_count": q_words,
                    "required_range": f"{QUESTION_WORD_MIN}-{QUESTION_WORD_MAX}",
                    "text_preview": q_text[:50] + "..." if len(q_text) > 50 else q_text,
                    "issue": "short" if q_words < QUESTION_WORD_MIN else "long",
                }
            )

        # Check explanation
        exp_text = question.get("explanation", "")
        exp_words = word_count(exp_text)
        if not (EXPLANATION_WORD_MIN <= exp_words <= EXPLANATION_WORD_MAX):
            issues.append(
                {
                    "location": f"quiz_pool[{q_idx}].explanation",
                    "current_count": exp_words,
                    "required_range": f"{EXPLANATION_WORD_MIN}-{EXPLANATION_WORD_MAX}",
                    "text_preview": (
                        exp_text[:50] + "..." if len(exp_text) > 50 else exp_text
                    ),
                    "issue": "short" if exp_words < EXPLANATION_WORD_MIN else "long",
                }
            )

        # Check options
        options = question.get("options", [])
        if not isinstance(options, list):
            issues.append(
                {
                    "location": f"quiz_pool[{q_idx}].options",
                    "error": "Options is not a list",
                }
            )
            continue

        for opt_idx, option in enumerate(options):
            if not isinstance(option, dict):
                continue

            opt_text = option.get("text", "")
            opt_words = word_count(opt_text)
            opt_key = option.get("key", f"[{opt_idx}]")

            if not (OPTION_WORD_MIN <= opt_words <= OPTION_WORD_MAX):
                issues.append(
                    {
                        "location": f"quiz_pool[{q_idx}].options[{opt_key}].text",
                        "current_count": opt_words,
                        "required_range": f"{OPTION_WORD_MIN}-{OPTION_WORD_MAX}",
                        "text_preview": (
                            opt_text[:50] + "..." if len(opt_text) > 50 else opt_text
                        ),
                        "issue": "short" if opt_words < OPTION_WORD_MIN else "long",
                    }
                )

            # Check rationale
            rationale = option.get("rationale", "")
            rat_words = word_count(rationale)
            if rat_words > RATIONALE_WORD_MAX:
                issues.append(
                    {
                        "location": f"quiz_pool[{q_idx}].options[{opt_key}].rationale",
                        "current_count": rat_words,
                        "required_range": f"0-{RATIONALE_WORD_MAX}",
                        "text_preview": (
                            rationale[:50] + "..." if len(rationale) > 50 else rationale
                        ),
                        "issue": "long",
                    }
                )

    return len(issues) == 0, issues


def format_word_count_issues(issues: List[Dict[str, Any]]) -> str:
    """
    Format word count issues for logging or critic prompt.
    """
    if not issues:
        return "No word count issues found."

    lines = ["Word count violations found:"]
    for issue in issues:
        if "error" in issue:
            lines.append(f"  • {issue['location']}: {issue['error']}")
        else:
            status = "TOO SHORT" if issue.get("issue") == "short" else "TOO LONG"
            lines.append(
                f"  • {issue['location']}: {issue['current_count']} words ({status}, "
                f"need {issue['required_range']})"
            )
            lines.append(f"    Text: \"{issue['text_preview']}\"")

    return "\n".join(lines)


def attempt_word_count_fix(data: dict) -> dict:
    """
    Attempt to fix obvious word count issues in the data.

    This is a best-effort fix for simple cases:
    - Truncates overly long text
    - Cannot reliably expand short text (need LLM for that)

    Returns the potentially modified data.
    """
    if not isinstance(data, dict):
        return data

    quiz_pool = data.get("quiz_pool", [])
    if not isinstance(quiz_pool, list):
        return data

    for question in quiz_pool:
        if not isinstance(question, dict):
            continue

        # Truncate long question text
        q_text = question.get("question", "")
        q_words = q_text.split()
        if len(q_words) > QUESTION_WORD_MAX:
            question["question"] = " ".join(q_words[:QUESTION_WORD_MAX])

        # Truncate long explanation
        exp_text = question.get("explanation", "")
        exp_words = exp_text.split()
        if len(exp_words) > EXPLANATION_WORD_MAX:
            question["explanation"] = " ".join(exp_words[:EXPLANATION_WORD_MAX])

        # Process options
        options = question.get("options", [])
        if not isinstance(options, list):
            continue

        for option in options:
            if not isinstance(option, dict):
                continue

            # Truncate long option text
            opt_text = option.get("text", "")
            opt_words = opt_text.split()
            if len(opt_words) > OPTION_WORD_MAX:
                option["text"] = " ".join(opt_words[:OPTION_WORD_MAX])

            # Truncate long rationale
            rationale = option.get("rationale", "")
            rat_words = rationale.split()
            if len(rat_words) > RATIONALE_WORD_MAX:
                option["rationale"] = " ".join(rat_words[:RATIONALE_WORD_MAX])

    return data


def get_short_option_summary(data: dict) -> str:
    """
    Get a summary of options that are too short, formatted for the critic.
    """
    _, issues = check_word_counts(data)

    short_options = [
        i
        for i in issues
        if i.get("issue") == "short" and "options" in i.get("location", "")
    ]

    if not short_options:
        return ""

    lines = [f"Found {len(short_options)} options that are TOO SHORT:"]
    for issue in short_options[:10]:  # Limit to first 10
        lines.append(f"  • {issue['location']}: only {issue['current_count']} words")
        lines.append(f"    Current: \"{issue['text_preview']}\"")
        lines.append(
            f"    → Need to expand to {OPTION_WORD_MIN}-{OPTION_WORD_MAX} words"
        )

    if len(short_options) > 10:
        lines.append(f"  ... and {len(short_options) - 10} more")

    return "\n".join(lines)
