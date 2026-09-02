import re
from typing import List, Dict, Any

class RankingAgent:
    """
    Ranks retrieved cardiology papers according to semantic relevance,
    recency of publication, citation counts, and study metadata completeness.
    """
    @staticmethod
    def rank(papers: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        query_words = set(re.findall(r'\w+', query.lower()))
        
        ranked_list = []
        for paper in papers:
            title = paper.get("title", "").lower()
            abstract = paper.get("abstract", "").lower()
            
            # 1. Term overlap score
            title_matches = sum(1 for w in query_words if w in title)
            abs_matches = sum(1 for w in query_words if w in abstract)
            text_score = (title_matches * 3.0) + (abs_matches * 1.0)
            
            # 2. Recency score (2018-2026)
            year = paper.get("publication_year") or 2020
            recency_score = max(0.0, (year - 2018) * 0.5)
            
            # 3. Citation count log-score
            citations = paper.get("citation_count") or 0
            citation_score = min(5.0, (citations / 100.0))
            
            # 4. Metadata richness
            meta_score = 2.0 if paper.get("dataset_name") and paper.get("model_architecture") else 0.0

            total_score = round(text_score + recency_score + citation_score + meta_score, 2)
            
            paper_copy = paper.copy()
            paper_copy["relevance_score"] = total_score
            ranked_list.append(paper_copy)

        ranked_list.sort(key=lambda p: p["relevance_score"], reverse=True)
        return ranked_list
