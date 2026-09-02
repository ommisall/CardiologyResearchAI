import asyncio
import logging
from typing import List, Dict, Any
from app.services.pubmed import search_pubmed
from app.services.europe_pmc import search_europe_pmc
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)

class SearchAgent:
    """
    Federates literature retrieval across PubMed, Europe PMC, and local repositories.
    Deduplicates based on DOI / PMID and indexes chunks into the RAG vector store.
    """
    @staticmethod
    async def retrieve(queries: List[str], max_results: int = 6, sources: List[str] = None) -> List[Dict[str, Any]]:
        sources = sources or ["pubmed", "europe_pmc"]
        primary_query = queries[0] if queries else "deep learning cardiology"

        tasks = []
        if "pubmed" in sources:
            tasks.append(search_pubmed(primary_query, max_results=max_results))
        if "europe_pmc" in sources:
            tasks.append(search_europe_pmc(primary_query, max_results=max_results))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        merged_papers: List[Dict[str, Any]] = []
        seen_identifiers = set()

        for res in results:
            if isinstance(res, list):
                for paper in res:
                    identifier = paper.get("doi") or paper.get("pmid") or paper.get("title")
                    if identifier and identifier not in seen_identifiers:
                        seen_identifiers.add(identifier)
                        merged_papers.append(paper)
                        
                        # Index paper abstract into vector store for RAG
                        if paper.get("abstract"):
                            abstract_chunks = [{
                                "chunk_id": f"{paper['id']}_abs",
                                "page_number": 1,
                                "section": "Abstract",
                                "text": f"{paper['title']}. {paper['abstract']}"
                            }]
                            vector_store.add_chunks(abstract_chunks, paper["id"], paper["title"])

        return merged_papers[:max_results]
