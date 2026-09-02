import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from app.database import Base

class ResearchQuery(Base):
    __tablename__ = "research_queries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), index=True, nullable=True)
    project_id = Column(String(36), ForeignKey("projects.id"), index=True, nullable=True)
    query_text = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)
    sub_queries = Column(Text, nullable=True)  # JSON array string
    filters = Column(Text, nullable=True)      # JSON string
    results_count = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
