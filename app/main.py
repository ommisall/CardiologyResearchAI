from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import select

from app.config import settings
from app.database import init_db, AsyncSessionLocal
from app.models.project import Project
from app.models.paper import Paper
from app.services.pubmed import CURATED_CARDIOLOGY_STUDIES
from app.services.vector_store import vector_store

from app.routers.auth import router as auth_router
from app.routers.research import router as research_router
from app.routers.papers import router as papers_router
from app.routers.projects import router as projects_router
from app.routers.analytics import router as analytics_router
from app.routers.settings import router as settings_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database Tables
    await init_db()
    
    # Seed default demonstration project & papers if database is empty
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Project))
        if not result.scalars().first():
            demo_project = Project(
                id="default-project-1",
                title="Deep Learning in ECG & Arrhythmia Detection",
                description="Investigation of 1D-CNNs, ResNets, and Attention Transformers for clinical electrocardiography classification."
            )
            session.add(demo_project)

            for study in CURATED_CARDIOLOGY_STUDIES:
                db_paper = Paper(
                    id=f"pubmed_{study['pmid']}",
                    pmid=study["pmid"],
                    doi=study["doi"],
                    title=study["title"],
                    authors=study["authors"],
                    journal=study["journal"],
                    publication_date=study["publication_date"],
                    publication_year=study["publication_year"],
                    abstract=study["abstract"],
                    url=study["url"],
                    source="pubmed",
                    citation_count=study["citation_count"],
                    study_type=study.get("study_type"),
                    dataset_name=study.get("dataset_name"),
                    sample_size=study.get("sample_size"),
                    model_architecture=study.get("model_architecture"),
                    evaluation_metrics=study.get("evaluation_metrics"),
                    results_summary=study.get("results_summary"),
                    limitations=study.get("limitations"),
                    conclusion=study.get("conclusion")
                )
                session.add(db_paper)
                
                # Seed vector store chunks
                vector_store.add_chunks([{
                    "chunk_id": f"chk_{study['pmid']}_seed",
                    "page_number": 1,
                    "section": "Abstract",
                    "text": f"{study['title']}. {study['abstract']}"
                }], paper_id=db_paper.id, paper_title=study["title"])

            await session.commit()
            
    yield
    # Shutdown

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Agentic AI Research Assistant for Cardiology — Multi-Agent RAG Literature Discovery & Synthesis",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth_router)
app.include_router(research_router)
app.include_router(papers_router)
app.include_router(projects_router)
app.include_router(analytics_router)
app.include_router(settings_router)

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "llm_provider": settings.DEFAULT_LLM_PROVIDER,
        "medical_disclaimer": "Intended for research and educational purposes only."
    }

# Static Files & SPA Frontend
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # If file exists in static folder directly, serve it
    file_path = STATIC_DIR / full_path
    if full_path and file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    # Otherwise fallback to index.html for SPA client-side routing
    return FileResponse(STATIC_DIR / "index.html")
