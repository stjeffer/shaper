"""Programmatic evaluation contracts and upgrade regression gates."""

from __future__ import annotations

import csv
import json
import random
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from shaper.domain.models import canonical_hash


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


class PairedCaseOutcome(BaseModel):
    """Baseline and shaped pass outcomes for one unchanged evaluation case."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str = Field(min_length=1, max_length=128)
    baseline_passed: bool
    shaped_passed: bool


class ImprovementReport(BaseModel):
    """Evidence-backed paired pass-rate comparison, never model confidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    metric: str
    input_hash: str
    sample_size: int = Field(ge=1, le=500)
    baseline_pass_rate: float = Field(ge=0, le=1)
    shaped_pass_rate: float = Field(ge=0, le=1)
    absolute_improvement_percentage_points: float
    relative_improvement_percent: float | None
    confidence_level: float = Field(gt=0.5, lt=1)
    confidence_interval_percentage_points: tuple[float, float]
    improved_cases: int = Field(ge=0)
    regressed_cases: int = Field(ge=0)
    unchanged_cases: int = Field(ge=0)
    claim_status: str
    explanation: str
    limitations: tuple[str, ...] = Field(min_length=1)


def compare_paired_answer_pass_rates(
    outcomes: Sequence[PairedCaseOutcome],
    *,
    dataset_reviewed: bool,
    confidence_level: float = 0.95,
) -> ImprovementReport:
    """Compare unchanged baseline and shaped cases with a paired bootstrap interval."""
    if not outcomes:
        raise ValueError("An improvement comparison requires at least one paired outcome")
    if len(outcomes) > 500:
        raise ValueError("An improvement comparison accepts at most 500 paired outcomes")
    if not 0.5 < confidence_level < 1:
        raise ValueError("Confidence level must be between 0.5 and 1")
    case_ids = [outcome.case_id for outcome in outcomes]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Paired outcome case IDs must be unique")

    count = len(outcomes)
    baseline_rate = sum(outcome.baseline_passed for outcome in outcomes) / count
    shaped_rate = sum(outcome.shaped_passed for outcome in outcomes) / count
    differences = tuple(
        int(outcome.shaped_passed) - int(outcome.baseline_passed) for outcome in outcomes
    )
    improvement = shaped_rate - baseline_rate
    interval = _paired_bootstrap_interval(differences, confidence_level)
    improved = differences.count(1)
    regressed = differences.count(-1)

    if improvement <= 0:
        claim_status = "no_measured_improvement"
    elif dataset_reviewed and count >= 30 and interval[0] > 0:
        claim_status = "eligible_for_reviewed_claim"
    else:
        claim_status = "observed_only"

    limitations = [
        "The interval estimates paired pass-rate uncertainty, not model confidence or "
        "per-answer correctness."
    ]
    if not dataset_reviewed:
        limitations.append(
            "The dataset has not completed evaluation-design and subject-matter review; "
            "do not use this result for production quality claims."
        )
    if count < 30:
        limitations.append(
            "Fewer than 30 paired cases cannot reliably separate improvement from noise "
            "across evaluation categories."
        )

    percentage_points = round(100 * improvement, 1)
    explanation = (
        f"Across {count} unchanged paired cases, baseline pass rate was "
        f"{100 * baseline_rate:.1f}% and shaped pass rate was {100 * shaped_rate:.1f}%, "
        f"an observed change of {percentage_points:+.1f} percentage points. "
        f"The {100 * confidence_level:.0f}% paired bootstrap interval is "
        f"[{interval[0]:.1f}, {interval[1]:.1f}] percentage points."
    )
    identity = {
        "metric": "paired_answer_pass_rate",
        "outcomes": [outcome.model_dump(mode="json") for outcome in outcomes],
        "dataset_reviewed": dataset_reviewed,
        "confidence_level": confidence_level,
    }
    return ImprovementReport(
        metric="paired_answer_pass_rate",
        input_hash=canonical_hash(identity),
        sample_size=count,
        baseline_pass_rate=round(baseline_rate, 4),
        shaped_pass_rate=round(shaped_rate, 4),
        absolute_improvement_percentage_points=percentage_points,
        relative_improvement_percent=(
            None if baseline_rate == 0 else round(100 * improvement / baseline_rate, 1)
        ),
        confidence_level=confidence_level,
        confidence_interval_percentage_points=interval,
        improved_cases=improved,
        regressed_cases=regressed,
        unchanged_cases=count - improved - regressed,
        claim_status=claim_status,
        explanation=explanation,
        limitations=tuple(limitations),
    )


def _paired_bootstrap_interval(
    differences: tuple[int, ...],
    confidence_level: float,
    *,
    samples: int = 10_000,
) -> tuple[float, float]:
    """Return a deterministic percentile interval over paired case differences."""
    randomizer = random.Random(0)
    count = len(differences)
    estimates = sorted(
        sum(randomizer.choice(differences) for _ in range(count)) / count for _ in range(samples)
    )
    tail = (1 - confidence_level) / 2
    lower = estimates[int(tail * (samples - 1))]
    upper = estimates[int((1 - tail) * (samples - 1))]
    return round(100 * lower, 1), round(100 * upper, 1)


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
