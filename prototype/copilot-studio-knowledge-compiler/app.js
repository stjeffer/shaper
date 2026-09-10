const knowledgeDialog = document.querySelector("#knowledgeDialog");
const compilerDialog = document.querySelector("#compilerDialog");
const addKnowledgeButton = document.querySelector("#addKnowledgeButton");
const compilerOption = document.querySelector("#compilerOption");
const closeCompiler = document.querySelector("#closeCompiler");
const cancelCompiler = document.querySelector("#cancelCompiler");
const connectSharePoint = document.querySelector("#connectSharePoint");
const uploadFiles = document.querySelector("#uploadFiles");
const fileInput = document.querySelector("#fileInput");
const sourceReady = document.querySelector("#sourceReady");
const sourceName = document.querySelector("#sourceName");
const sourceDetail = document.querySelector("#sourceDetail");
const setupView = document.querySelector("#setupView");
const progressView = document.querySelector("#progressView");
const reviewView = document.querySelector("#reviewView");
const releaseView = document.querySelector("#releaseView");
const compileButton = document.querySelector("#compileButton");
const approveButton = document.querySelector("#approveButton");
const publishRelease = document.querySelector("#publishRelease");
const doneButton = document.querySelector("#doneButton");
const compilerHint = document.querySelector("#compilerHint");
const progressTitle = document.querySelector("#progressTitle");
const progressDetail = document.querySelector("#progressDetail");
const progressBar = document.querySelector("#progressBar");
const progressPercent = document.querySelector("#progressPercent");
const knowledgeChips = document.querySelector("#knowledgeChips");
const toast = document.querySelector("#toast");
const steps = [...document.querySelectorAll(".stepper li")];

let lastCompilerTrigger = compilerOption;

function showToast(message) {
  toast.textContent = message;
  toast.hidden = false;
  window.setTimeout(() => {
    toast.hidden = true;
  }, 3200);
}

function closeDialog(dialog, trigger) {
  dialog.close();
  trigger.focus();
}

function installDialogKeyboard(dialog, trigger) {
  dialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    closeDialog(dialog, trigger);
  });
}

installDialogKeyboard(knowledgeDialog, addKnowledgeButton);
installDialogKeyboard(compilerDialog, lastCompilerTrigger);

addKnowledgeButton.addEventListener("click", () => knowledgeDialog.showModal());

compilerOption.addEventListener("click", () => {
  lastCompilerTrigger = compilerOption;
  knowledgeDialog.close();
  compilerDialog.showModal();
  connectSharePoint.focus();
});

closeCompiler.addEventListener("click", () => closeDialog(compilerDialog, lastCompilerTrigger));
cancelCompiler.addEventListener("click", () => closeDialog(compilerDialog, lastCompilerTrigger));

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  if (compilerDialog.open) {
    event.preventDefault();
    closeDialog(compilerDialog, lastCompilerTrigger);
  } else if (knowledgeDialog.open) {
    event.preventDefault();
    closeDialog(knowledgeDialog, addKnowledgeButton);
  }
});

function connectSource(name, detail) {
  sourceName.textContent = name;
  sourceDetail.textContent = detail;
  sourceReady.hidden = false;
  compileButton.disabled = false;
  compilerHint.textContent = "Source ready • Estimated output: 10–15 units";
  steps[0].classList.add("complete");
  showToast("Source connected and ready to compile.");
}

connectSharePoint.addEventListener("click", () => {
  connectSource("HR policy library", "12 files • SharePoint • Synchronized");
});

uploadFiles.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => {
  const files = [...fileInput.files];
  if (!files.length) return;
  connectSource(
    files.length === 1 ? files[0].name : `${files.length} uploaded files`,
    `${files.length} file${files.length === 1 ? "" : "s"} • Scanned and ready`,
  );
});

const progressStages = [
  [18, "Reading source structure and permissions..."],
  [42, "Finding policy rules, qualifiers, and exceptions..."],
  [67, "Generating canonical questions and grounded answers..."],
  [88, "Validating claims against exact source spans..."],
  [100, "12 answer-ready units created for review."],
];

compileButton.addEventListener("click", () => {
  setupView.hidden = true;
  progressView.hidden = false;
  compileButton.hidden = true;
  cancelCompiler.hidden = true;
  compilerHint.textContent = "Compilation runs within bounded model and token budgets";
  steps[1].classList.add("active");
  let stage = 0;

  function advance() {
    const [percent, detail] = progressStages[stage];
    progressPercent.textContent = `${percent}%`;
    progressBar.style.width = `${percent}%`;
    progressDetail.textContent = detail;
    stage += 1;
    if (stage < progressStages.length) {
      window.setTimeout(advance, 420);
      return;
    }
    window.setTimeout(() => {
      progressTitle.textContent = "Compilation complete";
      progressView.hidden = true;
      reviewView.hidden = false;
      approveButton.hidden = false;
      cancelCompiler.hidden = false;
      compilerHint.textContent = "Human approval is required before publication";
      steps[1].classList.replace("active", "complete");
      steps[2].classList.add("active");
      reviewView.querySelector(".unit").focus();
      showToast("Compilation complete. 12 answer-ready units need review.");
    }, 350);
  }

  advance();
});

document.querySelectorAll(".unit").forEach((unit) => {
  unit.addEventListener("click", () => {
    document.querySelectorAll(".unit").forEach((item) => item.classList.remove("active"));
    unit.classList.add("active");
  });
});

approveButton.addEventListener("click", () => {
  document.querySelectorAll(".unit-status").forEach((status) => {
    status.textContent = "Approved";
    status.style.color = "#107c10";
  });
  approveButton.hidden = true;
  publishRelease.hidden = false;
  compilerHint.textContent = "All required units approved • Ready to publish";
  steps[2].classList.replace("active", "complete");
  steps[3].classList.add("active");
  showToast("All required units approved.");
});

publishRelease.addEventListener("click", () => {
  reviewView.hidden = true;
  releaseView.hidden = false;
  publishRelease.hidden = true;
  cancelCompiler.hidden = true;
  doneButton.hidden = false;
  compilerHint.textContent = "Immutable release attached to FAQifier";
  steps[3].classList.replace("active", "complete");
  showToast("Release v1 published and attached to FAQifier.");
});

doneButton.addEventListener("click", () => {
  if (!knowledgeChips.querySelector("[data-compiler-chip]")) {
    const chip = document.createElement("span");
    chip.dataset.compilerChip = "true";
    chip.innerHTML =
      '✦ Answer-ready policies v1 <button type="button" aria-label="Remove Answer-ready policies">×</button>';
    knowledgeChips.append(chip);
  }
  closeDialog(compilerDialog, addKnowledgeButton);
  showToast("Answer-ready policies v1 added to FAQifier knowledge.");
});

document.querySelector(".toggle").addEventListener("click", (event) => {
  const toggle = event.currentTarget;
  const enabled = toggle.getAttribute("aria-checked") === "true";
  toggle.setAttribute("aria-checked", String(!enabled));
});
