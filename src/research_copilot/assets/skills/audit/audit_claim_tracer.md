# Claim Tracer — Evidence Graph Builder

## Purpose
Builds a claim-to-evidence graph for the entire manuscript. Every factual claim must be traceable to either computed data or a verified citation. Any claim with a broken trace is flagged as UNSUPPORTED and blocked from final output.

## Invocation
Run by `audit_validate` agent as Audit #7 after the manuscript is compiled.

## Protocol

### Step 1: Extract All Claims from Manuscript
Parse the manuscript (`reports/manuscript/research_findings.md`) and identify all factual claims:

**Claim types:**
1. **Statistical claims:** "X is associated with Y (r=0.42, p<0.001)"
2. **Literature claims:** "Prior studies show effects between 0.3-0.5"
3. **Descriptive claims:** "The sample consisted of 1,234 participants"
4. **Methodological claims:** "We used a mixed-effects model following Bates et al. (2015)"
5. **Comparative claims:** "Our results are consistent with Smith et al. (2023)"

### Step 2: Trace Each Claim

For each claim, build a trace chain:

**Type A: Computed from Data**
```
Claim: "X is associated with Y (r=0.42)"
  └── Source: reports/analysis/q1/results.json (line 47)
      └── Input: data/03_analytical/analysis_q1.csv (hash: abc123)
          └── Raw: 00_inputs/raw_data/survey.csv (hash: def456)
              └── Script: scripts/02_analysis.py (function: compute_correlation)
```

**Type B: From Literature**
```
Claim: "Prior studies show effects between 0.3-0.5"
  └── Source: DOI:10.xxxx/yyyy (CrossRef verified ✓, content verified ✓)
      └── Abstract: Semantic Scholar API (fetched 2026-05-19)
      └── Corpus entry: reports/literature/literature_corpus.json (entry #12)
```

**Type C: From Web Search**
```
Claim: "Python 3.12 introduced a 10% speedup"
  └── Source: https://docs.python.org/3/whatsnew/3.12.html
      └── Search: reports/literature/search_log.json (entry #5)
      └── Verified: 2026-05-19 via Context7
```

### Step 3: Validate Traces

For each trace, verify:
1. **Source file exists** — the referenced file is present in the project
2. **Data hash matches** — the data file hasn't been modified since the claim was made
3. **Citation is verified** — if the claim cites a paper, it passed all 3 verification passes
4. **Number matches** — the statistic in the claim matches the computed value exactly

### Step 4: Build Report

Output: `reports/audit/claim_trace_report.json`

```json
{
  "schema_version": "1.0.0",
  "generated_at": "ISO 8601",
  "total_claims": 47,
  "summary": {
    "fully_traced": 42,
    "partially_traced": 3,
    "unsupported": 2
  },
  "verdict": "PASS|FAIL",
  "claims": [
    {
      "id": "claim_001",
      "text": "X is associated with Y (r=0.42, p=0.003)",
      "type": "statistical",
      "location": "research_findings.md:line_47",
      "trace": {
        "source_type": "computed_data",
        "source_file": "reports/analysis/q1/results.json",
        "data_file": "data/03_analytical/analysis_q1.csv",
        "data_hash": "abc123",
        "raw_file": "00_inputs/raw_data/survey.csv",
        "raw_hash": "def456",
        "script": "scripts/02_analysis.py",
        "verified": true
      },
      "status": "fully_traced"
    }
  ]
}
```

**Verdict Rules:**
- PASS: all claims fully traced
- FAIL: any claim is unsupported
- CONDITIONAL: some claims partially traced but none unsupported

### Step 5: Flag Unsupported Claims

Any claim that cannot be traced is flagged:
```
UNSUPPORTED CLAIM:
  Text: "..."
  Location: research_findings.md:line_X
  Reason: No source file found / citation not verified / data hash mismatch
  Action: Remove from manuscript or provide trace
```

## Integration

- Runs as part of `audit_validate` (Audit #7)
- Uses `citation_verification_report.json` from Audit #6
- Uses `data_lineage.json` for data hash verification
- Unsupported claims = gate FAIL
