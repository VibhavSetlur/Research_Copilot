"""Tests for the verified-citations module."""

from unittest.mock import patch

from research_os.tools.actions.synthesis.citations import (
    cap_for,
    collect_for_section,
    format_apa,
    format_bib,
    format_vancouver,
)


def test_cap_for_output_types():
    assert cap_for("paper") == 40
    assert cap_for("poster") == 6
    assert cap_for("abstract") == 3
    assert cap_for("unknown") == 25  # default


def test_collect_for_section_dedupes_and_filters_keyless(tmp_path):
    s2_hits = [
        {"title": "Real Paper", "authors": ["A B"], "year": 2024,
         "url": "http://x", "doi": "10.1/x"},
        {"title": "No DOI No URL", "authors": ["C D"], "year": 2024,
         "url": "", "doi": ""},
    ]
    cr_hits = [
        # duplicate by DOI
        {"title": "Real Paper", "authors": ["A B"], "year": 2024,
         "url": "http://x", "doi": "10.1/X"},
        {"title": "Crossref Only", "authors": ["E F"], "year": 2023,
         "url": "http://cr", "doi": "10.1/cr"},
    ]
    with patch(
        "research_os.tools.actions.search.search.search_semantic_scholar",
        return_value=s2_hits,
    ), patch(
        "research_os.tools.actions.search.search.search_crossref",
        return_value=cr_hits,
    ):
        out = collect_for_section("test query", k=5,
                                  providers=["semantic_scholar", "crossref"])
    # No-DOI/URL dropped; one duplicate merged → 2 entries.
    assert len(out) == 2
    assert all(e.get("citation_key") for e in out)
    assert any(e.get("verified_via") == "semantic_scholar" for e in out)


def test_format_bib_returns_valid_entry():
    entry = {
        "citation_key": "smith2024foo",
        "authors": ["Alice Smith", "Bob Jones"],
        "title": "On foo",
        "year": 2024,
        "doi": "10.1/foo",
    }
    bib = format_bib(entry)
    assert "@article{smith2024foo," in bib
    assert "Alice Smith and Bob Jones" in bib
    assert "10.1/foo" in bib


def test_format_apa():
    entry = {"authors": ["Alice Smith", "Bob Jones"], "title": "On foo",
             "year": 2024, "doi": "10.1/foo"}
    apa = format_apa(entry)
    assert "Smith" in apa or "Alice Smith" in apa
    assert "(2024)" in apa
    assert "10.1/foo" in apa


def test_format_vancouver():
    entry = {"authors": ["A B", "C D"], "title": "T",
             "year": 2024, "doi": "10.1/x"}
    v = format_vancouver(entry)
    assert "T" in v
    assert "10.1/x" in v
