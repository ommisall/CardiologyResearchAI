import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pypdf
import logging

logger = logging.getLogger(__name__)

def extract_pdf_content(file_path: str) -> Dict[str, Any]:
    """
    Extract text, pages, and metadata from an uploaded research PDF.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found at {file_path}")

    pages_text: List[Dict[str, Any]] = []
    full_text_list: List[str] = []
    metadata = {}

    try:
        reader = pypdf.PdfReader(str(path))
        doc_info = reader.metadata or {}
        metadata = {
            "title": doc_info.get("/Title") or path.stem.replace("_", " ").title(),
            "author": doc_info.get("/Author") or "Uploaded Author",
            "subject": doc_info.get("/Subject") or "Cardiology Research",
            "page_count": len(reader.pages)
        }

        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            # Clean non-printable / control characters
            text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            pages_text.append({
                "page_number": idx + 1,
                "text": text
            })
            full_text_list.append(text)

    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        raise ValueError(f"Failed to parse PDF document: {str(e)}")

    full_text = "\n\n".join(full_text_list)
    chunks = chunk_text(pages_text)

    return {
        "metadata": metadata,
        "full_text": full_text,
        "page_count": len(pages_text),
        "chunks": chunks
    }

def chunk_text(pages_text: List[Dict[str, Any]], chunk_size: int = 600, overlap: int = 100) -> List[Dict[str, Any]]:
    """
    Creates overlapping semantic text chunks tagged with page numbers and section detection.
    """
    chunks: List[Dict[str, Any]] = []
    chunk_counter = 0

    section_regex = re.compile(
        r'\b(abstract|introduction|background|methods|methodology|dataset|materials|results|discussion|limitations|conclusion|references)\b',
        re.IGNORECASE
    )

    current_section = "General"

    for page_info in pages_text:
        page_num = page_info["page_number"]
        text = page_info["text"]
        if not text:
            continue

        words = text.split(" ")
        step = max(1, chunk_size - overlap)

        for i in range(0, len(words), step):
            chunk_words = words[i:i + chunk_size]
            chunk_str = " ".join(chunk_words).strip()
            if len(chunk_str) < 50:
                continue

            # Detect section from content
            match = section_regex.search(chunk_str[:150])
            if match:
                current_section = match.group(1).title()

            chunk_counter += 1
            chunks.append({
                "chunk_id": f"chk_{page_num}_{chunk_counter}",
                "page_number": page_num,
                "section": current_section,
                "text": chunk_str
            })

    return chunks
