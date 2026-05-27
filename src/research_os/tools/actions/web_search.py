"""Web search & scraping — Firecrawl (preferred), SerpAPI (fallback)."""

from __future__ import annotations

import json
import logging
import os
import urllib.parse
import urllib.request
from typing import Any

logger = logging.getLogger("research_os.tools.web_search")


def _log_error(message: str) -> None:
    try:
        from research_os.project_ops import now_iso
        from research_os.utils.common import find_project_root

        root = find_project_root()
        if not (root / ".os_state").exists():
            return
        log_path = root / "workspace" / "logs" / "errors.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{now_iso()}] {message}\n")
    except Exception:
        pass


def _firecrawl_key() -> str | None:
    return os.environ.get("FIRECRAWL_API_KEY") or os.environ.get("FIRECRAWL")


def _serpapi_key() -> str | None:
    return os.environ.get("SERPAPI_API_KEY") or os.environ.get("SERPAPI")


def search_web(query: str, limit: int = 5) -> dict[str, Any]:
    """Search the web. Firecrawl first; SerpAPI fallback; clear warning when neither is configured."""
    fc = _firecrawl_key()
    serpapi = _serpapi_key()

    if fc:
        try:
            from firecrawl import FirecrawlApp  # type: ignore

            app = FirecrawlApp(api_key=fc)
            response = app.search(query)
            raw = response.get("data", []) if isinstance(response, dict) else []
            results = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "description": r.get("description", "") or r.get("snippet", ""),
                }
                for r in raw[:limit]
            ]
            return {
                "query": query,
                "source": "firecrawl",
                "count": len(results),
                "results": results,
            }
        except Exception as e:
            _log_error(f"Firecrawl search failed, trying SerpAPI: {e}")

    if serpapi:
        try:
            url = (
                "https://serpapi.com/search?engine=google"
                f"&q={urllib.parse.quote(query)}&api_key={serpapi}"
            )
            with urllib.request.urlopen(url, timeout=15) as resp:
                data = json.loads(resp.read())
            organic = data.get("organic_results", [])[:limit]
            results = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("link", ""),
                    "description": r.get("snippet", ""),
                }
                for r in organic
            ]
            return {
                "query": query,
                "source": "serpapi",
                "count": len(results),
                "results": results,
            }
        except Exception as e:
            _log_error(f"SerpAPI search failed: {e}")

    return {
        "query": query,
        "source": "web",
        "count": 0,
        "results": [],
        "warning": (
            "No web-search provider configured. Add 'firecrawl' or 'serpapi' to "
            "inputs/researcher_config.yaml api_keys."
        ),
    }


def scrape_web(url: str) -> dict[str, Any]:
    """Scrape a webpage to markdown. Firecrawl preferred, trafilatura fallback."""
    fc = _firecrawl_key()
    if fc:
        try:
            from firecrawl import FirecrawlApp  # type: ignore

            app = FirecrawlApp(api_key=fc)
            r = app.scrape_url(url, params={"formats": ["markdown"]})
            content = r.get("markdown") if isinstance(r, dict) else None
            if content:
                return {"url": url, "source": "firecrawl", "content": content}
        except Exception as e:
            _log_error(f"Firecrawl scrape failed: {e}")

    try:
        import trafilatura  # type: ignore

        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            content = trafilatura.extract(downloaded) or ""
            return {"url": url, "source": "trafilatura", "content": content}
    except Exception as e:
        _log_error(f"trafilatura scrape failed: {e}")

    return {
        "url": url,
        "content": "",
        "warning": (
            "No scraper available — install trafilatura or set firecrawl api key."
        ),
    }
