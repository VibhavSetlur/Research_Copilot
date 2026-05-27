"""Literature & web search tests — all network calls mocked."""

import json
from unittest.mock import MagicMock, patch

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
