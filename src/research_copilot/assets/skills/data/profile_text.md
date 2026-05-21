---
skill_id: "profile_text"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "nltk|spacy"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/text_profile.json"]
complexity: "intermediate"
---

# Skill: Text Corpus Profiling

## Purpose
Profile text columns to understand corpus size, vocabulary richness, language distribution, readability, and structural properties.

## When to Use
- Dataset contains free-text columns (surveys, documents, social media)
- Before NLP analysis (topic modeling, sentiment, embeddings)
- To assess text quality and preprocessing needs

## When NOT to Use
- Text is already tokenized or preprocessed
- Only a few short string fields (e.g., names, labels)

## Execution Protocol

### Step 1: Basic Corpus Statistics
- Document count (N), total tokens, total characters
- Per-document: token count, character count, sentence count, word count
- Average document length, SD, min, max
- Empty document count and proportion

### Step 2: Vocabulary Analysis
- Vocabulary size (unique types)
- Type-token ratio (TTR = types / tokens)
- Hapax legomena: words appearing exactly once
- Top-20 most frequent tokens (excluding stopwords)
- Average word length, SD

### Step 3: Language Detection
- Detect language per document (if multilingual suspected)
- Report language distribution
- Flag documents with low-confidence language detection

### Step 4: Readability Assessment
- Flesch-Kincaid Grade Level
- Flesch Reading Ease score
- Gunning Fog Index
- Average sentence length
- Proportion of complex words (> 3 syllables)

### Step 5: Quality Screening
- Duplicate documents: exact match count
- Near-duplicates: Jaccard similarity > 0.90 on token sets
- Documents with excessive special characters (> 20% non-alphanumeric)
- Documents with extremely short length (< 3 tokens)
- Documents with extremely long length (> 99th percentile)

### Step 6: Structural Properties
- Paragraph count per document
- Punctuation density
- Proportion of uppercase characters (shouting detection)
- URL/email/mention count (for social media text)
- Hashtag count (for social media)

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| TTR | 0.4 - 0.8 | Lexically impoverished or overly diverse | Check for boilerplate or mixed languages |
| Readability | Grade 6-16 | Too simple or too complex | Adjust preprocessing or segment corpus |
| Language consistency | Single dominant language | Multilingual corpus | Split by language or use multilingual models |
| Duplicate rate | < 5% | Significant duplication | Deduplicate before analysis |

### Red Flags
- **> 30% empty or near-empty documents**: data collection issue; filter before analysis
- **Extreme length skew**: few very long documents dominate; consider truncation or weighting
- **High special character ratio**: encoding issues or non-text data; inspect raw bytes
- **All documents identical length**: possible template or form data; not suitable for topic modeling

## Output Specification
- `data/01_ingested/text_profile.json`: corpus stats, vocabulary analysis, language distribution, readability scores, quality flags

## Validation Checks
- [ ] Document count matches source
- [ ] Vocabulary size ≤ total tokens
- [ ] Readability scores in plausible ranges
- [ ] Language codes are valid ISO 639
