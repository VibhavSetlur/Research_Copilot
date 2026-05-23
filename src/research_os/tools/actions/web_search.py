import logging
import json
from typing import Dict, Any
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
)
from research_os.config import settings
from pathlib import Path
from research_os.project_ops import now_iso

logger = logging.getLogger("research.tools.web_search")


def _log_error(message: str):
    from research_os.utils.common import find_project_root
    try:
        root = find_project_root()
        if not (root / ".os_state").exists():
            return
        log_path = root / "workspace" / "logs" / "errors.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{now_iso()}] {message}\n")
    except Exception:
        pass


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def _firecrawl_search(query: str, limit: int):
    from firecrawl import FirecrawlApp

    app = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY)
    return app.search(query)


def search_web(query: str, limit: int = 5) -> Dict[str, Any]:
    try:
        if not settings.FIRECRAWL_API_KEY:
            logger.warning("Firecrawl API key not set, falling back to stub.")
            return {
                "query": query,
                "source": "web (stub)",
                "count": 0,
                "results": [],
                "warning": "Firecrawl API key not set",
            }

        try:
            response = _firecrawl_search(query, limit)
        except Exception as e:
            _log_error(f"Firecrawl search failed: {e}. Falling back to SerpAPI.")
            # Fallback to SerpAPI if Firecrawl fails
            if getattr(settings, "SERPAPI_API_KEY", None):
                import urllib.request

                url = f"https://serpapi.com/search?engine=google&q={urllib.parse.quote(query)}&api_key={settings.SERPAPI_API_KEY}"
                req = urllib.request.urlopen(url)
                data = json.loads(req.read())
                results = data.get("organic_results", [])[:limit]
                formatted = [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("link", ""),
                        "description": r.get("snippet", ""),
                    }
                    for r in results
                ]
                return {
                    "query": query,
                    "source": "web (serpapi fallback)",
                    "count": len(formatted),
                    "results": formatted,
                }
            else:
                raise e

        results = response.get("data", [])[:limit]
        formatted = []
        for r in results:
            formatted.append(
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "description": r.get("description", ""),
                }
            )
        return {
            "query": query,
            "source": "web",
            "count": len(formatted),
            "results": formatted,
        }
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        _log_error(f"Web search failed: {e}")
        return {
            "query": query,
            "source": "web",
            "count": 0,
            "results": [],
            "warning": str(e),
        }


def scrape_web(url: str) -> Dict[str, Any]:
    try:
        try:
            import trafilatura
        except ImportError:
            trafilatura = None

        from firecrawl import FirecrawlApp

        if settings.FIRECRAWL_API_KEY:
            app = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY)
            scrape_result = app.scrape_url(url, params={"formats": ["markdown"]})
            content = scrape_result.get("markdown", "")
            return {"url": url, "content": content}

        if trafilatura:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                content = trafilatura.extract(downloaded)
                return {"url": url, "content": content}

        return {
            "url": url,
            "content": "",
            "warning": "Firecrawl API key not set and trafilatura fallback failed",
        }
    except Exception as e:
        logger.error(f"Web scrape failed: {e}")
        _log_error(f"Web scrape failed: {e}")
        return {"url": url, "content": "", "warning": str(e)}
