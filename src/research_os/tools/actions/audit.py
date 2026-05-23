import logging
from typing import Dict, Any
from pathlib import Path
import re

logger = logging.getLogger("research.tools.audit")


def audit_synthesis(paper_path: str, root: Path) -> Dict[str, Any]:
    try:
        p = root / paper_path
        if not p.exists() or not p.is_file():
            return {"status": "error", "message": f"Paper not found at {paper_path}"}

        content = p.read_text().lower()

        # Check required sections
        missing_sections = []
        for sec in ["abstract", "methods", "results", "discussion"]:
            if sec not in content:
                missing_sections.append(sec)

        # Check causal language if only associational evidence
        # (Very simple regex for demonstration)
        causal_words = ["causes", "caused by", "proves", "proof of"]
        found_causal = [w for w in causal_words if w in content]

        # In a real implementation, we'd check bibliography and cited figures here
        has_bibliography = "references" in content or "bibliography" in content

        report = {
            "missing_sections": missing_sections,
            "causal_language_found": found_causal,
            "has_bibliography": has_bibliography,
            "figures_cited": True,  # Placeholder
        }

        if missing_sections or found_causal or not has_bibliography:
            return {
                "status": "warning",
                "report": report,
                "message": "Synthesis audit produced warnings.",
            }
        return {
            "status": "success",
            "report": report,
            "message": "Synthesis passed audit.",
        }
    except Exception as e:
        logger.error(f"Audit synthesis failed: {e}")
        return {"status": "error", "message": str(e)}
