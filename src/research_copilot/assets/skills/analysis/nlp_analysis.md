---
skill_id: "nlp_analysis"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "scikit-learn", "gensim|bertopic", "spacy"]
depends_on: ["profile_text"]
produces: ["analysis/03_analytical/nlp_results.json"]
complexity: "advanced"
---

# Skill: Text Analysis & Topic Modeling

## Purpose
Extract latent topics, compute text representations, and perform statistical analysis on text corpora.

## When to Use
- Research question involves text content (themes, sentiment, discourse)
- Need to reduce text to quantifiable features
- Comparing text across groups or over time

## When NOT to Use
- Text is too short (< 10 words per document)
- Only keyword counting needed (use simple frequency analysis)
- Corpus is too small (< 50 documents)

## Decision Protocol

### Method Selection
| Goal | Method |
|------|--------|
| Discover latent themes | LDA, NMF, or BERTopic |
| Document similarity | TF-IDF + cosine similarity, or embeddings |
| Sentiment analysis | VADER, TextBlob, or fine-tuned transformer |
| Text classification | Naive Bayes, SVM, or fine-tuned LLM |
| Keyword extraction | RAKE, YAKE, or KeyBERT |
| Topic evolution over time | Dynamic Topic Modeling |

## Execution Protocol

### Step 1: Text Preprocessing
- Lowercase, remove punctuation, remove numbers (optional)
- Remove stopwords (domain-specific list if available)
- Lemmatize (not stem: preserves interpretability)
- Remove documents with < 3 tokens after preprocessing
- Remove tokens appearing in < 2 documents or > 95% of documents

### Step 2: Topic Modeling
**LDA (Latent Dirichlet Allocation):**
- Iterate k = 2 to 20 topics
- Select optimal k by: coherence score (C_v), perplexity, or silhouette
- Report: top-10 terms per topic, topic proportions per document
- Interpret: name each topic based on top terms

**BERTopic (modern alternative):**
- Uses sentence embeddings + HDBSCAN + class-based TF-IDF
- Auto-detects number of topics
- More coherent topics than LDA
- Supports dynamic topic modeling

### Step 3: Topic Validation
- Coherence score C_v: > 0.50 = interpretable, > 0.60 = good
- Topic diversity: measure overlap between top terms
- Human validation: sample documents from each topic, check coherence
- Stability: run multiple times with different seeds; check consistency

### Step 4: Downstream Analysis
- Topic prevalence by group: chi-square or ANOVA on topic proportions
- Topic prevalence over time: trend analysis
- Document-level: correlate topic proportions with outcome variables
- Topic networks: which topics co-occur in documents?

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Coherence C_v | > 0.50 | Topics uninterpretable | Adjust k, change preprocessing |
| Topic diversity | > 0.70 | Topics overlap heavily | Increase alpha, reduce k |
| Stability | Consistent across runs | Unstable topics | Increase corpus size or iterations |
| Coverage | > 80% docs assigned | Many docs unassigned | Lower threshold or add "other" topic |

### Red Flags
- **Dominant topic (> 50% of documents)**: preprocessing too aggressive or k too small
- **Topics differ only by function words**: stopwords not properly removed
- **Coherence decreases as k increases**: overfitting; choose smaller k
- **BERTopic produces single "miscellaneous" topic**: embeddings not discriminative; try different model

## Reporting Template
> "Topic modeling was performed using [LDA/BERTopic] with k = [value] topics selected by [criterion]. The average coherence score was C_v = [value]. Top topics included: [Topic 1 name] ([percentage]% of documents), [Topic 2 name] ([percentage]%). Topic prevalence differed significantly between [groups] (χ² = [value], p = [value])."

## Output Specification
- `analysis/03_analytical/nlp_results.json`: topic assignments, coherence scores, top terms per topic, topic proportions, downstream analysis results

## Validation Checks
- [ ] Optimal k justified by coherence or other criterion
- [ ] Each topic is interpretable and named
- [ ] Coherence score reported
- [ ] Topic proportions sum to 1.0 per document
