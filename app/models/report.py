import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from app.database import Base

class ResearchReport(Base):
    __tablename__ = "research_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), index=True, nullable=True)
    project_id = Column(String(36), ForeignKey("projects.id"), index=True, nullable=True)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), default="literature_review")  # literature_review, comparison, research_gaps
    content = Column(Text, nullable=False)
    paper_ids = Column(Text, nullable=True)  # JSON array string
    citation_format = Column(String(20), default="APA")
    created_at = Column(DateTime, default=datetime.utcnow)
