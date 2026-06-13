const form = document.getElementById("queryForm");
const queryInput = document.getElementById("query");
const domainInput = document.getElementById("domain");
const stakesInput = document.getElementById("stakes");
const constraintInput = document.getElementById("constraint");
const notesInput = document.getElementById("notes");
const loadSampleButton = document.getElementById("loadSample");
const exportReportButton = document.getElementById("exportReport");
const exportMarkdownButton = document.getElementById("exportMarkdown");
const clearHistoryButton = document.getElementById("clearHistory");
const themeToggle = document.getElementById("themeToggle");
const compareA = document.getElementById("compareA");
const compareB = document.getElementById("compareB");
const compareReportsButton = document.getElementById("compareReports");

const statusText = document.getElementById("statusText");
const summary = document.getElementById("summary");
const recommendation = document.getElementById("recommendation");
const confidence = document.getElementById("confidence");
const riskCount = document.getElementById("riskCount");
const dissentCount = document.getElementById("dissentCount");
const supportingClaims = document.getElementById("supportingClaims");
const dissentingViews = document.getElementById("dissentingViews");
const risks = document.getElementById("risks");
const tradeoffs = document.getElementById("tradeoffs");
const agents = document.getElementById("agents");
const validations = document.getElementById("validations");
const changeTriggers = document.getElementById("changeTriggers");
const historyList = document.getElementById("historyList");
const compareResult = document.getElementById("compareResult");

const HISTORY_KEY = "dip-free-history";
const THEME_KEY = "dip-free-theme";

let currentReport = null;
let currentInput = null;

const samplePayload = {
  query: "Should Delhi prioritize economic growth or aggressive pollution control?",
  domain: "policy",
  stakes: "high",
  constraints: ["must remain auditable"],
  notes: ["example input for DIP free mode"],
};

function setStatus(message, tone = "idle") {
  statusText.textContent = message;
  statusText.dataset.tone = tone;
}

function getTheme() {
  return localStorage.getItem(THEME_KEY) || "presentation";
}

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem(THEME_KEY, theme);
  themeToggle.textContent = theme === "midnight" ? "Light theme" : "Dark theme";
  themeToggle.setAttribute("aria-pressed", String(theme === "midnight"));
}

function toggleTheme() {
  setTheme(getTheme() === "midnight" ? "presentation" : "midnight");
}

function clearElement(element, fallbackText = "") {
  element.innerHTML = "";
  if (fallbackText) {
    element.textContent = fallbackText;
    element.classList.add("empty-state");
  } else {
    element.classList.remove("empty-state");
  }
}

function createItem(text) {
  const item = document.createElement("div");
  item.className = "list-item";
  item.textContent = text;
  return item;
}

function createChip(text) {
  const chip = document.createElement("span");
  chip.className = "chip";
  chip.textContent = text;
  return chip;
}

function toMarkdown(report) {
  const lines = [];
  lines.push(`# DIP Decision Report`);
  lines.push(``);
  lines.push(`**Decision ID:** ${report.query_id}`);
  lines.push(`**Recommendation:** ${report.recommendation}`);
  lines.push(`**Confidence:** ${Math.round((report.confidence_score || 0) * 100)}%`);
  lines.push(``);
  lines.push(`## Supporting Claims`);
  (report.supporting_claims || []).forEach((item) => lines.push(`- ${item}`));
  if ((report.supporting_claims || []).length === 0) lines.push(`- None`);
  lines.push(``);
  lines.push(`## Dissenting Views`);
  (report.dissenting_views || []).forEach((item) => lines.push(`- ${item}`));
  if ((report.dissenting_views || []).length === 0) lines.push(`- None`);
  lines.push(``);
  lines.push(`## Risks`);
  (report.risks || []).forEach((item) => lines.push(`- ${item}`));
  if ((report.risks || []).length === 0) lines.push(`- None`);
  lines.push(``);
  lines.push(`## Tradeoffs`);
  (report.tradeoffs || []).forEach((item) => lines.push(`- ${item}`));
  lines.push(``);
  lines.push(`## Agent Debate`);
  (report.agent_outputs || []).forEach((agent) => {
    lines.push(`### ${agent.agent_name}`);
    lines.push(`- Stance: ${agent.stance}`);
    lines.push(`- Confidence: ${Math.round((agent.confidence || 0) * 100)}%`);
    lines.push(`- Claims: ${(agent.claims || []).join(" | ") || "None"}`);
    lines.push(`- Risks: ${(agent.risks || []).join(" | ") || "None"}`);
    lines.push(``);
  });
  lines.push(`## Validation Matrix`);
  (report.validations || []).forEach((validation) => {
    lines.push(`- ${validation.claim} -> ${validation.status} (${validation.source})`);
  });
  lines.push(``);
  lines.push(`## What Would Change the Decision`);
  (report.what_would_change_the_decision || []).forEach((item) => lines.push(`- ${item}`));
  return lines.join("\n");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function getHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveHistory(history) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, 8)));
}

function addToHistory(entry) {
  const history = getHistory();
  const nextEntry = {
    id: entry.report.query_id,
    timestamp: new Date().toISOString(),
    input: entry.input,
    report: entry.report,
  };

  const filtered = history.filter((item) => item.id !== nextEntry.id);
  filtered.unshift(nextEntry);
  saveHistory(filtered);
  renderHistory();
  renderCompareOptions();
}

function renderHistory() {
  const history = getHistory();
  historyList.innerHTML = "";

  if (history.length === 0) {
    historyList.classList.add("empty-state");
    historyList.textContent = "No history yet.";
    clearHistoryButton.disabled = true;
    return;
  }

  historyList.classList.remove("empty-state");
  clearHistoryButton.disabled = false;

  history.forEach((item) => {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "history-item";
    row.innerHTML = `
      <span class="history-title">${escapeHtml(item.input.query || "Untitled query")}</span>
      <span class="history-meta">${escapeHtml(item.input.domain)} · ${Math.round((item.report.confidence_score || 0) * 100)}% · ${new Date(item.timestamp).toLocaleString()}</span>
    `;

    row.addEventListener("click", () => {
      currentInput = item.input;
      currentReport = item.report;
      populateFormFromInput(item.input);
      renderReport(item.report, false);
      setStatus("Loaded from history", "idle");
      exportReportButton.disabled = false;
    });

    historyList.appendChild(row);
  });
}

function renderCompareOptions() {
  const history = getHistory();
  compareA.innerHTML = "";
  compareB.innerHTML = "";

  if (history.length === 0) {
    compareA.disabled = true;
    compareB.disabled = true;
    compareReportsButton.disabled = true;
    compareA.appendChild(new Option("No saved reports", ""));
    compareB.appendChild(new Option("No saved reports", ""));
    return;
  }

  compareA.disabled = false;
  compareB.disabled = false;
  compareReportsButton.disabled = history.length < 2;

  history.forEach((item, index) => {
    const label = `${item.input.query || "Untitled query"} (${item.input.domain})`;
    compareA.add(new Option(label, item.id));
    compareB.add(new Option(label, item.id));
  });

  compareA.selectedIndex = 0;
  compareB.selectedIndex = Math.min(1, history.length - 1);
}

function populateFormFromInput(input) {
  queryInput.value = input.query || "";
  domainInput.value = input.domain || "general";
  stakesInput.value = input.stakes || "medium";
  constraintInput.value = (input.constraints || []).join(", ");
  notesInput.value = (input.notes || []).join("\n");
}

function downloadReport(report) {
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const safeId = report.query_id || "dip-report";
  link.href = url;
  link.download = `${safeId}.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function downloadMarkdown(report) {
  const blob = new Blob([toMarkdown(report)], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const safeId = report.query_id || "dip-report";
  link.href = url;
  link.download = `${safeId}.md`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function renderList(element, items, emptyText) {
  clearElement(element);
  if (!items || items.length === 0) {
    element.classList.add("empty-state");
    element.textContent = emptyText;
    return;
  }

  items.forEach((item) => element.appendChild(createItem(item)));
}

function renderChips(element, items, emptyText) {
  clearElement(element);
  if (!items || items.length === 0) {
    element.classList.add("empty-state");
    element.textContent = emptyText;
    return;
  }

  items.forEach((item) => element.appendChild(createChip(item)));
}

function renderAgents(items) {
  clearElement(agents);
  if (!items || items.length === 0) {
    agents.classList.add("empty-state");
    agents.textContent = "No agent output yet.";
    return;
  }

  items.forEach((agent) => {
    const card = document.createElement("article");
    card.className = "agent-card";

    const title = document.createElement("div");
    title.className = "agent-title";

    const name = document.createElement("div");
    name.textContent = agent.agent_name;

    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = `${Math.round((agent.confidence || 0) * 100)}%`;

    title.append(name, badge);

    const stance = document.createElement("div");
    stance.className = "agent-meta";
    stance.textContent = agent.stance;

    const claims = document.createElement("div");
    claims.className = "agent-claims";
    claims.textContent = `Claims: ${(agent.claims || []).join(" • ")}`;

    const risksLine = document.createElement("div");
    risksLine.className = "agent-meta";
    risksLine.textContent = `Risks: ${(agent.risks || []).join(" • ")}`;

    card.append(title, stance, claims, risksLine);
    agents.appendChild(card);
  });
}

function findHistoryItem(id) {
  return getHistory().find((item) => item.id === id);
}

function renderComparison(left, right) {
  if (!left || !right) {
    compareResult.classList.add("empty-state");
    compareResult.textContent = "Select two saved reports to compare them.";
    return;
  }

  compareResult.classList.remove("empty-state");
  compareResult.innerHTML = `
    <div class="comparison-grid">
      <article class="comparison-card">
        <div class="comparison-label">Report A</div>
        <h4>${escapeHtml(left.input.query || "Untitled query")}</h4>
        <div class="comparison-meta">${escapeHtml(left.input.domain)} · ${escapeHtml(left.input.stakes || "medium")}</div>
        <div class="comparison-metric">Confidence: ${Math.round((left.report.confidence_score || 0) * 100)}%</div>
        <div class="comparison-text">${escapeHtml(left.report.recommendation || "No recommendation")}</div>
      </article>
      <article class="comparison-card">
        <div class="comparison-label">Report B</div>
        <h4>${escapeHtml(right.input.query || "Untitled query")}</h4>
        <div class="comparison-meta">${escapeHtml(right.input.domain)} · ${escapeHtml(right.input.stakes || "medium")}</div>
        <div class="comparison-metric">Confidence: ${Math.round((right.report.confidence_score || 0) * 100)}%</div>
        <div class="comparison-text">${escapeHtml(right.report.recommendation || "No recommendation")}</div>
      </article>
    </div>
    <div class="comparison-diff">
      <div><strong>Confidence Gap:</strong> ${Math.round(Math.abs((left.report.confidence_score || 0) - (right.report.confidence_score || 0)) * 100)}%</div>
      <div><strong>Recommendation Difference:</strong> ${escapeHtml(left.report.recommendation || "") === escapeHtml(right.report.recommendation || "") ? "No change" : "Different recommendation"}</div>
      <div><strong>Risk Difference:</strong> ${Math.abs((left.report.risks || []).length - (right.report.risks || []).length)} item(s)</div>
    </div>
  `;
}

function renderValidations(items) {
  clearElement(validations);
  if (!items || items.length === 0) {
    validations.classList.add("empty-state");
    validations.textContent = "No validations yet.";
    return;
  }

  items.forEach((validation) => {
    const card = document.createElement("article");
    card.className = "validation-card";

    const top = document.createElement("div");
    top.className = "validation-title";

    const claim = document.createElement("div");
    claim.textContent = validation.claim;

    const badge = document.createElement("span");
    badge.className = `badge ${validation.status}`;
    badge.textContent = validation.status.replaceAll("_", " ");

    top.append(claim, badge);

    const meta = document.createElement("div");
    meta.className = "validation-meta";
    meta.textContent = `Source: ${validation.source} | Confidence: ${Math.round((validation.confidence || 0) * 100)}%`;

    const note = document.createElement("div");
    note.className = "validation-note";
    note.textContent = validation.notes;

    card.append(top, meta, note);
    validations.appendChild(card);
  });
}

function renderReport(report, enableExport = true) {
  currentReport = report;
  exportReportButton.disabled = !enableExport;
  exportMarkdownButton.disabled = !enableExport;
  recommendation.textContent = report.recommendation || "No recommendation";
  confidence.textContent = `${Math.round((report.confidence_score || 0) * 100)}%`;
  riskCount.textContent = String((report.risks || []).length);
  dissentCount.textContent = String((report.dissenting_views || []).length);

  summary.innerHTML = "";
  summary.classList.remove("empty-state");

  const summaryLines = [
    `Decision ID: ${report.query_id}`,
    `Confidence: ${Math.round((report.confidence_score || 0) * 100)}%`,
    `Recommendation: ${report.recommendation}`,
  ];

  summaryLines.forEach((line) => summary.appendChild(createItem(line)));

  renderList(supportingClaims, report.supporting_claims, "No supporting claims found.");
  renderList(dissentingViews, report.dissenting_views, "No dissenting views found.");
  renderList(risks, report.risks, "No risks found.");
  renderChips(tradeoffs, report.tradeoffs, "No tradeoffs found.");
  renderAgents(report.agent_outputs || []);
  renderValidations(report.validations || []);
  renderChips(changeTriggers, report.what_would_change_the_decision, "No change triggers found.");

  setStatus("Analysis complete", "done");
}

async function analyzeQuery(payload) {
  setStatus("Analyzing locally...", "busy");
  form.querySelector("button[type='submit']").disabled = true;

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Analysis failed.");
    }

    currentInput = payload;
    renderReport(data, true);
    addToHistory({ input: payload, report: data });
    renderCompareOptions();
  } catch (error) {
    setStatus("Analysis failed", "error");
    summary.classList.add("empty-state");
    summary.textContent = error.message;
  } finally {
    form.querySelector("button[type='submit']").disabled = false;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const query = queryInput.value.trim();
  const constraint = constraintInput.value.trim();
  const notes = notesInput.value.trim();

  analyzeQuery({
    query,
    domain: domainInput.value,
    stakes: stakesInput.value,
    constraints: constraint ? [constraint] : [],
    notes: notes ? [notes] : [],
  });
});

loadSampleButton.addEventListener("click", () => {
  queryInput.value = samplePayload.query;
  domainInput.value = samplePayload.domain;
  stakesInput.value = samplePayload.stakes;
  constraintInput.value = samplePayload.constraints.join(", ");
  notesInput.value = samplePayload.notes.join("\n");
  setStatus("Sample loaded", "idle");
});

exportReportButton.addEventListener("click", () => {
  if (!currentReport) {
    return;
  }

  downloadReport(currentReport);
  setStatus("Report exported", "done");
});

exportMarkdownButton.addEventListener("click", () => {
  if (!currentReport) {
    return;
  }

  downloadMarkdown(currentReport);
  setStatus("Markdown exported", "done");
});

clearHistoryButton.addEventListener("click", () => {
  localStorage.removeItem(HISTORY_KEY);
  renderHistory();
  renderCompareOptions();
  setStatus("History cleared", "idle");
});

themeToggle.addEventListener("click", toggleTheme);

compareReportsButton.addEventListener("click", () => {
  const left = findHistoryItem(compareA.value);
  const right = findHistoryItem(compareB.value);
  renderComparison(left, right);
  setStatus("Comparison updated", "idle");
});

setTheme(getTheme());
setStatus("Waiting for a query", "idle");
renderHistory();
renderCompareOptions();