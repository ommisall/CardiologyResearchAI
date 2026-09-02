# CardioResearch AI — System Architecture & Technical Specification

## 1. Multi-Agent Architecture

CardioResearch AI employs an autonomous multi-agent pipeline designed to eliminate LLM hallucinations by enforcing strict evidence retrieval, citation verification, and cross-study parameter extraction.

```
                    ┌────────────────────────────┐
                    │      RESEARCH USER         │
                    └─────────────┬──────────────┘
                                  │ Natural Language Query
                                  ▼
                    ┌────────────────────────────┐
                    │     ORCHESTRATOR AGENT     │
                    │   Coordinates Execution    │
                    └─────────────┬──────────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 ▼                ▼                ▼
        ┌─────────────────┐ ┌───────────┐ ┌─────────────────┐
        │  Query Analyzer │ │ Search Agt│ │ PDF Ingestion   │
        │ Intent & MeSH   │ │ (PubMed / │ │ (pypdf Chunker) │
        │ Expansion       │ │ EuropePMC)│ │                 │
        └────────┬────────┘ └─────┬─────┘ └────────┬────────┘
                 └────────────────┼────────────────┘
                                  ▼
                    ┌────────────────────────────┐
                    │    PAPER RANKING AGENT     │
                    │ Relevance, Recency, Impact │
                    └─────────────┬──────────────┘
                                  ▼
                    ┌────────────────────────────┐
                    │    PAPER ANALYSIS AGENT    │
                    │ Dataset, Model, Metrics    │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
        ┌───────────────────────┐   ┌───────────────────────┐
        │   COMPARISON AGENT    │   │  RESEARCH GAP AGENT   │
        │ Cross-Study Matrix    │   │ Systematic Limitations│
        └───────────┬───────────┘   └───────────┬───────────┘
                    └─────────────┬─────────────┘
                                  ▼
                    ┌────────────────────────────┐
                    │        REPORT AGENT        │
                    │  8-Section Academic Paper  │
                    └─────────────┬──────────────┘
                                  ▼
                    ┌────────────────────────────┐
                    │       CITATION AGENT       │
                    │ APA / IEEE / Vancouver     │
                    └────────────────────────────┘
```

---

## 2. Agent Responsibilities

| Agent Name | Core Responsibility | Input | Output |
|---|---|---|---|
| **Orchestrator Agent** | Coordinates pipeline execution, emits real-time telemetry logs | Research Question | `ResearchPipelineResult` |
| **Query Analyzer Agent** | Deconstructs clinical intent and expands Boolean / MeSH search terms | User String | Expanded Queries & Keywords |
| **Search Agent** | Federates queries across NCBI PubMed and Europe PMC | Expanded Queries | Deduplicated Papers |
| **Paper Ranking Agent** | Computes composite semantic relevance and recency scores | Raw Papers | Ranked Papers |
| **Paper Analysis Agent** | Extracts Dataset, Model, Sample Size, Metrics, Limitations | Paper Abstract / Fulltext | Structured Study Parameters |
| **Evidence Extraction Agent** | Maps claims to supporting passages with confidence ratings | Paper Chunks | `ClaimEvidence` with High/Med/Low |
| **Comparison Agent** | Synthesizes side-by-side comparative matrices | Selected Studies | Comparison Table & Tradeoffs |
| **Research Gap Agent** | Cross-analyzes limitations to detect systemic gaps | Multi-study Corpus | Inferred Gaps with AI Synthesis Badge |
| **Report Agent** | Compiles publication-ready 8-section academic review | Study Data & Gaps | Structured Academic Report |
| **Citation Agent** | Formats bibliographies and prevents fabricated references | Paper Metadata | Verified APA/IEEE/Vancouver Refs |

---

## 3. RAG Retrieval & Vector Store

- **Chunking Pipeline:** Overlapping sliding window (600 characters, 100 overlap) with automatic page number tagging and section boundary detection (Abstract, Introduction, Methods, Results, Limitations).
- **Embedding Index:** Normalized sub-word and token TF-IDF representation with dense Cosine Similarity search:
  $$\text{CosineSim}(\mathbf{q}, \mathbf{d}) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\| \|\mathbf{d}\|}$$
- **Hallucination Guard:** If cosine similarity across indexed passages fails to satisfy the threshold ($S < 0.08$), the chatbot explicitly responds: *"Insufficient evidence was retrieved to provide a reliable answer."*

---

## 4. Database Schema (SQLite / PostgreSQL)

- **`users`**: `id` (UUID), `name`, `email`, `password_hash`, `role`, `created_at`
- **`projects`**: `id` (UUID), `user_id`, `title`, `description`, `created_at`, `updated_at`
- **`papers`**: `id`, `pmid`, `doi`, `title`, `authors`, `journal`, `publication_date`, `publication_year`, `abstract`, `url`, `source`, `dataset_name`, `sample_size`, `model_architecture`, `evaluation_metrics`, `results_summary`, `limitations`, `conclusion`
- **`saved_papers`**: `id`, `user_id`, `project_id`, `paper_id`, `notes`, `tags`, `saved_at`
- **`research_queries`**: `id`, `user_id`, `project_id`, `query_text`, `intent`, `sub_queries`, `created_at`
- **`research_reports`**: `id`, `user_id`, `project_id`, `title`, `report_type`, `content`, `paper_ids`, `created_at`
