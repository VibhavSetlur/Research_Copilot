"""Literature search adapters — one function per provider, returning a unified dict."""

from __future__ import annotations

from typing import Any

from research_os.tools.actions.literature_retrieval import retrieve_literature


def search_semantic_scholar(query: str, limit: int = 5) -> dict[str, Any]:
    return retrieve_literature(query, source="semantic_scholar", limit=limit)


def search_crossref(query: str, limit: int = 5) -> dict[str, Any]:
    return retrieve_literature(query, source="crossref", limit=limit)


def search_pubmed(query: str, limit: int = 5) -> dict[str, Any]:
    return retrieve_literature(query, source="pubmed", limit=limit)


def search_arxiv(query: str, limit: int = 5) -> dict[str, Any]:
    """Search arXiv (preprints) via its public API — no key required."""
    import urllib.parse
    import urllib.request
    import xml.etree.ElementTree as ET

    base = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": limit,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    url = f"{base}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return {"query": query, "source": "arxiv", "count": 0, "results": [], "warning": str(e)}

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(body)
    except ET.ParseError as e:
        return {"query": query, "source": "arxiv", "count": 0, "results": [], "warning": f"XML parse error: {e}"}

    results = []
    for entry in root.findall("atom:entry", ns):
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
        summary = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
        link = entry.findtext("atom:id", default="", namespaces=ns) or ""
        published = entry.findtext("atom:published", default="", namespaces=ns) or ""
        authors = [
            (a.findtext("atom:name", default="", namespaces=ns) or "")
            for a in entry.findall("atom:author", ns)
        ]
        results.append(
            {
                "title": title,
                "url": link,
                "published": published,
                "authors": authors,
                "description": summary[:500],
            }
        )

    return {
        "query": query,
        "source": "arxiv",
        "count": len(results),
        "results": results,
    }
