import logging
import json
from typing import Dict, Any, List
import os
import time
import hashlib
from pathlib import Path
from tenacity import retry, wait_exponential, stop_after_attempt
from research_os.config import settings

logger = logging.getLogger("research.tools.literature_retrieval")

# Rate limiting for Semantic Scholar
_S2_LAST_CALL = 0.0


def _get_cache_path(query: str, source: str) -> Path:
    from research_os.utils.common import find_project_root
    q_hash = hashlib.md5(query.encode()).hexdigest()
    root = find_project_root()
    return root / ".os_state" / "cache" / f"{source}_{q_hash}.json"


def _read_cache(query: str, source: str) -> List[Dict[str, Any]]:
    path = _get_cache_path(query, source)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return None


def _write_cache(query: str, source: str, data: List[Dict[str, Any]]):
    path = _get_cache_path(query, source)
    if not path.parent.parent.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def search_semantic_scholar(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    global _S2_LAST_CALL
    cached = _read_cache(query, "semantic_scholar")
    if cached is not None:
        return cached[:limit]

    try:
        import urllib.request
        import urllib.parse

        # Rate limit handling
        now = time.time()
        elapsed = now - _S2_LAST_CALL
        # 1 req/s without key, 10 req/s with key (0.1s)
        api_key = getattr(settings, "S2_API_KEY", None)
        min_interval = 0.1 if api_key else 1.1
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        _S2_LAST_CALL = time.time()

        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={urllib.parse.quote(query)}&limit={limit}&fields=title,authors,year,url,externalIds"
        headers = {}
        if api_key:
            headers["x-api-key"] = api_key

        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req).read()
        data = json.loads(response)

        results = []
        for item in data.get("data", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "authors": [a.get("name", "") for a in item.get("authors", [])],
                    "year": item.get("year", ""),
                    "url": item.get("url", ""),
                    "doi": item.get("externalIds", {}).get("DOI", ""),
                }
            )

        _write_cache(query, "semantic_scholar", results)
        return results
    except Exception as e:
        logger.error(f"Semantic Scholar search failed: {e}")
        return []


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def search_crossref(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        from habanero import Crossref

        cr = Crossref()
        result = cr.works(query=query, limit=limit)
        items = result.get("message", {}).get("items", [])
        return [
            {
                "title": item.get("title", [""])[0],
                "authors": [a.get("family", "") for a in item.get("author", [])],
                "year": item.get("issued", {}).get("date-parts", [[None]])[0][0],
                "url": item.get("URL", ""),
                "doi": item.get("DOI", ""),
            }
            for item in items
        ]
    except Exception as e:
        logger.error(f"Crossref search failed: {e}")
        return []


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def search_pubmed(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        from metapub import PubMedFetcher

        if settings.NCBI_API_KEY:
            os.environ["NCBI_API_KEY"] = settings.NCBI_API_KEY
        fetch = PubMedFetcher()
        pmids = fetch.pmids_for_query(query, retmax=limit)

        if not pmids:
            # Fallback/MeSH expansion hint
            logger.warning("No PubMed results. Suggesting broader terms.")
            # For a real MeSH expansion, we could query eutils esearch with terms, but simple fallback:
            # If query has AND, try replacing with OR, or warn user.
            raise Exception(
                "No results found. Suggestion: Broaden your search terms, remove quotes, or use general MeSH terms."
            )

        results = []
        for pmid in pmids:
            try:
                article = fetch.article_by_pmid(pmid)
                results.append(
                    {
                        "title": article.title,
                        "authors": article.authors,
                        "year": article.year,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "doi": article.doi,
                    }
                )
            except Exception:
                continue
        return results
    except Exception as e:
        logger.error(f"PubMed search failed: {e}")
        return []


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def search_arxiv(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    # Simple arxiv search via urllib
    import urllib.request
    import xml.etree.ElementTree as ET

    try:
        url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&max_results={limit}"
        response = urllib.request.urlopen(url).read()
        root = ET.fromstring(response)
        ns = {"arxiv": "http://www.w3.org/2005/Atom"}
        results = []
        for entry in root.findall("arxiv:entry", ns):
            results.append(
                {
                    "title": entry.find("arxiv:title", ns).text.strip(),
                    "authors": [
                        a.find("arxiv:name", ns).text
                        for a in entry.findall("arxiv:author", ns)
                    ],
                    "year": entry.find("arxiv:published", ns).text[:4],
                    "url": entry.find("arxiv:id", ns).text,
                    "doi": "",
                }
            )
        return results
    except Exception as e:
        logger.error(f"Arxiv search failed: {e}")
        return []


def retrieve_literature(
    query: str, source: str = "crossref", limit: int = 5
) -> Dict[str, Any]:
    """Retrieve literature from live sources."""
    limit = min(limit, 5)  # Enforce max 5
    try:
        results = []
        if source == "crossref":
            results = search_crossref(query, limit)
        elif source == "pubmed":
            try:
                results = search_pubmed(query, limit)
            except Exception as e:
                logger.warning(f"PubMed failed, falling back to Crossref: {e}")
                results = search_crossref(query, limit)
                source = "crossref (fallback)"
        elif source == "arxiv":
            results = search_arxiv(query, limit)
        elif source == "semantic_scholar":
            results = search_semantic_scholar(query, limit)
        else:
            results = search_crossref(query, limit)

        payload = {
            "status": "success",
            "source": source,
            "query": query,
            "results": results,
        }

        # Token truncation
        payload_str = json.dumps(payload)
        if len(payload_str) > 15000:
            payload["results"] = payload["results"][:2]
            payload["warning"] = (
                "[Data truncated. Narrow your search terms to see more specific results.]"
            )

        return payload
    except Exception as e:
        logger.error(f"Retrieve literature failed: {e}")
        return {
            "status": "error",
            "details": str(e),
            "suggestion": "Try reducing the date range or narrowing the query.",
        }
