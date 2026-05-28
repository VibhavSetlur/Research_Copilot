"""Audits for the new quality stack: code, prose, claims."""

from pathlib import Path

from research_os.tools.actions.audit.claim_grounding import (
    audit_claims,
    extract_claims,
)
from research_os.tools.actions.audit.code_quality import audit_script
from research_os.tools.actions.audit.prose_quality import audit_prose_document


# ─── Code quality ────────────────────────────────────────────────────


def test_clean_script_passes(tmp_path: Path):
    p = tmp_path / "clean.py"
    p.write_text(
        '"""Clean module."""\n\n'
        "def double(x: int) -> int:\n"
        '    """Double an integer."""\n'
        "    return x * 2\n"
    )
    r = audit_script(p)
    assert r["ok"]
    assert r["module_docstring"]


def test_bare_except_blocks(tmp_path: Path):
    p = tmp_path / "bad.py"
    p.write_text(
        '"""Bad module."""\n'
        "def x():\n"
        "    try:\n"
        "        pass\n"
        "    except:\n"
        "        pass\n"
    )
    r = audit_script(p)
    assert not r["ok"]
    assert any("bare" in b for b in r["blockers"])


def test_import_star_blocks(tmp_path: Path):
    p = tmp_path / "bad.py"
    p.write_text('"""docstring."""\nfrom os import *\n')
    r = audit_script(p)
    assert not r["ok"]
    assert any("import" in b for b in r["blockers"])


def test_very_long_function_blocks(tmp_path: Path):
    body = "    x = 1\n" * 160
    p = tmp_path / "long.py"
    p.write_text(f'"""docstring."""\ndef big():\n{body}\n')
    r = audit_script(p)
    assert not r["ok"]
    assert any("function `big`" in b for b in r["blockers"])


# ─── Prose quality ───────────────────────────────────────────────────


def test_prose_catches_vague_quantifiers(tmp_path: Path):
    p = tmp_path / "doc.md"
    p.write_text(
        "# Findings\n\n"
        "Many subjects showed substantial variability. "
        "Several measures appear to be considerable. "
        "The effect tends to be relatively strong.\n"
    )
    r = audit_prose_document(p)
    assert any("vague" in w.lower() for w in r["warnings"])
    assert len(r["hedges"]) >= 1


def test_prose_causal_blocks_for_observational(tmp_path: Path):
    p = tmp_path / "doc.md"
    p.write_text("# Discussion\n\nDiet causes weight loss.\n")
    r = audit_prose_document(p, is_observational=True)
    assert any("causal" in b.lower() for b in r["blockers"])


def test_prose_reading_level_computed(tmp_path: Path):
    p = tmp_path / "doc.md"
    p.write_text(
        "# Methods\n\n"
        "We applied a heteroscedasticity-robust covariance estimator. "
        "Effect modification was assessed via stratification.\n"
    )
    r = audit_prose_document(p)
    assert r["fk_grade"] > 0


# ─── Claim grounding ────────────────────────────────────────────────


def test_extract_claims_basic():
    text = "# Heading 2024\n\nThe AUROC was 0.84 (95% CI 0.79-0.89). n = 423."
    # Use tmp file because extract_claims expects a path.
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(text)
        path = Path(f.name)
    claims = extract_claims(path)
    tokens = {c["token"] for c in claims}
    assert "0.84" in tokens
    assert "0.79" in tokens
    # 2024 is a year — excluded.
    assert "2024" not in tokens
    path.unlink()


def test_claims_grounded_against_corpus(tmp_path: Path):
    # Build a tiny workspace with one paper claim grounded by a CSV.
    ws = tmp_path / "workspace" / "01_eda" / "outputs" / "reports"
    ws.mkdir(parents=True)
    (ws / "summary.md").write_text("Mean = 12.3\n")
    syn = tmp_path / "synthesis"
    syn.mkdir(parents=True)
    (syn / "paper.md").write_text(
        "# Paper\n\nThe mean was 12.3 (95% CI 10.1-14.5)."
    )
    res = audit_claims(tmp_path)
    # 12.3 should ground; 10.1 / 14.5 don't appear in corpus.
    assert res["total_claims"] >= 3
    assert res["grounded"] >= 1
    assert res["ungrounded"] >= 1
