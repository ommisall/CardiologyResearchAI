from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class PaperBase(BaseModel):
    id: str
    pmid: Optional[str] = None
    doi: Optional[str] = None
    title: str
    authors: Optional[str] = None
    journal: Optional[str] = None
    publication_date: Optional[str] = None
    publication_year: Optional[int] = None
    abstract: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = "pubmed"
    citation_count: Optional[int] = 0
    is_uploaded_pdf: Optional[bool] = False

class PaperStudyDetails(BaseModel):
    study_type: Optional[str] = None
    dataset_name: Optional[str] = None
    sample_size: Optional[str] = None
    model_architecture: Optional[str] = None
    evaluation_metrics: Optional[str] = None
    results_summary: Optional[str] = None
    limitations: Optional[str] = None
    conclusion: Optional[str] = None

class PaperResponse(PaperBase, PaperStudyDetails):
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SavedPaperCreate(BaseModel):
    paper_id: str
    project_id: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None

class SavedPaperResponse(BaseModel):
    id: str
    user_id: Optional[str]
    project_id: Optional[str]
    paper_id: str
    notes: Optional[str]
    tags: Optional[str]
    saved_at: datetime
    paper: Optional[PaperResponse] = None

    class Config:
        from_attributes = True
