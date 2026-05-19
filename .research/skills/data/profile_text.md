---
skill_id: "profile_text"
version: "3.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "nltk", "spacy"]
estimated_tokens: 3000
depends_on: []
produces: ["data/01_ingested/profile_text.json"]
---

# Skill: Text Corpus Profiling

## Purpose
Profile natural language datasets or text corpora to extract lexical statistics, token distributions, and readability metrics.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `corpus_path` | Path | Yes | Path to text directory, CSV, or JSONL containing text fields |
| `text_column` | Str | No | Target column name if dataset is tabular |

## Execution Protocol

### Step 1: Corpus Load & Tokenization
- Load text files. Normalize encodings (replace invalid bytes).
- Load SpaCy or NLTK tokenization pipeline.
- Extract basic counts: Total Document Count, Total Tokens, Total Sentences.

### Step 2: Lexical Richness & Vocabulary Analysis
- Calculate Type-Token Ratio (TTR) to measure vocabulary diversity.
- Calculate Lexical Density (proportion of content words: nouns, verbs, adjectives).
- Extract vocabulary overlap index across documents.

### Step 3: N-gram & Term Frequency
- Filter out standard stop words.
- Calculate frequency distributions for unigrams, bigrams, and trigrams.
- Save top 50 n-grams with frequency counts.

### Step 4: Readability & Document Quality Metrics
- Compute Flesch-Kincaid Grade Level and Flesch Reading Ease scores.
- Identify outlier documents: Empty texts, high non-alphanumeric ratio texts, or duplicate documents.

## Output Specification
Produces:
- `data/01_ingested/profile_text.json` containing lexical metrics, n-grams, and outlier lists.

## Validation Criteria
- [ ] TTR score is bounded between 0 and 1.
- [ ] Stop words are successfully excluded from frequency lists.