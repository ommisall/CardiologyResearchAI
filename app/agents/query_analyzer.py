import re
import json
from typing import Dict, Any, List
from app.services.llm_provider import LLMProvider

class QueryAnalyzerAgent:
    """
    Deconstructs natural-language cardiology questions into structured research intents
    and generates targeted Boolean / MeSH search queries for scientific databases.
    """
    @staticmethod
    async def analyze(user_query: str) -> Dict[str, Any]:
        clean_q = user_query.strip()
        
        # Clinical cardiology concepts detection
        keywords = []
        if re.search(r'\b(ecg|ekg|electrocardiogram)\b', clean_q, re.I):
            keywords.append("electrocardiography")
        if re.search(r'\b(arrhythmia|fibrillation|afib|tachycardia)\b', clean_q, re.I):
            keywords.append("cardiac arrhythmia")
        if re.search(r'\b(cnn|convolutional|resnet)\b', clean_q, re.I):
            keywords.append("convolutional neural network")
        if re.search(r'\b(transformer|attention|bert)\b', clean_q, re.I):
            keywords.append("transformer neural network")
        if re.search(r'\b(heart failure|ventricular|ejection fraction)\b', clean_q, re.I):
            keywords.append("ventricular dysfunction")
        if re.search(r'\b(wearable|smartwatch|photoplethysmography|ppg)\b', clean_q, re.I):
            keywords.append("wearable health technology")

        if not keywords:
            keywords = ["cardiology", "artificial intelligence", "deep learning"]

        # Formulate search queries
        expanded_queries = [
            f"{clean_q} cardiology",
            f"deep learning {' '.join(keywords[:2])}",
            f"{' '.join(keywords)} machine learning",
            f"artificial intelligence {clean_q}"
        ]

        # Deduplicate and trim
        dedup_queries = list(dict.fromkeys(expanded_queries))[:4]

        return {
            "original_query": clean_q,
            "intent": f"Systematic investigation of {clean_q}",
            "keywords": keywords,
            "expanded_queries": dedup_queries
        }
