# CardioResearch AI — Final-Year Project Viva & Presentation Guide

## 1. Project Pitch (30-Second Elevator Pitch)
> "CardioResearch AI is an autonomous, evidence-grounded multi-agent research assistant for cardiology. Traditional chatbots hallucinate facts and fabricate citations when answering complex medical questions. CardioResearch AI solves this by deploying specialized AI agents that query live medical databases (PubMed & Europe PMC), extract key study parameters (datasets, ML architectures, AUC metrics, and limitations), synthesize side-by-side comparative matrices, and generate publication-grade 8-section literature reviews with strictly verified citations."

---

## 2. Key Architectural Differentiators

1. **Multi-Agent Orchestration over Monolithic LLMs:**
   - Rather than relying on a single prompt, 12 specialized agents handle query deconstruction, federated search, ranking, parameter extraction, evidence grounding, comparison, research gap inference, and citation verification.
2. **Strict Hallucination Guardrails & Abstention:**
   - Every claim in the chat assistant is grounded in specific chunk passages with a confidence rating (High/Medium/Low). If evidence is insufficient, the system abstains rather than inventing data.
3. **Automated Cross-Study Comparison:**
   - Automatically parses unstructured medical abstracts and full-text PDFs to extract standardized parameters: Objective, Dataset (e.g. PTB-XL), Model (1D-CNN vs Transformer), Metrics, and Limitations.
4. **AI-Generated Synthesis Labeling:**
   - Inferred research gaps are explicitly tagged as *AI-Generated Synthesis (Cross-Study Inference)* to distinguish machine hypotheses from reported clinical facts.
5. **Medical Safety Compliance:**
   - Prominently displays safety disclaimers adhering to international research-only medical guidelines.

---

## 3. Demonstration Script (5-Minute Live Viva Demo)

- **Step 1: Dashboard Overview (`/`)**
  - Show live metrics, AI model distribution (ResNet vs Transformer vs LSTM), and publication trends from 2019–2025.
- **Step 2: Autonomous Research Query**
  - In Research Explorer, trigger: *"Recent deep learning models for ECG arrhythmia detection"*.
  - Show the **Agent Execution Stepper** animating through Orchestrator → Query Analyzer → Search Agent → Ranking Agent → Analysis Agent → Evidence Agent.
  - Review retrieved cards showing extracted parameters (PTB-XL, Mayo Clinic, 1D-ResNet, AUC: 0.925).
- **Step 3: Study Comparison Matrix**
  - Click "+ Compare" on 2–3 papers and navigate to the **Study Comparison** tab.
  - Show the side-by-side comparative matrix and click "Export CSV".
- **Step 4: 8-Section Literature Review**
  - Open **Literature Review Studio**.
  - Show the synthesized paper outline: Abstract, Introduction, Background, Literature Review, Comparative Analysis, Research Gaps, Future Directions, Conclusion, References (APA 7th).
- **Step 5: Synthesized Research Gaps**
  - View the **Research Gaps** tab highlighting lack of multi-center prospective validation, rare pathology class imbalance, and wearable edge constraints.
- **Step 6: PDF Upload & RAG Chat**
  - Demonstrate dragging a research paper PDF into the **PDF Lab**.
  - Open **AI Chat** and ask: *"What are the reported limitations of CNNs on the PTB-XL dataset?"*
  - Point out the confidence badge and source citations.

---

## 4. Frequently Asked Examiner Questions & Model Answers

### Q1: Why did you build a multi-agent system instead of just using ChatGPT or Claude?
> **Answer:** "General LLMs are trained on broad web corpora and suffer from high hallucination rates, knowledge cutoffs, and fabricated citations. In clinical cardiology, factual accuracy is non-negotiable. Our multi-agent system decouples query planning, live literature retrieval from PubMed/Europe PMC, and citation verification into distinct deterministic steps, ensuring that every claim is grounded in verifiable evidence."

### Q2: How does the system extract structured study parameters (like sample size or AUC) from unstructured text?
> **Answer:** "We use a hybrid extraction approach combining regex-based clinical parameter parsers (for standard metrics like AUC-ROC, F1, sensitivity) with our Paper Analysis Agent. This extracts datasets, sample cohorts, and deep learning architectures into structured Pydantic schemas."

### Q3: What happens if an external LLM API is down or unavailable?
> **Answer:** "The platform features a multi-provider gateway supporting Google Gemini, OpenAI, Groq, Anthropic, and local Ollama. Furthermore, we engineered an offline Cardiology Expert Heuristic Synthesizer that ensures the entire 12-agent pipeline, comparison matrix, and review generator remain 100% functional even in completely air-gapped or zero-token evaluation environments."
