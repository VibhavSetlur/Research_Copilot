#!/usr/bin/env python3
"""
Research Copilot Skill Indexer
Parses all Markdown files in .research/skills/ and generates a lightweight search index
at .research/cache/skill_index.json.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any

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


def build_index(project_root: Path) -> Path:
    skills_dir = project_root / ".research" / "skills"
    cache_dir = project_root / ".research" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    index_path = cache_dir / "skill_index.json"

    if not skills_dir.exists():
        print(f"ERROR: Skills directory not found: {skills_dir}")
        sys.exit(1)

    skills_index = {"skills": []}

    for md_file in sorted(skills_dir.rglob("*.md")):
        if md_file.name == "SKILL_TEMPLATE.md":
            continue

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
                    # Grab the next non-empty lines
                    purpose_lines = []
                    for next_line in lines[i+1:]:
                        if next_line.startswith("## ") or next_line.startswith("---"):
                            break
                        if next_line.strip():
                            purpose_lines.append(next_line.strip())
                    purpose = " ".join(purpose_lines)
                    break

            # Fallback if no Purpose section found
            if not purpose:
                purpose = f"Methodology and instructions for {title.lower()}."

            category = md_file.parent.name
            relative_path = md_file.relative_to(project_root)

            keywords = extract_keywords(title, purpose, category, content)

            skill_entry = {
                "id": md_file.stem,
                "title": title,
                "category": category,
                "description": purpose,
                "keywords": keywords,
                "path": str(relative_path)
            }
            skills_index["skills"].append(skill_entry)

        except Exception as e:
            print(f"WARNING: Failed to parse skill file {md_file.name}: {e}")

    with open(index_path, "w") as f:
        json.dump(skills_index, f, indent=2)

    print(f"Successfully generated skill index: {index_path} ({len(skills_index['skills'])} skills indexed)")
    return index_path


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
