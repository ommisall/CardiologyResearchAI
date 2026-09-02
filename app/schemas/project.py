from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    user_id: Optional[str]
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    saved_papers_count: int = 0
    reports_count: int = 0

    class Config:
        from_attributes = True

class NoteCreate(BaseModel):
    title: Optional[str] = "Untitled Note"
    content: str

class NoteResponse(BaseModel):
    id: str
    project_id: str
    title: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
