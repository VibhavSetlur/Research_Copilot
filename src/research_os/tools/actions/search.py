"""Back-compat shim — moved into search/search.py."""

from research_os.tools.actions.search.search import (  # noqa: F401
    retrieve_literature,
    scrape_web,
    search_arxiv,
    search_crossref,
    search_pubmed,
    search_semantic_scholar,
    search_web,
)
