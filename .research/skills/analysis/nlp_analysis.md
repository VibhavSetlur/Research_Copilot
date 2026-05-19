---
skill_id: "nlp_analysis"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "gensim", "scikit-learn"]
estimated_tokens: 3000
depends_on: ["profile_text"]
produces: ["analysis/03_analytical/nlp_results.json"]
---

# Skill: Text NLP Analysis & Topic Modeling

## Purpose
Preprocess texts, fit LDA models, and compute topic coherence scores.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `corpus_path` | Path | Yes | Corpus path |

## Execution Protocol
1. Tokenize and lemmatize text inputs, filtering stop words.
2. Fit LDA. Optimize number of topics using coherence scores ($C_v$).
3. Output top keywords for each topic.

## Diagnostics & Interpretation Guide (What to Look For)
- **Coherence Score $C_v < 0.40$**:
  - *Interpret*: Topics are uninterpretable or contain mixed concepts.
  - *Action*: Recheck stop words list, increase Dirichlet hyperparameters alpha/beta, or adjust topic count.

## Writing & Reporting Standards
> "We fit an LDA model to the text corpus. The optimal topic count was selected by maximizing coherence ($C_v = .58$). Table 2 lists the top terms associated with each topic."

## Reference Python Implementation
```python
from gensim.models import LdaModel
from gensim.corpora import Dictionary
from gensim.models.coherencemodel import CoherenceModel

def fit_lda(texts, k=5):
    dictionary = Dictionary(texts)
    corpus = [dictionary.doc2bow(t) for t in texts]
    lda = LdaModel(corpus, id2word=dictionary, num_topics=k)
    cm = CoherenceModel(model=lda, texts=texts, dictionary=dictionary, coherence='c_v')
    return lda, cm.get_coherence()
```

## Validation Criteria
- [ ] Topic coherence score is calculated.