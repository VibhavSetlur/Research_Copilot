---
skill_id: "abstract_generator"
version: "1.0.0"
category: "writing"
depends_on: ["execute_analysis", "compile_outputs"]
produces: ["03_synthesis/manuscript/abstract_apa.md", "03_synthesis/manuscript/abstract_nature.md", "03_synthesis/manuscript/abstract_plain.md", "03_synthesis/manuscript/abstract_tweet.txt"]
complexity: "quick"
---

# Skill: Abstract Generator

## Purpose
Generates abstracts in four formats from computed results. Every claim grounded in data with source file tags. No hallucination.

---

## Inputs
`key_findings.json`, `decisions.yaml` (method summary), `*_results.json` (effect sizes), data profile (sample info), `intake.md` (research question). All required.

---

## Protocol

### Step 1: Extract Grounded Facts
Build fact table from inputs. Each fact must have a `source_file`. If no source, exclude from abstract.

### Step 2: APA Structured (~250 words)
Four sections: **Background** (1-2 sentences, research question), **Methods** (1-2 sentences, design/sample/method), **Results** (2-3 sentences with effect sizes + CIs + p-values), **Conclusion** (1 sentence, grounded in results). Every numerical claim includes effect size + CI + p-value. No causal language unless design supports it.

### Step 3: Nature-Style Unstructured (~150 words)
Single paragraph, no headers. Structure: problem (1 sentence) → what we did (1 sentence) → findings with numbers (2-3 sentences) → meaning (1 sentence). Lead with most important finding. Include at least one effect size with CI.

### Step 4: Plain Language (~100 words)
Non-specialist audience. No statistical jargon. Use "X out of Y" or "about Z%" instead of effect sizes. Every claim still traceable to source file.

### Step 5: Tweet-Length (280 chars)
One key finding with one number. Implication in ≤5 words. Include `#Research` or domain hashtag.

### Step 6: Source Tagging
Output `abstract_sources.json` with: abstract type, word count, array of claims (each with text, source_file, effect_size, CI, p_value), generated_at timestamp.

---

## Anti-Hallucination Rules
1. Empty `key_findings.json` → output "No findings available."
2. Missing effect size → exclude that finding.
3. Unknown sample size → do NOT invent one.
4. Never use "proves", "confirms", "demonstrates" — use "suggests", "is associated with".
5. Exploratory analysis → state "These findings are exploratory and require confirmation."

---

## Validation
- [ ] Every numerical claim has source file
- [ ] No causal language without design justification
- [ ] APA ≤ 250 words, Nature ≤ 150, Plain ≤ 100, Tweet ≤ 280 chars
- [ ] Plain language: no jargon
- [ ] Effect sizes include CIs
- [ ] p-values formatted correctly
