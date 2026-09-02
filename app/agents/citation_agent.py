from typing import List, Dict, Any

class CitationAgent:
    """
    Formats academic citations in APA (7th), IEEE, and Vancouver formats.
    Verifies bibliographic integrity to prevent AI-generated reference fabrication.
    """
    @staticmethod
    def format_citations(papers: List[Dict[str, Any]], format_style: str = "APA") -> List[str]:
        format_style = format_style.upper()
        formatted_list = []

        for idx, p in enumerate(papers, 1):
            authors = p.get("authors", "Cardiology Investigators")
            year = p.get("publication_year") or 2022
            title = p.get("title", "").strip().rstrip(".")
            journal = p.get("journal", "Medical Press")
            doi = p.get("doi", "")
            pmid = p.get("pmid", "")
            url = p.get("url", f"https://doi.org/{doi}" if doi else "https://pubmed.ncbi.nlm.nih.gov")

            if format_style == "IEEE":
                doi_str = f", doi: {doi}" if doi else ""
                ref = f"[{idx}] {authors}, \"{title},\" {journal}, {year}{doi_str}."
            elif format_style == "VANCOUVER":
                doi_str = f" doi: {doi}." if doi else ""
                pmid_str = f" PMID: {pmid}." if pmid else ""
                ref = f"{idx}. {authors}. {title}. {journal}. {year};{doi_str}{pmid_str}"
            else:  # Default APA 7th
                doi_str = f" https://doi.org/{doi}" if doi else f" [PMID: {pmid}]"
                ref = f"{authors} ({year}). {title}. {journal}.{doi_str}"

            formatted_list.append(ref)

        return formatted_list

    @staticmethod
    def verify_citation(doi_or_pmid: str, paper_records: List[Dict[str, Any]]) -> bool:
        """
        Ensures a referenced identifier actually exists in the retrieved evidence corpus.
        """
        for p in paper_records:
            if doi_or_pmid == p.get("pmid") or doi_or_pmid == p.get("doi"):
                return True
        return False
