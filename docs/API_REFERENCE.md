# CardioResearch AI — API Reference Manual

The backend provides interactive OpenAPI / Swagger documentation at `/docs` and Redoc at `/redoc`.

## 1. Authentication Endpoints

### Register User
`POST /api/auth/register`
```json
{
  "name": "Dr. Sarah Lin",
  "email": "sarah.lin@cardio-research.edu",
  "password": "SecurePassword123!"
}
```

### Login
`POST /api/auth/login`
```json
{
  "email": "sarah.lin@cardio-research.edu",
  "password": "SecurePassword123!"
}
```
**Response:** Returns JWT `access_token` and user profile.

---

## 2. Autonomous Research Pipeline

### Execute Research Query
`POST /api/research/query`
```json
{
  "query": "Recent deep learning models for ECG arrhythmia detection",
  "sources": ["pubmed", "europe_pmc"],
  "max_results": 6
}
```
**Response:**
Returns `ResearchPipelineResult` containing:
- `intent`
- `expanded_queries`
- `papers` (with extracted datasets, models, metrics, limitations)
- `extracted_evidence` (claim-evidence pairings with confidence ratings)
- `agent_logs` (execution timestamps for UI stepper)
- `synthesis_summary`
- `medical_disclaimer`

### Conversational RAG Assistant
`POST /api/research/chat`
```json
{
  "message": "Which deep learning model achieved the highest AUC on the PTB-XL dataset?",
  "project_id": "default-project-1"
}
```
**Response:** Returns evidence-grounded answer, confidence level, and source citations.

### 8-Section Literature Review
`POST /api/research/literature-review`
```json
{
  "topic": "Deep Learning for Arrhythmia Classification",
  "paper_ids": ["pubmed_32958742", "pubmed_31548366"],
  "citation_format": "APA"
}
```
**Response:** Returns 8-section structured review (Title, Abstract, 1. Introduction, 2. Background, 3. Literature Review, 4. Comparative Analysis, 5. Research Gaps, 6. Future Directions, 7. Conclusion, 8. References).

### Cross-Study Research Gaps
`POST /api/research/research-gaps`
```json
{
  "topic": "Cardiology AI Benchmarks",
  "paper_ids": ["pubmed_32958742", "pubmed_34426589"]
}
```

---

## 3. Paper Management & PDF Ingestion

### List / Search Papers
`GET /api/papers?q=arrhythmia&limit=10`

### Upload Paper PDF
`POST /api/papers/upload`
- Multipart form: `file` (PDF), `project_id` (optional).
- Parses text, creates overlapping chunks, and indexes into the RAG Vector Store.

### Compare Studies
`POST /api/papers/compare`
```json
{
  "paper_ids": ["pubmed_32958742", "pubmed_31548366", "pubmed_33979435"]
}
```
**Response:** Side-by-side comparison matrix with model architectures, datasets, metrics, reported performance, advantages, and limitations.

---

## 4. Workspaces & Analytics

- `GET /api/projects`: List user research projects
- `POST /api/projects`: Create project
- `POST /api/projects/{id}/save-paper`: Bookmark paper
- `GET /api/analytics/dashboard`: KPI statistics, model distribution, and publication trends
- `GET /api/settings` & `POST /api/settings`: Configure active LLM provider (Gemini, OpenAI, Groq, Ollama, Heuristic)
