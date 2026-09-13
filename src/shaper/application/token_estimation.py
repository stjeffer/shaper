"""Deterministic token estimates for proposed transformations."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Sequence

from shaper.application.model import SHAPING_PROMPT
from shaper.application.shaping import CandidatePayload
from shaper.domain import TokenEstimate
from shaper.domain.models import canonical_hash

ESTIMATOR_VERSION = "1.3"
ESTIMATED_MODEL_CALLS = 4
_WORD = re.compile(r"\w+|[^\w\s]", re.UNICODE)
_LEXICAL_MULTIPLIER = 1.5
_CONTEXT_ENVELOPE_OVERHEAD = 800
_SAFETY_FACTOR = 1.25


def _lexical_tokens(value: str) -> int:
    return max(1, math.ceil(len(_WORD.findall(value)) * _LEXICAL_MULTIPLIER))


_PROMPT_OVERHEAD = _lexical_tokens(SHAPING_PROMPT)
_SCHEMA_OVERHEAD = _lexical_tokens(json.dumps(CandidatePayload.model_json_schema(), sort_keys=True))


class TokenEstimator:
    """Estimate a transparent range and enforceable worst-case maximum."""

    def __init__(
        self,
        *,
        model_deployment: str,
        platform_maximum: int = 100_000,
        estimator_version: str = ESTIMATOR_VERSION,
    ) -> None:
        self._model_deployment = model_deployment
        self._platform_maximum = platform_maximum
        self._estimator_version = estimator_version

    def estimate(self, text: str, proposed_changes: Sequence[str]) -> TokenEstimate:
        """Estimate without invoking a model or promising exact provider billing."""
        if not text.strip():
            raise ValueError("Token estimation requires non-empty source text")
        if not proposed_changes:
            raise ValueError("Token estimation requires at least one proposed change")
        source_tokens = _lexical_tokens(text)
        input_expected = (
            source_tokens + _PROMPT_OVERHEAD + _SCHEMA_OVERHEAD + _CONTEXT_ENVELOPE_OVERHEAD
        )
        input_min = max(1, math.floor(input_expected * 0.85))
        input_max = math.ceil(input_expected * 1.2)
        output_factor = min(1.6, 0.55 + 0.12 * len(proposed_changes))
        output_expected = max(200, math.ceil(source_tokens * output_factor))
        output_min = max(1, math.floor(output_expected * 0.7))
        output_max = math.ceil(output_expected * 1.4)
        expected_total = input_expected + output_expected
        upper_total = input_max + output_max
        enforced_maximum = math.ceil(upper_total * ESTIMATED_MODEL_CALLS * _SAFETY_FACTOR)
        if enforced_maximum > self._platform_maximum:
            raise TokenEstimateLimitError(
                "Estimated transformation maximum exceeds the platform quota; "
                "narrow or split the source document"
            )
        assumptions = (
            "Source tokens use a deterministic lexical approximation.",
            "Input includes the current shaping prompt, response schema, and context envelope.",
            "Output range scales with source size and proposed intervention count.",
            "Maximum reserves an initial response and up to three bounded repair attempts.",
        )
        identity = {
            "model_deployment": self._model_deployment,
            "estimator_version": self._estimator_version,
            "input_min": input_min,
            "input_max": input_max,
            "output_min": output_min,
            "output_max": output_max,
            "expected_total": expected_total,
            "enforced_maximum": enforced_maximum,
            "changes": tuple(proposed_changes),
            "text_hash": canonical_hash(text),
        }
        return TokenEstimate(
            estimate_id=canonical_hash(identity),
            model_deployment=self._model_deployment,
            estimator_version=self._estimator_version,
            input_min=input_min,
            input_max=input_max,
            output_min=output_min,
            output_max=output_max,
            expected_total=expected_total,
            enforced_maximum=enforced_maximum,
            assumptions=assumptions,
            confidence=0.65,
        )


class TokenEstimateLimitError(ValueError):
    """Raised when an estimate cannot fit within the configured quota."""
