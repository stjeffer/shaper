"""Versioned runtime system prompts loaded from package resources."""

from __future__ import annotations

from functools import cache
from importlib import resources

PROMPT_VERSION = "1.7"


class PromptResourceError(RuntimeError):
    """Raised when a required packaged prompt cannot be used."""


def _require_prompt_content(resource_name: str, content: str) -> str:
    if not content.strip():
        raise PromptResourceError(f"Prompt resource {resource_name!r} is blank")
    return content


@cache
def load_prompt(resource_name: str) -> str:
    """Load one non-blank prompt from this package or fail explicitly."""
    try:
        content = (
            resources.files("shaper.prompts").joinpath(resource_name).read_text(encoding="utf-8")
        )
    except (FileNotFoundError, ModuleNotFoundError) as error:
        raise PromptResourceError(f"Prompt resource {resource_name!r} is missing") from error
    return _require_prompt_content(resource_name, content)


SHAPING_PROMPT = load_prompt("shaping.md")
EVALUATION_PROMPT = load_prompt("evaluation.md")

__all__ = [
    "EVALUATION_PROMPT",
    "PROMPT_VERSION",
    "SHAPING_PROMPT",
    "PromptResourceError",
    "load_prompt",
]
