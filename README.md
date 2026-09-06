# CardioResearch AI : Agentic AI Research Platform for Cardiology



[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **CardioResearch AI** is an intelligent, evidence-grounded multi-agent research assistant designed to help medical researchers, students, and cardiologists discover, analyze, compare, and synthesize scientific literature across PubMed and Europe PMC without hallucinations.

---

## 🌟 Key Features

1. **Multi-Agent Research Pipeline:**
   - **Orchestrator Agent**: Coordinates graph execution and emits live telemetry logs.
   - **Query Analyzer Agent**: Deconstructs research intent and expands targeted Boolean/MeSH queries.
   - **Literature Search Agent**: Live federated queries across NCBI PubMed & Europe PMC.
   - **Paper Ranking Agent**: Composite semantic relevance and recency scoring.
   - **Study Parameter Extractor**: Extracts Dataset (PTB-XL, MIT-BIH), AI Model (1D-CNN, Transformer), Sample Size, and AUC metrics.
   - **Evidence Grounding Agent**: Anchors claims to literature passages with confidence levels (High/Medium/Low).
   - **Study Comparison Agent**: Synthesizes side-by-side comparative matrices with CSV export.
   - **Research Gap Agent**: Synthesizes recurring cross-study limitations with explicit AI-synthesis labeling.
   - **8-Section Literature Review Generator**: Generates full academic reviews with APA/IEEE/Vancouver references.
   - **Citation Verification Agent**: Validates DOIs and PMIDs to prevent fabricated citations.

2. **RAG & PDF Ingestion Lab:**
   - Upload research papers in PDF format.
   - Automatic section extraction, semantic chunking (600 characters, 100 overlap), and cosine vector search.
   - Conversational AI research co-pilot with strict citation anchors.

3. **Modern Cyber-Medical Dark UI:**
   - Glassmorphic interface with ruby cardiac and pulse cyan accents.
   - Real-time agent execution stepper.
   - Interactive analytics charts (AI model distribution, publication trends).
   - Prominently displayed medical safety disclaimer banner.

---

## 🚀 Quickstart Guide

### 1. Requirements
- Python 3.10+ (Tested up to Python 3.14 on Windows)
- Zero external Node.js dependencies needed!

### 2. Installation
```powershell
pip install -r requirements.txt
```

### 3. Run Application Server
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Open in Browser
Visit **[http://localhost:8000](http://localhost:8000)** in your web browser.
Interactive API documentation is available at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

---

## 🧪 Run Automated Tests
```powershell
python -m pytest tests/test_pipeline.py -v
```

---

## 📁 Repository Structure

```
├── app/
│   ├── main.py              # FastAPI entrypoint & SPA router
│   ├── config.py            # App settings & LLM keys
│   ├── database.py          # SQLite async database engine
│   ├── models/              # SQLAlchemy database tables
│   ├── schemas/             # Pydantic validation models
│   ├── auth/                # JWT authentication & security
│   ├── services/            # PubMed, Europe PMC, VectorStore, PDF Parser, LLM Gateway
│   ├── agents/              # 12 Specialized Research Agents
│   └── routers/             # REST endpoints (auth, research, papers, projects, analytics)
├── static/                  # Modern Glassmorphic SPA Frontend
│   ├── index.html           # Main SPA HTML
│   ├── css/style.css        # Bespoke medical dark theme
│   └── js/                  # App logic & REST API client
├── docs/                    # Final-Year Academic Deliverables
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   └── VIVA_PRESENTATION_GUIDE.md
├── tests/                   # Automated pytest suite
├── requirements.txt
├── .env.example
└── README.md
```

---


> **CardioResearch AI is intended for research and educational purposes only.**
