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
  activeFindingDocumentId: null,
  findingTrigger: null,
  restoreFindingFocus: true,
  transitioningFindingPresentation: false,
  assessmentChecks: null,
  assessmentCheckCategory: 0,
  evaluationSuggestions: [],
  selectedEvaluationSuggestions: new Set(),
  evaluationSuggestionErrors: [],
  actionEstate: null,
  openEstateMenuId: null,
};

const RESULT_PRESENTATION = Object.freeze({
  poor_metadata: {
    label: "Limited metadata",
    detail: "Core topic and content metadata is incomplete.",
    agentImpact:
      "Weak metadata gives retrieval systems less context for filtering and ranking the right passage.",
    icon: "◇",
    tone: "info",
  },
  structure_gap: {
    label: "Weak structure",
    detail: "Headings or focused content sections are missing.",
    agentImpact:
      "Weak section boundaries make it harder to create focused chunks and retrieve the right passage.",
    icon: "▤",
    tone: "info",
  },
  stale: {
    label: "Freshness risk",
    detail: "The source is beyond the three-year review threshold.",
    agentImpact: "Outdated guidance can cause an agent to return obsolete rules as current.",
    icon: "◷",
    tone: "warning",
  },
  long_paragraph: {
    label: "Long paragraph",
    detail: "A passage exceeds 150 words and may reduce retrieval precision.",
    agentImpact: "Oversized passages mix ideas and can reduce chunk and retrieval precision.",
    icon: "↔",
    tone: "warning",
  },
  cross_policy_reference: {
    label: "Document reference",
    detail: "A reference to another governed source needs explicit context.",
    agentImpact:
      "A reference without local context can leave the agent with an incomplete rule.",
    icon: "↗",
    tone: "warning",
  },
  faq_gap: {
    label: "No question coverage",
    detail: "No FAQ or question-shaped content was detected.",
    agentImpact:
      "Missing question-shaped content can reduce direct matches for common user requests.",
    icon: "?",
    tone: "info",
  },
  procedure_gap: {
    label: "Implicit procedure",
    detail: "Procedural language is not organized into explicit steps.",
    agentImpact:
      "Implicit steps make it harder for an agent to extract and present a reliable sequence.",
    icon: "1·",
    tone: "warning",
  },
});

const ACCOUNTABILITY_ONLY_FINDINGS = new Set(["missing_owner"]);

const elements = {
  workspace: document.querySelector("#workspace"),
  status: document.querySelector("#status"),
  alert: document.querySelector("#alert"),
  loading: document.querySelector("#loadingView"),
  noAccess: document.querySelector("#noAccessView"),
  assessmentChecksView: document.querySelector("#assessmentChecksView"),
  assessmentCheckGroups: document.querySelector("#assessmentCheckGroups"),
  estateListView: document.querySelector("#estateListView"),
  estateView: document.querySelector("#estateView"),
  estateList: document.querySelector("#estateList"),
  estateEmpty: document.querySelector("#estateEmpty"),
  estateListCount: document.querySelector("#estateListCount"),
  estateTotal: document.querySelector("#estateTotal"),
  estateActive: document.querySelector("#estateActive"),
  estateAssessed: document.querySelector("#estateAssessed"),
  createDialog: document.querySelector("#createDialog"),
  createForm: document.querySelector("#createForm"),
  editDialog: document.querySelector("#editDialog"),
  editForm: document.querySelector("#editForm"),
  editEstateName: document.querySelector("#editEstateName"),
  editEstateDescription: document.querySelector("#editEstateDescription"),
  editArtifactTemplate: document.querySelector("#editArtifactTemplate"),
  editEvaluations: document.querySelector("#editEvaluations"),
  editConfirmButton: document.querySelector("#editConfirmButton"),
  editError: document.querySelector("#editError"),
  sourceInputTabs: document.querySelector(".source-input-tabs"),
  deleteDialog: document.querySelector("#deleteDialog"),
  deleteForm: document.querySelector("#deleteForm"),
  deleteEstateName: document.querySelector("#deleteEstateName"),
  deleteConfirmation: document.querySelector("#deleteConfirmation"),
  deleteConfirmButton: document.querySelector("#deleteConfirmButton"),
  deleteError: document.querySelector("#deleteError"),
  sourceForm: document.querySelector("#sourceForm"),
  sourceKind: document.querySelector("#sourceKind"),
  sharePointCredentialField: document.querySelector("#sharePointCredentialField"),
  sharePointCredentialMode: document.querySelector("#sharePointCredentialMode"),
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
  proposalStatus: document.querySelector("#proposalStatus"),
  proposalStatusTitle: document.querySelector("#proposalStatusTitle"),
  proposalStatusDetail: document.querySelector("#proposalStatusDetail"),
  evaluationOptions: document.querySelector("#evaluationOptions"),
  evaluationTarget: document.querySelector("#evaluationTarget"),
  evaluationTargetGuidance: document.querySelector("#evaluationTargetGuidance"),
  evaluationSuggestionList: document.querySelector("#evaluationSuggestionList"),
  evaluationSelectionSummary: document.querySelector("#evaluationSelectionSummary"),
  downloadEvaluations: document.querySelector("#downloadEvaluations"),
  approvalSummary: document.querySelector("#approvalSummary"),
  generateEvaluations: document.querySelector("#generateEvaluations"),
  transformButton: document.querySelector("#transformButton"),
  artifactList: document.querySelector("#artifactList"),
  artifactEmpty: document.querySelector("#artifactEmpty"),
  archiveButton: document.querySelector("#archiveButton"),
  purgeButton: document.querySelector("#purgeButton"),
  purgeDialog: document.querySelector("#purgeDialog"),
  purgeForm: document.querySelector("#purgeForm"),
  purgePhrase: document.querySelector("#purgePhrase"),
  documentDialog: document.querySelector("#documentDialog"),
  documentDialogTitle: document.querySelector("#documentDialogTitle"),
  documentDownload: document.querySelector("#documentDownload"),
  documentSourceStatus: document.querySelector("#documentSourceStatus"),
  documentContent: document.querySelector("#documentContent"),
  discoveryReviewLayout: document.querySelector("#discoveryReviewLayout"),
  documentFindingsPanel: document.querySelector("#documentFindingsPanel"),
  documentFindingsTitle: document.querySelector("#documentFindingsTitle"),
  documentFindingsSummary: document.querySelector("#documentFindingsSummary"),
  documentFindingsBody: document.querySelector("#documentFindingsBody"),
  documentFindingsDialog: document.querySelector("#documentFindingsDialog"),
  documentFindingsDialogTitle: document.querySelector("#documentFindingsDialogTitle"),
  documentFindingsDialogSummary: document.querySelector("#documentFindingsDialogSummary"),
  documentFindingsDialogBody: document.querySelector("#documentFindingsDialogBody"),
};
const findingsDialogMedia = window.matchMedia("(max-width: 1240px)");

function announce(message) {
  elements.status.textContent = "";
  requestAnimationFrame(() => {
    elements.status.textContent = message;
  });
}

function evaluationPassages(sourceText) {
  const passages = [];
  let heading = "";
  sourceText
    .split(/\n\s*\n/)
    .map((part) => part.trim())
    .filter(Boolean)
    .forEach((part) => {
      const headingMatch = part.match(/^#{1,6}\s+([^\n]+)(?:\n+([\s\S]+))?$/);
      let content = part;
      if (headingMatch) {
        heading = headingMatch[1].trim();
        content = (headingMatch[2] ?? "").trim();
        if (!content) return;
      }
      const candidates =
        content.length > 1200
          ? content.match(/[^.!?]+[.!?]+|[^.!?]+$/g)?.map((sentence) => sentence.trim()) ??
            []
          : [content];
      candidates
        .filter((candidate) => candidate.length >= 40)
        .forEach((candidate) => passages.push({ heading, text: candidate.slice(0, 1000) }));
    });
  const seen = new Set();
  return passages.filter((passage) => {
    const key = `${passage.heading}\n${passage.text}`.toLocaleLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function evaluationKeywords(passage) {
  const excluded = new Set([
    "about",
    "after",
    "before",
    "from",
    "have",
    "must",
    "shall",
    "that",
    "their",
    "there",
    "these",
    "this",
    "with",
  ]);
  return [...new Set(passage.toLocaleLowerCase().match(/[a-z][a-z-]{3,}/g) ?? [])]
    .filter((word) => !excluded.has(word))
    .slice(0, 5);
}

function suggestedEvaluations(proposal, documentValue, sourceText) {
  return evaluationPassages(sourceText)
    .slice(0, 5)
    .map((passage, index) => {
      const focus = passage.heading || passage.text.split(/\s+/).slice(0, 7).join(" ");
      return {
        id: `${proposal.recommendation_id}-evaluation-${index + 1}`,
        document_id: documentValue.document_id,
        source_version: documentValue.source_version,
        source_reference: `${documentValue.document_id}@${documentValue.source_version}`,
        query: passage.heading
          ? `According to ${documentValue.title}, what guidance is provided under "${focus}"?`
          : `According to ${documentValue.title}, what does the source say about "${focus}…"?`,
        ground_truth: passage.text,
        context: passage.text,
        keywords: evaluationKeywords(`${passage.heading} ${passage.text}`),
        foundry_evaluators: ["groundedness", "relevance", "completeness"],
        copilot_studio_methods: ["General quality", "Compare meaning", "Keyword match"],
        needs_sme_review: true,
      };
    });
}

async function loadEvaluationSuggestions() {
  state.evaluationSuggestions = [];
  state.selectedEvaluationSuggestions.clear();
  state.evaluationSuggestionErrors = [];
  const estateId = recordValue(state.estate).estate_id;
  for (const proposal of state.proposals) {
    const documentRecord = state.documents.find(
      (item) => recordValue(item).document_id === proposal.document_id,
    );
    const documentValue = documentRecord ? recordValue(documentRecord) : null;
    if (!documentValue) {
      state.evaluationSuggestionErrors.push(
        `The source document for ${proposal.expected_artifact} is unavailable.`,
      );
      continue;
    }
    try {
      const sourceText = await apiText(
        `/v1/estates/${estateId}/documents/${encodeURIComponent(
          documentValue.document_id,
        )}/content?source_version=${encodeURIComponent(documentValue.source_version)}`,
      );
      state.evaluationSuggestions.push(
        ...suggestedEvaluations(proposal, documentValue, sourceText),
      );
    } catch (error) {
      state.evaluationSuggestionErrors.push(
        `Suggestions for ${documentValue.title} could not be created: ${error.message}`,
      );
    }
  }
  state.evaluationSuggestions.forEach((suggestion) => {
    state.selectedEvaluationSuggestions.add(suggestion.id);
  });
}

function renderEvaluationOptions() {
  const hasPlans = state.proposals.length > 0;
  elements.evaluationOptions.hidden = !hasPlans;
  if (!hasPlans) {
    elements.evaluationSuggestionList.replaceChildren();
    return;
  }
  const target = elements.evaluationTarget.value;
  elements.evaluationTargetGuidance.textContent =
    target === "foundry"
      ? "Exports JSONL using Foundry standard columns: query, ground_truth, and context. Select groundedness, relevance, and completeness evaluators when configuring the run."
      : "Exports question and expectedResponse for a Copilot Studio single-response test set. Suggested keywords remain here for configuring keyword-match evaluation after import.";
  const items = state.evaluationSuggestions.map((suggestion) => {
    const item = document.createElement("article");
    item.className = "evaluation-suggestion";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = state.selectedEvaluationSuggestions.has(suggestion.id);
    checkbox.dataset.evaluationSuggestion = suggestion.id;
    checkbox.setAttribute("aria-label", `Include evaluation: ${suggestion.query}`);
    const content = document.createElement("div");
    const methods =
      target === "foundry"
        ? suggestion.foundry_evaluators.join(", ")
        : suggestion.copilot_studio_methods.join(", ");
    content.append(
      text("h4", suggestion.query),
      text("p", suggestion.ground_truth, "evaluation-expected-answer"),
      text("p", `Suggested evaluation methods: ${methods}`, "evaluation-methods"),
    );
    if (target === "copilot-studio") {
      content.append(
        text(
          "p",
          `Suggested keywords: ${suggestion.keywords.join(", ")}`,
          "evaluation-methods",
        ),
      );
    }
    item.append(checkbox, content);
    return item;
  });
  if (state.evaluationSuggestionErrors.length) {
    items.push(
      text(
        "p",
        state.evaluationSuggestionErrors.join(" "),
        "evaluation-suggestion-warning",
      ),
    );
  }
  if (items.length === 0) {
    items.push(
      text(
        "p",
        "No sufficiently substantive passages were found. Add test cases manually after reviewing the source.",
        "evaluation-suggestion-warning",
      ),
    );
  }
  elements.evaluationSuggestionList.replaceChildren(...items);
  const selected = state.selectedEvaluationSuggestions.size;
  elements.evaluationSelectionSummary.textContent = `${selected} suggested evaluation${
    selected === 1 ? "" : "s"
  } selected`;
  elements.downloadEvaluations.disabled = selected === 0;
}

function csvCell(value) {
  return `"${String(value).replaceAll('"', '""')}"`;
}

function downloadEvaluationDataset() {
  const selected = state.evaluationSuggestions.filter((suggestion) =>
    state.selectedEvaluationSuggestions.has(suggestion.id),
  );
  if (selected.length === 0) return;
  const target = elements.evaluationTarget.value;
  let content;
  let filename;
  let type;
  if (target === "foundry") {
    content = selected
      .map((suggestion) =>
        JSON.stringify({
          query: suggestion.query,
          ground_truth: suggestion.ground_truth,
          context: suggestion.context,
          metadata: {
            case_id: suggestion.id,
            source_reference: suggestion.source_reference,
            needs_sme_review: suggestion.needs_sme_review,
          },
        }),
      )
      .join("\n");
    filename = "shaper-foundry-evaluation-dataset.jsonl";
    type = "application/x-ndjson";
  } else {
    const rows = [
      ["question", "expectedResponse"],
      ...selected.map((suggestion) => [suggestion.query, suggestion.ground_truth]),
    ];
    content = rows.map((row) => row.map(csvCell).join(",")).join("\r\n");
    filename = "shaper-copilot-studio-test-set.csv";
    type = "text/csv";
  }
  const url = URL.createObjectURL(new Blob([content], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  announce(`${selected.length} evaluation cases prepared for download`);
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

async function redirectToSignIn() {
  const returnPath = `${window.location.pathname}${window.location.hash}`;
  window.location.assign(
    `/.auth/login/aad?post_login_redirect_uri=${encodeURIComponent(returnPath)}`,
  );
  await new Promise(() => {});
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("Accept", "application/json");
  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(path, {
    credentials: "same-origin",
    redirect: "manual",
    ...options,
    headers,
  });
  if (response.status === 401 || response.type === "opaqueredirect") {
    await redirectToSignIn();
  }
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

async function apiText(path) {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: state.token ? { Authorization: `Bearer ${state.token}` } : {},
    redirect: "manual",
  });
  if (response.status === 401 || response.type === "opaqueredirect") {
    await redirectToSignIn();
  }
  if (!response.ok) {
    throw new Error(`Request failed with HTTP ${response.status}`);
  }
  return response.text();
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
  elements.assessmentChecksView.hidden = view !== "assessment-checks";
  elements.estateListView.hidden = view !== "list";
  elements.estateView.hidden = view !== "estate";
}

function text(tag, value, className) {
  const node = document.createElement(tag);
  node.textContent = value;
  if (className) node.className = className;
  return node;
}

function resultItem({
  label,
  detail,
  agentImpact,
  tone,
  evidence = [],
  review_required = false,
}) {
  const item = document.createElement("li");
  item.className = `result-item ${tone}`;
  const copy = document.createElement("div");
  copy.className = "result-copy";
  const heading = document.createElement("div");
  heading.className = "result-heading";
  heading.append(text("strong", label));
  if (tone !== "clear") {
    heading.append(
      text(
        "span",
        tone === "high" ? "High priority" : tone === "warning" ? "Review" : "Advisory",
        `result-severity ${tone}`,
      ),
    );
  }
  copy.append(heading, text("p", detail, "result-detail"));
  if (agentImpact) {
    const impact = document.createElement("p");
    impact.className = "result-impact";
    impact.append(
      text("span", "Agent impact:", "result-impact-label"),
      document.createTextNode(` ${agentImpact}`),
    );
    copy.append(impact);
  }
  if (review_required) {
    copy.append(text("span", "Content owner review required", "review-required"));
  }
  if (evidence.length > 0) {
    const details = document.createElement("details");
    details.className = "result-evidence";
    details.append(text("summary", `Evidence (${evidence.length})`));
    evidence.forEach((entry) => {
      const figure = document.createElement("figure");
      figure.append(text("blockquote", entry.quote), text("figcaption", entry.location));
      details.append(figure);
    });
    copy.append(details);
  }
  item.append(copy);
  return item;
}

function classifyFindings(report = {}) {
  if (report.findings?.length) {
    return report.findings.map((finding) => {
      const presentation = RESULT_PRESENTATION[finding.code] ?? {};
      return {
        label: finding.label,
        detail: finding.explanation,
        agentImpact:
          finding.agent_impact ??
          presentation.agentImpact ??
          "This issue can make agent answers less reliable or complete.",
        icon: presentation.icon ?? "!",
        tone: presentation.tone ?? finding.severity ?? "warning",
        evidence: finding.evidence ?? [],
        review_required: finding.review_required,
      };
    });
  }
  const codes = report.finding_codes ?? [];
  const classified = codes
    .map((code) => RESULT_PRESENTATION[code])
    .filter((result) => result !== undefined);
  const hasUnknown = codes.some(
    (code) => !RESULT_PRESENTATION[code] && !ACCOUNTABILITY_ONLY_FINDINGS.has(code),
  );
  if (hasUnknown) {
    classified.push({
      label: "Additional issue detected",
      detail: "This assessment includes a result this version cannot display yet.",
      agentImpact:
        "The effect on agent responses is unknown until this result type is supported.",
      icon: "!",
      tone: "unknown",
    });
  }
  return classified;
}

function documentFindings(report, documentTitle = "Document") {
  const classified = classifyFindings(report);
  const results = document.createElement("ul");
  results.className = "result-list";
  results.setAttribute("aria-label", `${documentTitle} content quality findings`);
  results.append(...classified.map(resultItem));
  if (classified.length === 0) {
    results.append(
      resultItem({
        label: "No content issues detected",
        detail: "No supported reshaping issues were found in this source version.",
        icon: "✓",
        tone: "clear",
      }),
    );
    return results;
  }

  return results;
}

function findingReviewButton(report, documentValue) {
  const classified = classifyFindings(report);
  if (classified.length === 0) {
    return text("span", "No findings", "no-findings");
  }
  const highPriority = classified.filter((finding) => finding.tone === "high").length;
  const button = document.createElement("button");
  button.type = "button";
  button.className = "findings-review-button";
  button.dataset.reviewFindings = documentValue.document_id;
  button.setAttribute(
    "aria-label",
    `Review ${classified.length} finding${
      classified.length === 1 ? "" : "s"
    } for ${documentValue.title}`,
  );
  button.setAttribute("aria-controls", "documentFindingsPanel documentFindingsDialog");
  button.setAttribute(
    "aria-pressed",
    `${state.activeFindingDocumentId === documentValue.document_id}`,
  );
  const summaryCopy = document.createElement("span");
  summaryCopy.className = "findings-summary-copy";
  summaryCopy.append(
    text(
      "strong",
      `${classified.length} finding${classified.length === 1 ? "" : "s"}`,
    ),
    text(
      "small",
      highPriority > 0
        ? `${highPriority} high priority · Review agent impact and evidence`
        : "Review agent impact and evidence",
    ),
  );
  button.append(summaryCopy, text("span", "›", "findings-chevron"));
  return button;
}

function populateFindingsDetail(documentValue, report, title, summary, body) {
  const findings = classifyFindings(report);
  title.textContent = documentValue.title;
  summary.textContent = `${findings.length} finding${
    findings.length === 1 ? "" : "s"
  } · ${report.checks_completed?.length ?? 7} checks run`;
  body.replaceChildren(documentFindings(report, documentValue.title));
}

function updateFindingButtons() {
  elements.documentRows.querySelectorAll("[data-review-findings]").forEach((button) => {
    const active = button.dataset.reviewFindings === state.activeFindingDocumentId;
    button.setAttribute("aria-pressed", `${active}`);
    button.closest("tr")?.classList.toggle("findings-active", active);
  });
}

function closeDocumentFindings({ restoreFocus = true } = {}) {
  if (elements.documentFindingsDialog.open) {
    state.restoreFindingFocus = restoreFocus;
    elements.documentFindingsDialog.close();
    return;
  }
  elements.documentFindingsPanel.hidden = true;
  elements.discoveryReviewLayout.classList.remove("has-findings");
  state.activeFindingDocumentId = null;
  updateFindingButtons();
  if (restoreFocus && state.findingTrigger?.isConnected) state.findingTrigger.focus();
  state.findingTrigger = null;
}

function openDocumentFindings(button) {
  const documentId = button.dataset.reviewFindings;
  if (
    state.activeFindingDocumentId === documentId &&
    !elements.documentFindingsPanel.hidden
  ) {
    closeDocumentFindings();
    return;
  }
  const documentRecord = state.documents.find(
    (record) => recordValue(record).document_id === documentId,
  );
  const documentValue = documentRecord ? recordValue(documentRecord) : null;
  const report = state.reports.get(documentId);
  if (!documentValue || !report) return;
  state.activeFindingDocumentId = documentId;
  state.findingTrigger = button;
  updateFindingButtons();
  if (findingsDialogMedia.matches) {
    populateFindingsDetail(
      documentValue,
      report,
      elements.documentFindingsDialogTitle,
      elements.documentFindingsDialogSummary,
      elements.documentFindingsDialogBody,
    );
    elements.documentFindingsDialog.showModal();
    elements.documentFindingsDialogTitle.focus();
    return;
  }
  populateFindingsDetail(
    documentValue,
    report,
    elements.documentFindingsTitle,
    elements.documentFindingsSummary,
    elements.documentFindingsBody,
  );
  elements.documentFindingsPanel.hidden = false;
  elements.discoveryReviewLayout.classList.add("has-findings");
  elements.documentFindingsTitle.focus();
}

function moveOpenFindingsToCurrentLayout() {
  const documentId = state.activeFindingDocumentId;
  if (!documentId) return;
  const documentRecord = state.documents.find(
    (record) => recordValue(record).document_id === documentId,
  );
  const documentValue = documentRecord ? recordValue(documentRecord) : null;
  const report = state.reports.get(documentId);
  if (!documentValue || !report) {
    closeDocumentFindings({ restoreFocus: false });
    return;
  }
  if (findingsDialogMedia.matches && !elements.documentFindingsDialog.open) {
    elements.documentFindingsPanel.hidden = true;
    elements.discoveryReviewLayout.classList.remove("has-findings");
    populateFindingsDetail(
      documentValue,
      report,
      elements.documentFindingsDialogTitle,
      elements.documentFindingsDialogSummary,
      elements.documentFindingsDialogBody,
    );
    elements.documentFindingsDialog.showModal();
    elements.documentFindingsDialogTitle.focus();
  } else if (!findingsDialogMedia.matches && elements.documentFindingsDialog.open) {
    state.transitioningFindingPresentation = true;
    elements.documentFindingsDialog.close();
    populateFindingsDetail(
      documentValue,
      report,
      elements.documentFindingsTitle,
      elements.documentFindingsSummary,
      elements.documentFindingsBody,
    );
    elements.documentFindingsPanel.hidden = false;
    elements.discoveryReviewLayout.classList.add("has-findings");
    elements.documentFindingsTitle.focus();
  }
}

function fileFormatLabel(documentValue) {
  const extension = documentValue.filename?.split(".").at(-1)?.toLocaleLowerCase();
  const labels = {
    docx: "DOCX",
    md: "Markdown",
    pdf: "PDF",
    txt: "Text",
  };
  if (labels[extension]) return labels[extension];
  const mediaTypeLabels = {
    "application/pdf": "PDF",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
    "text/markdown": "Markdown",
    "text/plain": "Text",
  };
  return mediaTypeLabels[documentValue.media_type] ?? "File";
}

function formatShortDate(value) {
  if (!value) return "Not available";
  return new Intl.DateTimeFormat("en-GB", {
    dateStyle: "short",
  }).format(new Date(value));
}

function recordValue(record) {
  return record?.value ?? record;
}

function requestedEstateRoute() {
  const match = /^#estate\/([^/]+)\/(sources|discover|recommend|transform)$/.exec(
    window.location.hash,
  );
  if (!match) return null;
  return { estateId: decodeURIComponent(match[1]), tab: match[2] };
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
      throw new Error(recordValue(record).error || `Workflow ended with status ${status}`);
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
    if (!state.session.hasGrant || collections.length === 0) {
      showView("no-access");
      return;
    }
    state.collectionId = collections[0];
    await loadEstates(true);
  } catch (error) {
    showView("loading");
    elements.loading.querySelector("h1").textContent = "Shaper could not open";
    elements.loading.querySelector("p").textContent = error.message;
    showAlert(error.message);
  }
}

async function loadEstates(restoreRoute = false) {
  const payload = await api(
    `/v1/estates?collection_id=${encodeURIComponent(state.collectionId)}`,
  );
  state.estates = payload.items;
  renderEstates();
  if (restoreRoute && window.location.hash === "#assessment-checks") {
    await openAssessmentChecks();
    return;
  }
  const route = restoreRoute ? requestedEstateRoute() : null;
  if (
    route &&
    state.estates.some((record) => recordValue(record).estate_id === route.estateId)
  ) {
    await openEstate(route.estateId, route.tab);
    return;
  }
  showView("list");
  history.replaceState(null, "", "#estates");
  elements.estateListView.querySelector("h1").focus?.();
}

function renderEstates() {
  const estates = state.estates.map(recordValue);
  elements.estateTotal.textContent = estates.length;
  elements.estateListCount.textContent = `${estates.length} item${
    estates.length === 1 ? "" : "s"
  }`;
  elements.estateActive.textContent = estates.filter(
    (estate) => estate.status === "active",
  ).length;
  elements.estateAssessed.textContent = state.estates.filter(
    (record) => record.assessment_status === "assessed",
  ).length;
  elements.estateList.replaceChildren(
    ...state.estates.map((record) => {
      const estate = recordValue(record);
      const article = document.createElement("article");
      article.className = "estate-card";
      const button = document.createElement("button");
      button.type = "button";
      button.className = "estate-open-button";
      button.dataset.estateId = estate.estate_id;
      button.setAttribute("aria-label", `Open ${estate.name}`);
      const lifecycle = text("span", estate.status, `badge ${estate.status}`);
      lifecycle.dataset.label = "Lifecycle";
      const nameCell = document.createElement("div");
      nameCell.className = "estate-name";
      const nameCopy = document.createElement("div");
      nameCopy.append(
        text("h2", estate.name),
        text("p", estate.description || "No estate description has been added."),
      );
      nameCell.append(text("span", "K", "estate-row-icon"), nameCopy);
      const footer = document.createElement("footer");
      footer.dataset.label = "Last modified";
      footer.append(text("span", formatShortDate(estate.updated_at)));
      const documentCount = text(
        "span",
        `${record.document_count}`,
        "estate-document-count",
      );
      documentCount.dataset.label = "Documents";
      const assessment = assessmentStatus(record);
      assessment.dataset.label = "Assessment";
      button.append(
        nameCell,
        documentCount,
        assessment,
        lifecycle,
        footer,
        text("span", "", "estate-action-space"),
      );
      const actions = document.createElement("div");
      actions.className = "estate-actions";
      const menuButton = document.createElement("button");
      menuButton.type = "button";
      menuButton.className = "estate-menu-trigger";
      menuButton.dataset.estateMenuToggle = estate.estate_id;
      menuButton.setAttribute("aria-label", `Actions for ${estate.name}`);
      menuButton.setAttribute("aria-haspopup", "menu");
      menuButton.setAttribute("aria-expanded", "false");
      menuButton.textContent = "⋯";
      const menu = document.createElement("div");
      menu.className = "estate-menu";
      menu.dataset.estateMenu = estate.estate_id;
      menu.setAttribute("role", "menu");
      menu.setAttribute("aria-label", `Actions for ${estate.name}`);
      menu.hidden = true;
      const editButton = document.createElement("button");
      editButton.type = "button";
      editButton.setAttribute("role", "menuitem");
      editButton.dataset.estateEdit = estate.estate_id;
      editButton.textContent = "Edit";
      editButton.disabled = estate.status === "archived";
      if (editButton.disabled) {
        editButton.title = "Archived estates cannot be edited";
      }
      const deleteButton = document.createElement("button");
      deleteButton.type = "button";
      deleteButton.className = "destructive-menu-item";
      deleteButton.setAttribute("role", "menuitem");
      deleteButton.dataset.estateDelete = estate.estate_id;
      deleteButton.textContent = "Delete";
      menu.append(editButton, deleteButton);
      actions.append(menuButton, menu);
      article.append(button, actions);
      return article;
    }),
  );
  elements.estateEmpty.hidden = estates.length !== 0;
  elements.estateList.closest(".estate-list-shell").hidden = estates.length === 0;
}

function estateRecord(estateId) {
  return state.estates.find((record) => recordValue(record).estate_id === estateId);
}

function closeEstateMenus({ restoreFocus = false } = {}) {
  const openId = state.openEstateMenuId;
  document.querySelectorAll("[data-estate-menu]").forEach((menu) => {
    menu.hidden = true;
    menu.closest(".estate-card")?.classList.remove("menu-open");
  });
  document.querySelectorAll("[data-estate-menu-toggle]").forEach((button) => {
    button.setAttribute("aria-expanded", "false");
  });
  state.openEstateMenuId = null;
  if (restoreFocus && openId) {
    document.querySelector(`[data-estate-menu-toggle="${CSS.escape(openId)}"]`)?.focus();
  }
}

function toggleEstateMenu(estateId, { focusFirst = false } = {}) {
  const shouldOpen = state.openEstateMenuId !== estateId;
  closeEstateMenus();
  if (!shouldOpen) return;
  const menu = document.querySelector(`[data-estate-menu="${CSS.escape(estateId)}"]`);
  const trigger = document.querySelector(
    `[data-estate-menu-toggle="${CSS.escape(estateId)}"]`,
  );
  menu.hidden = false;
  menu.closest(".estate-card")?.classList.add("menu-open");
  trigger.setAttribute("aria-expanded", "true");
  state.openEstateMenuId = estateId;
  if (focusFirst) {
    menu.querySelector('[role="menuitem"]:not(:disabled)')?.focus();
  }
}

function assessmentStatus(record) {
  const labels = {
    no_documents: "No documents",
    not_assessed: "Not assessed",
    partially_assessed: "Assessed",
    assessed: "Assessed",
  };
  const label = labels[record.assessment_status] ?? "Assessment unavailable";
  const coverage =
    record.document_count > 0
      ? ` · ${record.assessed_document_count} of ${record.document_count}`
      : "";
  return text(
    "span",
    `${label}${coverage}`,
    `assessment-status ${record.assessment_status ?? "unknown"}`,
  );
}

async function openAssessmentChecks() {
  clearAlert();
  showView("assessment-checks");
  setBusy(elements.assessmentChecksView, true, "Loading assessment checks…");
  try {
    await ensureAssessmentChecks();
    renderAssessmentChecks();
    history.replaceState(null, "", "#assessment-checks");
    document.querySelector("#assessmentChecksTitle").focus?.();
  } catch (error) {
    showAlert(error.message);
  } finally {
    setBusy(elements.assessmentChecksView, false);
  }
}

async function ensureAssessmentChecks() {
  if (state.assessmentChecks) return state.assessmentChecks;
  const payload = await api("/v1/assessment-checks");
  state.assessmentChecks = payload.items;
  return state.assessmentChecks;
}

function renderAssessmentChecks() {
  const groups = new Map();
  state.assessmentChecks.forEach((check) => {
    const group = groups.get(check.category) ?? [];
    group.push(check);
    groups.set(check.category, group);
  });
  const tablist = document.createElement("div");
  tablist.className = "assessment-check-tabs";
  tablist.setAttribute("role", "tablist");
  tablist.setAttribute("aria-label", "Assessment check categories");
  tablist.setAttribute("aria-orientation", "horizontal");
  const panels = document.createElement("div");
  panels.className = "assessment-check-panels";
  [...groups.entries()].forEach(([category, checks], index) => {
    const tab = document.createElement("button");
    tab.id = `assessment-check-tab-${index}`;
    tab.type = "button";
    tab.setAttribute("role", "tab");
    tab.setAttribute("aria-controls", `assessment-check-panel-${index}`);
    tab.dataset.assessmentCheckTab = `${index}`;
    tab.append(text("span", category), text("span", `${checks.length}`, "tab-count"));
    tablist.append(tab);

    const section = document.createElement("section");
    section.id = `assessment-check-panel-${index}`;
    section.className = "assessment-check-panel";
    section.setAttribute("role", "tabpanel");
    section.setAttribute("aria-labelledby", tab.id);
    section.tabIndex = 0;
    section.append(
      text("h2", category),
      text(
        "p",
        `${checks.length} deterministic check${checks.length === 1 ? "" : "s"} in this category`,
        "assessment-check-count",
      ),
    );
    const list = document.createElement("div");
    list.className = "assessment-check-list";
    checks.forEach((check, checkIndex) => {
      const article = document.createElement("article");
      article.className = "assessment-check-card";
      const number = text("span", `${checkIndex + 1}`, "assessment-check-number");
      number.setAttribute("aria-hidden", "true");
      const content = document.createElement("div");
      const impact = document.createElement("p");
      impact.className = "assessment-check-impact";
      impact.append(
        text("strong", "Likely agent impact"),
        document.createTextNode(` ${check.agent_impact}`),
      );
      content.append(
        text("h3", check.label),
        text("p", check.what_it_checks),
        impact,
      );
      article.append(number, content);
      list.append(article);
    });
    section.append(list);
    panels.append(section);
  });
  elements.assessmentCheckGroups.replaceChildren(tablist, panels);
  switchAssessmentCheckCategory(
    Math.min(state.assessmentCheckCategory, groups.size - 1),
    false,
  );
}

function switchAssessmentCheckCategory(index, focus = true) {
  const tabs = [
    ...elements.assessmentCheckGroups.querySelectorAll("[data-assessment-check-tab]"),
  ];
  const panels = [
    ...elements.assessmentCheckGroups.querySelectorAll(".assessment-check-panel"),
  ];
  if (!tabs[index]) return;
  state.assessmentCheckCategory = index;
  tabs.forEach((tab, tabIndex) => {
    const selected = tabIndex === index;
    tab.setAttribute("aria-selected", `${selected}`);
    tab.tabIndex = selected ? 0 : -1;
  });
  panels.forEach((panel, panelIndex) => {
    panel.hidden = panelIndex !== index;
  });
  if (focus) tabs[index].focus();
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
        ensureAssessmentChecks(),
      ]);
    state.estate = estate;
    state.sources = sources.items;
    state.documents = documents.items;
    state.runs = runs.items;
    state.decisions = new Map(
      decisions.items.map((item) => {
        const decision = recordValue(item);
        return [decision.document_id, decision];
      }),
    );
    state.artifacts = artifacts.items;
    state.selectedDocuments.clear();
    await restoreWorkflowEvidence(estateId);
    renderEstate();
    switchSourceInputTab("location", false);
    switchTab(targetTab, false);
    history.replaceState(null, "", `#estate/${estateId}/${targetTab}`);
  } catch (error) {
    showAlert(error.message);
  } finally {
    setBusy(elements.estateView, false);
  }
}

async function restoreWorkflowEvidence(estateId) {
  const runs = state.runs
    .map(recordValue)
    .sort((left, right) => Date.parse(left.created_at) - Date.parse(right.created_at));
  const latestDiscovery = runs
    .filter((run) => run.kind === "discover" && ["completed", "partial"].includes(run.status))
    .at(-1);
  state.discoveryRunId = latestDiscovery?.run_id ?? null;
  state.reports = new Map();
  if (state.discoveryRunId) {
    const reports = await api(
      `/v1/estates/${estateId}/discovery-reports?run_id=${encodeURIComponent(
        state.discoveryRunId,
      )}`,
    );
    state.reports = new Map(reports.items.map((report) => [report.document_id, report]));
    const currentDocuments = new Map(
      state.documents
        .map(recordValue)
        .filter((document) => !document.deleted)
        .map((document) => [document.document_id, document]),
    );
    const completedDocumentIds =
      latestDiscovery.completed_document_ids?.length > 0
        ? latestDiscovery.completed_document_ids
        : [...state.reports.keys()];
    const discoveryIsCurrent =
      completedDocumentIds.length > 0 &&
      completedDocumentIds.every((documentId) => {
        const document = currentDocuments.get(documentId);
        return (
          document &&
          state.reports.get(documentId)?.source_version === document.source_version
        );
      });
    if (!discoveryIsCurrent) {
      state.discoveryRunId = null;
      state.reports = new Map();
    }
  }
  setProposalStatus("idle");
  const latestRecommendation = runs.filter((run) => run.kind === "recommend").at(-1);
  state.proposalRunId = latestRecommendation?.run_id ?? null;
  state.proposals = [];
  state.evaluationSuggestions = [];
  state.selectedEvaluationSuggestions.clear();
  state.evaluationSuggestionErrors = [];
  if (latestRecommendation?.status === "failed") {
    setProposalStatus(
      "error",
      "No improvement plan was created",
      latestRecommendation.error ||
        "Run discovery again, reselect the documents, and retry.",
    );
  } else if (latestRecommendation && ["queued", "running"].includes(latestRecommendation.status)) {
    setProposalStatus(
      "working",
      "Creating improvement plan",
      "The latest recommendation run is still in progress.",
    );
  } else if (
    state.discoveryRunId &&
    latestRecommendation &&
    ["completed", "partial"].includes(latestRecommendation.status)
  ) {
    const proposals = await api(
      `/v1/estates/${estateId}/proposals?run_id=${encodeURIComponent(
        state.proposalRunId,
      )}`,
    );
    state.proposals = proposals.items.filter((proposal) => {
      const report = state.reports.get(proposal.document_id);
      return report?.report_id === proposal.report_id;
    });
    if (state.proposals.length > 0 && latestRecommendation.status === "partial") {
      setProposalStatus(
        "warning",
        `${state.proposals.length} improvement ${
          state.proposals.length === 1 ? "plan" : "plans"
        } restored`,
        latestRecommendation.error || "Some selected documents were skipped.",
      );
    }
    if (state.proposals.length > 0) {
      await loadEvaluationSuggestions();
    }
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
  elements.generateEvaluations.checked = estate.generate_evaluations;
  renderSources();
  renderDocuments();
  renderProposals();
  renderArtifacts();
  updateWorkflowProgress();
  renderLifecycle();
}

function updateWorkflowProgress() {
  const completion = {
    sources: state.sources.length > 0,
    discover: state.reports.size > 0,
    recommend: state.proposals.length > 0,
    transform: state.artifacts.length > 0,
  };
  document.querySelectorAll(".workflow [data-tab]").forEach((button) => {
    const complete = completion[button.dataset.tab];
    button.dataset.complete = complete ? "true" : "false";
    button.setAttribute(
      "aria-label",
      `${button.textContent.trim()}${complete ? ", complete" : ""}`,
    );
  });
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
        text("p", sourceDisplayDetail(source)),
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
  updateWorkflowProgress();
}

function sourceDisplayDetail(source) {
  const labels = {
    sharepoint: "SharePoint",
    url: "URL",
    upload: "Uploaded file",
    zip: "Uploaded ZIP bundle",
  };
  const label = labels[source.kind] ?? "Registered source";
  const isPublicLocation =
    ["sharepoint", "url"].includes(source.kind) &&
    !source.locator?.toLocaleLowerCase().startsWith("asset:");
  const detail = isPublicLocation
    ? `${label} · ${source.locator}`
    : label;
  if (source.kind !== "sharepoint") return detail;
  const access =
    source.credential_mode === "application"
      ? "Organization-managed access"
      : "Signed-in user access";
  return `${detail} · ${access}`;
}

function updateSourceCredentialOptions() {
  const isSharePoint = elements.sourceKind.value === "sharepoint";
  elements.sharePointCredentialField.hidden = !isSharePoint;
  elements.sharePointCredentialMode.disabled = !isSharePoint;
}

function switchSourceInputTab(name, focus = true) {
  document.querySelectorAll("[data-source-input-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.sourceInputPanel !== name;
  });
  document.querySelectorAll("[data-source-input-tab]").forEach((button) => {
    const selected = button.dataset.sourceInputTab === name;
    button.setAttribute("aria-selected", `${selected}`);
    button.tabIndex = selected ? 0 : -1;
    if (selected && focus) button.focus();
  });
}

function renderDocuments() {
  if (state.activeFindingDocumentId) {
    closeDocumentFindings({ restoreFocus: false });
  }
  elements.documentRows.replaceChildren(
    ...state.documents
      .filter((record) => !recordValue(record).deleted)
      .map((record) => {
        const documentValue = recordValue(record);
        const report = state.reports.get(documentValue.document_id);
        const row = document.createElement("tr");
        const selectCell = document.createElement("td");
        selectCell.className = "select-cell";
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.dataset.documentId = documentValue.document_id;
        checkbox.checked = state.selectedDocuments.has(documentValue.document_id);
        checkbox.disabled = isArchived();
        checkbox.setAttribute("aria-label", `Select ${documentValue.title}`);
        selectCell.append(checkbox);
        const documentCell = document.createElement("td");
        documentCell.className = "document-cell";
        documentCell.append(
          text("strong", documentValue.title),
          text("p", fileFormatLabel(documentValue)),
        );
        const viewDocument = text("button", "Review extracted text", "text-button");
        viewDocument.type = "button";
        viewDocument.dataset.viewDocument = documentValue.document_id;
        viewDocument.dataset.sourceVersion = documentValue.source_version;
        viewDocument.dataset.documentTitle = documentValue.title;
        viewDocument.dataset.sourceRetained = `${record.source_retained === true}`;
        documentCell.append(viewDocument);
        const findingsCell = document.createElement("td");
        findingsCell.className = "results-cell";
        if (report) {
          findingsCell.append(
            text(
              "p",
              `${report.checks_completed?.length ?? 7} checks run`,
              "checks-completed",
            ),
            findingReviewButton(report, documentValue),
          );
        } else {
          findingsCell.append(text("span", "Run discovery to assess this source version.", "pending-result"));
        }
        row.append(selectCell, documentCell, findingsCell);
        return row;
      }),
  );
  elements.documentEmpty.hidden = state.documents.length !== 0;
  renderDiscoverySummary();
  updateSelection();
  updateWorkflowProgress();
}

function renderDiscoverySummary() {
  const reports = [...state.reports.values()];
  elements.discoverySummary.hidden = reports.length === 0;
  if (reports.length === 0) return;
  const findings = reports.reduce(
    (total, report) => total + classifyFindings(report).length,
    0,
  );
  elements.discoverySummary.replaceChildren(
    metric("Documents assessed", reports.length),
    metric("Findings found", findings),
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
  } selected for improvement planning`;
  elements.recommendButton.disabled = count === 0 || !state.discoveryRunId;
}

function invalidateAssessmentEvidence() {
  state.discoveryRunId = null;
  state.reports = new Map();
  state.selectedDocuments.clear();
  state.proposalRunId = null;
  state.proposals = [];
  state.evaluationSuggestions = [];
  state.selectedEvaluationSuggestions.clear();
  state.evaluationSuggestionErrors = [];
  setProposalStatus("idle");
  renderDocuments();
  renderProposals();
}

function proposalAssessmentResults(report) {
  const section = document.createElement("section");
  section.className = "proposal-assessment";
  const heading = text("h4", "Deterministic assessment");
  const headingId = `proposal-assessment-${crypto.randomUUID()}`;
  heading.id = headingId;
  section.setAttribute("aria-labelledby", headingId);

  if (!report) {
    section.append(
      heading,
      text(
        "p",
        "The assessment evidence for this source version is unavailable. Run discovery again.",
        "proposal-assessment-warning",
      ),
    );
    return section;
  }

  const completedCodes = report.checks_completed ?? [];
  const findingCodes = new Set(
    report.findings?.length
      ? report.findings.map((finding) => finding.code)
      : (report.finding_codes ?? []).filter(
          (code) => RESULT_PRESENTATION[code] || !ACCOUNTABILITY_ONLY_FINDINGS.has(code),
        ),
  );
  const checksByCode = new Map(
    (state.assessmentChecks ?? []).map((check) => [check.code, check]),
  );
  const passedChecks = completedCodes
    .filter((code) => !findingCodes.has(code))
    .map((code) => checksByCode.get(code))
    .filter(Boolean);
  const findings = classifyFindings(report);
  const failedCheckCount = completedCodes.filter((code) => findingCodes.has(code)).length;
  const highPriority = findings.filter((finding) => finding.tone === "high").length;

  const summary = document.createElement("div");
  summary.className = "assessment-outcome-summary";
  summary.append(
    metric("Checks completed", completedCodes.length),
    metric("Checks needing attention", failedCheckCount),
    metric("Passed", passedChecks.length),
  );
  section.append(
    heading,
    text(
      "p",
      highPriority > 0
        ? `${highPriority} high-priority ${highPriority === 1 ? "finding needs" : "findings need"} content-owner review.`
        : "No high-priority findings were detected.",
      highPriority > 0 ? "proposal-assessment-warning" : "proposal-assessment-clear",
    ),
    summary,
  );

  if (findings.length > 0) {
    section.append(text("h5", "Checks that need attention"));
    const failedList = document.createElement("ul");
    failedList.className = "result-list proposal-finding-list";
    failedList.setAttribute("aria-label", "Checks that need attention");
    failedList.append(...findings.map(resultItem));
    section.append(failedList);
  }

  const passed = document.createElement("details");
  passed.className = "passed-checks";
  passed.append(text("summary", `${passedChecks.length} checks passed`));
  const passedList = document.createElement("ul");
  passedList.className = "passed-check-list";
  passedChecks.forEach((check) => {
    const item = document.createElement("li");
    item.append(
      text("strong", check.label),
      text("span", check.category),
      text("p", check.what_it_checks),
    );
    passedList.append(item);
  });
  passed.append(passedList);
  section.append(passed);
  return section;
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
      const currentReport = state.reports.get(proposal.document_id);
      const report = currentReport?.report_id === proposal.report_id ? currentReport : null;
      const card = document.createElement("article");
      card.className = "proposal-card";
      card.dataset.proposalId = proposal.recommendation_id;
      const heading = document.createElement("div");
      heading.className = "proposal-heading";
      const decisionLabel =
        decision?.outcome === "approve"
          ? "Approved"
          : decision?.outcome === "decline"
            ? "Declined"
            : "Awaiting decision";
      heading.append(
        text("h3", documentValue?.title || proposal.expected_artifact),
        text("span", decisionLabel, `decision-badge ${decision?.outcome || ""}`),
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
      const recommendation = document.createElement("section");
      recommendation.className = "proposal-recommendation";
      recommendation.append(
        text("h4", "Recommended changes"),
        text("p", proposal.rationale, "proposal-rationale"),
        changes,
      );
      const risk = document.createElement("p");
      risk.className = "proposal-risk";
      risk.append(
        text("strong", "Review constraint:"),
        document.createTextNode(` ${proposal.risk}`),
      );
      recommendation.append(risk);
      const usage = document.createElement("details");
      usage.className = "token-estimate-disclosure";
      usage.append(
        text(
          "summary",
          `View estimated model usage · ${estimate.expected_total.toLocaleString()} tokens`,
        ),
        tokenEstimateGraphic(estimate, proposal.expected_artifact),
      );
      const actions = document.createElement("div");
      actions.className = "proposal-actions";
      const approve = text(
        "button",
        decision?.outcome === "approve" ? "Transformation approved" : "Approve transformation",
        "button primary",
      );
      approve.type = "button";
      approve.disabled = isArchived() || decision?.outcome === "approve";
      approve.dataset.decision = "approve";
      approve.dataset.proposalId = proposal.recommendation_id;
      const decline = text(
        "button",
        decision?.outcome === "decline" ? "Transformation declined" : "Decline",
        "button danger",
      );
      decline.type = "button";
      decline.disabled = isArchived() || decision?.outcome === "decline";
      decline.dataset.decision = "decline";
      decline.dataset.proposalId = proposal.recommendation_id;
      actions.append(approve, decline);
      card.append(
        heading,
        proposalAssessmentResults(report),
        recommendation,
        usage,
        ...(decision?.outcome === "approve"
          ? [
              text(
                "p",
                "Approved. This document is ready to transform.",
                "decision-confirmation",
              ),
            ]
          : []),
        actions,
      );
      return card;
    }),
  );
  elements.proposalEmpty.hidden =
    state.proposals.length !== 0 || !elements.proposalStatus.hidden;
  renderEvaluationOptions();
  updateApprovals();
  updateWorkflowProgress();
}

function setProposalStatus(kind, title = "", detail = "") {
  elements.proposalStatus.hidden = kind === "idle";
  elements.proposalStatus.dataset.state = kind;
  elements.proposalStatusTitle.textContent = title;
  elements.proposalStatusDetail.textContent = detail;
}

function tokenEstimateGraphic(estimate, filename) {
  const section = document.createElement("section");
  section.className = "token-estimate";
  const heading = text("h4", "Estimated token use");
  const headingId = `token-estimate-${crypto.randomUUID()}`;
  heading.id = headingId;
  section.setAttribute("aria-labelledby", headingId);
  const inputEstimate = (estimate.input_min + estimate.input_max) / 2;
  const outputEstimate = (estimate.output_min + estimate.output_max) / 2;
  const componentTotal = inputEstimate + outputEstimate;
  const expectedInput =
    componentTotal === 0 ? 0 : estimate.expected_total * (inputEstimate / componentTotal);
  const expectedOutput = Math.max(0, estimate.expected_total - expectedInput);
  const remaining = Math.max(0, estimate.enforced_maximum - estimate.expected_total);
  const percentage = (value) =>
    `${Math.min(100, (100 * value) / estimate.enforced_maximum).toFixed(2)}%`;
  const chart = document.createElement("div");
  chart.className = "token-estimate-chart";
  chart.setAttribute("role", "img");
  chart.setAttribute(
    "aria-label",
    `Expected total ${estimate.expected_total} tokens: input ${estimate.input_min} to ` +
      `${estimate.input_max}, output ${estimate.output_min} to ${estimate.output_max}, ` +
      `${remaining} contingency tokens cover one repair attempt and safety margin ` +
      `before the ${estimate.enforced_maximum} token maximum.`,
  );
  const inputSegment = document.createElement("span");
  inputSegment.className = "token-segment input";
  inputSegment.style.width = percentage(expectedInput);
  const outputSegment = document.createElement("span");
  outputSegment.className = "token-segment output";
  outputSegment.style.width = percentage(expectedOutput);
  const remainingSegment = document.createElement("span");
  remainingSegment.className = "token-segment remaining";
  remainingSegment.style.width = percentage(remaining);
  chart.append(inputSegment, outputSegment, remainingSegment);
  const legend = document.createElement("ul");
  legend.className = "token-estimate-legend";
  legend.append(
    tokenLegend(
      "input",
      "Input",
      `${estimate.input_min.toLocaleString()}–${estimate.input_max.toLocaleString()}`,
      "Content read",
    ),
    tokenLegend(
      "output",
      "Output",
      `${estimate.output_min.toLocaleString()}–${estimate.output_max.toLocaleString()}`,
      "Content written",
    ),
    tokenLegend(
      "remaining",
      "Contingency",
      remaining.toLocaleString(),
      "One repair and safety margin",
    ),
  );
  const footer = document.createElement("footer");
  footer.className = "token-estimate-footer";
  footer.append(
    text("strong", `Expected total: ${estimate.expected_total.toLocaleString()} tokens`),
    text("span", `Chart maximum: ${estimate.enforced_maximum.toLocaleString()} tokens`),
    text("span", `Confidence: ${Math.round(estimate.confidence * 100)}%`),
    text("span", `Planned output: ${filename}`),
  );
  section.append(
    heading,
    text(
      "p",
      "Tokens are pieces of text the model reads and writes. This estimate is checked before reshaping starts.",
      "token-estimate-intro",
    ),
    chart,
    legend,
    footer,
  );
  return section;
}

function tokenLegend(tone, label, value, detail) {
  const item = document.createElement("li");
  item.append(
    text("span", "", `token-legend-swatch ${tone}`),
    text("strong", label),
    text("span", `${value} tokens`),
    text("small", detail),
  );
  return item;
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

function comparisonPanel(title, description, content) {
  const panel = document.createElement("section");
  panel.className = "comparison-panel";
  const heading = text("h4", title);
  const headingId = `comparison-${crypto.randomUUID()}`;
  heading.id = headingId;
  panel.setAttribute("aria-labelledby", headingId);
  panel.append(heading, text("p", description, "comparison-description"), content);
  return panel;
}

async function loadArtifactComparison(artifact, sourceContent, outputPreview, outputStatus) {
  const estateId = recordValue(state.estate).estate_id;
  const sourcePath =
    `/v1/estates/${estateId}/documents/${encodeURIComponent(artifact.document_id)}/content` +
    `?source_version=${encodeURIComponent(artifact.source_version)}`;
  const outputPath = `/v1/artifacts/${encodeURIComponent(artifact.artifact_id)}/preview`;

  sourceContent.setAttribute("aria-busy", "true");
  outputPreview.setAttribute("aria-busy", "true");

  try {
    sourceContent.textContent = await apiText(sourcePath);
  } catch (error) {
    sourceContent.textContent = `Original content could not be loaded. ${error.message}`;
    sourceContent.classList.add("comparison-error");
  } finally {
    sourceContent.setAttribute("aria-busy", "false");
  }

  try {
    outputPreview.srcdoc = await apiText(outputPath);
    outputPreview.hidden = false;
    outputStatus.remove();
  } catch (error) {
    outputStatus.textContent = `Reshaped content could not be loaded. ${error.message}`;
    outputStatus.classList.add("comparison-error");
  } finally {
    outputPreview.setAttribute("aria-busy", "false");
  }
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
      const sourceContent = text("pre", "Loading original content…", "comparison-source");
      sourceContent.tabIndex = 0;
      const outputStatus = text("p", "Loading reshaped content…", "comparison-status");
      outputStatus.setAttribute("role", "status");
      const outputPreview = document.createElement("iframe");
      outputPreview.className = "comparison-preview";
      outputPreview.title = `After reshaping: ${artifact.filename}`;
      outputPreview.setAttribute("sandbox", "");
      outputPreview.hidden = true;
      const comparison = document.createElement("div");
      comparison.className = "artifact-comparison";
      comparison.setAttribute("aria-label", `Before and after comparison for ${artifact.filename}`);
      comparison.append(
        comparisonPanel(
          "Before reshaping",
          "Complete extracted text from the retained source file.",
          sourceContent,
        ),
        comparisonPanel(
          "After reshaping",
          "Generated agent-ready HTML awaiting or reflecting human review.",
          (() => {
            const outputContent = document.createElement("div");
            outputContent.className = "comparison-output";
            outputContent.append(outputStatus, outputPreview);
            return outputContent;
          })(),
        ),
      );
      card.append(
        heading,
        text("p", `Source version ${artifact.source_version.slice(0, 12)}…`),
        comparison,
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
      void loadArtifactComparison(artifact, sourceContent, outputPreview, outputStatus);
      return card;
    }),
  );
  elements.artifactEmpty.hidden = state.artifacts.length !== 0;
  updateWorkflowProgress();
}

function switchTab(name, focus = true) {
  document.querySelectorAll("[data-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.panel !== name;
  });
  document.querySelectorAll("[data-tab]").forEach((button) => {
    if (button.dataset.tab === name) {
      button.setAttribute("aria-current", "page");
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
        generate_evaluations: data.has("generate_evaluations"),
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

function openEditDialog(estateId) {
  const record = estateRecord(estateId);
  if (!record || recordValue(record).status === "archived") return;
  const estate = recordValue(record);
  state.actionEstate = record;
  closeEstateMenus();
  elements.editForm.reset();
  elements.editEstateName.value = estate.name;
  elements.editEstateDescription.value = estate.description || "";
  elements.editArtifactTemplate.value = estate.artifact_name_template;
  elements.editEvaluations.checked = estate.generate_evaluations;
  elements.editError.hidden = true;
  elements.editError.textContent = "";
  elements.editDialog.showModal();
  elements.editEstateName.focus();
}

function closeEditDialog() {
  elements.editDialog.close();
  elements.editForm.reset();
  elements.editError.hidden = true;
  elements.editError.textContent = "";
  state.actionEstate = null;
}

async function editEstate(event) {
  event.preventDefault();
  const record = state.actionEstate;
  if (!record) return;
  const estate = recordValue(record);
  const data = new FormData(elements.editForm);
  elements.editConfirmButton.disabled = true;
  elements.editError.hidden = true;
  try {
    const updated = await api(`/v1/estates/${estate.estate_id}`, {
      method: "PUT",
      body: JSON.stringify({
        expected_revision: record.revision,
        name: data.get("name"),
        description: data.get("description"),
        artifact_name_template: data.get("artifact_name_template"),
        generate_evaluations: data.has("generate_evaluations"),
      }),
    });
    state.estates = state.estates.map((item) =>
      recordValue(item).estate_id === estate.estate_id
        ? {
            ...updated,
            document_count: item.document_count,
            assessed_document_count: item.assessed_document_count,
            assessment_status: item.assessment_status,
          }
        : item,
    );
    closeEditDialog();
    renderEstates();
    document
      .querySelector(
        `[data-estate-menu-toggle="${CSS.escape(recordValue(updated).estate_id)}"]`,
      )
      ?.focus();
    announce(`${recordValue(updated).name} updated`);
  } catch (error) {
    elements.editError.textContent = error.message;
    elements.editError.hidden = false;
  } finally {
    elements.editConfirmButton.disabled = false;
  }
}

function selectedActionEstate() {
  return state.actionEstate || state.estate;
}

function openDeleteDialog(estateId) {
  if (estateId) {
    state.actionEstate = estateRecord(estateId);
  }
  const estate = recordValue(selectedActionEstate());
  if (!estate) return;
  closeEstateMenus();
  elements.deleteEstateName.textContent = estate.name;
  elements.deleteForm.reset();
  elements.deleteConfirmButton.disabled = true;
  elements.deleteError.hidden = true;
  elements.deleteError.textContent = "";
  elements.deleteDialog.showModal();
  elements.deleteConfirmation.focus();
}

function closeDeleteDialog() {
  elements.deleteDialog.close();
  elements.deleteForm.reset();
  elements.deleteConfirmButton.disabled = true;
  elements.deleteError.hidden = true;
  elements.deleteError.textContent = "";
  state.actionEstate = null;
}

function updateDeleteConfirmation() {
  const estate = recordValue(selectedActionEstate());
  if (!estate) return;
  elements.deleteConfirmButton.disabled =
    elements.deleteConfirmation.value !== estate.name;
}

async function deleteEstate(event) {
  event.preventDefault();
  const record = selectedActionEstate();
  const estate = recordValue(record);
  if (!record || !estate) return;
  if (elements.deleteConfirmation.value !== estate.name) {
    updateDeleteConfirmation();
    return;
  }

  elements.deleteConfirmButton.disabled = true;
  elements.deleteError.hidden = true;
  try {
    if (estate.status !== "archived") {
      await api(`/v1/estates/${estate.estate_id}/archive`, {
        method: "POST",
        body: JSON.stringify({ expected_revision: record.revision }),
      });
    }
    await api(`/v1/estates/${estate.estate_id}/purge`, {
      method: "POST",
      body: JSON.stringify({
        confirmation: `PURGE ${estate.name}`,
        reason: "Deleted through the knowledge estate workspace.",
      }),
    });
    closeDeleteDialog();
    state.estate = null;
    await loadEstates();
    announce(`${estate.name} deleted`);
  } catch (error) {
    elements.deleteError.textContent = error.message;
    elements.deleteError.hidden = false;
    updateDeleteConfirmation();
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
    updateSourceCredentialOptions();
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
    invalidateAssessmentEvidence();
    announce(
      `${result.documents.length} document${
        result.documents.length === 1 ? "" : "s"
      } inventoried. Run discovery to assess the updated estate.`,
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
  const selectedCount = state.selectedDocuments.size;
  state.proposals = [];
  setProposalStatus(
    "working",
    "Creating improvement plan",
    `Reviewing assessment evidence for ${selectedCount} selected ${
      selectedCount === 1 ? "document" : "documents"
    }. This may take a moment.`,
  );
  renderProposals();
  switchTab("recommend");
  elements.recommendButton.disabled = true;
  try {
    await ensureAssessmentChecks();
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
    const runRecord = await waitForRun(state.proposalRunId);
    const run = recordValue(runRecord);
    state.proposals = await api(
      `/v1/estates/${recordValue(state.estate).estate_id}/proposals?run_id=${encodeURIComponent(
        state.proposalRunId,
      )}`,
    ).then((payload) => payload.items);
    if (state.proposals.length === 0) {
      throw new Error(
        run.error ||
          "No improvement plans were created. Run discovery again, then reselect the documents.",
      );
    }
    await loadEvaluationSuggestions();
    renderProposals();
    if (run.failed_document_ids?.length) {
      setProposalStatus(
        "warning",
        `${state.proposals.length} improvement ${
          state.proposals.length === 1 ? "plan" : "plans"
        } created`,
        run.error || "Some selected documents were skipped. Run discovery again for those sources.",
      );
    } else {
      setProposalStatus(
        "success",
        `${state.proposals.length} improvement ${
          state.proposals.length === 1 ? "plan is" : "plans are"
        } ready to review`,
        "Review each assessment result and proposed change before approving a transformation.",
      );
    }
    announce(`${state.proposals.length} improvement plans ready to review`);
  } catch (error) {
    setProposalStatus(
      "error",
      "No improvement plan was created",
      `${error.message} Return to Assess, run discovery again if the source changed, and retry.`,
    );
    renderProposals();
    showAlert(error.message);
  } finally {
    updateSelection();
  }
}

async function decide(proposalId, outcome) {
  clearAlert();
  const proposal = state.proposals.find(
    (item) => item.recommendation_id === proposalId,
  );
  if (!proposal) {
    showAlert("The selected transformation proposal is no longer available. Refresh the estate.");
    return;
  }
  const current = state.decisions.get(proposal.document_id);
  const card = document
    .querySelector(`[data-proposal-id="${CSS.escape(proposalId)}"]`)
    ?.closest(".proposal-card");
  if (card) setBusy(card, true, "Recording decision…");
  try {
    const response = await api(`/v1/proposals/${proposalId}/decision`, {
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
    const decision = recordValue(response);
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
    const estateRecord = state.estate;
    const estate = recordValue(estateRecord);
    if (estate.generate_evaluations !== elements.generateEvaluations.checked) {
      state.estate = await api(`/v1/estates/${estate.estate_id}`, {
        method: "PUT",
        body: JSON.stringify({
          expected_revision: estateRecord.revision,
          name: estate.name,
          description: estate.description,
          artifact_name_template: estate.artifact_name_template,
          generate_evaluations: elements.generateEvaluations.checked,
        }),
      });
      const estateIndex = state.estates.findIndex(
        (item) => recordValue(item).estate_id === estate.estate_id,
      );
      if (estateIndex >= 0) state.estates[estateIndex] = state.estate;
    }
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

async function openDocument(documentId, sourceVersion, title, sourceRetained) {
  clearAlert();
  elements.documentDialogTitle.textContent = title;
  elements.documentDownload.hidden = !sourceRetained;
  elements.documentSourceStatus.textContent = sourceRetained
    ? "Findings use this lossless text derivative. The exact uploaded file is retained separately as the source of record."
    : "This document predates source retention. Re-upload the original file to retain it; the extracted text below remains available.";
  elements.documentDownload.href =
    `/v1/estates/${recordValue(state.estate).estate_id}/documents/` +
    `${encodeURIComponent(documentId)}/source?source_version=${encodeURIComponent(sourceVersion)}`;
  elements.documentContent.textContent = "Loading document content…";
  elements.documentDialog.showModal();
  try {
    elements.documentContent.textContent = await apiText(
      `/v1/estates/${recordValue(state.estate).estate_id}/documents/` +
        `${encodeURIComponent(documentId)}/content?source_version=${encodeURIComponent(
          sourceVersion,
        )}`,
    );
  } catch (error) {
    elements.documentContent.textContent = "";
    elements.documentDialog.close();
    showAlert(error.message);
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
  if (!event.target.closest(".estate-actions")) {
    closeEstateMenus();
  }
  const target = event.target.closest("button, a");
  if (!target) return;
  if (target.dataset.action === "home") {
    event.preventDefault();
    await loadEstates();
  } else if (target.dataset.action === "assessment-checks") {
    await openAssessmentChecks();
  } else if (target.dataset.assessmentCheckTab) {
    switchAssessmentCheckCategory(Number(target.dataset.assessmentCheckTab), false);
  } else if (target.id === "downloadEvaluations") {
    downloadEvaluationDataset();
  } else if (target.dataset.action === "open-create") {
    elements.createDialog.showModal();
  } else if (target.dataset.action === "close-create") {
    elements.createDialog.close();
  } else if (target.dataset.action === "close-edit") {
    closeEditDialog();
  } else if (target.dataset.estateMenuToggle) {
    toggleEstateMenu(target.dataset.estateMenuToggle);
  } else if (target.dataset.estateEdit) {
    openEditDialog(target.dataset.estateEdit);
  } else if (target.dataset.estateDelete) {
    openDeleteDialog(target.dataset.estateDelete);
  } else if (target.dataset.action === "open-delete") {
    openDeleteDialog();
  } else if (target.dataset.action === "close-delete") {
    closeDeleteDialog();
  } else if (target.dataset.action === "close-purge") {
    elements.purgeDialog.close();
  } else if (target.dataset.action === "close-document") {
    elements.documentDialog.close();
  } else if (target.dataset.action === "close-findings") {
    closeDocumentFindings();
  } else if (target.dataset.reviewFindings) {
    openDocumentFindings(target);
  } else if (target.dataset.viewDocument) {
    await openDocument(
      target.dataset.viewDocument,
      target.dataset.sourceVersion,
      target.dataset.documentTitle,
      target.dataset.sourceRetained === "true",
    );
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

document.addEventListener("keydown", (event) => {
  const assessmentTab = event.target.closest("[data-assessment-check-tab]");
  if (
    assessmentTab &&
    ["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)
  ) {
    event.preventDefault();
    const tabs = [
      ...elements.assessmentCheckGroups.querySelectorAll("[data-assessment-check-tab]"),
    ];
    const current = tabs.indexOf(assessmentTab);
    let next = 0;
    if (event.key === "End") {
      next = tabs.length - 1;
    } else if (event.key === "ArrowLeft") {
      next = current <= 0 ? tabs.length - 1 : current - 1;
    } else if (event.key === "ArrowRight") {
      next = current === tabs.length - 1 ? 0 : current + 1;
    }
    switchAssessmentCheckCategory(next);
    return;
  }
  if (event.key === "Escape" && state.openEstateMenuId) {
    event.preventDefault();
    closeEstateMenus({ restoreFocus: true });
    return;
  }
  const trigger = event.target.closest("[data-estate-menu-toggle]");
  if (trigger && event.key === "ArrowDown") {
    event.preventDefault();
    const estateId = trigger.dataset.estateMenuToggle;
    if (state.openEstateMenuId === estateId) {
      document
        .querySelector(`[data-estate-menu="${CSS.escape(estateId)}"]`)
        ?.querySelector('[role="menuitem"]:not(:disabled)')
        ?.focus();
    } else {
      toggleEstateMenu(estateId, { focusFirst: true });
    }
    return;
  }

  const menu = event.target.closest("[data-estate-menu]");
  if (!menu) return;
  if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
  event.preventDefault();
  const items = [...menu.querySelectorAll('[role="menuitem"]:not(:disabled)')];
  if (items.length === 0) return;
  const current = items.indexOf(document.activeElement);
  let next = 0;
  if (event.key === "End") {
    next = items.length - 1;
  } else if (event.key === "ArrowUp") {
    next = current <= 0 ? items.length - 1 : current - 1;
  } else if (event.key === "ArrowDown") {
    next = current === items.length - 1 ? 0 : current + 1;
  }
  items[next].focus();
});

document.addEventListener("focusin", (event) => {
  if (state.openEstateMenuId && !event.target.closest(".estate-actions")) {
    closeEstateMenus();
  }
});

elements.createForm.addEventListener("submit", createEstate);
elements.editForm.addEventListener("submit", editEstate);
elements.deleteForm.addEventListener("submit", deleteEstate);
elements.deleteConfirmation.addEventListener("input", updateDeleteConfirmation);
elements.sourceInputTabs.addEventListener("click", (event) => {
  const tab = event.target.closest("[data-source-input-tab]");
  if (tab) switchSourceInputTab(tab.dataset.sourceInputTab, false);
});
elements.sourceInputTabs.addEventListener("keydown", (event) => {
  const tab = event.target.closest("[data-source-input-tab]");
  if (!tab || !["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
  event.preventDefault();
  const tabs = [...elements.sourceInputTabs.querySelectorAll("[data-source-input-tab]")];
  const current = tabs.indexOf(tab);
  let next = 0;
  if (event.key === "End") {
    next = tabs.length - 1;
  } else if (event.key === "ArrowLeft") {
    next = current <= 0 ? tabs.length - 1 : current - 1;
  } else if (event.key === "ArrowRight") {
    next = current === tabs.length - 1 ? 0 : current + 1;
  }
  switchSourceInputTab(tabs[next].dataset.sourceInputTab);
});
elements.sourceForm.addEventListener("submit", addSource);
elements.sourceKind.addEventListener("change", updateSourceCredentialOptions);
updateSourceCredentialOptions();
elements.uploadForm.addEventListener("submit", uploadFiles);
elements.discoverButton.addEventListener("click", runDiscovery);
elements.recommendButton.addEventListener("click", requestRecommendations);
elements.transformButton.addEventListener("click", transformApproved);
elements.archiveButton.addEventListener("click", archiveEstate);
elements.purgeButton.addEventListener("click", openPurgeDialog);
elements.purgeForm.addEventListener("submit", purgeEstate);
elements.evaluationTarget.addEventListener("change", renderEvaluationOptions);
elements.evaluationSuggestionList.addEventListener("change", (event) => {
  const checkbox = event.target.closest("[data-evaluation-suggestion]");
  if (!checkbox) return;
  if (checkbox.checked) {
    state.selectedEvaluationSuggestions.add(checkbox.dataset.evaluationSuggestion);
  } else {
    state.selectedEvaluationSuggestions.delete(checkbox.dataset.evaluationSuggestion);
  }
  renderEvaluationOptions();
});
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
elements.documentFindingsDialog.addEventListener("close", () => {
  if (state.transitioningFindingPresentation) {
    state.transitioningFindingPresentation = false;
    return;
  }
  state.activeFindingDocumentId = null;
  updateFindingButtons();
  if (state.restoreFindingFocus && state.findingTrigger?.isConnected) {
    state.findingTrigger.focus();
  }
  state.restoreFindingFocus = true;
  state.findingTrigger = null;
});
elements.documentFindingsDialog.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  event.preventDefault();
  closeDocumentFindings();
});
document.addEventListener("keydown", (event) => {
  if (
    event.key === "Escape" &&
    state.activeFindingDocumentId &&
    !elements.documentFindingsDialog.open &&
    !elements.documentFindingsPanel.hidden
  ) {
    event.preventDefault();
    closeDocumentFindings();
  }
});
findingsDialogMedia.addEventListener("change", moveOpenFindingsToCurrentLayout);

initialize();
