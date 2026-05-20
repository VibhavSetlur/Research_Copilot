---
skill_id: "literature_zotero_integration"
version: "1.0.0"
category: "literature"
description: "Sync with Zotero/Mendeley libraries, read highlighted notes, and export bibliography.bib back to reference managers"
domain_compatibility: ["all"]
applies_to_phases: ["literature_deep"]
---

# Skill: Zotero & Semantic Scholar Integration

## Purpose

Extend literature search beyond PubMed/arXiv by integrating with the researcher's personal reference manager (Zotero or Mendeley). The agent reads the user's existing library, incorporates their highlights and notes, and outputs a formatted bibliography that syncs back to their reference manager.

## Protocol

### Step 1: Detect Reference Manager

Check for available integrations:
1. **Zotero**: Check for `ZOTERO_USER_ID` and `ZOTERO_API_KEY` environment variables
2. **Zotero local**: Check for Zotero SQLite database at `~/.zotero/zotero/*/zotero.sqlite`
3. **Mendeley**: Check for `MENDELEY_CLIENT_ID` and `MENDELEY_CLIENT_SECRET`
4. **BibTeX file**: Check for `.bib` files in `inputs/papers/`

### Step 2: Zotero API Integration

If Zotero credentials are available:

```python
import requests
from pyzotero import zotero

# Connect to Zotero library
zot = zotero.Zotero(library_id, 'user', api_key)

# Get items from a specific collection (if specified)
items = zot.collection_items(collection_key)

# Or search by tags
items = zot.items(tags='research-copilot')

# Extract metadata
for item in items:
    data = {
        'title': item['data'].get('title', ''),
        'authors': item['data'].get('creators', []),
        'year': item['data'].get('date', '')[:4],
        'doi': item['data'].get('DOI', ''),
        'abstract': item['data'].get('abstractNote', ''),
        'tags': [t['tag'] for t in item['data'].get('tags', [])],
        'notes': [],
        'highlights': [],
    }
    
    # Get notes (user's annotations)
    notes = zot.item_notes(item['key'])
    for note in notes:
        data['notes'].append(note['data'].get('note', ''))
    
    # Get attachments (for PDF extraction if needed)
    attachments = zot.item_children(item['key'])
```

### Step 3: Semantic Scholar API Enhancement

Supplement Zotero items with Semantic Scholar data:

```python
import requests

def enrich_with_semantic_scholar(doi):
    """Get citation count, influential citations, and tldr from Semantic Scholar."""
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
    params = {
        "fields": "title,authors,year,citationCount,influentialCitationCount,tldr,abstract,fieldsOfStudy",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

# For each paper, enrich with:
# - Citation count (impact measure)
# - Influential citation count (quality measure)
# - TLDR (quick summary)
# - Fields of study (relevance check)
```

### Step 4: Process User Highlights and Notes

Extract key insights from user's annotations:

```python
from bs4 import BeautifulSoup

def extract_highlights(note_html):
    """Extract highlighted text and user comments from Zotero notes."""
    soup = BeautifulSoup(note_html, 'html.parser')
    
    highlights = []
    for blockquote in soup.find_all('blockquote'):
        highlight = {
            'text': blockquote.get_text().strip(),
            'comment': '',
        }
        # Get user's comment after the highlight
        next_elem = blockquote.find_next_sibling()
        if next_elem and next_elem.name == 'p':
            highlight['comment'] = next_elem.get_text().strip()
        highlights.append(highlight)
    
    return highlights
```

### Step 5: Build Enhanced Evidence Matrix

Combine Zotero library with search results:

```markdown
| Paper | DOI | Citations | User Rating | Key Finding | Relevance |
|-------|-----|-----------|-------------|-------------|-----------|
| [Title] | doi | N | ⭐⭐⭐⭐ | [From user notes] | High |
```

User ratings derived from:
- Number of highlights (more highlights = more important)
- Presence of user comments (engaged with = important)
- Collection membership (in research collection = relevant)

### Step 6: Generate Enhanced Bibliography

Create `reports/literature/bibliography.bib` with enriched entries:

```bibtex
@article{key,
  title = {Title},
  author = {Author1 and Author2},
  journal = {Journal},
  year = {2024},
  doi = {10.xxxx/xxxxx},
  citation_count = {42},
  influential_citations = {5},
  fields_of_study = {Economics, Econometrics},
  user_highlights = {3},
  user_notes = {Yes},
  relevance_score = {0.85},
  abstract = {Abstract text},
  tldr = {AI-generated summary},
}
```

### Step 7: Sync Back to Zotero (Optional)

If the user wants the bibliography synced back:

```python
def sync_to_zotero(bibliography, collection_name="Research Copilot"):
    """Create a new Zotero collection with the bibliography."""
    # Create collection
    collection = zot.create_collections([{'name': collection_name}])
    collection_key = collection[0]['key']
    
    # Add items
    for entry in bibliography:
        item = {
            'itemType': 'journalArticle',
            'title': entry['title'],
            'creators': entry['authors'],
            'DOI': entry['doi'],
            'date': entry['year'],
            'abstractNote': entry['abstract'],
            'tags': [{'tag': 'research-copilot'}, {'tag': entry['relevance']}],
        }
        zot.create_items([item])
```

## Quality Rules

1. NEVER modify the user's Zotero library without explicit permission
2. ALWAYS preserve the original Zotero data — create new collections, don't modify existing
3. ALWAYS respect API rate limits (Zotero: 100 req/min, Semantic Scholar: 100 req/5min)
4. ALWAYS cache API responses to avoid redundant calls
5. ALWAYS handle missing DOIs gracefully (search by title instead)
6. ALWAYS include user's own notes and highlights in the evidence matrix
7. NEVER share API keys or library data
