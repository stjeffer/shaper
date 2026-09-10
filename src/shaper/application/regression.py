"""Programmatic evaluation contracts and upgrade regression gates."""

from __future__ import annotations

import csv
import json
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Difficulty(StrEnum):
    """Evaluation balance categories."""

    EASY = "easy"
    GROUNDING = "grounding"
    HARD = "hard"
    NEGATIVE = "negative"
    SAFETY = "safety"


class EvaluationCase(BaseModel):
    """One stable observable-behavior evaluation case."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(pattern=r"^\d{3}$")
    query: str = Field(min_length=1)
    expected_response: str = Field(min_length=1)
    category: str = Field(min_length=1)
    difficulty: Difficulty
    populations: tuple[str, ...] = ()
    tools_expected: tuple[str, ...] = ()
    source_reference: str | None = None
    needs_sme_review: bool
    notes: str = Field(min_length=1)

    @model_validator(mode="after")
    def require_grounding_source(self) -> EvaluationCase:
        """Require an explicit source for each grounding case."""
        if self.difficulty is Difficulty.GROUNDING and self.source_reference is None:
            raise ValueError("Grounding cases require source_reference")
        return self


class DatasetMetadata(BaseModel):
    """Dataset-level scope, distribution, and review state."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    system_name: str
    created_date: str
    version: str
    total_pairs: int = Field(ge=30)
    distribution: dict[Difficulty, int]
    user_populations: tuple[str, ...]
    population_coverage: dict[str, int]
    approach: str
    evaluation_mode: tuple[str, ...]
    recommended_tooling: str
    review_state: str
    validation_status: str
    generation_method: str
    interview_status: str


@dataclass(frozen=True)
class CaseResult:
    """Observed deterministic and advisory metrics for one case."""

    case_id: str
    deterministic_passed: bool
    model_assisted_passed: bool
    latency_ms: float
    model_tokens: int
    retrieved_rank: int | None
    tool_accurate: bool


@dataclass(frozen=True)
class BenchmarkSummary:
    """Aggregate metrics for one shaping or retrieval strategy."""

    strategy: str
    case_count: int
    deterministic_pass_rate: float
    model_assisted_pass_rate: float
    recall_at_5: float
    mean_reciprocal_rank: float
    tool_accuracy: float
    p95_latency_ms: float
    mean_model_tokens: float


@dataclass(frozen=True)
class RegressionDecision:
    """Upgrade gate result and explicit reasons."""

    passed: bool
    reasons: tuple[str, ...]


def load_dataset(
    cases_path: Path,
    metadata_path: Path,
) -> tuple[DatasetMetadata, tuple[EvaluationCase, ...]]:
    """Load JSONL cases and reject drift in distribution or population coverage."""
    metadata = DatasetMetadata.model_validate_json(metadata_path.read_text(encoding="utf-8"))
    cases = tuple(
        EvaluationCase.model_validate_json(line)
        for line in cases_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    if len(cases) != metadata.total_pairs:
        raise ValueError(f"Dataset declares {metadata.total_pairs} pairs but contains {len(cases)}")
    distribution = Counter(case.difficulty for case in cases)
    if dict(distribution) != metadata.distribution:
        raise ValueError("Dataset difficulty distribution does not match metadata")
    known_populations = set(metadata.user_populations)
    if any(set(case.populations) - known_populations for case in cases):
        raise ValueError("Evaluation case references an unconfirmed user population")
    coverage = {
        population: sum(population in case.populations for case in cases)
        for population in metadata.user_populations
    }
    if coverage != metadata.population_coverage:
        raise ValueError("Dataset population coverage does not match metadata")
    return metadata, cases


def run_benchmark(
    strategy: str,
    cases: Sequence[EvaluationCase],
    execute: Callable[[EvaluationCase], CaseResult],
) -> BenchmarkSummary:
    """Execute one strategy over the same cases and aggregate comparable metrics."""
    results = tuple(execute(case) for case in cases)
    if len(results) != len(cases) or any(
        result.case_id != case.id for result, case in zip(results, cases, strict=True)
    ):
        raise ValueError("Benchmark results must preserve evaluation-case identity and order")
    count = len(results)
    if count == 0:
        raise ValueError("A benchmark requires at least one evaluation case")
    retrieved = [result for result in results if result.retrieved_rank is not None]
    recall_at_5 = (
        sum(result.retrieved_rank is not None and result.retrieved_rank <= 5 for result in results)
        / count
    )
    reciprocal_rank = (
        sum(1 / result.retrieved_rank for result in retrieved if result.retrieved_rank) / count
    )
    latencies = sorted(result.latency_ms for result in results)
    p95_index = max(0, -(-95 * count // 100) - 1)
    return BenchmarkSummary(
        strategy=strategy,
        case_count=count,
        deterministic_pass_rate=sum(result.deterministic_passed for result in results) / count,
        model_assisted_pass_rate=sum(result.model_assisted_passed for result in results) / count,
        recall_at_5=recall_at_5,
        mean_reciprocal_rank=reciprocal_rank,
        tool_accuracy=sum(result.tool_accurate for result in results) / count,
        p95_latency_ms=latencies[p95_index],
        mean_model_tokens=sum(result.model_tokens for result in results) / count,
    )


def check_regression(
    current: BenchmarkSummary,
    baseline: BenchmarkSummary,
) -> RegressionDecision:
    """Enforce approved deterministic, advisory, latency, and token tolerances."""
    reasons: list[str] = []
    if current.deterministic_pass_rate < baseline.deterministic_pass_rate:
        reasons.append("deterministic pass rate decreased")
    if current.model_assisted_pass_rate < baseline.model_assisted_pass_rate - 0.05:
        reasons.append("model-assisted pass rate decreased by more than 5 percentage points")
    if current.p95_latency_ms > baseline.p95_latency_ms * 1.20:
        reasons.append("p95 latency increased by more than 20 percent")
    if current.mean_model_tokens > baseline.mean_model_tokens * 1.20:
        reasons.append("mean model-token use increased by more than 20 percent")
    return RegressionDecision(passed=not reasons, reasons=tuple(reasons))


def write_csv(cases: Sequence[EvaluationCase], path: Path) -> None:
    """Write the pair-only CSV companion from authoritative JSONL cases."""
    fieldnames = list(EvaluationCase.model_fields)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for case in cases:
            row = case.model_dump(mode="json")
            row["populations"] = ";".join(case.populations)
            row["tools_expected"] = ";".join(case.tools_expected)
            writer.writerow(row)


def summary_json(summary: BenchmarkSummary) -> str:
    """Serialize a stable benchmark report for CI artifacts."""
    return json.dumps(summary.__dict__, indent=2, sort_keys=True) + "\n"
