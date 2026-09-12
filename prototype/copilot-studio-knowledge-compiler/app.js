const state = {
  session: null,
  collectionId: null,
  estates: [],
  estate: null,
  sources: [],
  documents: [],
  reports: new Map(),
  runs: [],
  discoveryRunId: null,
  proposalRunId: null,
  proposals: [],
  decisions: new Map(),
  artifacts: [],
  selectedDocuments: new Set(),
};

const elements = {
  workspace: document.querySelector("#workspace"),
  status: document.querySelector("#status"),
  alert: document.querySelector("#alert"),
  loading: document.querySelector("#loadingView"),
  noAccess: document.querySelector("#noAccessView"),
  estateListView: document.querySelector("#estateListView"),
  estateView: document.querySelector("#estateView"),
  estateList: document.querySelector("#estateList"),
  estateEmpty: document.querySelector("#estateEmpty"),
  createDialog: document.querySelector("#createDialog"),
  createForm: document.querySelector("#createForm"),
  sourceForm: document.querySelector("#sourceForm"),
  uploadForm: document.querySelector("#uploadForm"),
  files: document.querySelector("#files"),
  fileSummary: document.querySelector("#fileSummary"),
  sourceList: document.querySelector("#sourceList"),
  sourceCount: document.querySelector("#sourceCount"),
  documentRows: document.querySelector("#documentRows"),
  documentEmpty: document.querySelector("#documentEmpty"),
  discoverySummary: document.querySelector("#discoverySummary"),
  discoverButton: document.querySelector("#discoverButton"),
  recommendButton: document.querySelector("#recommendButton"),
  selectionSummary: document.querySelector("#selectionSummary"),
  proposalList: document.querySelector("#proposalList"),
  proposalEmpty: document.querySelector("#proposalEmpty"),
  approvalSummary: document.querySelector("#approvalSummary"),
  transformButton: document.querySelector("#transformButton"),
  artifactList: document.querySelector("#artifactList"),
  artifactEmpty: document.querySelector("#artifactEmpty"),
  archiveButton: document.querySelector("#archiveButton"),
  purgeButton: document.querySelector("#purgeButton"),
  purgeDialog: document.querySelector("#purgeDialog"),
  purgeForm: document.querySelector("#purgeForm"),
  purgePhrase: document.querySelector("#purgePhrase"),
};

function announce(message) {
  elements.status.textContent = "";
  requestAnimationFrame(() => {
    elements.status.textContent = message;
  });
}

function showAlert(message) {
  elements.alert.textContent = message;
  elements.alert.hidden = false;
  elements.alert.focus?.();
}

function clearAlert() {
  elements.alert.hidden = true;
  elements.alert.textContent = "";
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("Accept", "application/json");
  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers,
  });
  if (!response.ok) {
    let detail = `Request failed with HTTP ${response.status}`;
    try {
      const payload = await response.json();
      detail =
        typeof payload.detail === "string"
          ? payload.detail
          : JSON.stringify(payload.detail ?? payload);
    } catch {
      // The status remains actionable when a proxy returns a non-JSON error page.
    }
    throw new Error(detail);
  }
  return response.status === 204 ? null : response.json();
}

function setBusy(container, busy, message = "Working…") {
  container.querySelector(".busy-overlay")?.remove();
  container.setAttribute("aria-busy", `${busy}`);
  if (!busy) return;
  const overlay = document.querySelector("#busyTemplate").content.cloneNode(true);
  overlay.querySelector("strong").textContent = message;
  container.append(overlay);
}

function showView(view) {
  elements.loading.hidden = view !== "loading";
  elements.noAccess.hidden = view !== "no-access";
  elements.estateListView.hidden = view !== "list";
  elements.estateView.hidden = view !== "estate";
}

function text(tag, value, className) {
  const node = document.createElement(tag);
  node.textContent = value;
  if (className) node.className = className;
  return node;
}

function formatDate(value) {
  if (!value) return "Not available";
  return new Intl.DateTimeFormat("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function recordValue(record) {
  return record?.value ?? record;
}

function isArchived() {
  return recordValue(state.estate)?.status === "archived";
}

function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function waitForRun(runId) {
  const estateId = recordValue(state.estate).estate_id;
  for (let attempt = 0; attempt < 120; attempt += 1) {
    const payload = await api(`/v1/estates/${estateId}/runs`);
    state.runs = payload.items;
    const record = state.runs.find((item) => recordValue(item).run_id === runId);
    if (!record) throw new Error(`Workflow run ${runId} is unavailable`);
    const status = recordValue(record).status;
    announce(`Workflow ${status.replaceAll("_", " ")}`);
    if (["completed", "partial"].includes(status)) return record;
    if (["failed", "cancelled"].includes(status)) {
      throw new Error(`Workflow ended with status ${status}`);
    }
    await sleep(1000);
  }
  throw new Error("Workflow is still running. Refresh the estate to check its status.");
}

async function initialize() {
  clearAlert();
  showView("loading");
  try {
    state.session = await api("/v1/session");
    const collections = Object.keys(state.session.collectionRoles || {});
    document.querySelector("#avatar").textContent = state.session.subject
      .slice(0, 2)
      .toUpperCase();
    if (!state.session.hasGrant || collections.length === 0) {
      showView("no-access");
      return;
    }
    state.collectionId = collections[0];
    await loadEstates();
  } catch (error) {
    showView("loading");
    elements.loading.querySelector("h1").textContent = "Shaper could not open";
    elements.loading.querySelector("p").textContent = error.message;
    showAlert(error.message);
  }
}

async function loadEstates() {
  const payload = await api(
    `/v1/estates?collection_id=${encodeURIComponent(state.collectionId)}`,
  );
  state.estates = payload.items;
  renderEstates();
  showView("list");
  history.replaceState(null, "", "#estates");
  elements.estateListView.querySelector("h1").focus?.();
}

function renderEstates() {
  elements.estateList.replaceChildren(
    ...state.estates.map((record) => {
      const estate = recordValue(record);
      const article = document.createElement("article");
      article.className = "estate-card";
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.estateId = estate.estate_id;
      const badge = text("span", estate.status, `badge ${estate.status}`);
      const heading = text("h2", estate.name);
      const description = text(
        "p",
        estate.description || "No estate description has been added.",
      );
      const footer = document.createElement("footer");
      footer.append(
        text("span", `Revision ${record.revision}`),
        text("span", `Updated ${formatDate(estate.updated_at)}`),
      );
      button.append(badge, heading, description, footer);
      article.append(button);
      return article;
    }),
  );
  elements.estateEmpty.hidden = state.estates.length !== 0;
}

async function openEstate(estateId, targetTab = "sources") {
  clearAlert();
  showView("estate");
  setBusy(elements.estateView, true, "Loading estate…");
  try {
    const [estate, sources, documents, runs, decisions, artifacts] =
      await Promise.all([
        api(`/v1/estates/${estateId}`),
        api(`/v1/estates/${estateId}/sources`),
        api(`/v1/estates/${estateId}/documents`),
        api(`/v1/estates/${estateId}/runs`),
        api(`/v1/estates/${estateId}/decisions`),
        api(`/v1/estates/${estateId}/artifacts`),
      ]);
    state.estate = estate;
    state.sources = sources.items;
    state.documents = documents.items;
    state.runs = runs.items;
    state.decisions = new Map(
      decisions.items.map((decision) => [decision.document_id, decision]),
    );
    state.artifacts = artifacts.items;
    state.selectedDocuments.clear();
    await restoreWorkflowEvidence(estateId);
    renderEstate();
    switchTab(targetTab, false);
    history.replaceState(null, "", `#estate/${estateId}/${targetTab}`);
  } catch (error) {
    showAlert(error.message);
  } finally {
    setBusy(elements.estateView, false);
  }
}

async function restoreWorkflowEvidence(estateId) {
  const runs = state.runs.map(recordValue);
  const latestDiscovery = [...runs]
    .reverse()
    .find((run) => run.kind === "discover" && ["completed", "partial"].includes(run.status));
  state.discoveryRunId = latestDiscovery?.run_id ?? null;
  state.reports = new Map();
  if (state.discoveryRunId) {
    const reports = await api(
      `/v1/estates/${estateId}/discovery-reports?run_id=${encodeURIComponent(
        state.discoveryRunId,
      )}`,
    );
    state.reports = new Map(reports.items.map((report) => [report.document_id, report]));
  }
  const latestRecommendation = [...runs]
    .reverse()
    .find((run) => run.kind === "recommend" && ["completed", "partial"].includes(run.status));
  state.proposalRunId = latestRecommendation?.run_id ?? null;
  state.proposals = [];
  if (state.proposalRunId) {
    const proposals = await api(
      `/v1/estates/${estateId}/proposals?run_id=${encodeURIComponent(
        state.proposalRunId,
      )}`,
    );
    state.proposals = proposals.items;
  }
}

function renderEstate() {
  const estate = recordValue(state.estate);
  document.querySelector("#estateTitle").textContent = estate.name;
  document.querySelector("#estateDescription").textContent =
    estate.description || "No description has been added.";
  const status = document.querySelector("#estateStatus");
  status.textContent = estate.status;
  status.className = `badge ${estate.status}`;
  renderSources();
  renderDocuments();
  renderProposals();
  renderArtifacts();
  renderLifecycle();
}

function renderLifecycle() {
  const archived = isArchived();
  elements.archiveButton.disabled = archived;
  elements.purgeButton.disabled = !archived;
  document.querySelector("#lifecycleDescription").textContent = archived
    ? "This estate is read-only. Permanently purge its content only when retention policy permits."
    : "Archive this estate to make its evidence read-only. Purge becomes available after archive.";
  if (archived) {
    for (const control of [
      ...elements.sourceForm.elements,
      ...elements.uploadForm.elements,
      elements.discoverButton,
      elements.recommendButton,
      elements.transformButton,
    ]) {
      control.disabled = true;
    }
  }
}

function renderSources() {
  elements.sourceCount.textContent = `${state.sources.length} source${
    state.sources.length === 1 ? "" : "s"
  }`;
  elements.sourceList.replaceChildren(
    ...state.sources.map((record) => {
      const source = recordValue(record);
      const row = document.createElement("article");
      row.className = "item-row";
      const copy = document.createElement("div");
      copy.className = "item-copy";
      copy.append(
        text("h3", source.display_name),
        text("p", `${source.kind} · ${source.locator}`),
      );
      row.append(
        copy,
        text(
          "span",
          source.status.replaceAll("_", " "),
          `source-status ${source.status}`,
        ),
      );
      return row;
    }),
  );
  if (state.sources.length === 0) {
    elements.sourceList.append(
      text("p", "No sources have been registered.", "empty-inline"),
    );
  }
}

function renderDocuments() {
  elements.documentRows.replaceChildren(
    ...state.documents
      .filter((record) => !recordValue(record).deleted)
      .map((record) => {
        const documentValue = recordValue(record);
        const report = state.reports.get(documentValue.document_id);
        const row = document.createElement("tr");
        const selectCell = document.createElement("td");
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.dataset.documentId = documentValue.document_id;
        checkbox.checked = state.selectedDocuments.has(documentValue.document_id);
        checkbox.disabled = !report;
        checkbox.setAttribute("aria-label", `Select ${documentValue.title}`);
        selectCell.append(checkbox);
        const documentCell = document.createElement("td");
        documentCell.append(
          text("strong", documentValue.title),
          text("p", `${documentValue.media_type} · ${formatDate(documentValue.modified_at)}`),
        );
        const scoreCell = document.createElement("td");
        scoreCell.append(text("span", report ? `${report.readiness_score}` : "—", "score"));
        const effortCell = document.createElement("td");
        effortCell.append(
          text(
            "span",
            report ? report.effort_band : "Not assessed",
            `effort ${report?.effort_band ?? ""}`,
          ),
        );
        const findingsCell = document.createElement("td");
        findingsCell.textContent = report
          ? report.reasons.join(" ")
          : "Run discovery to assess this source version.";
        row.append(selectCell, documentCell, scoreCell, effortCell, findingsCell);
        return row;
      }),
  );
  elements.documentEmpty.hidden = state.documents.length !== 0;
  renderDiscoverySummary();
  updateSelection();
}

function renderDiscoverySummary() {
  const reports = [...state.reports.values()];
  elements.discoverySummary.hidden = reports.length === 0;
  if (reports.length === 0) return;
  const average = Math.round(
    reports.reduce((total, report) => total + report.readiness_score, 0) /
      reports.length,
  );
  const highEffort = reports.filter((report) => report.effort_band === "high").length;
  const findings = reports.reduce(
    (total, report) => total + report.finding_codes.length,
    0,
  );
  elements.discoverySummary.replaceChildren(
    metric("Estate readiness", `${average}/100`),
    metric("High-effort documents", highEffort),
    metric("Quality findings", findings),
  );
}

function metric(label, value) {
  const card = document.createElement("div");
  card.className = "metric";
  card.append(text("span", label), text("strong", `${value}`));
  return card;
}

function updateSelection() {
  const count = state.selectedDocuments.size;
  elements.selectionSummary.textContent = `${count} document${
    count === 1 ? "" : "s"
  } selected`;
  elements.recommendButton.disabled = count === 0 || !state.discoveryRunId;
}

function renderProposals() {
  elements.proposalList.replaceChildren(
    ...state.proposals.map((proposal) => {
      const documentValue = recordValue(
        state.documents.find(
          (documentRecord) =>
            recordValue(documentRecord).document_id === proposal.document_id,
        ),
      );
      const decision = state.decisions.get(proposal.document_id);
      const card = document.createElement("article");
      card.className = "proposal-card";
      card.dataset.proposalId = proposal.recommendation_id;
      const heading = document.createElement("div");
      heading.className = "proposal-heading";
      heading.append(
        text("h3", documentValue?.title || proposal.expected_artifact),
        text(
          "span",
          decision?.outcome || "Awaiting decision",
          `decision-badge ${decision?.outcome || ""}`,
        ),
      );
      const changes = document.createElement("ul");
      changes.className = "changes";
      changes.append(
        ...proposal.proposed_changes.map((change) => {
          const item = document.createElement("li");
          item.textContent = change;
          return item;
        }),
      );
      const estimate = proposal.token_estimate;
      const tokenGrid = document.createElement("div");
      tokenGrid.className = "token-grid";
      tokenGrid.append(
        tokenMetric("Input range", `${estimate.input_min}–${estimate.input_max}`),
        tokenMetric("Output range", `${estimate.output_min}–${estimate.output_max}`),
        tokenMetric("Expected total", estimate.expected_total),
        tokenMetric("Enforced maximum", estimate.enforced_maximum),
      );
      const actions = document.createElement("div");
      actions.className = "proposal-actions";
      const approve = text("button", "Approve transformation", "button primary");
      approve.type = "button";
      approve.disabled = isArchived();
      approve.dataset.decision = "approve";
      approve.dataset.proposalId = proposal.recommendation_id;
      const decline = text("button", "Decline", "button danger");
      decline.type = "button";
      decline.disabled = isArchived();
      decline.dataset.decision = "decline";
      decline.dataset.proposalId = proposal.recommendation_id;
      actions.append(approve, decline);
      card.append(
        heading,
        text("p", proposal.rationale),
        changes,
        tokenGrid,
        text(
          "p",
          `Output: ${proposal.expected_artifact} · Estimate confidence ${Math.round(
            estimate.confidence * 100,
          )}%`,
        ),
        actions,
      );
      return card;
    }),
  );
  elements.proposalEmpty.hidden = state.proposals.length !== 0;
  updateApprovals();
}

function tokenMetric(label, value) {
  const item = document.createElement("div");
  item.append(text("span", label), text("strong", `${value}`));
  return item;
}

function updateApprovals() {
  const approved = state.proposals.filter(
    (proposal) => state.decisions.get(proposal.document_id)?.outcome === "approve",
  );
  elements.approvalSummary.textContent = `${approved.length} approved transformation${
    approved.length === 1 ? "" : "s"
  }`;
  elements.transformButton.disabled = approved.length === 0;
}

function renderArtifacts() {
  elements.artifactList.replaceChildren(
    ...state.artifacts.map((record) => {
      const artifact = recordValue(record);
      const card = document.createElement("article");
      card.className = "artifact-card";
      const heading = document.createElement("div");
      heading.className = "artifact-heading";
      heading.append(
        text("h3", artifact.filename),
        text("span", artifact.status.replaceAll("_", " "), `badge ${artifact.status}`),
      );
      const actions = document.createElement("div");
      actions.className = "artifact-actions";
      const evaluation = artifact.evaluation;
      const evaluationGrid = document.createElement("div");
      evaluationGrid.className = "token-grid";
      if (evaluation) {
        evaluationGrid.setAttribute("aria-label", "Transformation evaluation");
        evaluationGrid.append(
          tokenMetric("Overall evaluation", `${evaluation.overall_score}/100`),
          tokenMetric("Citation coverage", `${evaluation.citation_coverage_score}/100`),
          tokenMetric("Structure", `${evaluation.structure_score}/100`),
          tokenMetric("Validation", `${evaluation.validation_score}/100`),
        );
      }
      if (artifact.status !== "approved") {
        const approve = text("button", "Approve for publication", "button primary");
        approve.type = "button";
        approve.dataset.approveArtifact = artifact.artifact_id;
        approve.dataset.artifactRevision = record.revision;
        approve.disabled = isArchived();
        actions.append(approve);
      } else {
        const view = text("a", "Open approved HTML", "button secondary");
        view.href = `/v1/artifacts/${encodeURIComponent(artifact.artifact_id)}/content`;
        view.target = "_blank";
        view.rel = "noopener";
        actions.append(view);
      }
      card.append(
        heading,
        text("p", `Source version ${artifact.source_version.slice(0, 12)}…`),
        ...(evaluation
          ? [
              evaluationGrid,
              text(
                "p",
                evaluation.passed
                  ? "Automated evaluation passed. Human review is still required."
                  : `${evaluation.blocking_findings} blocking evaluation finding(s).`,
              ),
            ]
          : []),
        actions,
      );
      return card;
    }),
  );
  elements.artifactEmpty.hidden = state.artifacts.length !== 0;
}

function switchTab(name, focus = true) {
  document.querySelectorAll("[data-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.panel !== name;
  });
  document.querySelectorAll("[data-tab]").forEach((button) => {
    if (button.dataset.tab === name) {
      button.setAttribute("aria-current", "step");
    } else {
      button.removeAttribute("aria-current");
    }
  });
  if (state.estate) {
    history.replaceState(
      null,
      "",
      `#estate/${recordValue(state.estate).estate_id}/${name}`,
    );
  }
  if (focus) {
    const heading = document.querySelector(`[data-panel="${name}"] h2`);
    heading?.focus();
    announce(`${heading?.textContent || name} opened`);
  }
}

async function createEstate(event) {
  event.preventDefault();
  clearAlert();
  const data = new FormData(elements.createForm);
  try {
    const record = await api("/v1/estates", {
      method: "POST",
      body: JSON.stringify({
        collection_id: state.collectionId,
        name: data.get("name"),
        description: data.get("description"),
        artifact_name_template: data.get("artifact_name_template"),
      }),
    });
    elements.createDialog.close();
    elements.createForm.reset();
    document.querySelector("#artifactTemplate").value = "shaper_{source_stem}.html";
    state.estates.push(record);
    renderEstates();
    announce("Knowledge estate created");
    await openEstate(recordValue(record).estate_id);
  } catch (error) {
    showAlert(error.message);
  }
}

async function addSource(event) {
  event.preventDefault();
  clearAlert();
  const data = new FormData(elements.sourceForm);
  setBusy(document.querySelector('[data-panel="sources"]'), true, "Adding source…");
  try {
    const record = await api(
      `/v1/estates/${recordValue(state.estate).estate_id}/sources`,
      {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(data)),
      },
    );
    state.sources.push(record);
    elements.sourceForm.reset();
    renderSources();
    announce("Source registered. Connection has not been claimed.");
  } catch (error) {
    showAlert(error.message);
  } finally {
    setBusy(document.querySelector('[data-panel="sources"]'), false);
  }
}

async function uploadFiles(event) {
  event.preventDefault();
  clearAlert();
  if (elements.files.files.length === 0) return;
  const body = new FormData();
  [...elements.files.files].forEach((file) => body.append("files", file));
  const panel = document.querySelector('[data-panel="sources"]');
  setBusy(panel, true, "Scanning and inventorying files…");
  try {
    const result = await api(
      `/v1/estates/${recordValue(state.estate).estate_id}/uploads`,
      { method: "POST", body },
    );
    state.sources.push(...result.sources);
    state.documents.push(...result.documents);
    elements.uploadForm.reset();
    elements.fileSummary.textContent = "No files selected";
    renderSources();
    renderDocuments();
    announce(
      `${result.documents.length} document${
        result.documents.length === 1 ? "" : "s"
      } inventoried`,
    );
  } catch (error) {
    showAlert(error.message);
  } finally {
    setBusy(panel, false);
  }
}

async function runDiscovery() {
  clearAlert();
  const panel = document.querySelector('[data-panel="discover"]');
  setBusy(panel, true, "Five specialist agents are assessing the estate…");
  try {
    const result = await api(
      `/v1/estates/${recordValue(state.estate).estate_id}/discovery-runs`,
      { method: "POST", body: JSON.stringify({}) },
    );
    state.discoveryRunId = recordValue(result.run).run_id;
    await waitForRun(state.discoveryRunId);
    const reports = await api(
      `/v1/estates/${recordValue(state.estate).estate_id}/discovery-reports?run_id=${encodeURIComponent(
        state.discoveryRunId,
      )}`,
    );
    state.reports = new Map(
      reports.items.map((report) => [report.document_id, report]),
    );
    renderDocuments();
    announce(`Discovery completed for ${reports.items.length} documents`);
  } catch (error) {
    showAlert(error.message);
  } finally {
    setBusy(panel, false);
  }
}

async function requestRecommendations() {
  clearAlert();
  const panel = document.querySelector('[data-panel="discover"]');
  setBusy(panel, true, "Preparing recommendations and token estimates…");
  try {
    const result = await api(
      `/v1/estates/${recordValue(state.estate).estate_id}/recommendation-runs`,
      {
        method: "POST",
        body: JSON.stringify({
          discovery_run_id: state.discoveryRunId,
          ids: [...state.selectedDocuments],
        }),
      },
    );
    state.proposalRunId = recordValue(result.run).run_id;
    await waitForRun(state.proposalRunId);
    state.proposals = await api(
      `/v1/estates/${recordValue(state.estate).estate_id}/proposals?run_id=${encodeURIComponent(
        state.proposalRunId,
      )}`,
    ).then((payload) => payload.items);
    renderProposals();
    switchTab("recommend");
  } catch (error) {
    showAlert(error.message);
  } finally {
    setBusy(panel, false);
  }
}

async function decide(proposalId, outcome) {
  clearAlert();
  const proposal = state.proposals.find(
    (item) => item.recommendation_id === proposalId,
  );
  if (!proposal) return;
  const current = state.decisions.get(proposal.document_id);
  const card = document
    .querySelector(`[data-proposal-id="${CSS.escape(proposalId)}"]`)
    ?.closest(".proposal-card");
  if (card) setBusy(card, true, "Recording decision…");
  try {
    const decision = await api(`/v1/proposals/${proposalId}/decision`, {
      method: "PUT",
      body: JSON.stringify({
        outcome,
        reason:
          outcome === "approve"
            ? "Approved by reviewer in the Shaper estate workspace."
            : "Declined by reviewer in the Shaper estate workspace.",
        expected_current_decision_id: current?.decision_id ?? null,
      }),
    });
    state.decisions.set(proposal.document_id, decision);
    renderProposals();
    announce(`Transformation ${outcome === "approve" ? "approved" : "declined"}`);
  } catch (error) {
    showAlert(error.message);
  } finally {
    if (card) setBusy(card, false);
  }
}

async function transformApproved() {
  clearAlert();
  const approvedIds = state.proposals
    .filter(
      (proposal) =>
        state.decisions.get(proposal.document_id)?.outcome === "approve",
    )
    .map((proposal) => proposal.recommendation_id);
  const panel = document.querySelector('[data-panel="recommend"]');
  setBusy(panel, true, "Creating approved agent-ready HTML…");
  try {
    const result = await api(
      `/v1/estates/${recordValue(state.estate).estate_id}/transformation-runs`,
      {
        method: "POST",
        body: JSON.stringify({ ids: approvedIds }),
      },
    );
    await waitForRun(recordValue(result.run).run_id);
    state.artifacts = await api(
      `/v1/estates/${recordValue(state.estate).estate_id}/artifacts`,
    ).then((payload) => payload.items);
    renderArtifacts();
    switchTab("transform");
    announce(
      `Transformation ${recordValue(result.run).status}. ${state.artifacts.length} artifact records available.`,
    );
  } catch (error) {
    showAlert(error.message);
  } finally {
    setBusy(panel, false);
  }
}

async function approveArtifact(artifactId, revision) {
  clearAlert();
  const panel = document.querySelector('[data-panel="transform"]');
  setBusy(panel, true, "Publishing reviewed artifact…");
  try {
    await api(`/v1/artifacts/${artifactId}/approve`, {
      method: "POST",
      body: JSON.stringify({
        reason: "Grounding and output reviewed in the Shaper estate workspace.",
        expected_review_revision: 1,
        expected_artifact_revision: Number(revision),
      }),
    });
    state.artifacts = await api(
      `/v1/estates/${recordValue(state.estate).estate_id}/artifacts`,
    ).then((payload) => payload.items);
    renderArtifacts();
    announce("Artifact approved for publication");
  } catch (error) {
    showAlert(error.message);
  } finally {
    setBusy(panel, false);
  }
}

async function archiveEstate() {
  const estate = recordValue(state.estate);
  if (
    !window.confirm(
      `Archive "${estate.name}"? The estate will become read-only and cannot be restored.`,
    )
  ) {
    return;
  }
  clearAlert();
  setBusy(elements.estateView, true, "Archiving estate…");
  try {
    state.estate = await api(`/v1/estates/${estate.estate_id}/archive`, {
      method: "POST",
      body: JSON.stringify({ expected_revision: state.estate.revision }),
    });
    renderEstate();
    announce("Knowledge estate archived and is now read-only");
  } catch (error) {
    showAlert(error.message);
  } finally {
    setBusy(elements.estateView, false);
  }
}

function openPurgeDialog() {
  const estate = recordValue(state.estate);
  elements.purgePhrase.textContent = `PURGE ${estate.name}`;
  elements.purgeForm.reset();
  elements.purgeDialog.showModal();
}

async function purgeEstate(event) {
  event.preventDefault();
  clearAlert();
  const estate = recordValue(state.estate);
  const data = new FormData(elements.purgeForm);
  setBusy(elements.purgeDialog, true, "Permanently purging estate…");
  try {
    await api(`/v1/estates/${estate.estate_id}/purge`, {
      method: "POST",
      body: JSON.stringify({
        confirmation: data.get("confirmation"),
        reason: data.get("reason"),
      }),
    });
    elements.purgeDialog.close();
    state.estate = null;
    announce("Knowledge estate purged");
    await loadEstates();
  } catch (error) {
    showAlert(error.message);
  } finally {
    setBusy(elements.purgeDialog, false);
  }
}

document.addEventListener("click", async (event) => {
  const target = event.target.closest("button, a");
  if (!target) return;
  if (target.dataset.action === "home") {
    event.preventDefault();
    await loadEstates();
  } else if (target.dataset.action === "open-create") {
    elements.createDialog.showModal();
  } else if (target.dataset.action === "close-create") {
    elements.createDialog.close();
  } else if (target.dataset.action === "close-purge") {
    elements.purgeDialog.close();
  } else if (target.dataset.estateId) {
    await openEstate(target.dataset.estateId);
  } else if (target.dataset.tab) {
    switchTab(target.dataset.tab);
  } else if (target.dataset.decision) {
    await decide(target.dataset.proposalId, target.dataset.decision);
  } else if (target.dataset.approveArtifact) {
    await approveArtifact(
      target.dataset.approveArtifact,
      target.dataset.artifactRevision,
    );
  }
});

elements.createForm.addEventListener("submit", createEstate);
elements.sourceForm.addEventListener("submit", addSource);
elements.uploadForm.addEventListener("submit", uploadFiles);
elements.discoverButton.addEventListener("click", runDiscovery);
elements.recommendButton.addEventListener("click", requestRecommendations);
elements.transformButton.addEventListener("click", transformApproved);
elements.archiveButton.addEventListener("click", archiveEstate);
elements.purgeButton.addEventListener("click", openPurgeDialog);
elements.purgeForm.addEventListener("submit", purgeEstate);
elements.files.addEventListener("change", () => {
  const count = elements.files.files.length;
  elements.fileSummary.textContent =
    count === 0 ? "No files selected" : `${count} file${count === 1 ? "" : "s"} selected`;
});
elements.documentRows.addEventListener("change", (event) => {
  const checkbox = event.target.closest('input[type="checkbox"][data-document-id]');
  if (!checkbox) return;
  if (checkbox.checked) {
    state.selectedDocuments.add(checkbox.dataset.documentId);
  } else {
    state.selectedDocuments.delete(checkbox.dataset.documentId);
  }
  updateSelection();
});

initialize();
