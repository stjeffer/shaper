"""Generate deterministic JSON Schema snapshots from canonical Pydantic models."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from shaper.domain import (
    AgentRun,
    AnswerUnit,
    Collection,
    CompileJob,
    EstateAssessment,
    KnowledgeDocumentProfile,
    KnowledgeTransformationAnalysis,
    Principal,
    ReleaseManifest,
    ReviewDecision,
    SourceDocument,
    SourceSpan,
    ValidationFinding,
)

SCHEMA_PATH = Path("schemas/v1/domain.schema.json")
MODELS = (
    AgentRun,
    AnswerUnit,
    Collection,
    CompileJob,
    EstateAssessment,
    KnowledgeDocumentProfile,
    KnowledgeTransformationAnalysis,
    Principal,
    ReleaseManifest,
    ReviewDecision,
    SourceDocument,
    SourceSpan,
    ValidationFinding,
)


def rendered_schema() -> str:
    """Return the canonical schema bundle."""
    bundle = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:shaper:schema:domain:1.0",
        "models": {model.__name__: model.model_json_schema() for model in MODELS},
    }
    return json.dumps(bundle, indent=2, sort_keys=True) + "\n"


def create_parser() -> argparse.ArgumentParser:
    """Create the schema command parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when the snapshot has drifted")
    parser.add_argument("--output", type=Path, default=SCHEMA_PATH)
    return parser


def main() -> int:
    """Generate or check the schema snapshot."""
    args = create_parser().parse_args()
    expected = rendered_schema()
    if args.check:
        if not args.output.is_file():
            raise FileNotFoundError(f"Schema snapshot does not exist: {args.output}")
        if args.output.read_text(encoding="utf-8") != expected:
            raise RuntimeError(f"Schema snapshot has drifted: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
