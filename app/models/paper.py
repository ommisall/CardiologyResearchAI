import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Integer
from app.database import Base

class Paper(Base):
    __tablename__ = "papers"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    pmid = Column(String(50), index=True, nullable=True)
    doi = Column(String(150), index=True, nullable=True)
    title = Column(Text, nullable=False)
    authors = Column(Text, nullable=True)  # JSON or comma-separated
    journal = Column(String(255), nullable=True)
    publication_date = Column(String(50), nullable=True)
    publication_year = Column(Integer, nullable=True)
    abstract = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    source = Column(String(50), default="pubmed")  # pubmed, europe_pmc, semantic_scholar, upload
    citation_count = Column(Integer, default=0)
    
    # RAG / PDF ingestion info
    is_uploaded_pdf = Column(Boolean, default=False)
    file_path = Column(String(500), nullable=True)
    
    # Study Elements extracted by Analysis Agent
    study_type = Column(String(100), nullable=True)
    dataset_name = Column(String(255), nullable=True)
    sample_size = Column(String(100), nullable=True)
    model_architecture = Column(String(200), nullable=True)
    evaluation_metrics = Column(Text, nullable=True)
    results_summary = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    conclusion = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class SavedPaper(Base):
    __tablename__ = "saved_papers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), index=True, nullable=True)
    project_id = Column(String(36), ForeignKey("projects.id"), index=True, nullable=True)
    paper_id = Column(String(64), ForeignKey("papers.id"), index=True, nullable=False)
    notes = Column(Text, nullable=True)
    tags = Column(String(255), nullable=True)
    saved_at = Column(DateTime, default=datetime.utcnow)
