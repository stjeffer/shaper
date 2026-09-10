"""Deterministic token estimates for proposed transformations."""

from __future__ import annotations

import math
import re
from collections.abc import Sequence

from shaper.domain import TokenEstimate
from shaper.domain.models import canonical_hash

ESTIMATOR_VERSION = "1.0"
_WORD = re.compile(r"\w+|[^\w\s]", re.UNICODE)
_PROMPT_OVERHEAD = 600
_SCHEMA_OVERHEAD = 300


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
        source_tokens = max(1, math.ceil(len(_WORD.findall(text)) * 1.3))
        input_expected = source_tokens + _PROMPT_OVERHEAD + _SCHEMA_OVERHEAD
        input_min = max(1, math.floor(input_expected * 0.85))
        input_max = math.ceil(input_expected * 1.2)
        output_factor = min(1.6, 0.55 + 0.12 * len(proposed_changes))
        output_expected = max(200, math.ceil(source_tokens * output_factor))
        output_min = max(1, math.floor(output_expected * 0.7))
        output_max = math.ceil(output_expected * 1.4)
        expected_total = input_expected + output_expected
        upper_total = input_max + output_max
        enforced_maximum = math.ceil(upper_total * 1.25)
        if enforced_maximum > self._platform_maximum:
            raise TokenEstimateLimitError(
                "Estimated transformation maximum exceeds the platform quota; "
                "narrow or split the source document"
            )
        assumptions = (
            "Source tokens use a deterministic lexical approximation.",
            "Input includes fixed prompt and schema overhead.",
            "Output range scales with source size and proposed intervention count.",
            "Maximum includes one bounded repair allowance.",
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
