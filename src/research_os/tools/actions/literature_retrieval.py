"""Live literature retrieval — Crossref, Semantic Scholar, PubMed, arXiv.

Every call is cached in ``.os_state/cache/`` to avoid duplicated API hits.
Falls back gracefully when an API key is missing or a service is unavailable.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

logger = logging.getLogger("research_os.tools.literature_retrieval")


def _read_setting(name: str) -> str | None:
    """Read a credential first from env, then from research_os.config.settings."""
    val = os.environ.get(name)
    if val:
        return val
    try:
        from research_os.config import settings

        return getattr(settings, name, None)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------


def _cache_path(query: str, source: str) -> Path | None:
    try:
        from research_os.utils.common import find_project_root

        root = find_project_root()
    except Exception:
        return None
    h = hashlib.md5(f"{source}::{query}".encode()).hexdigest()
    return root / ".os_state" / "cache" / f"{source}_{h}.json"


def _read_cache(query: str, source: str) -> list[dict[str, Any]] | None:
    p = _cache_path(query, source)
    if p and p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return None
    return None


def _write_cache(query: str, source: str, data: list[dict[str, Any]]) -> None:
    p = _cache_path(query, source)
    if not p:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        p.write_text(json.dumps(data))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------


_S2_LAST_CALL = 0.0


def search_semantic_scholar(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search Semantic Scholar Graph API."""
    global _S2_LAST_CALL
    cached = _read_cache(query, "semantic_scholar")
    if cached is not None:
        return cached[:limit]

    api_key = _read_setting("SEMANTIC_SCHOLAR_API_KEY") or _read_setting("S2_API_KEY")
    min_interval = 0.11 if api_key else 1.1
    elapsed = time.time() - _S2_LAST_CALL
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    _S2_LAST_CALL = time.time()

    url = (
        "https://api.semanticscholar.org/graph/v1/paper/search"
        f"?query={urllib.parse.quote(query)}&limit={limit}"
        "&fields=title,authors,year,url,externalIds,abstract"
    )
    headers = {"User-Agent": "Research-OS/1.0"}
    if api_key:
        headers["x-api-key"] = api_key
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        logger.warning(f"Semantic Scholar search failed: {e}")
        return []

    results = []
    for item in data.get("data", []) or []:
        results.append(
            {
                "title": item.get("title", ""),
                "authors": [a.get("name", "") for a in item.get("authors", []) or []],
                "year": item.get("year"),
                "url": item.get("url", ""),
                "doi": (item.get("externalIds") or {}).get("DOI", ""),
                "abstract": item.get("abstract", ""),
            }
        )
    _write_cache(query, "semantic_scholar", results)
    return results


def search_crossref(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search Crossref via REST API (no key required)."""
    cached = _read_cache(query, "crossref")
    if cached is not None:
        return cached[:limit]

    url = (
        "https://api.crossref.org/works"
        f"?query={urllib.parse.quote(query)}&rows={limit}"
    )
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "Research-OS/1.0"}),
            timeout=15,
        ) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        logger.warning(f"Crossref search failed: {e}")
        return []

    items = (data.get("message") or {}).get("items", []) or []
    results = []
    for item in items:
        title_list = item.get("title") or [""]
        title = title_list[0] if title_list else ""
        date = (item.get("issued") or {}).get("date-parts") or [[None]]
        year = date[0][0] if date and date[0] else None
        results.append(
            {
                "title": title,
                "authors": [
                    f"{a.get('given', '').strip()} {a.get('family', '').strip()}".strip()
                    for a in item.get("author", []) or []
                ],
                "year": year,
                "url": item.get("URL", ""),
                "doi": item.get("DOI", ""),
                "abstract": (item.get("abstract") or "")[:1000],
            }
        )
    _write_cache(query, "crossref", results)
    return results


def search_pubmed(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search PubMed via NCBI eutils (no library dependency)."""
    cached = _read_cache(query, "pubmed")
    if cached is not None:
        return cached[:limit]

    api_key = _read_setting("NCBI_API_KEY")
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    esearch = (
        f"{base}/esearch.fcgi?db=pubmed&retmode=json"
        f"&retmax={limit}&term={urllib.parse.quote(query)}"
    )
    if api_key:
        esearch += f"&api_key={api_key}"
    try:
        with urllib.request.urlopen(esearch, timeout=15) as resp:
            ids = (json.loads(resp.read()).get("esearchresult") or {}).get("idlist", []) or []
    except Exception as e:
        logger.warning(f"PubMed esearch failed: {e}")
        return []

    if not ids:
        return []

    esummary = (
        f"{base}/esummary.fcgi?db=pubmed&retmode=json&id={','.join(ids)}"
    )
    if api_key:
        esummary += f"&api_key={api_key}"
    try:
        with urllib.request.urlopen(esummary, timeout=15) as resp:
            summary = (json.loads(resp.read()).get("result") or {})
    except Exception as e:
        logger.warning(f"PubMed esummary failed: {e}")
        return []

    results = []
    for pmid in ids:
        item = summary.get(pmid)
        if not item:
            continue
        results.append(
            {
                "title": item.get("title", ""),
                "authors": [
                    a.get("name", "") for a in item.get("authors", []) or []
                ],
                "year": (item.get("pubdate") or "")[:4],
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "doi": next(
                    (
                        a.get("value")
                        for a in item.get("articleids", []) or []
                        if a.get("idtype") == "doi"
                    ),
                    "",
                ),
            }
        )
    _write_cache(query, "pubmed", results)
    return results


def search_arxiv(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search arXiv (no key required)."""
    cached = _read_cache(query, "arxiv")
    if cached is not None:
        return cached[:limit]
    url = (
        "http://export.arxiv.org/api/query"
        f"?search_query=all:{urllib.parse.quote(query)}&max_results={limit}"
        "&sortBy=relevance&sortOrder=descending"
    )
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            body = resp.read()
    except Exception as e:
        logger.warning(f"arXiv search failed: {e}")
        return []

    try:
        root = ET.fromstring(body)
    except ET.ParseError as e:
        logger.warning(f"arXiv parse failed: {e}")
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
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
                "authors": authors,
                "year": published[:4],
                "url": link,
                "doi": "",
                "abstract": summary[:1000],
            }
        )
    _write_cache(query, "arxiv", results)
    return results


# ---------------------------------------------------------------------------
# Unified retrieval entrypoint
# ---------------------------------------------------------------------------


def retrieve_literature(
    query: str, source: str = "crossref", limit: int = 5
) -> dict[str, Any]:
    """Retrieve literature from one of: crossref | pubmed | arxiv | semantic_scholar."""
    limit = max(1, min(limit, 10))
    source = (source or "crossref").lower()

    try:
        if source == "semantic_scholar":
            results = search_semantic_scholar(query, limit)
        elif source == "pubmed":
            results = search_pubmed(query, limit)
            if not results:
                results = search_crossref(query, limit)
                source = "crossref (pubmed fallback)"
        elif source == "arxiv":
            results = search_arxiv(query, limit)
        else:
            results = search_crossref(query, limit)

        payload: dict[str, Any] = {
            "status": "success",
            "source": source,
            "query": query,
            "count": len(results),
            "results": results,
        }

        if len(json.dumps(payload)) > 15000:
            payload["results"] = payload["results"][:3]
            payload["warning"] = "Truncated; narrow the query for more specific results."

        return payload
    except Exception as e:
        logger.exception("retrieve_literature failed")
        return {
            "status": "error",
            "source": source,
            "query": query,
            "details": str(e),
        }
