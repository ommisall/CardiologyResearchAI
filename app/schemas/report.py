from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class CompareRequest(BaseModel):
    paper_ids: Optional[List[str]] = []
    project_id: Optional[str] = None
    custom_metrics: Optional[List[str]] = None

class PaperComparisonRow(BaseModel):
    paper_id: str
    title: str
    authors: str
    year: Optional[int] = None
    objective: str
    dataset: str
    sample_size: str
    method_model: str
    evaluation_metrics: str
    reported_performance: str
    advantages: str
    limitations: str

class ComparisonResult(BaseModel):
    matrix: List[PaperComparisonRow]
    synthesis_analysis: str
    key_takeaways: List[str]

class ResearchGapItem(BaseModel):
    category: str  # Dataset limitations, Sample size, Lack of external validation, Interpretability, Demographic bias
    gap_title: str
    description: str
    affected_papers: List[str]
    potential_future_direction: str
    synthesis_badge: str = "AI-Generated Synthesis (Cross-Study Inference)"

class ResearchGapsResult(BaseModel):
    topic: str
    analyzed_paper_count: int
    gaps: List[ResearchGapItem]
    overall_recommendation: str

class LiteratureReviewRequest(BaseModel):
    topic: str
    paper_ids: Optional[List[str]] = []
    project_id: Optional[str] = None
    citation_format: str = "APA"  # APA, IEEE, Vancouver

class LiteratureReviewSection(BaseModel):
    section_number: int
    title: str
    content: str

class LiteratureReviewResult(BaseModel):
    title: str
    abstract: str
    sections: List[LiteratureReviewSection]
    references: List[str]
    citation_format: str
    full_markdown: str

class ReportSaveRequest(BaseModel):
    project_id: Optional[str] = None
    title: str
    report_type: str
    content: str
    paper_ids: Optional[List[str]] = []
    citation_format: Optional[str] = "APA"
