/**
 * CardioResearch AI - Centralized REST Client
 */

const API_BASE = "";

class ApiClient {
  constructor() {
    this.token = localStorage.getItem("cardio_token") || "";
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem("cardio_token", token);
    } else {
      localStorage.removeItem("cardio_token");
    }
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
      ...(options.headers || {})
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    try {
      const response = await fetch(url, { ...options, headers });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  }

  // Auth
  async register(name, email, password) {
    const res = await this.request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password })
    });
    this.setToken(res.access_token);
    return res;
  }

  async login(email, password) {
    const res = await this.request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
    this.setToken(res.access_token);
    return res;
  }

  async getMe() {
    return this.request("/api/auth/me");
  }

  // Research Pipeline
  async executeResearchQuery(query, projectId = null, maxResults = 6) {
    return this.request("/api/research/query", {
      method: "POST",
      body: JSON.stringify({
        query,
        project_id: projectId,
        sources: ["pubmed", "europe_pmc"],
        max_results: maxResults
      })
    });
  }

  async chat(message, projectId = null, history = []) {
    return this.request("/api/research/chat", {
      method: "POST",
      body: JSON.stringify({ message, project_id: projectId, history })
    });
  }

  async generateLiteratureReview(topic, paperIds = [], citationFormat = "APA") {
    return this.request("/api/research/literature-review", {
      method: "POST",
      body: JSON.stringify({ topic, paper_ids: paperIds, citation_format: citationFormat })
    });
  }

  async getResearchGaps(topic, paperIds = []) {
    return this.request("/api/research/research-gaps", {
      method: "POST",
      body: JSON.stringify({ topic, paper_ids: paperIds })
    });
  }

  // Papers & PDF
  async listPapers(q = "") {
    const queryStr = q ? `?q=${encodeURIComponent(q)}` : "";
    return this.request(`/api/papers${queryStr}`);
  }

  async getPaper(id) {
    return this.request(`/api/papers/${id}`);
  }

  async uploadPdf(file, projectId = null) {
    const formData = new FormData();
    formData.append("file", file);
    if (projectId) formData.append("project_id", projectId);

    return this.request("/api/papers/upload", {
      method: "POST",
      body: formData
    });
  }

  async comparePapers(paperIds) {
    return this.request("/api/papers/compare", {
      method: "POST",
      body: JSON.stringify({ paper_ids: paperIds })
    });
  }

  // Projects
  async getProjects() {
    return this.request("/api/projects");
  }

  async createProject(title, description) {
    return this.request("/api/projects", {
      method: "POST",
      body: JSON.stringify({ title, description })
    });
  }

  async getSavedPapers(projectId) {
    return this.request(`/api/projects/${projectId}/saved-papers`);
  }

  async savePaper(projectId, paperId, notes = "", tags = "") {
    return this.request(`/api/projects/${projectId}/save-paper`, {
      method: "POST",
      body: JSON.stringify({ paper_id: paperId, notes, tags })
    });
  }

  async removeSavedPaper(projectId, paperId) {
    return this.request(`/api/projects/${projectId}/saved-papers/${paperId}`, {
      method: "DELETE"
    });
  }

  // Analytics & Settings
  async getDashboardAnalytics() {
    return this.request("/api/analytics/dashboard");
  }

  async getSettings() {
    return this.request("/api/settings");
  }

  async updateSettings(settingsData) {
    return this.request("/api/settings", {
      method: "POST",
      body: JSON.stringify(settingsData)
    });
  }
}

window.api = new ApiClient();
