import asyncio
from app.agents.query_analyzer import QueryAnalyzerAgent
from app.agents.ranking_agent import RankingAgent
from app.agents.analysis_agent import PaperAnalysisAgent
from app.agents.comparison_agent import ComparisonAgent
from app.agents.research_gap_agent import ResearchGapAgent
from app.agents.citation_agent import CitationAgent
from app.agents.orchestrator import OrchestratorAgent
from app.services.vector_store import VectorStore
from app.services.pubmed import CURATED_CARDIOLOGY_STUDIES

def test_query_analyzer():
    res = asyncio.run(QueryAnalyzerAgent.analyze("What are recent deep learning models for ECG arrhythmia detection?"))
    assert "intent" in res
    assert len(res["expanded_queries"]) >= 3
    assert any("ecg" in q.lower() or "electrocardiography" in q.lower() or "arrhythmia" in q.lower() for q in res["expanded_queries"])

def test_paper_ranking():
    papers = CURATED_CARDIOLOGY_STUDIES.copy()
    query = "PTB-XL benchmark convolutional neural networks"
    ranked = RankingAgent.rank(papers, query)
    assert len(ranked) == len(papers)
    assert ranked[0].get("pmid") == "32958742" or "PTB-XL" in ranked[0]["title"]
    assert ranked[0]["relevance_score"] >= ranked[-1]["relevance_score"]

def test_paper_analysis_agent():
    sample_paper = {
        "title": "Deep learning on PTB-XL ECG dataset",
        "abstract": "We evaluated 1D ResNet on 21,837 patients. Model achieved Macro AUC of 0.925."
    }
    analyzed = PaperAnalysisAgent.analyze_paper(sample_paper)
    assert "PTB-XL" in analyzed["dataset_name"]
    assert "ResNet" in analyzed["model_architecture"]
    assert "0.925" in analyzed["evaluation_metrics"]

def test_comparison_agent():
    papers = CURATED_CARDIOLOGY_STUDIES[:3]
    res = ComparisonAgent.compare_studies(papers)
    assert len(res["matrix"]) == 3
    assert "synthesis_analysis" in res
    assert len(res["key_takeaways"]) > 0
    assert res["matrix"][0]["dataset"] != ""

def test_research_gap_agent():
    papers = CURATED_CARDIOLOGY_STUDIES[:3]
    gaps_data = ResearchGapAgent.identify_gaps(papers, "Cardiology Deep Learning")
    assert len(gaps_data["gaps"]) >= 3
    assert all("synthesis_badge" in g for g in gaps_data["gaps"])
    assert any("Validation" in g["category"] for g in gaps_data["gaps"])

def test_citation_agent_formats():
    papers = CURATED_CARDIOLOGY_STUDIES[:2]
    apa_refs = CitationAgent.format_citations(papers, "APA")
    ieee_refs = CitationAgent.format_citations(papers, "IEEE")
    vancouver_refs = CitationAgent.format_citations(papers, "VANCOUVER")

    assert len(apa_refs) == 2
    assert len(ieee_refs) == 2
    assert len(vancouver_refs) == 2
    assert "doi" in ieee_refs[0].lower() or "10." in ieee_refs[0]
    assert apa_refs[0].startswith("Wagner") or "(" in apa_refs[0]

def test_vector_store_cosine_similarity():
    vs = VectorStore()
    chunks = [
        {"chunk_id": "c1", "text": "PTB-XL is a gold standard dataset of 21,837 clinical 12-lead ECG records for neural networks."},
        {"chunk_id": "c2", "text": "Cardiac magnetic resonance imaging for myocardial scar segmentation using U-Net."}
    ]
    vs.add_chunks(chunks, "doc1", "PTB-XL Paper")
    
    results = vs.query("12-lead ECG neural network dataset", top_k=1)
    assert len(results) > 0
    assert results[0]["chunk_id"] == "c1"
    assert results[0]["score"] > 0.1

def test_full_orchestrator_pipeline():
    result = asyncio.run(OrchestratorAgent.run_pipeline("Atrial fibrillation detection deep learning", max_results=3))
    assert result["total_found"] >= 3
    assert len(result["papers"]) >= 3
    assert len(result["agent_logs"]) >= 6
    assert len(result["extracted_evidence"]) > 0
    assert "medical_disclaimer" in result
