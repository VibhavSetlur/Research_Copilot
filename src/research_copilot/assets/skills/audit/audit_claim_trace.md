# Skill: Audit Claim Trace

> Audit #7: Every factual claim in manuscript traced to computed data OR verified citation.

## Purpose
Build a claim-to-evidence graph for the entire manuscript. Any claim with a broken trace is flagged as UNSUPPORTED and blocked from final output.

---

## Protocol

### Step 1: Extract Claims from Manuscript
1. Read `reports/manuscript/research_findings.md`
2. Identify factual claims using pattern matching:
   - Numeric claims: "X is associated with Y (r=0.42)"
   - Comparative claims: "Group A scored higher than Group B"
   - Literature claims: "Prior studies show effects between 0.3-0.5"
   - Causal claims: "X causes Y"
3. For each claim, record:
   - Claim text
   - Location in manuscript (section, paragraph)
   - Claim type (numeric, comparative, literature, causal)

### Step 2: Trace Numeric Claims to Data
For each numeric claim:
1. Search analysis outputs in `reports/analysis/` for matching values
2. Trace to source data file:
   - Check `docs/data_lineage.json` for transformation chain
   - Verify SHA-256 hash of source data matches
3. Record trace:
   ```
   Claim: "X is associated with Y (r=0.42)"
     └── Source: reports/analysis/q1/results.json (line 47)
         └── Input: data/03_analytical/analysis_q1.csv (hash: abc123)
             └── Raw: inputs/data/raw/survey.csv (hash: def456)
   ```

### Step 3: Trace Literature Claims to Verified Citations
For each literature claim:
1. Find the citation(s) supporting the claim
2. Check `reports/literature/citation_verification_report.json`
3. Verify citation passed all three verification passes
4. Record trace:
   ```
   Claim: "Prior studies show effects between 0.3-0.5"
     └── Source: DOI:10.xxxx/yyyy (CrossRef verified ✓, content verified ✓, retraction check ✓)
   ```

### Step 4: Build Claim-to-Evidence Graph
Create `reports/audit/claim_trace_report.json`:

```json
{
  "schema_version": "1.0.0",
  "timestamp": "ISO 8601",
  "total_claims": 87,
  "summary": {
    "fully_traced": 78,
    "partially_traced": 5,
    "unsupported": 4
  },
  "claims": [
    {
      "claim_id": "C001",
      "claim_text": "X is associated with Y (r=0.42, p=0.003)",
      "claim_type": "numeric",
      "location": "Section 3.2, paragraph 2",
      "trace": {
        "status": "FULLY_TRACED",
        "source_file": "reports/analysis/q1/results.json",
        "data_file": "data/03_analytical/analysis_q1.csv",
        "data_hash": "abc123",
        "raw_file": "inputs/data/raw/survey.csv",
        "raw_hash": "def456"
      }
    },
    {
      "claim_id": "C002",
      "claim_text": "Prior studies show effects between 0.3-0.5",
      "claim_type": "literature",
      "location": "Section 2.1, paragraph 3",
      "trace": {
        "status": "FULLY_TRACED",
        "source": "DOI:10.xxxx/yyyy",
        "verification": {
          "existence": "PASS",
          "content": "PASS",
          "retraction": "PASS"
        }
      }
    },
    {
      "claim_id": "C003",
      "claim_text": "This effect is universal across populations",
      "claim_type": "causal",
      "location": "Section 4.1, paragraph 1",
      "trace": {
        "status": "UNSUPPORTED",
        "reason": "No data supports universality claim; only tested on single population",
        "remediation": "Qualify claim to reflect actual sample, or remove"
      }
    }
  ],
  "unsupported_claims": [
    {
      "claim_id": "C003",
      "claim_text": "...",
      "location": "...",
      "remediation": "..."
    }
  ]
}
```

### Step 5: Verdict
- **PASS:** All claims fully traced
- **CONDITIONAL:** Some claims partially traced (missing intermediate step in data lineage)
- **FAIL:** Any claim unsupported

### Step 6: Auto-Healing
If FAIL or CONDITIONAL:
1. For unsupported claims: Search analysis outputs for supporting data
2. If no supporting data found: Flag as UNSUPPORTED, remove from manuscript
3. For partially traced claims: Complete the trace by finding missing intermediate files
4. Re-run claim tracer after fixes

---

## Integration
- Called by: `audit_validate` agent as Audit #7
- Uses: `claim_tracer.py` script
- Outputs to: `reports/audit/claim_trace_report.json`
- Blocks manuscript if: FAIL verdict
