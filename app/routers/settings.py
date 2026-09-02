from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.config import settings

router = APIRouter(prefix="/api/settings", tags=["Settings"])

class SettingsUpdate(BaseModel):
    default_provider: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    ollama_base_url: Optional[str] = None

@router.get("")
async def get_settings():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "default_provider": settings.DEFAULT_LLM_PROVIDER,
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_openai_key": bool(settings.OPENAI_API_KEY),
        "has_groq_key": bool(settings.GROQ_API_KEY),
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "supported_providers": ["heuristic", "gemini", "openai", "groq", "ollama", "anthropic"],
        "medical_disclaimer_enabled": True
    }

@router.post("")
async def update_settings(req: SettingsUpdate):
    if req.default_provider:
        settings.DEFAULT_LLM_PROVIDER = req.default_provider
    if req.gemini_api_key is not None:
        settings.GEMINI_API_KEY = req.gemini_api_key
    if req.openai_api_key is not None:
        settings.OPENAI_API_KEY = req.openai_api_key
    if req.groq_api_key is not None:
        settings.GROQ_API_KEY = req.groq_api_key
    if req.ollama_base_url:
        settings.OLLAMA_BASE_URL = req.ollama_base_url

    return {
        "status": "success",
        "message": "Settings updated successfully",
        "default_provider": settings.DEFAULT_LLM_PROVIDER,
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_openai_key": bool(settings.OPENAI_API_KEY),
        "has_groq_key": bool(settings.GROQ_API_KEY)
    }
