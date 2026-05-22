import pytest
import json
from unittest.mock import patch, MagicMock
from research_os.tools.actions.web_search import search_web
from research_os.tools.actions.literature_retrieval import search_semantic_scholar, search_pubmed

@patch("research_os.tools.actions.web_search.settings")
@patch("research_os.tools.actions.web_search._firecrawl_search")
def test_search_web_success(mock_firecrawl, mock_settings):
    mock_settings.FIRECRAWL_API_KEY = "test_key"
    mock_firecrawl.return_value = {
        "data": [{"title": "Test Title", "url": "http://test.com", "description": "Test Desc"}]
    }
    
    res = search_web("test query", limit=1)
    
    assert res["count"] == 1
    assert res["results"][0]["title"] == "Test Title"
    assert res["source"] == "web"

@patch("research_os.tools.actions.web_search.settings")
@patch("research_os.tools.actions.web_search._firecrawl_search")
@patch("urllib.request.urlopen")
def test_search_web_fallback(mock_urlopen, mock_firecrawl, mock_settings):
    mock_settings.FIRECRAWL_API_KEY = "test_key"
    mock_settings.SERPAPI_API_KEY = "test_serp_key"
    mock_firecrawl.side_effect = Exception("Firecrawl Down")
    
    # Mock serpapi response
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "organic_results": [{"title": "Serp Title", "link": "http://serp.com", "snippet": "Serp Desc"}]
    }).encode("utf-8")
    mock_urlopen.return_value = mock_response
    
    res = search_web("test query", limit=1)
    
    assert res["count"] == 1
    assert res["results"][0]["title"] == "Serp Title"
    assert "fallback" in res["source"]

@patch("urllib.request.urlopen")
def test_search_semantic_scholar_success(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "data": [{"title": "S2 Paper", "authors": [{"name": "Auth"}], "year": 2023, "url": "http://s2.com", "externalIds": {"DOI": "10.123"}}]
    }).encode("utf-8")
    mock_urlopen.return_value = mock_response
    
    res = search_semantic_scholar("test", limit=1)
    
    assert len(res) == 1
    assert res[0]["title"] == "S2 Paper"
