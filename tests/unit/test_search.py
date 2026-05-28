"""Literature & web search tests — all network calls mocked."""

import json
from unittest.mock import patch

from research_os.tools.actions.search.search import (
    search_crossref,
    search_pubmed,
    search_semantic_scholar,
    search_web,
)


@patch("urllib.request.urlopen")
def test_search_semantic_scholar(mock_urlopen):
    body = json.dumps(
        {
            "data": [
                {
                    "title": "S2 Paper",
                    "authors": [{"name": "Auth"}],
                    "year": 2023,
                    "url": "http://s2.com",
                    "externalIds": {"DOI": "10.123"},
                }
            ]
        }
    ).encode()
    mock_urlopen.return_value.__enter__.return_value.read.return_value = body
    res = search_semantic_scholar("test", limit=1)
    assert len(res) == 1
    assert res[0]["title"] == "S2 Paper"


@patch("urllib.request.urlopen")
def test_search_crossref(mock_urlopen):
    body = json.dumps(
        {"message": {"items": [{"title": ["CrossRef Paper"], "DOI": "10.123/abc"}]}}
    ).encode()
    mock_urlopen.return_value.__enter__.return_value.read.return_value = body
    res = search_crossref("test", limit=1)
    assert len(res) == 1
    assert res[0]["title"] == "CrossRef Paper"


@patch("urllib.request.urlopen")
def test_search_pubmed_empty(mock_urlopen):
    body = json.dumps({"esearchresult": {"idlist": []}}).encode()
    mock_urlopen.return_value.__enter__.return_value.read.return_value = body
    res = search_pubmed("xyz", limit=1)
    assert isinstance(res, list)


def test_search_web_no_provider(monkeypatch):
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    res = search_web("q")
    assert res["count"] == 0
    assert "warning" in res


def test_cache_clear_no_cache(tmp_path):
    """cache_clear is a no-op when the cache dir doesn't exist."""
    from research_os.tools.actions.search import cache_clear

    res = cache_clear(tmp_path)
    assert res["status"] == "success"
    assert res["removed"] == 0


def test_cache_clear_removes_entries(tmp_path):
    """cache_clear wipes per-provider entries (or all when source=None)."""
    from research_os.tools.actions.search import cache_clear

    cache_root = tmp_path / ".os_state" / "cache" / "search"
    for provider in ("semantic_scholar", "crossref", "pubmed"):
        d = cache_root / provider
        d.mkdir(parents=True, exist_ok=True)
        (d / "abc.json").write_text('{"results": []}')

    # Clear only one provider.
    res = cache_clear(tmp_path, source="crossref")
    assert res["status"] == "success"
    assert res["removed"] == 1
    assert (cache_root / "semantic_scholar" / "abc.json").exists()
    assert not (cache_root / "crossref" / "abc.json").exists()

    # Clear all remaining.
    res = cache_clear(tmp_path)
    assert res["removed"] == 2


def test_cache_ttl_invalidates_old_entries(tmp_path, monkeypatch):
    """Stale cache entries (older than TTL) are ignored on read."""
    import os
    import time

    from research_os.tools.actions.search.search import _read_cache, _write_cache

    monkeypatch.setenv("RESEARCH_OS_CACHE_TTL_SECONDS", "1")
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".os_state").mkdir(parents=True, exist_ok=True)

    _write_cache("q", "semantic_scholar", [{"title": "T"}])
    # Fresh read works.
    assert _read_cache("q", "semantic_scholar") is not None

    # Age the file out.
    import hashlib
    h = hashlib.md5("semantic_scholar::q".encode()).hexdigest()
    cache_file = tmp_path / ".os_state" / "cache" / "search" / "semantic_scholar" / f"{h}.json"
    os.utime(cache_file, (time.time() - 10, time.time() - 10))
    assert _read_cache("q", "semantic_scholar") is None  # stale
