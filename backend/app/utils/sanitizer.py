"""Input sanitizer — protects LLM prompts from injection attacks.

Strips common prompt injection patterns from user inputs and
retrieved document text before they reach the LLM context.
"""
from __future__ import annotations

import re

# Patterns that commonly signal prompt injection attempts
_INJECTION_PATTERNS = [
    # Direct override instructions
    r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+instructions?\b",
    r"(?i)\bforget\s+(all\s+)?previous\s+instructions?\b",
    r"(?i)\bact\s+as\s+(a\s+)?(?:different|new|another)\b",
    r"(?i)\byou\s+are\s+now\b",
    r"(?i)\bnew\s+system\s+prompt\b",
    r"(?i)\boverride\s+(system\s+)?(prompt|instruction)\b",
    r"(?i)```\s*system\b",
    # Jailbreak signals
    r"(?i)\bDAN\b",
    r"(?i)\bdo\s+anything\s+now\b",
    r"(?i)\bjailbreak\b",
    # Attempts to exfiltrate system prompt
    r"(?i)\brepeat\s+(your\s+)?(system|initial)\s+prompt\b",
    r"(?i)\bwhat\s+(is\s+)?your\s+system\s+prompt\b",
    # HTML/XML injection in retrieved docs
    r"<\s*/?[A-Za-z][^>]*?>",
]

_COMPILED = [re.compile(p) for p in _INJECTION_PATTERNS]

# Maximum allowed input length (characters)
_MAX_INPUT_LENGTH = 2000


def sanitize_for_llm(text: str) -> str:
    """
    Sanitize user input or retrieved document text before including in
    an LLM prompt.

    - Truncates to max length
    - Strips prompt injection patterns
    - Strips null bytes and control characters
    - Collapses excessive whitespace

    Args:
        text: Raw input text

    Returns:
        Sanitized text safe for inclusion in LLM prompts
    """
    if not isinstance(text, str):
        return ""

    # Truncate
    text = text[:_MAX_INPUT_LENGTH]

    # Remove null bytes and control characters (keep newlines and tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Strip injection patterns
    for pattern in _COMPILED:
        text = pattern.sub("[REMOVED]", text)

    # Collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {3,}", " ", text)

    return text.strip()


def sanitize_document_chunk(text: str, max_length: int = 1500) -> str:
    """
    Sanitize retrieved RAG document chunks (may be longer than user input).
    Same rules but higher length limit.
    """
    return sanitize_for_llm(text[:max_length])

