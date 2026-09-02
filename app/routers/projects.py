from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from app.database import get_db
from app.models.project import Project, ProjectNote
from app.models.paper import Paper, SavedPaper
from app.schemas.project import ProjectCreate, ProjectResponse, NoteCreate, NoteResponse
from app.schemas.paper import SavedPaperCreate, SavedPaperResponse
from app.auth.dependencies import get_current_user_optional

router = APIRouter(prefix="/api/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
async def get_projects(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user_optional)
):
    stmt = select(Project)
    if user:
        stmt = stmt.where(Project.user_id == user.id)
    stmt = stmt.order_by(Project.created_at.desc())
    result = await db.execute(stmt)
    projects = result.scalars().all()
    
    # Enrich with count of saved papers
    out = []
    for prj in projects:
        sp_res = await db.execute(select(SavedPaper).where(SavedPaper.project_id == prj.id))
        count = len(sp_res.scalars().all())
        out.append(ProjectResponse(
            id=prj.id,
            user_id=prj.user_id,
            title=prj.title,
            description=prj.description,
            created_at=prj.created_at,
            updated_at=prj.updated_at,
            saved_papers_count=count,
            reports_count=1
        ))
    return out

@router.post("", response_model=ProjectResponse)
async def create_project(
    req: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user_optional)
):
    project = Project(
        user_id=user.id if user else None,
        title=req.title,
        description=req.description
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectResponse(
        id=project.id,
        user_id=project.user_id,
        title=project.title,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
        saved_papers_count=0,
        reports_count=0
    )

@router.get("/{project_id}/saved-papers", response_model=List[SavedPaperResponse])
async def get_saved_papers(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SavedPaper).where(SavedPaper.project_id == project_id))
    saved_items = result.scalars().all()
    out = []
    for item in saved_items:
        p_res = await db.execute(select(Paper).where(Paper.id == item.paper_id))
        p = p_res.scalars().first()
        out.append(SavedPaperResponse(
            id=item.id,
            user_id=item.user_id,
            project_id=item.project_id,
            paper_id=item.paper_id,
            notes=item.notes,
            tags=item.tags,
            saved_at=item.saved_at,
            paper=p
        ))
    return out

@router.post("/{project_id}/save-paper", response_model=SavedPaperResponse)
async def save_paper_to_project(
    project_id: str,
    req: SavedPaperCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user_optional)
):
    existing = await db.execute(
        select(SavedPaper).where(
            SavedPaper.project_id == project_id,
            SavedPaper.paper_id == req.paper_id
        )
    )
    item = existing.scalars().first()
    if not item:
        item = SavedPaper(
            user_id=user.id if user else None,
            project_id=project_id,
            paper_id=req.paper_id,
            notes=req.notes,
            tags=req.tags
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)

    p_res = await db.execute(select(Paper).where(Paper.id == req.paper_id))
    paper = p_res.scalars().first()

    return SavedPaperResponse(
        id=item.id,
        user_id=item.user_id,
        project_id=item.project_id,
        paper_id=item.paper_id,
        notes=item.notes,
        tags=item.tags,
        saved_at=item.saved_at,
        paper=paper
    )

@router.delete("/{project_id}/saved-papers/{paper_id}")
async def remove_saved_paper(
    project_id: str,
    paper_id: str,
    db: AsyncSession = Depends(get_db)
):
    await db.execute(
        delete(SavedPaper).where(
            SavedPaper.project_id == project_id,
            SavedPaper.paper_id == paper_id
        )
    )
    await db.commit()
    return {"status": "success", "message": "Paper removed from project"}

@router.post("/{project_id}/notes", response_model=NoteResponse)
async def create_note(
    project_id: str,
    req: NoteCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user_optional)
):
    note = ProjectNote(
        project_id=project_id,
        user_id=user.id if user else None,
        title=req.title,
        content=req.content
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note
