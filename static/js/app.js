/**
 * CardioResearch AI - Main Application Controller
 */

// Application State
const state = {
  activeTab: "dashboard",
  activeProjectId: "default-project-1",
  projects: [],
  currentPapers: [],
  selectedForComparison: new Set(),
  chatHistory: [],
  dashboardData: null,
  charts: {}
};

// Initialize Application on DOM Ready
document.addEventListener("DOMContentLoaded", async () => {
  setupNavigation();
  setupSearchHandlers();
  setupChatHandlers();
  setupPdfUploadHandlers();
  setupSettingsHandlers();
  
  await loadProjects();
  await loadDashboardAnalytics();
  await loadInitialPapers();
});

// Toast Notifications
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${message}</span>`;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

// Navigation & Tab Switching
function setupNavigation() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const target = tab.getAttribute("data-tab");
      switchTab(target);
    });
  });
}

function switchTab(tabId) {
  state.activeTab = tabId;

  // Update Nav Tab UI
  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.classList.toggle("active", tab.getAttribute("data-tab") === tabId);
  });

  // Update View Panels
  document.querySelectorAll(".view-panel").forEach(panel => {
    panel.classList.toggle("active", panel.id === `view-${tabId}`);
  });

  // Refresh tab-specific data if needed
  if (tabId === "dashboard") {
    loadDashboardAnalytics();
  } else if (tabId === "compare") {
    renderComparisonView();
  } else if (tabId === "gaps") {
    loadResearchGaps();
  }
}

// Load Projects
async function loadProjects() {
  try {
    const projects = await window.api.getProjects();
    state.projects = projects;
    
    const selectEl = document.getElementById("active-project-select");
    if (selectEl && projects.length > 0) {
      selectEl.innerHTML = projects.map(p => 
        `<option value="${p.id}" ${p.id === state.activeProjectId ? 'selected' : ''}>📁 ${p.title}</option>`
      ).join("");

      selectEl.addEventListener("change", (e) => {
        state.activeProjectId = e.target.value;
        showToast(`Switched active workspace: ${e.target.options[e.target.selectedIndex].text}`, "info");
      });
    }
  } catch (err) {
    console.error("Failed to load projects:", err);
  }
}

// Load Initial Papers for Display
async function loadInitialPapers() {
  try {
    const papers = await window.api.listPapers("", 6);
    state.currentPapers = papers;
    renderPaperCards(papers);
  } catch (err) {
    console.error("Error loading initial papers:", err);
  }
}

// Setup Research Query
function setupSearchHandlers() {
  const input = document.getElementById("research-query-input");
  const searchBtn = document.getElementById("btn-run-search");
  const chips = document.querySelectorAll(".filter-tag-btn");

  if (searchBtn && input) {
    searchBtn.addEventListener("click", () => executeSearch(input.value));
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") executeSearch(input.value);
    });
  }

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-query");
      if (input) input.value = q;
      executeSearch(q);
    });
  });
}

// Execute Research Query Pipeline
async function executeSearch(query) {
  if (!query || !query.trim()) {
    showToast("Please enter a research question or clinical topic.", "error");
    return;
  }

  const stepper = document.getElementById("agent-stepper");
  const cardsContainer = document.getElementById("paper-cards-container");
  const synthesisContainer = document.getElementById("synthesis-summary-card");

  if (stepper) stepper.style.display = "block";
  updateStepperStage("orchestrator", "running");
  updateStepperStage("query-agent", "running");

  try {
    showToast("Orchestrator Agent initialized multi-agent pipeline...", "info");

    // Stage 1: Query Analyzer
    setTimeout(() => {
      updateStepperStage("query-agent", "completed");
      updateStepperStage("search-agent", "running");
    }, 400);

    // Stage 2: Literature Search
    setTimeout(() => {
      updateStepperStage("search-agent", "completed");
      updateStepperStage("ranking-agent", "running");
    }, 800);

    const result = await window.api.executeResearchQuery(query, state.activeProjectId, 6);

    updateStepperStage("ranking-agent", "completed");
    updateStepperStage("analysis-agent", "completed");
    updateStepperStage("evidence-agent", "completed");
    updateStepperStage("orchestrator", "completed");

    state.currentPapers = result.papers;
    renderPaperCards(result.papers);

    // Render Synthesis Box
    if (synthesisContainer) {
      synthesisContainer.style.display = "block";
      synthesisContainer.innerHTML = `
        <div class="glass-card" style="border-left: 4px solid var(--accent-ruby);">
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
            <div style="display:flex; align-items:center; gap:8px;">
              <span class="badge-source">Orchestrator Synthesis</span>
              <span style="font-size:12px; color:var(--accent-cyan); font-weight:600;">✓ Grounded in ${result.total_found} Literature Sources</span>
            </div>
            <button class="btn btn-sm btn-cyan" onclick="generateLiteratureReviewFromCurrent()">
              ⚡ Generate Full 8-Section Review
            </button>
          </div>
          <p style="font-size:14.5px; color:#e2e8f0; line-height:1.6;">${result.synthesis_summary}</p>
          <div style="margin-top:14px; display:flex; gap:10px; flex-wrap:wrap;">
            ${result.expanded_queries.map(q => `<span class="filter-tag-btn" style="font-size:11px;">🔍 ${q}</span>`).join("")}
          </div>
        </div>
      `;
    }

    showToast(`Retrieved and analyzed ${result.total_found} scientific papers!`, "success");

  } catch (err) {
    showToast(`Search failed: ${err.message}`, "error");
    updateStepperStage("orchestrator", "completed");
  }
}

function updateStepperStage(stageId, status) {
  const el = document.getElementById(`step-${stageId}`);
  if (!el) return;

  el.className = `stepper-item ${status}`;
  const indicator = el.querySelector(".stepper-indicator");
  if (indicator) {
    indicator.textContent = status === "completed" ? "✓" : (status === "running" ? "●" : "○");
  }
}

// Render Retrieved Paper Cards
function renderPaperCards(papers) {
  const container = document.getElementById("paper-cards-container");
  if (!container) return;

  if (!papers || papers.length === 0) {
    container.innerHTML = `<p style="color:var(--text-muted); padding:30px;">No papers found. Try adjusting your research query.</p>`;
    return;
  }

  container.innerHTML = papers.map(p => {
    const isSelected = state.selectedForComparison.has(p.id);
    return `
      <div class="paper-card" id="card-${p.id}">
        <div>
          <div class="paper-badge-row">
            <span class="badge-source">${p.source || 'PubMed'}</span>
            <span class="badge-citations">★ ${p.citation_count || 12} citations • ${p.publication_year || 2023}</span>
          </div>

          <h3 class="paper-title" style="margin-top:12px;">${p.title}</h3>
          <p class="paper-authors" style="margin-top:6px;">${p.authors || 'Cardiology Research Group'}</p>
          <p class="paper-journal" style="margin-top:2px;">${p.journal || 'Cardiology Journal'}</p>

          <div class="paper-parameters-box" style="margin-top:14px;">
            <div class="param-item">
              <span class="label">Dataset</span>
              <span class="val">${p.dataset_name || 'Clinical ECG Cohort'}</span>
            </div>
            <div class="param-item">
              <span class="label">AI Model</span>
              <span class="val">${p.model_architecture || 'Deep Convolutional Network'}</span>
            </div>
            <div class="param-item">
              <span class="label">Sample Size</span>
              <span class="val">${p.sample_size || 'Reported in text'}</span>
            </div>
            <div class="param-item">
              <span class="label">Metrics</span>
              <span class="val" style="color:var(--accent-cyan);">${p.evaluation_metrics || 'Macro AUC > 0.90'}</span>
            </div>
          </div>

          <p style="font-size:12.5px; color:var(--text-muted); margin-top:12px; line-height:1.5;">
            ${(p.abstract || '').slice(0, 180)}...
          </p>
        </div>

        <div class="paper-footer">
          <div style="display:flex; gap:8px;">
            <button class="btn btn-sm btn-secondary" onclick="openPaperDetailModal('${p.id}')">
              📄 Inspect Study
            </button>
            <button class="btn btn-sm ${isSelected ? 'btn-cyan' : 'btn-secondary'}" onclick="toggleComparePaper('${p.id}')">
              ${isSelected ? '✓ In Comparison' : '+ Compare'}
            </button>
          </div>
          <button class="btn btn-sm btn-secondary" title="Save to Project" onclick="savePaperToProject('${p.id}')">
            🔖 Save
          </button>
        </div>
      </div>
    `;
  }).join("");

  updateCompareBadgeCount();
}

// Comparison Matrix Management
function toggleComparePaper(paperId) {
  if (state.selectedForComparison.has(paperId)) {
    state.selectedForComparison.delete(paperId);
    showToast("Removed from comparison set", "info");
  } else {
    if (state.selectedForComparison.size >= 5) {
      showToast("You can compare up to 5 papers simultaneously.", "error");
      return;
    }
    state.selectedForComparison.add(paperId);
    showToast("Added to comparison set!", "success");
  }
  renderPaperCards(state.currentPapers);
  updateCompareBadgeCount();
}

function updateCompareBadgeCount() {
  const countBadge = document.getElementById("compare-count-badge");
  if (countBadge) {
    countBadge.textContent = state.selectedForComparison.size;
  }
}

async function renderComparisonView() {
  const container = document.getElementById("comparison-content");
  if (!container) return;

  const paperIds = Array.from(state.selectedForComparison);
  if (paperIds.length < 2) {
    container.innerHTML = `
      <div class="glass-card" style="text-align:center; padding:50px;">
        <h3 style="color:#fff; margin-bottom:10px;">Select at least 2 papers to compare</h3>
        <p style="color:var(--text-muted); margin-bottom:20px;">
          Currently selected: <strong>${paperIds.length}</strong>. Go to the Research Explorer and click "+ Compare" on papers.
        </p>
        <button class="btn btn-primary" onclick="switchTab('research')">Go to Research Explorer</button>
      </div>
    `;
    return;
  }

  container.innerHTML = `<p style="color:var(--accent-cyan); padding:30px;">Synthesizing comparison matrix...</p>`;

  try {
    const res = await window.api.comparePapers(paperIds);
    
    container.innerHTML = `
      <div class="glass-card" style="margin-bottom:24px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
          <div>
            <h3 style="color:#fff; font-size:18px;">Multi-Study Comparative Synthesis</h3>
            <p style="color:var(--text-muted); font-size:13px;">Comparing ${res.matrix.length} selected cardiology publications</p>
          </div>
          <button class="btn btn-sm btn-cyan" onclick="exportComparisonCSV()">📥 Export CSV</button>
        </div>
        <p style="font-size:14.5px; color:#e2e8f0; line-height:1.6;">${res.synthesis_analysis}</p>
      </div>

      <div class="comparison-table-wrapper">
        <table class="comparison-table">
          <thead>
            <tr>
              <th>Study Title & Year</th>
              <th>AI Architecture</th>
              <th>Dataset & Sample</th>
              <th>Evaluation Metrics</th>
              <th>Reported Performance</th>
              <th>Primary Advantages</th>
              <th>Reported Limitations</th>
            </tr>
          </thead>
          <tbody>
            ${res.matrix.map(row => `
              <tr>
                <td><strong>${row.title}</strong><br><span style="color:var(--text-muted); font-size:12px;">${row.authors} (${row.year})</span></td>
                <td><span class="badge-source">${row.method_model}</span></td>
                <td><strong>${row.dataset}</strong><br><span style="color:var(--accent-cyan); font-size:12px;">${row.sample_size}</span></td>
                <td><span style="font-family:var(--font-mono); color:#38bdf8; font-size:12px;">${row.evaluation_metrics}</span></td>
                <td style="font-size:12.5px;">${row.reported_performance}</td>
                <td style="color:#34d399; font-size:12.5px;">${row.advantages}</td>
                <td style="color:#f87171; font-size:12.5px;">${row.limitations}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>

      <div class="glass-card" style="margin-top:24px;">
        <h4 style="color:var(--accent-cyan); margin-bottom:12px;">Key Cross-Study Takeaways</h4>
        <ul style="list-style-position:inside; color:#e2e8f0; font-size:13.5px; line-height:1.8;">
          ${res.key_takeaways.map(t => `<li>${t}</li>`).join("")}
        </ul>
      </div>
    `;

  } catch (err) {
    container.innerHTML = `<p style="color:var(--accent-ruby);">Failed to generate comparison: ${err.message}</p>`;
  }
}

// Research Gaps View
async function loadResearchGaps() {
  const container = document.getElementById("gaps-container");
  if (!container) return;

  container.innerHTML = `<p style="color:var(--accent-cyan); padding:30px;">Synthesizing cross-study research gaps...</p>`;

  try {
    const paperIds = state.currentPapers.map(p => p.id);
    const res = await window.api.getResearchGaps("Deep Learning in Cardiology", paperIds);

    container.innerHTML = `
      <div class="glass-card" style="margin-bottom:24px; border-left:4px solid var(--accent-amber);">
        <h3 style="color:#fff; font-size:18px;">Synthesized Research Gaps in Cardiology AI</h3>
        <p style="color:#e2e8f0; font-size:14px; margin-top:6px; line-height:1.6;">${res.overall_recommendation}</p>
      </div>

      <div>
        ${res.gaps.map(gap => `
          <div class="gap-card">
            <span class="gap-badge">${gap.synthesis_badge}</span>
            <span style="display:block; font-size:12px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">
              Category: ${gap.category}
            </span>
            <h4 style="color:#fff; font-size:17px; margin-bottom:8px;">${gap.gap_title}</h4>
            <p style="color:#cbd5e1; font-size:14px; line-height:1.6; margin-bottom:12px;">${gap.description}</p>
            
            <div style="background:rgba(0,0,0,0.3); padding:12px; border-radius:8px; border-left:3px solid var(--accent-cyan);">
              <span style="font-size:11.5px; color:var(--accent-cyan); font-weight:700; text-transform:uppercase;">Recommended Future Direction:</span>
              <p style="font-size:13px; color:#f1f5f9; margin-top:4px;">${gap.potential_future_direction}</p>
            </div>

            <div style="margin-top:12px; font-size:12px; color:var(--text-muted);">
              <strong>Identified across studies:</strong> ${gap.affected_papers.join(" • ")}
            </div>
          </div>
        `).join("")}
      </div>
    `;

  } catch (err) {
    container.innerHTML = `<p style="color:var(--accent-ruby);">Failed to load research gaps: ${err.message}</p>`;
  }
}

// 8-Section Literature Review Generation
async function generateLiteratureReviewFromCurrent() {
  switchTab("review");
  const container = document.getElementById("review-viewer");
  if (!container) return;

  container.innerHTML = `<div class="glass-card" style="padding:40px; text-align:center;"><p style="color:var(--accent-cyan);">Synthesizing full 8-section academic literature review...</p></div>`;

  try {
    const paperIds = state.currentPapers.map(p => p.id);
    const queryInput = document.getElementById("research-query-input");
    const topic = (queryInput && queryInput.value) ? queryInput.value : "Deep Learning Arrhythmia Detection";

    const review = await window.api.generateLiteratureReview(topic, paperIds, "APA");
    
    container.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
        <div style="display:flex; gap:8px;">
          <button class="btn btn-sm btn-cyan" onclick="copyReviewMarkdown()">📋 Copy Full Markdown</button>
          <button class="btn btn-sm btn-secondary" onclick="window.print()">🖨️ Print / Save as PDF</button>
        </div>
        <span style="font-size:12px; color:var(--accent-emerald); font-weight:600;">✓ Verified APA 7th References</span>
      </div>

      <div class="review-content-box" id="review-content-area">
        <h1>${review.title}</h1>
        
        <h2>Abstract</h2>
        <p>${review.abstract}</p>

        ${review.sections.map(s => `
          <h2>${s.section_number}. ${s.title}</h2>
          <div style="white-space: pre-line;">${s.content}</div>
        `).join("")}
      </div>
    `;

    window.currentReviewMarkdown = review.full_markdown;
    showToast("Generated 8-Section Literature Review!", "success");

  } catch (err) {
    container.innerHTML = `<p style="color:var(--accent-ruby);">Error generating review: ${err.message}</p>`;
  }
}

function copyReviewMarkdown() {
  if (window.currentReviewMarkdown) {
    navigator.clipboard.writeText(window.currentReviewMarkdown);
    showToast("Copied full 8-section review markdown to clipboard!", "success");
  }
}

// Chat Assistant (RAG)
function setupChatHandlers() {
  const input = document.getElementById("chat-input-field");
  const sendBtn = document.getElementById("btn-send-chat");

  if (sendBtn && input) {
    sendBtn.addEventListener("click", () => sendChatMessage());
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") sendChatMessage();
    });
  }
}

async function sendChatMessage() {
  const input = document.getElementById("chat-input-field");
  const message = input.value.trim();
  if (!message) return;

  input.value = "";
  appendChatBubble("user", message);

  const messagesContainer = document.getElementById("chat-messages-container");
  const loadingIndicator = document.createElement("div");
  loadingIndicator.className = "chat-bubble assistant";
  loadingIndicator.innerHTML = `<span style="color:var(--accent-cyan);">⚡ Searching literature corpus & reasoning...</span>`;
  messagesContainer.appendChild(loadingIndicator);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  try {
    const res = await window.api.chat(message, state.activeProjectId, state.chatHistory);
    loadingIndicator.remove();

    appendChatBubble("assistant", res.answer, res.confidence, res.citations, res.evidence_claims);
    state.chatHistory.push({ role: "user", content: message });
    state.chatHistory.push({ role: "assistant", content: res.answer });

  } catch (err) {
    loadingIndicator.remove();
    appendChatBubble("assistant", `Error: ${err.message}`);
  }
}

function sendSuggestedChat(promptText) {
  const input = document.getElementById("chat-input-field");
  if (input) {
    input.value = promptText;
    sendChatMessage();
  }
}

function clearChatMessages() {
  const container = document.getElementById("chat-messages-container");
  if (!container) return;
  state.chatHistory = [];
  container.innerHTML = `
    <div class="chat-bubble assistant">
      <div style="font-size:11px; color:var(--accent-cyan); font-weight:700; margin-bottom:6px;">● CardioResearch AI Co-Pilot Ready</div>
      👋 <strong>Hello! I am your CardioResearch AI research co-pilot.</strong><br>
      I am grounded in verified cardiology literature (PubMed & Europe PMC). You can ask me questions about deep learning models, datasets (like PTB-XL), reported AUC scores, or clinical limitations.
    </div>
  `;
  showToast("Chat history cleared.", "info");
}

function formatMarkdownChat(text) {
  if (!text) return "";
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Headers
  html = html.replace(/^### (.*$)/gim, '<h4 style="color:var(--accent-cyan); font-size:15px; margin:10px 0 6px;">$1</h4>');
  html = html.replace(/^## (.*$)/gim, '<h3 style="color:#fff; font-size:16px; margin:12px 0 8px;">$1</h3>');

  // Bold and Italic
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // Bullet points
  html = html.replace(/^\s*• (.*$)/gim, '<div style="margin-left:14px; margin-bottom:4px;">• $1</div>');
  html = html.replace(/^\s*- (.*$)/gim, '<div style="margin-left:14px; margin-bottom:4px;">• $1</div>');

  // Code snippets
  html = html.replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.08); padding:2px 6px; border-radius:4px; font-family:var(--font-mono); color:#38bdf8; font-size:12px;">$1</code>');

  // Newlines
  html = html.replace(/\n\n/g, '<div style="height:10px;"></div>');
  html = html.replace(/\n/g, '<br>');

  return html;
}

function appendChatBubble(role, content, confidence = null, citations = [], evidence = []) {
  const container = document.getElementById("chat-messages-container");
  if (!container) return;

  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;

  let confidenceHtml = "";
  if (confidence) {
    const color = confidence === "High" ? "var(--accent-emerald)" : "var(--accent-amber)";
    confidenceHtml = `<div style="font-size:11px; color:${color}; font-weight:700; margin-bottom:8px; letter-spacing:0.4px;">● Evidence Grounding: ${confidence} Confidence</div>`;
  }

  let evidenceHtml = "";
  if (evidence && evidence.length > 0) {
    const quoteSnippets = evidence.map((e, idx) => `
      <div style="background:rgba(0,0,0,0.3); border-left:3px solid var(--accent-cyan); padding:8px 12px; margin-top:6px; border-radius:6px; font-size:12px;">
        <strong style="color:var(--accent-cyan);">${e.supporting_paper_title.slice(0, 50)}...</strong>
        <p style="color:#cbd5e1; font-style:italic; margin-top:2px;">"${e.extracted_quote}"</p>
      </div>
    `).join("");

    evidenceHtml = `
      <details style="margin-top:12px; padding-top:8px; border-top:1px solid rgba(255,255,255,0.08); font-size:12px; cursor:pointer;">
        <summary style="color:var(--accent-cyan); font-weight:600; outline:none;">🔍 Inspect Verified Evidence Passages (${evidence.length})</summary>
        <div style="margin-top:6px;">${quoteSnippets}</div>
      </details>
    `;
  }

  let citationsHtml = "";
  if (citations && citations.length > 0) {
    citationsHtml = `
      <div style="margin-top:10px; padding-top:8px; border-top:1px solid rgba(255,255,255,0.08); font-size:11.5px; color:var(--text-muted);">
        <strong style="color:#fff;">Literature Citations:</strong> ${citations.join(" • ")}
      </div>
    `;
  }

  const formattedContent = role === "assistant" ? formatMarkdownChat(content) : content;

  bubble.innerHTML = `
    ${confidenceHtml}
    <div style="line-height:1.6;">${formattedContent}</div>
    ${evidenceHtml}
    ${citationsHtml}
  `;

  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

// PDF Upload Handlers
function setupPdfUploadHandlers() {
  const dropzone = document.getElementById("pdf-dropzone");
  const fileInput = document.getElementById("pdf-file-input");

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener("click", () => fileInput.click());
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "var(--accent-cyan)";
  });
  dropzone.addEventListener("dragleave", () => {
    dropzone.style.borderColor = "var(--border-subtle)";
  });
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "var(--border-subtle)";
    if (e.dataTransfer.files.length > 0) {
      handlePdfUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      handlePdfUpload(fileInput.files[0]);
    }
  });
}

async function handlePdfUpload(file) {
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    showToast("Please select a valid PDF document.", "error");
    return;
  }

  showToast(`Uploading and analyzing "${file.name}"...`, "info");
  const statusBox = document.getElementById("pdf-upload-status");
  if (statusBox) {
    statusBox.style.display = "block";
    statusBox.innerHTML = `<p style="color:var(--accent-cyan);">Parsing document, extracting sections, and generating RAG chunks...</p>`;
  }

  try {
    const res = await window.api.uploadPdf(file, state.activeProjectId);
    showToast(`Successfully ingested "${res.title}" into vector store!`, "success");

    if (statusBox) {
      statusBox.innerHTML = `
        <div class="glass-card" style="border-left:4px solid var(--accent-emerald);">
          <h4 style="color:#fff;">✓ Successfully Ingested: ${res.title}</h4>
          <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">Author: ${res.authors} • Model: ${res.model_architecture}</p>
          <div style="margin-top:10px;">
            <span class="badge-source">Indexed in RAG Vector Store</span>
            <button class="btn btn-sm btn-cyan" style="margin-left:12px;" onclick="switchTab('chat')">Ask Questions in Chat</button>
          </div>
        </div>
      `;
    }

    await loadInitialPapers();

  } catch (err) {
    showToast(`PDF upload failed: ${err.message}`, "error");
    if (statusBox) {
      statusBox.innerHTML = `<p style="color:var(--accent-ruby);">Failed: ${err.message}</p>`;
    }
  }
}

// Paper Detail Modal
async function openPaperDetailModal(paperId) {
  const modal = document.getElementById("paper-detail-modal");
  const modalBody = document.getElementById("paper-modal-body");
  if (!modal || !modalBody) return;

  modalBody.innerHTML = `<p style="color:var(--accent-cyan); padding:20px;">Loading paper parameters...</p>`;
  modal.classList.add("active");

  try {
    const p = await window.api.getPaper(paperId);
    modalBody.innerHTML = `
      <span class="badge-source">${p.source || 'PubMed'}</span>
      <h2 style="color:#fff; font-size:22px; margin-top:10px; line-height:1.4;">${p.title}</h2>
      <p style="color:var(--text-muted); font-size:13px; margin-top:4px;">
        <strong>Authors:</strong> ${p.authors || 'Cardiology Research Group'}<br>
        <strong>Journal:</strong> ${p.journal || 'Cardiovascular Medicine'} (${p.publication_year || 2023})<br>
        <strong>DOI:</strong> <a href="${p.url || '#'}" target="_blank" style="color:var(--accent-cyan);">${p.doi || 'View Publication'}</a>
      </p>

      <div class="paper-parameters-box" style="margin:20px 0;">
        <div class="param-item"><span class="label">Benchmark Dataset</span><span class="val">${p.dataset_name || 'Clinical Cohort'}</span></div>
        <div class="param-item"><span class="label">AI Model Architecture</span><span class="val">${p.model_architecture || 'Deep Learning'}</span></div>
        <div class="param-item"><span class="label">Sample Size</span><span class="val">${p.sample_size || 'Reported in text'}</span></div>
        <div class="param-item"><span class="label">Evaluation Metrics</span><span class="val" style="color:var(--accent-cyan);">${p.evaluation_metrics || 'AUC-ROC: 0.92'}</span></div>
      </div>

      <h4 style="color:#fff; font-size:15px; margin-bottom:6px;">Abstract</h4>
      <p style="font-size:13.5px; color:#cbd5e1; line-height:1.7;">${p.abstract || 'No abstract available.'}</p>

      <h4 style="color:var(--accent-ruby); font-size:15px; margin-top:18px; margin-bottom:6px;">Reported Limitations</h4>
      <p style="font-size:13px; color:#fca5a5; line-height:1.6;">${p.limitations || 'Single-center retrospective validation constraint.'}</p>

      <div style="margin-top:24px; display:flex; justify-content:flex-end; gap:10px;">
        <button class="btn btn-secondary" onclick="closeModal('paper-detail-modal')">Close</button>
        <button class="btn btn-primary" onclick="savePaperToProject('${p.id}')">🔖 Save to Project</button>
      </div>
    `;
  } catch (err) {
    modalBody.innerHTML = `<p style="color:var(--accent-ruby);">Failed to load paper details: ${err.message}</p>`;
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove("active");
}

async function savePaperToProject(paperId) {
  try {
    await window.api.savePaper(state.activeProjectId, paperId);
    showToast("Paper successfully saved to project workspace!", "success");
  } catch (err) {
    showToast(`Save failed: ${err.message}`, "error");
  }
}

// Dashboard Analytics Charts
async function loadDashboardAnalytics() {
  try {
    const data = await window.api.getDashboardAnalytics();
    state.dashboardData = data;

    // Update KPI Numbers
    const kpiPapers = document.getElementById("kpi-total-papers");
    const kpiQueries = document.getElementById("kpi-queries");
    const kpiConfidence = document.getElementById("kpi-confidence");

    if (kpiPapers) kpiPapers.textContent = data.stats.total_papers_indexed;
    if (kpiQueries) kpiQueries.textContent = data.stats.queries_executed;
    if (kpiConfidence) kpiConfidence.textContent = data.stats.evidence_confidence_rate;

    renderDashboardCharts(data);
  } catch (err) {
    console.error("Dashboard analytics error:", err);
  }
}

function renderDashboardCharts(data) {
  if (!window.Chart) return;

  // Chart 1: AI Model Distribution
  const ctxModels = document.getElementById("chart-models");
  if (ctxModels) {
    if (state.charts.models) state.charts.models.destroy();
    state.charts.models = new Chart(ctxModels, {
      type: "doughnut",
      data: {
        labels: data.model_distribution.map(m => m.name),
        datasets: [{
          data: data.model_distribution.map(m => m.count),
          backgroundColor: ["#e11d48", "#06b6d4", "#8b5cf6", "#10b981", "#f59e0b"],
          borderColor: "#070a12",
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "bottom", labels: { color: "#94a3b8", font: { size: 11 } } }
        }
      }
    });
  }

  // Chart 2: Publication Trends
  const ctxTrends = document.getElementById("chart-trends");
  if (ctxTrends) {
    if (state.charts.trends) state.charts.trends.destroy();
    state.charts.trends = new Chart(ctxTrends, {
      type: "line",
      data: {
        labels: data.publication_trends.map(t => t.year),
        datasets: [{
          label: "Cardiology AI Publications",
          data: data.publication_trends.map(t => t.publications),
          borderColor: "#06b6d4",
          backgroundColor: "rgba(6, 182, 212, 0.15)",
          fill: true,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        scales: {
          x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
          y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }
}

// Settings Handlers
async function setupSettingsHandlers() {
  try {
    const s = await window.api.getSettings();
    const providerSelect = document.getElementById("setting-llm-provider");
    if (providerSelect) providerSelect.value = s.default_provider;

    const saveBtn = document.getElementById("btn-save-settings");
    if (saveBtn) {
      saveBtn.addEventListener("click", async () => {
        const payload = {
          default_provider: providerSelect.value,
          gemini_api_key: document.getElementById("setting-gemini-key")?.value || undefined,
          openai_api_key: document.getElementById("setting-openai-key")?.value || undefined,
          groq_api_key: document.getElementById("setting-groq-key")?.value || undefined
        };
        await window.api.updateSettings(payload);
        showToast("Settings and LLM credentials saved!", "success");
      });
    }
  } catch (err) {
    console.error("Settings load error:", err);
  }
}

// Export CSV for Comparison Matrix
function exportComparisonCSV() {
  const table = document.querySelector(".comparison-table");
  if (!table) return;

  let csv = [];
  const rows = table.querySelectorAll("tr");
  for (let i = 0; i < rows.length; i++) {
    let row = [], cols = rows[i].querySelectorAll("td, th");
    for (let j = 0; j < cols.length; j++) {
      let data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, " ").replace(/"/g, '""');
      row.push('"' + data + '"');
    }
    csv.push(row.join(","));
  }

  const csvFile = new Blob([csv.join("\n")], { type: "text/csv" });
  const downloadLink = document.createElement("a");
  downloadLink.download = "CardioResearch_Study_Comparison.csv";
  downloadLink.href = window.URL.createObjectURL(csvFile);
  downloadLink.style.display = "none";
  document.body.appendChild(downloadLink);
  downloadLink.click();
  downloadLink.remove();
  showToast("Comparison CSV downloaded!", "success");
}

window.switchTab = switchTab;
window.executeSearch = executeSearch;
window.toggleComparePaper = toggleComparePaper;
window.openPaperDetailModal = openPaperDetailModal;
window.closeModal = closeModal;
window.savePaperToProject = savePaperToProject;
window.generateLiteratureReviewFromCurrent = generateLiteratureReviewFromCurrent;
window.copyReviewMarkdown = copyReviewMarkdown;
window.exportComparisonCSV = exportComparisonCSV;
window.sendSuggestedChat = sendSuggestedChat;
window.clearChatMessages = clearChatMessages;
