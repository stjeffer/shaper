"""Package dependency-direction tests."""

from __future__ import annotations

import ast
import re
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
    assert 'aria-label="Documents and assessment findings"' in markup
    assert '<div class="grid-cell" role="columnheader">Findings</div>' in markup
    assert "Findings" in markup
    assert ">Readiness<" not in markup
    assert "Reshaping effort" not in markup
    assert "report.effort_band" not in script
    assert "documentFindings(report, documentValue.title)" in script
    assert "classifyFindings(report).length" in script
    assert '"missing_owner"' in script
    assert "Add an accountable owner" not in script
    assert "Long paragraph" in script
    assert "Document reference" in script
    assert "Additional issue detected" in script
    assert 'metric("Findings found", findings)' in script
    assert "Agent impact:" in script
    assert '"Transformation approved"' in script
    assert "Approved. This document is ready to transform." in script
    assert "const decision = recordValue(response)" in script
    assert "report.readiness_score" not in script
    assert 'id="documentDialog"' in markup
    assert "checks run" in script
    assert 'id="documentFindingsPanel"' in markup
    assert 'id="documentFindingsDialog"' in markup
    assert "function openDocumentFindings(button)" in script
    assert "button.dataset.reviewFindings = documentValue.document_id" in script
    assert 'window.matchMedia("(max-width: 1240px)")' in script
    assert 'findingsDialogMedia.addEventListener("change"' in script
    assert "moveOpenFindingsToCurrentLayout" in script
    assert ".discovery-review-layout.has-findings" in styles
    assert ":focus-visible" in styles
    assert 'class="assessment-note"' in markup
    assert '"result-evidence"' in script
    assert '.result-list > [data-tone="high"]' in styles
    assert "font-family: inherit" in styles
    assert "/documents/` +" in script
    assert "result-list" in styles
    assert "result-impact" in styles
    assert 'id="assessmentChecksView"' in markup
    assert 'data-action="assessment-checks"' in markup
    assert "The 29 checks Shaper runs" in markup
    assert "assessment_status" in script
    assert "document_count" in script
    assert 'api("/v1/assessment-checks")' in script
    assert "renderAssessmentChecks" in script
    assert "assessment-check-card" in styles
    assert "assessment-check-impact" in styles


def test_given_generated_artifact_when_rendered_then_before_and_after_panels_are_present() -> None:
    concept_root = REPOSITORY_ROOT / "prototype/copilot-studio-knowledge-compiler"
    script = (concept_root / "app.js").read_text(encoding="utf-8")
    styles = (concept_root / "styles.css").read_text(encoding="utf-8")

    assert '"Before reshaping"' in script
    assert '"After reshaping"' in script
    assert "artifact.source_version" in script
    assert "artifact.document_id" in script
    assert "artifact.artifact_id" in script
    assert "/preview" in script
    assert "recordValue(record).error" in script
    assert 'outputPreview.setAttribute("sandbox", "")' in script
    assert "artifact-comparison" in styles
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in styles
    assert ".comparison-preview {" in styles


def test_given_approved_artifact_when_rendered_then_html_export_is_available() -> None:
    script = (REPOSITORY_ROOT / "prototype/copilot-studio-knowledge-compiler/app.js").read_text(
        encoding="utf-8"
    )

    assert '"Export approved HTML"' in script
    assert "/download" in script
    assert "download.download = artifact.filename" in script


def test_given_transformation_estimate_when_rendered_then_usage_is_explained() -> None:
    concept_root = REPOSITORY_ROOT / "prototype/copilot-studio-knowledge-compiler"
    script = (concept_root / "app.js").read_text(encoding="utf-8")
    styles = (concept_root / "styles.css").read_text(encoding="utf-8")

    assert '"Estimated token use"' in script
    assert '"Content read"' in script
    assert '"Content written"' in script
    assert "Chart maximum:" in script
    assert "estimate.enforced_maximum" in script
    assert 'chart.setAttribute("role", "img")' in script
    assert "token-estimate-chart" in styles
    assert "token-segment" in styles
    assert "token-estimate-legend" in styles


def test_given_runtime_image_when_inspected_then_cli_and_source_are_packaged() -> None:
    dockerfile = (REPOSITORY_ROOT / "Dockerfile").read_text(encoding="utf-8")
    cli = (REPOSITORY_ROOT / "src/shaper/interfaces/cli.py").read_text(encoding="utf-8")

    assert "COPY --from=builder --chown=shaper:shaper /app/src ./src" in dockerfile
    assert 'ENTRYPOINT ["shaper"]' in dockerfile
    assert 'CMD ["--host", "0.0.0.0", "--port", "8000"]' in dockerfile
    assert 'CMD ["serve"' not in dockerfile
    assert "pretty_exceptions_show_locals=False" in cli


def test_given_live_estate_workspace_when_inspected_then_lifecycle_actions_are_wired() -> None:
    # Arrange
    html = (REPOSITORY_ROOT / "prototype/copilot-studio-knowledge-compiler/index.html").read_text(
        encoding="utf-8"
    )
    javascript = (REPOSITORY_ROOT / "prototype/copilot-studio-knowledge-compiler/app.js").read_text(
        encoding="utf-8"
    )

    # Assert
    assert 'id="archiveButton"' in html
    assert 'id="purgeDialog"' in html
    assert "/archive" in javascript
    assert "/purge" in javascript
    assert "waitForRun" in javascript
    assert 'setAttribute("aria-busy"' in javascript
    assert 'if (estate.status !== "archived")' in javascript
    assert javascript.index("function openDeleteDialog(estateId)") > javascript.index(
        "async function createEstate"
    )


def test_given_hosted_workspace_when_inspected_then_copilot_studio_patterns_are_present() -> None:
    html = (REPOSITORY_ROOT / "prototype/copilot-studio-knowledge-compiler/index.html").read_text(
        encoding="utf-8"
    )
    icon_sprite = (
        REPOSITORY_ROOT
        / "prototype/copilot-studio-knowledge-compiler/vendor/fluent-system-icons.svg"
    ).read_text(encoding="utf-8")
    icon_license = (
        REPOSITORY_ROOT
        / "prototype/copilot-studio-knowledge-compiler/vendor/fluent-system-icons-LICENSE.txt"
    ).read_text(encoding="utf-8")
    browser_app = (
        REPOSITORY_ROOT / "prototype/copilot-studio-knowledge-compiler/app.js"
    ).read_text(encoding="utf-8")

    for tab in ("Sources", "Assess", "Approve", "Outputs"):
        assert f"<strong>{tab}</strong>" in html
    assert "Governed process" not in html
    assert 'id="estateSearch"' not in html
    assert 'class="nav-item"' in html
    assert 'data-action="open-create"' in html
    assert 'data-action="open-create" title="New estate"' in html
    assert '<span class="nav-item-label">New estate</span>' in html
    assert '<span class="nav-item-label">Checks</span>' in html
    assert html.count('class="nav-icon fluent-icon"') == 2
    assert html.count("./vendor/fluent-system-icons.svg#") >= 12
    assert "fluentIcon(" in browser_app
    assert '"more-horizontal-20"' in browser_app
    for icon_id in (
        "add-folder-24",
        "arrow-left-20",
        "checklist-20",
        "checkmark-circle-20",
        "dismiss-20",
        "dismiss-circle-20",
        "document-24",
        "error-circle-20",
        "folder-24",
        "info-20",
        "more-horizontal-20",
        "sync-circle-20",
        "warning-20",
    ):
        assert f'id="{icon_id}"' in icon_sprite
    assert "Copyright (c) 2020 Microsoft Corporation" in icon_license
    assert 'id="environment"' not in html
    assert 'id="avatar"' not in html
    assert 'querySelector("#avatar")' not in browser_app
    assert "Create improvement plan" in html
    assert "Review assessment and improvement plan" in html
    assert 'id="proposalStatus"' in html
    assert '"No improvement plan was created"' in browser_app
    assert "state.proposals.length === 0" in browser_app
    assert "function invalidateAssessmentEvidence()" in browser_app
    assert "Run discovery to assess the updated estate." in browser_app
    assert 'id="evaluationOptions"' in html
    assert 'class="approval-review-tabs"' in html
    assert 'aria-label="Improvement plan review"' in html
    assert 'data-approval-review-tab="assessment"' in html
    assert 'data-approval-review-tab="evaluations"' in html
    assert 'id="assessmentResultsPanel"' in html
    assert 'id="evaluationSetPanel"' in html
    assert "function switchApprovalReviewTab(name, focus = true)" in browser_app
    assert 'elements.approvalReviewTabs.addEventListener("keydown"' in browser_app
    assert html.index('id="transformButton"') < html.index('id="approvalReviewTabs"')
    assert 'id="transformationProgress"' in html
    assert 'id="transformationProgressAnnouncement"' in html
    assert "async function streamTransformation(" in browser_app
    assert "enforce_preservation_checks: enforcePreservationChecks" in browser_app
    assert "function updateTransformationProgress(event)" in browser_app
    assert "function resetTransformationProgress()" in browser_app
    assert "state.transformationAbortController?.abort()" in browser_app
    assert "const operationId = crypto.randomUUID()" in browser_app
    assert "if (!isCurrentOperation()) return;" in browser_app
    assert 'panel.setAttribute("aria-busy", "true")' not in browser_app
    assert "/transformation-runs/stream" in browser_app
    assert "Microsoft Foundry JSONL" in html
    assert "Copilot Studio CSV" in html
    assert "function suggestedEvaluations(" in browser_app
    assert "ground_truth: suggestion.ground_truth" in browser_app
    assert '["question", "expectedResponse"]' in browser_app
    assert "Suggested keywords:" in browser_app
    assert "needs_sme_review: suggestion.needs_sme_review" in browser_app
    assert "function proposalAssessmentResults(report)" in browser_app
    assert '"Checks completed"' in browser_app
    assert '"Checks that need attention"' in browser_app
    assert "checks passed" in browser_app
    assert "Recommended changes" in browser_app
    assert "View estimated model usage" in browser_app
    assert "await ensureAssessmentChecks()" in browser_app
    assert 'data-action="open-delete"' in html
    assert 'id="editDialog"' in html
    assert 'id="editForm"' in html
    assert 'aria-label="Add content source"' in html
    assert 'data-source-input-tab="location"' in html
    assert 'data-source-input-tab="upload"' in html
    assert 'data-source-input-panel="upload"' in html
    assert 'id="sharePointCredentialMode"' in html
    assert "Organization-managed connection" in html
    assert "Credentials are never entered or stored" in html
    assert 'class="source-workspace-grid"' in html
    assert 'class="registered-sources-panel"' in html
    assert 'id="deleteConfirmation"' in html
    assert 'id="deleteConfirmButton"' in html
    assert "function requestedEstateRoute()" in browser_app
    assert "formatShortDate(estate.updated_at)" in browser_app
    assert "function fileFormatLabel(documentValue)" in browser_app
    assert 'text("p", fileFormatLabel(documentValue))' in browser_app
    assert "documentValue.media_type} ·" not in browser_app
    assert 'partially_assessed: "Assessed"' in browser_app
    assert '"Partially assessed"' not in browser_app
    assert "checkbox.disabled = isArchived()" in browser_app
    assert "checkbox.disabled = !report" not in browser_app
    assert "selected for improvement planning" in browser_app
    assert 'tablist.setAttribute("role", "tablist")' in browser_app
    assert 'tab.setAttribute("role", "tab")' in browser_app
    assert 'section.setAttribute("role", "tabpanel")' in browser_app
    assert 'tab.setAttribute("aria-selected", `${selected}`)' in browser_app
    assert '["ArrowLeft", "ArrowRight", "Home", "End"]' in browser_app
    assert "\nfunction switchSourceInputTab(name, focus = true)" in browser_app
    assert "\n  function switchSourceInputTab(name, focus = true)" not in browser_app
    assert "function sourceDisplayDetail(source)" in browser_app
    assert 'upload: "Uploaded file"' in browser_app
    assert 'zip: "Uploaded ZIP bundle"' in browser_app
    assert 'startsWith("asset:")' in browser_app
    assert 'text("p", `${source.kind} · ${source.locator}`)' not in browser_app
    assert 'elements.sourceInputTabs.addEventListener("click"' in browser_app
    assert 'elements.sourceInputTabs.addEventListener("keydown"' in browser_app
    assert 'elements.sourceKind.addEventListener("change"' in browser_app
    assert 'source.credential_mode === "application"' in browser_app
    assert "await loadEstates(true)" in browser_app
    assert 'menu.setAttribute("role", "menu")' in browser_app
    assert browser_app.count('setAttribute("role", "menuitem")') == 2
    assert "`/v1/estates/${estate.estate_id}`" in browser_app
    assert "`/v1/estates/${estate.estate_id}/purge`" in browser_app
    assert "function selectedActionEstate()" in browser_app


def test_given_workspace_controls_when_inspected_then_native_design_system_is_applied() -> None:
    concept_root = REPOSITORY_ROOT / "prototype/copilot-studio-knowledge-compiler"
    html = (concept_root / "index.html").read_text(encoding="utf-8")
    browser_app = (concept_root / "app.js").read_text(encoding="utf-8")
    styles = (concept_root / "styles.css").read_text(encoding="utf-8")

    assert 'id="themePicker"' not in html
    assert "<legend>Theme</legend>" not in html
    assert 'src="fluent-theme.js' not in html
    assert 'href="styles.css?v=20260915-findings-workspace-v1"' in html
    assert 'src="app.js?v=20260915-findings-workspace-v1"' in html
    assert not re.search(r"<fluent-[a-z-]+", html)
    assert 'name="color-theme"' not in html
    assert "shaper-color-theme" not in html
    assert "COLOR_THEME_STORAGE_KEY" not in browser_app
    assert "applyColorTheme(" not in browser_app
    assert "themePicker" not in browser_app
    assert ':root[data-theme="teams"]' not in styles
    assert ':root[data-theme="office"]' not in styles
    assert "::part(control)" not in styles
    assert "--canvas: #06090b;" in styles
    assert "--surface: #0c1215;" in styles
    assert "--accent: #6de0d2;" in styles
    assert "--radius-lg: 4px;" in styles
    assert "--space-8: 32px;" in styles
    assert "@media (prefers-color-scheme: dark)" not in styles
    assert '"Segoe UI", "Segoe UI Web"' in styles
    assert "background: var(--surface-3);" in styles
    assert "border: 1px solid var(--line);" in styles
    assert "text-transform: uppercase;" in styles
    native_controls = re.findall(
        r"<(button|dialog|select|textarea|details|summary|input)\b([^>]*)>",
        html,
        flags=re.IGNORECASE,
    )
    assert len(native_controls) >= 20
    assert {"button", "input", "select", "textarea"} <= {
        element_name for element_name, _ in native_controls
    }
    assert 'type="file"' in html
    assert 'document.createElement("button")' in browser_app
    assert 'menu.setAttribute("role", "menu")' in browser_app
    assert 'setAttribute("role", "menuitem")' in browser_app
    assert "showModal(" not in browser_app
    assert "window.confirm(" not in browser_app
    assert 'id="workflowSourcesTab"' in html
    assert 'aria-controls="workflowSourcesPanel"' in html
    assert 'id="workflowSourcesPanel"' in html
    assert 'role="tabpanel"' in html
    assert 'button.setAttribute("aria-selected", `${selected}`);' in browser_app
    assert 'elements.workflowTabs.setAttribute("activeid", button.id);' in browser_app
    assert 'elements.workflowTabs.addEventListener("keydown"' in browser_app


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

    assert architecture.count("flowchart LR") == 1
    assert architecture.count("flowchart TB") == 6
    assert architecture.count("subGraphTitleMargin:") == 5
    assert "direction LR" not in architecture
    assert "C4Context" not in architecture
    assert "C4Container" not in architecture
    assert "ctr_malware_scanner_i" in architecture
    assert "cmp_estate_recommendation_service" in architecture
    assert "cmp_estate_transformation_service" in architecture
