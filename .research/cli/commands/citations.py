"""Citation commands: verify-citations, trace-claims."""
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def find_project_root():
    p = Path.cwd()
    for _ in range(10):
        if (p / ".research").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return None


def load_json(path: Path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def cmd_verify_citations(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    verifier_path = root / ".research" / "scripts" / "utils" / "citation_verifier.py"
    if not verifier_path.exists():
        print(f"ERROR: Citation verifier not found at {verifier_path}")
        sys.exit(1)

    bibliography = root / "reports" / "literature" / "bibliography.bib"
    corpus = root / "reports" / "literature" / "literature_corpus.json"
    manuscript = root / "reports" / "manuscript" / "research_findings.md"

    cmd = [sys.executable, str(verifier_path)]

    if bibliography.exists():
        cmd.extend(["--bibliography", str(bibliography)])
    elif manuscript.exists():
        cmd.extend(["--manuscript", str(manuscript)])
    else:
        print("ERROR: No bibliography or manuscript found to extract citations from.")
        sys.exit(1)

    if corpus.exists():
        cmd.extend(["--corpus", str(corpus)])

    print("Running citation verification...")
    try:
        result = subprocess.run(cmd, check=True, cwd=str(root))
        print()
        report_path = root / "reports" / "literature" / "citation_verification_report.json"
        if report_path.exists():
            report = load_json(report_path)
            summary = report.get("summary", {})
            print("CITATION VERIFICATION SUMMARY")
            print(f"  Total citations: {report.get('total_citations', 0)}")
            print(f"  Verified: {summary.get('all_pass', 0)}")
            print(f"  Unverified: {summary.get('existence_fail', 0) + summary.get('content_fail', 0)}")
            print(f"  Retracted: {summary.get('retracted', 0)}")
    except subprocess.CalledProcessError as e:
        print(f"Citation verification failed with exit code {e.returncode}")
        sys.exit(1)


def cmd_trace_claims(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    tracer_path = root / ".research" / "scripts" / "utils" / "claim_tracer.py"
    if not tracer_path.exists():
        print(f"ERROR: Claim tracer not found at {tracer_path}")
        sys.exit(1)

    manuscript = root / "reports" / "manuscript" / "research_findings.md"
    if not manuscript.exists():
        print("ERROR: No manuscript found at reports/manuscript/research_findings.md")
        sys.exit(1)

    cmd = [sys.executable, str(tracer_path), "--manuscript", str(manuscript)]

    data_lineage = root / "docs" / "data_lineage.json"
    if data_lineage.exists():
        cmd.extend(["--data-lineage", str(data_lineage)])

    citation_report = root / "reports" / "literature" / "citation_verification_report.json"
    if citation_report.exists():
        cmd.extend(["--citation-report", str(citation_report)])

    print("Running claim tracer...")
    try:
        result = subprocess.run(cmd, check=True, cwd=str(root))
        print()
        report_path = root / "reports" / "audit" / "claim_trace_report.json"
        if report_path.exists():
            report = load_json(report_path)
            summary = report.get("summary", {})
            print("CLAIM TRACE SUMMARY")
            print(f"  Total claims: {report.get('total_claims', 0)}")
            print(f"  Fully traced: {summary.get('fully_traced', 0)}")
            print(f"  Partially traced: {summary.get('partially_traced', 0)}")
            print(f"  Unsupported: {summary.get('unsupported', 0)}")
    except subprocess.CalledProcessError as e:
        print(f"Claim tracing failed with exit code {e.returncode}")
        sys.exit(1)
