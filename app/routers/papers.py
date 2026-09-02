import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.database import get_db
from app.models.paper import Paper
from app.schemas.paper import PaperResponse
from app.schemas.report import CompareRequest, ComparisonResult
from app.agents.comparison_agent import ComparisonAgent
from app.agents.analysis_agent import PaperAnalysisAgent
from app.services.pdf_parser import extract_pdf_content
from app.services.vector_store import vector_store
from app.config import settings

router = APIRouter(prefix="/api/papers", tags=["Papers"])

@router.get("", response_model=List[PaperResponse])
async def list_papers(
    q: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Paper)
    if q:
        stmt = stmt.where(Paper.title.ilike(f"%{q}%"))
    stmt = stmt.order_by(Paper.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalars().first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper

@router.post("/upload", response_model=PaperResponse)
async def upload_paper_pdf(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and parse PDF research paper:
    1. Saves PDF file to disk
    2. Extracts clean text and structured sections via pypdf
    3. Generates overlapping chunks and indexes into VectorStore
    4. Extracts study elements (Dataset, AI Model, Sample Size, Metrics)
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    dest_path = Path(settings.UPLOAD_PATH) / filename

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        parsed = extract_pdf_content(str(dest_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")

    meta = parsed.get("metadata", {})
    paper_title = meta.get("title") or file.filename.replace(".pdf", "").replace("_", " ")
    paper_author = meta.get("author", "Uploaded Paper Author")
    paper_id = f"pdf_{file_id[:8]}"

    # Index chunks into RAG Vector Store
    chunks = parsed.get("chunks", [])
    if chunks:
        vector_store.add_chunks(chunks, paper_id=paper_id, paper_title=paper_title)

    # Extract study parameters from full text
    abstract_text = (parsed["full_text"][:1200] + "...") if len(parsed["full_text"]) > 1200 else parsed["full_text"]
    raw_paper_dict = {
        "id": paper_id,
        "title": paper_title,
        "authors": paper_author,
        "abstract": abstract_text,
        "source": "upload",
        "is_uploaded_pdf": True,
        "file_path": str(dest_path)
    }

    analyzed = PaperAnalysisAgent.analyze_paper(raw_paper_dict)

    db_paper = Paper(
        id=paper_id,
        title=paper_title,
        authors=paper_author,
        journal="User Uploaded PDF",
        publication_date="2024",
        publication_year=2024,
        abstract=abstract_text,
        source="upload",
        is_uploaded_pdf=True,
        file_path=str(dest_path),
        study_type=analyzed.get("study_type", "Uploaded Research Document"),
        dataset_name=analyzed.get("dataset_name"),
        sample_size=analyzed.get("sample_size"),
        model_architecture=analyzed.get("model_architecture"),
        evaluation_metrics=analyzed.get("evaluation_metrics"),
        results_summary=analyzed.get("results_summary"),
        limitations=analyzed.get("limitations"),
        conclusion=analyzed.get("conclusion")
    )
    db.add(db_paper)
    await db.commit()
    await db.refresh(db_paper)

    return db_paper

@router.post("/compare", response_model=ComparisonResult)
async def compare_papers(
    req: CompareRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Compare multiple selected studies across objectives, datasets, models, metrics, and limitations.
    """
    papers_data = []
    for pid in req.paper_ids:
        result = await db.execute(select(Paper).where(Paper.id == pid))
        p = result.scalars().first()
        if p:
            papers_data.append({
                "id": p.id,
                "title": p.title,
                "authors": p.authors,
                "publication_year": p.publication_year,
                "dataset_name": p.dataset_name,
                "sample_size": p.sample_size,
                "model_architecture": p.model_architecture,
                "evaluation_metrics": p.evaluation_metrics,
                "results_summary": p.results_summary,
                "limitations": p.limitations
            })

    # If fewer than 2 papers found, supplement with curated benchmarks
    if len(papers_data) < 2:
        from app.services.pubmed import CURATED_CARDIOLOGY_STUDIES
        papers_data = CURATED_CARDIOLOGY_STUDIES[:3]

    comparison = ComparisonAgent.compare_studies(papers_data)
    return comparison
