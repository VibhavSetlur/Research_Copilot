---
skill_id: "parse_papers"
version: "1.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "playwright", "beautifulsoup4"]
depends_on: []
produces: ["inputs/context/paper_summaries/"]
complexity: "intermediate"
---

# Skill: Parse Papers from URLs or PDFs

## Purpose
Extract text, abstracts, and key sections from papers via URLs (using Playwright for JS-rendered pages) or local PDFs, producing structured summaries for the research context.

## When to Use
- User provided URLs to papers in `inputs/context/`
- Papers are behind JS-rendered sites (ScienceDirect, Springer, etc.)
- Need to extract abstracts/findings from paper PDFs
- Building literature context from web sources

## When NOT to Use
- Papers already provided as PDFs in `inputs/papers/`
- Only DOI/bibliographic data needed

## Execution Protocol

### Step 1: Source Discovery
- Scan `inputs/context/` for files containing URLs (`.md`, `.txt`, `.links`)
- Scan `inputs/papers/` for PDF files
- Collect all sources into a list

### Step 2: URL Parsing (Playwright)
For each URL:
- Launch Playwright browser (headless)
- Navigate to URL, wait for page load
- Extract: title, abstract, authors, year, journal, DOI
- If paywalled: extract abstract only (usually visible)
- Save as: `inputs/context/paper_summaries/{sanitized_title}.md`

```python
from playwright.sync_api import sync_playwright

def parse_paper_url(url, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)

        # Extract common paper metadata
        title = page.query_selector("h1, .article-title, #title")
        abstract = page.query_selector(".abstract, #abstract, .summary")

        content = {
            "url": url,
            "title": title.inner_text() if title else "",
            "abstract": abstract.inner_text() if abstract else "",
        }

        # Save summary
        with open(output_path, "w") as f:
            f.write(f"# {content['title']}\n\n")
            f.write(f"**URL**: {url}\n\n")
            f.write(f"## Abstract\n\n{content['abstract']}\n")

        browser.close()
```

### Step 3: PDF Parsing
For each PDF in `inputs/papers/`:
- Extract text using `pypdf` or `pdfplumber`
- Identify: title, abstract, section headers, conclusion
- Save as: `inputs/context/paper_summaries/{filename}.md`

### Step 4: Summary Index
Create `inputs/context/paper_summaries/INDEX.md` listing all parsed papers with:
- Title, source (URL or PDF), abstract, key findings (if extractable)

## Diagnostics

| Check | Pass | Fail → Action |
|-------|------|---------------|
| URL loads | Page loads in 30s | URL may be dead; log and skip |
| Abstract found | Abstract extracted | Page structure unknown; save full text |
| PDF readable | Text extracted | Scanned PDF; needs OCR (skip) |

## Output Specification
- `inputs/context/paper_summaries/`: individual paper summaries
- `inputs/context/paper_summaries/INDEX.md`: index of all parsed papers

## Validation Checks
- [ ] Each source (URL or PDF) produces a summary file
- [ ] Summaries contain at least title and abstract
- [ ] INDEX.md lists all summaries
- [ ] Failed sources logged with reason
