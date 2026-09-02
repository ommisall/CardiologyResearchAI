from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.schemas.paper import PaperResponse

class ResearchQueryRequest(BaseModel):
    query: str = Field(..., example="Recent deep learning models for ECG arrhythmia detection")
    project_id: Optional[str] = None
    sources: Optional[List[str]] = ["pubmed", "europe_pmc"]
    max_results: Optional[int] = 6
    year_start: Optional[int] = None
    year_end: Optional[int] = None

class AgentStepLog(BaseModel):
    agent_name: str
    status: str  # pending, running, completed, skipped, failed
    message: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None

class ClaimEvidence(BaseModel):
    claim: str
    supporting_paper_title: str
    supporting_paper_id: str
    extracted_quote: str
    confidence: str  # High, Medium, Low
    pmid_or_doi: Optional[str] = None

class ResearchPipelineResult(BaseModel):
    query: str
    intent: str
    expanded_queries: List[str]
    total_found: int
    papers: List[PaperResponse]
    extracted_evidence: List[ClaimEvidence]
    agent_logs: List[AgentStepLog]
    synthesis_summary: str
    medical_disclaimer: str

class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str
    evidence: Optional[List[ClaimEvidence]] = None
    citations: Optional[List[str]] = None

class ChatRequest(BaseModel):
    message: str
    project_id: Optional[str] = None
    paper_ids: Optional[List[str]] = None
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    answer: str
    confidence: str
    citations: List[str]
    evidence_claims: List[ClaimEvidence]
    grounded_in_sources: bool
