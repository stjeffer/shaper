"""Evaluation dataset and regression-gate tests."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from shaper.application.regression import (
    BenchmarkSummary,
    CaseResult,
    EvaluationCase,
    PairedCaseOutcome,
    check_regression,
    compare_paired_answer_pass_rates,
    load_dataset,
    run_benchmark,
    write_csv,
)

DATA = Path(__file__).parent


def test_given_synthetic_dataset_when_loaded_then_contract_and_distribution_match() -> None:
    metadata, cases = load_dataset(DATA / "cases.jsonl", DATA / "metadata.json")

    assert metadata.total_pairs == 30
    assert len(cases) == 30
    assert sum(metadata.distribution.values()) == 30


def test_given_agent_and_fixed_chain_when_benchmarked_then_agent_advantage_is_visible() -> None:
    _, cases = load_dataset(DATA / "cases.jsonl", DATA / "metadata.json")

    def agent(case: EvaluationCase) -> CaseResult:
        return CaseResult(
            case_id=case.id,
            deterministic_passed=True,
            model_assisted_passed=True,
            latency_ms=float(int(case.id)),
            model_tokens=100,
            retrieved_rank=1,
            tool_accurate=True,
        )

    def fixed(case: EvaluationCase) -> CaseResult:
        result = agent(case)
        if case.difficulty.value != "hard":
            return result
        return replace(
            result,
            deterministic_passed=False,
            model_assisted_passed=False,
            tool_accurate=False,
        )

    agent_summary = run_benchmark("bounded-agent", cases, agent)
    fixed_summary = run_benchmark("fixed-chain", cases, fixed)

    assert agent_summary.case_count == fixed_summary.case_count == 30
    assert agent_summary.deterministic_pass_rate > fixed_summary.deterministic_pass_rate
    assert agent_summary.tool_accuracy > fixed_summary.tool_accuracy


def test_given_units_and_chunks_when_retrieved_then_recall_uses_same_cases() -> None:
    _, cases = load_dataset(DATA / "cases.jsonl", DATA / "metadata.json")

    def retrieve(case: EvaluationCase, *, shaped: bool) -> CaseResult:
        rank = 1 if shaped or case.difficulty.value == "easy" else None
        return CaseResult(
            case_id=case.id,
            deterministic_passed=True,
            model_assisted_passed=True,
            latency_ms=10,
            model_tokens=0,
            retrieved_rank=rank,
            tool_accurate=True,
        )

    units = run_benchmark("answer-units", cases, lambda case: retrieve(case, shaped=True))
    chunks = run_benchmark(
        "contextual-chunks",
        cases,
        lambda case: retrieve(case, shaped=False),
    )

    assert units.recall_at_5 > chunks.recall_at_5


def test_given_excessive_latency_regression_when_checked_then_upgrade_is_blocked() -> None:
    baseline = BenchmarkSummary(
        strategy="approved",
        case_count=30,
        deterministic_pass_rate=1,
        model_assisted_pass_rate=0.9,
        recall_at_5=0.9,
        mean_reciprocal_rank=0.8,
        tool_accuracy=1,
        p95_latency_ms=100,
        mean_model_tokens=100,
    )

    decision = check_regression(replace(baseline, p95_latency_ms=121), baseline)

    assert not decision.passed
    assert decision.reasons == ("p95 latency increased by more than 20 percent",)


def test_given_jsonl_cases_when_exported_then_csv_has_same_pair_count(tmp_path: Path) -> None:
    _, cases = load_dataset(DATA / "cases.jsonl", DATA / "metadata.json")
    target = tmp_path / "cases.csv"

    write_csv(cases, target)

    assert len(target.read_text(encoding="utf-8").splitlines()) == 31


def test_given_paired_results_when_compared_then_improvement_and_uncertainty_are_reported() -> None:
    outcomes = tuple(
        PairedCaseOutcome(
            case_id=f"case-{index}",
            baseline_passed=index < 18,
            shaped_passed=index < 24,
        )
        for index in range(30)
    )

    report = compare_paired_answer_pass_rates(outcomes, dataset_reviewed=True)

    assert report.baseline_pass_rate == 0.6
    assert report.shaped_pass_rate == 0.8
    assert report.absolute_improvement_percentage_points == 20
    assert report.confidence_interval_percentage_points[0] > 0
    assert report.claim_status == "eligible_for_reviewed_claim"
    assert "model confidence" in report.limitations[0]


def test_given_draft_dataset_when_improved_then_production_claim_is_blocked() -> None:
    outcomes = tuple(
        PairedCaseOutcome(case_id=f"case-{index}", baseline_passed=False, shaped_passed=True)
        for index in range(30)
    )

    report = compare_paired_answer_pass_rates(outcomes, dataset_reviewed=False)

    assert report.claim_status == "observed_only"
    assert report.relative_improvement_percent is None
    assert any("do not use" in limitation for limitation in report.limitations)


def test_given_duplicate_pair_identity_when_compared_then_request_is_rejected() -> None:
    outcome = PairedCaseOutcome(case_id="same", baseline_passed=False, shaped_passed=True)

    with pytest.raises(ValueError, match="Paired outcome case IDs must be unique"):
        compare_paired_answer_pass_rates((outcome, outcome), dataset_reviewed=True)
