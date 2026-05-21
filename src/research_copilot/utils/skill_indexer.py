#!/usr/bin/env python3
"""
Research Copilot Skill Indexer

Parses all Markdown files in the skills directory and generates a lightweight
JSON keyword index at .research/cache/skill_index.json.

The index is used for fast keyword filtering; full BM25 semantic search is
provided by research_copilot.utils.context7_lookup.search_skills().

Search priority:
  1. .research/skills/  (user local overrides)
  2. src/research_copilot/assets/skills/  (bundled package skills)
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

# A basic list of stop words to filter out when generating keywords
STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'arent', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'cant', 'cannot', 'could',
    'couldnt', 'did', 'didnt', 'do', 'does', 'doesnt', 'doing', 'dont', 'down', 'during', 'each', 'few', 'for', 'from',
    'further', 'had', 'hadnt', 'has', 'hasnt', 'have', 'havent', 'having', 'he', 'hed', 'hell', 'hes', 'her', 'here',
    'heres', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'hows', 'i', 'id', 'ill', 'im', 'ive', 'if', 'in',
    'into', 'is', 'isnt', 'it', 'its', 'itself', 'lets', 'me', 'more', 'most', 'mustnt', 'my', 'myself', 'no', 'nor',
    'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
    'same', 'shant', 'she', 'shed', 'shell', 'shes', 'should', 'shouldnt', 'so', 'some', 'such', 'than', 'that', 'thats',
    'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'theres', 'these', 'they', 'theyd', 'theyll',
    'theyre', 'theyve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasnt', 'we',
    'wed', 'well', 'were', 'weve', 'werent', 'what', 'whats', 'when', 'whens', 'where', 'wheres', 'which', 'while',
    'who', 'whos', 'whom', 'why', 'whys', 'with', 'wont', 'would', 'wouldnt', 'you', 'youd', 'youll', 'youre', 'youve',
    'your', 'yours', 'yourself', 'yourselves', 'can', 'will', 'just', 'should', 'would', 'use', 'using', 'also', 'how',
    'the', 'this', 'that', 'them', 'these', 'those'
}

def clean_text(text: str) -> str:
    """Normalize text by removing special characters and lowercasing."""
    return re.sub(r'[^a-zA-Z0-9\s-]', '', text).lower()

def extract_keywords(title: str, purpose: str, category: str, content: str) -> List[str]:
    """Generate a clean list of keywords from skill metadata and content."""
    words = []
    # Add title words
    words.extend(clean_text(title).split())
    # Add category
    words.append(category.lower())
    # Add purpose words
    words.extend(clean_text(purpose).split())
    
    # Extract terms in the first 500 characters of content
    words.extend(clean_text(content[:500]).split())

    # Deduplicate and filter out stop words, short words, and numbers
    unique_keywords = []
    seen = set()
    for w in words:
        if w not in STOP_WORDS and len(w) > 2 and not w.isdigit():
            if w not in seen:
                seen.add(w)
                unique_keywords.append(w)
    
    return unique_keywords[:25]  # Limit to top 25 keywords per skill


def _find_skills_dirs(project_root: Path) -> List[Path]:
    """Return ordered list of skills directories to index.

    Local user overrides (``<root>/.research/skills``) take precedence.
    The bundled package assets (``src/research_copilot/assets/skills``) are
    included as a fallback so the index always covers the full skill set.
    """
    dirs: List[Path] = []

    # 1. User local overrides
    local = project_root / ".research" / "skills"
    if local.exists():
        dirs.append(local)

    # 2. Bundled package assets
    here = Path(__file__).parent
    bundled = here.parent / "assets" / "skills"
    if bundled.exists() and bundled not in dirs:
        dirs.append(bundled)

    return dirs


def build_index(project_root: Path) -> Path:
    cache_dir = project_root / ".research" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    index_path = cache_dir / "skill_index.json"

    skills_dirs = _find_skills_dirs(project_root)
    if not skills_dirs:
        print("ERROR: No skills directories found.")
        sys.exit(1)

    skills_index: Dict[str, Any] = {"skills": []}
    seen_stems: set = set()

    for skills_dir in skills_dirs:
        for md_file in sorted(skills_dir.rglob("*.md")):
            if md_file.name in ("SKILL_TEMPLATE.md",) or md_file.stem in seen_stems:
                continue
            seen_stems.add(md_file.stem)

            try:
                with open(md_file, "r") as f:
                    content = f.read()

                lines = content.split("\n")

                # Extract Title (First H1 heading)
                title = md_file.stem.replace("_", " ").title()
                for line in lines:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break

                # Extract Purpose (under ## Purpose heading)
                purpose = ""
                for i, line in enumerate(lines):
                    if line.strip() == "## Purpose":
                        purpose_lines = []
                        for next_line in lines[i + 1:]:
                            if next_line.startswith("## ") or next_line.startswith("---"):
                                break
                            if next_line.strip():
                                purpose_lines.append(next_line.strip())
                        purpose = " ".join(purpose_lines)
                        break

                if not purpose:
                    purpose = f"Methodology and instructions for {title.lower()}."

                category = md_file.parent.name
                # Make path relative to project root if possible, otherwise use absolute
                try:
                    relative_path = md_file.relative_to(project_root)
                except ValueError:
                    relative_path = md_file

                keywords = extract_keywords(title, purpose, category, content)

                skills_index["skills"].append({
                    "id": md_file.stem,
                    "title": title,
                    "category": category,
                    "description": purpose,
                    "keywords": keywords,
                    "path": str(relative_path),
                })

            except Exception as e:
                print(f"WARNING: Failed to parse skill file {md_file.name}: {e}")

    with open(index_path, "w") as f:
        json.dump(skills_index, f, indent=2)

    print(f"Successfully generated skill index: {index_path} ({len(skills_index['skills'])} skills indexed)")
    return index_path

import hashlib

MAX_DOC_CHARS = 2_000

def _tokenize(text: str) -> List[str]:
    """Lowercase, strip punctuation, split on whitespace."""
    return re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()

def _corpus_fingerprint(skills_dir: Path) -> str:
    md5 = hashlib.md5()
    for md_file in sorted(skills_dir.rglob("*.md")):
        md5.update(str(md_file.stat().st_mtime).encode())
    return md5.hexdigest()

def _build_bm25_index(skills_dir: Path) -> tuple[List[Dict], Any]:
    try:
        from rank_bm25 import BM25Okapi
    except ImportError as exc:
        raise RuntimeError("rank-bm25 is required: pip install rank-bm25") from exc

    corpus_meta = []
    tokenized_corpus = []

    for md_file in sorted(skills_dir.rglob("*.md")):
        if md_file.name in ("SKILL_TEMPLATE.md",):
            continue
        text = md_file.read_text(errors="replace")
        tokens = _tokenize(text)
        corpus_meta.append({"path": str(md_file), "title": md_file.stem})
        tokenized_corpus.append(tokens)

    if not tokenized_corpus:
        raise RuntimeError(f"No skill files found under {skills_dir}")

    return corpus_meta, BM25Okapi(tokenized_corpus)

_INDEX_META: Optional[List[Dict]] = None
_BM25: Optional[Any] = None
_INDEX_FINGERPRINT: Optional[str] = None

def _get_index(skills_dir: Path):
    global _INDEX_META, _BM25, _INDEX_FINGERPRINT
    fp = _corpus_fingerprint(skills_dir)
    if _BM25 is None or fp != _INDEX_FINGERPRINT:
        _INDEX_META, _BM25 = _build_bm25_index(skills_dir)
        _INDEX_FINGERPRINT = fp
    return _INDEX_META, _BM25

def search_skills(query: str, top_k: int = 1) -> List[Dict]:
    current = Path.cwd()
    root = None
    for p in [current] + list(current.parents):
        if (p / ".research").exists():
            root = p
            break
    if not root:
        skills_dirs = [Path(__file__).parent.parent / "assets" / "skills"]
    else:
        skills_dirs = _find_skills_dirs(root)
        
    skills_dir = skills_dirs[0] if skills_dirs else Path(__file__).parent.parent / "assets" / "skills"
    
    corpus_meta, bm25 = _get_index(skills_dir)
    tokens = _tokenize(query)
    scores = bm25.get_scores(tokens)

    ranked = sorted(zip(scores, corpus_meta), key=lambda t: t[0], reverse=True)

    results = []
    for score, meta in ranked[:top_k]:
        path = Path(meta["path"])
        try:
            content = path.read_text(errors="replace")[:MAX_DOC_CHARS]
        except OSError:
            content = ""
        results.append({
            "path": str(path),
            "title": meta["title"],
            "score": float(score),
            "content": content,
        })
    return results

def resolve_library_id(library_name: str, cache=None) -> str:
    results = search_skills(library_name, top_k=1)
    if results and results[0]["score"] > 0:
        return f"skill:{results[0]['title']}"
    return f"lib_{library_name.strip().lower()}_generic"

def get_library_docs(library_id: str, topic: str, cache=None) -> str:
    query = f"{library_id} {topic}"
    results = search_skills(query, top_k=1)
    if results and results[0]["score"] > 0:
        return results[0]["content"]
    return f"No local skill documentation found for '{topic}' in '{library_id}'.\nRefer to the official library documentation online."

if __name__ == "__main__":
    # Find project root
    current = Path.cwd()
    root = None
    for p in [current] + list(current.parents):
        if (p / ".research").exists():
            root = p
            break
    
    if not root:
        print("ERROR: Could not find project root containing .research/")
        sys.exit(1)

    build_index(root)
