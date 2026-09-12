"""Package dependency-direction tests."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SOURCE_ROOT = Path("src/shaper")
REPOSITORY_ROOT = Path(".")


@pytest.mark.parametrize("package", ["domain", "application"])
def test_given_inner_package_when_imports_inspected_then_outer_layers_are_absent(
    package: str,
) -> None:
    # Arrange
    forbidden = ("shaper.infrastructure", "shaper.interfaces")
    imports: list[str] = []

    # Act
    for path in (SOURCE_ROOT / package).glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports.extend(
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )

    # Assert
    assert not [name for name in imports if name.startswith(forbidden)]


def test_given_postgres_deployment_when_inspected_then_compatibility_state_is_local() -> None:
    template = (REPOSITORY_ROOT / "bicep/main.bicep").read_text(encoding="utf-8")
    script = (REPOSITORY_ROOT / "scripts/deploy.sh").read_text(encoding="utf-8")
    browser_app = (
        REPOSITORY_ROOT / "prototype/copilot-studio-knowledge-compiler/app.js"
    ).read_text(encoding="utf-8")

    assert "activeRevisionsMode: 'Single'" in template
    assert "name: 'SHAPER_DATABASE_PATH'" in template
    assert "value: ':memory:'" in template
    assert "name: 'SHAPER_POSTGRES_URL'" in template
    assert "secretRef: 'postgres-url'" in template
    assert "'/concept/*'" in template
    assert "unauthenticatedClientAction: 'Return401'" in template
    assert "name: 'SHAPER_SQLITE_JOURNAL_MODE'" in template
    assert "value: 'DELETE'" in template
    assert "SHAPER_SMOKE_TOKEN" in script
    assert "--enable-id-token-issuance true" in script
    assert 'redirect: "manual"' in browser_app
    assert 'response.type === "opaqueredirect"' in browser_app
    assert '"/.auth/me"' not in browser_app


def test_given_assessment_ui_when_inspected_then_results_are_content_focused() -> None:
    # Arrange
    concept_root = REPOSITORY_ROOT / "prototype/copilot-studio-knowledge-compiler"

    # Act
    markup = (concept_root / "index.html").read_text(encoding="utf-8")
    script = (concept_root / "app.js").read_text(encoding="utf-8")
    styles = (concept_root / "styles.css").read_text(encoding="utf-8")

    # Assert
    assert '<th scope="col">Results</th>' in markup
    assert "documentResults(report.finding_codes)" in script
    assert "classifyResults(report.finding_codes).length" in script
    assert '"missing_owner"' in script
    assert "Add an accountable owner" not in script
    assert "Long paragraph" in script
    assert "Document reference" in script
    assert "Additional issue detected" in script
    assert 'metric("Results found", results)' in script
    assert "result-list" in styles


def test_given_runtime_image_when_inspected_then_cli_and_source_are_packaged() -> None:
    dockerfile = (REPOSITORY_ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "COPY --from=builder --chown=shaper:shaper /app/src ./src" in dockerfile
    assert 'ENTRYPOINT ["shaper"]' in dockerfile
    assert 'CMD ["--host", "0.0.0.0", "--port", "8000"]' in dockerfile
    assert 'CMD ["serve"' not in dockerfile


def test_given_platform_architecture_when_inspected_then_shaper_is_not_an_agent() -> None:
    architecture = (REPOSITORY_ROOT / "docs/architecture.md").read_text(encoding="utf-8")
    readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")

    assert "Shaper is not an agent" in architecture
    assert "Shaper is not an agent" in readme
    assert "SharePoint remains an important source, dashboard, review, and delivery surface" in (
        architecture
    )
    for role in (
        "Assessment Agent",
        "Knowledge Agent",
        "Transformation Agent",
        "Governance Agent",
        "Agent Readiness Agent",
    ):
        assert role in architecture


def test_given_c4_diagrams_when_inspected_then_renderer_conventions_are_present() -> None:
    architecture = (REPOSITORY_ROOT / "docs/architecture.md").read_text(encoding="utf-8")

    assert architecture.count("flowchart TB") == 3
    assert architecture.count("subGraphTitleMargin:") == 3
    assert "direction LR" not in architecture
    assert "C4Context" not in architecture
    assert "C4Container" not in architecture
