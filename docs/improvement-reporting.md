---
title: Measure knowledge-shaping improvement
description: Compare paired baseline and shaped evaluation outcomes without overstating accuracy
ms.topic: concept
---

## Measurement contract

Shaper reports improvement only from paired evaluation outcomes. Each case must
run unchanged against the baseline content and the shaped knowledge. The report
compares whether each answer met its reviewed pass criterion.

The authenticated endpoint is:

```text
POST /v1/evaluations/improvement
```

The request identifies the collection, whether the evaluation dataset completed
human review, the confidence level, and the baseline and shaped result for each
stable case identifier.

```json
{
  "collection_id": "policy-knowledge",
  "dataset_reviewed": true,
  "confidence_level": 0.95,
  "outcomes": [
    {
      "case_id": "travel-001",
      "baseline_passed": false,
      "shaped_passed": true
    }
  ]
}
```

## Reported measures

The response includes:

* Baseline and shaped answer pass rates
* Absolute improvement in percentage points
* Relative improvement when the baseline rate is nonzero
* Improved, regressed, and unchanged case counts
* A deterministic paired bootstrap confidence interval
* Dataset sample size and content-addressed input identity
* Claim eligibility, explanation, and limitations

Absolute and relative improvement answer different questions. A change from 60%
to 80% is an increase of 20 percentage points and a relative improvement of
33.3%.

The confidence interval estimates uncertainty in the paired pass-rate
difference. It is not model confidence, a probability that an individual answer
is correct, or evidence that every source document improved.

## Claim safeguards

Shaper returns `eligible_for_reviewed_claim` only when:

* The dataset is recorded as human reviewed
* At least 30 unchanged paired cases were evaluated
* The lower bound of the confidence interval is above zero

Otherwise, positive results remain `observed_only`. A zero or negative change is
`no_measured_improvement`.

> [!IMPORTANT]
> The repository's synthetic dataset validates measurement mechanics only. It
> cannot support a production quality claim. A representative dataset still
> requires the evaluation-design interview, sample review, subject-matter
> approval, and a configured baseline and shaped run.

## Interpretation example

For 30 reviewed paired cases, a baseline pass rate of 60% and shaped pass rate
of 80% produces an observed increase of 20 percentage points. The report also
shows the 95% interval and the exact cases that improved or regressed. Publish
the result only when the claim status is eligible and the evaluation owner has
approved the evidence.
