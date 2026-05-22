from typing import List, Optional, Any, Dict
import uuid
from datetime import datetime, timezone

from research_copilot.state.state_ledger import ResearchLedger
from research_copilot.schemas.state_schema import (
    Hypothesis, Claim, Evidence, Contradiction, CognitiveObjects, CitationObject
)

class CognitiveStateTracker:
    """Manages the semantic/cognitive state of the research project."""

    def __init__(self, ledger: ResearchLedger):
        self.ledger = ledger

    def _get_cognitive_objects(self) -> dict:
        state = self.ledger.get()
        return state.get("research_objects", CognitiveObjects().model_dump())

    def _save_cognitive_objects(self, objects: dict):
        self.ledger.update(research_objects=objects)
        
    def _add_revision(self, obj: dict, change: str):
        revs = obj.setdefault("revisions", [])
        revs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "change": change
        })

    def add_hypothesis(self, description: str, provenance: str = "") -> str:
        """Add a new hypothesis to track."""
        objects = self._get_cognitive_objects()
        h_id = f"hyp_{uuid.uuid4().hex[:8]}"
        hyp = Hypothesis(id=h_id, description=description, provenance=provenance)
        objects.setdefault("hypotheses", []).append(hyp.model_dump())
        self._save_cognitive_objects(objects)
        return h_id

    def invalidate_hypothesis(self, hypothesis_id: str, reason: str):
        """Mark a hypothesis as invalidated and log the dead end."""
        objects = self._get_cognitive_objects()
        for h in objects.get("hypotheses", []):
            if h["id"] == hypothesis_id:
                h["status"] = "invalidated"
                h["confidence"] = 0.0
                self._add_revision(h, f"Invalidated: {reason}")
                # Also log in dead ends for quick context
                state = self.ledger.get()
                dead_ends = state.get("dead_ends", [])
                dead_ends.append(reason)
                self.ledger.update(dead_ends=dead_ends)
                break
        self._save_cognitive_objects(objects)

    def add_claim(self, description: str, provenance: str = "", source_nodes: Optional[List[str]] = None) -> str:
        """Record a verified or pending claim."""
        objects = self._get_cognitive_objects()
        c_id = f"claim_{uuid.uuid4().hex[:8]}"
        claim = Claim(id=c_id, description=description, provenance=provenance, supporting_nodes=source_nodes or [])
        objects.setdefault("claims", []).append(claim.model_dump())
        self._save_cognitive_objects(objects)
        return c_id
        
    def update_claim_confidence(self, claim_id: str, new_confidence: float, reason: str):
        """Updates claim confidence and tracks revision."""
        objects = self._get_cognitive_objects()
        for c in objects.get("claims", []):
            if c["id"] == claim_id:
                old_conf = c.get("confidence", 0.5)
                c["confidence"] = new_confidence
                self._add_revision(c, f"Confidence changed from {old_conf} to {new_confidence} because: {reason}")
                break
        self._save_cognitive_objects(objects)

    def add_evidence(self, description: str, source_file: Optional[str] = None, provenance: str = "") -> str:
        """Record a piece of evidence."""
        objects = self._get_cognitive_objects()
        e_id = f"ev_{uuid.uuid4().hex[:8]}"
        evidence = Evidence(id=e_id, description=description, source_file=source_file, provenance=provenance)
        objects.setdefault("evidence", []).append(evidence.model_dump())
        self._save_cognitive_objects(objects)
        return e_id
        
    def add_citation(self, title: str, authors: List[str], url_or_doi: Optional[str] = None) -> str:
        """Record a formal citation."""
        objects = self._get_cognitive_objects()
        cit_id = f"cit_{uuid.uuid4().hex[:8]}"
        cit = CitationObject(id=cit_id, description=f"Citation: {title}", title=title, authors=authors, url_or_doi=url_or_doi)
        objects.setdefault("citations", []).append(cit.model_dump())
        self._save_cognitive_objects(objects)
        return cit_id

    def link_evidence_to_hypothesis(self, evidence_id: str, hypothesis_id: str, supports: bool = True):
        """Link evidence to a hypothesis as supporting or contradicting."""
        objects = self._get_cognitive_objects()
        for h in objects.get("hypotheses", []):
            if h["id"] == hypothesis_id:
                if supports:
                    if evidence_id not in h.get("supporting_evidence", []):
                        h.setdefault("supporting_evidence", []).append(evidence_id)
                        self._add_revision(h, f"Added supporting evidence: {evidence_id}")
                else:
                    if evidence_id not in h.get("contradicting_evidence", []):
                        h.setdefault("contradicting_evidence", []).append(evidence_id)
                        self._add_revision(h, f"Added contradicting evidence: {evidence_id}")
                break
        self._save_cognitive_objects(objects)

    def log_contradiction(self, description: str, related_claims: Optional[List[str]] = None) -> str:
        """Log a contradiction and decay confidence in related claims."""
        objects = self._get_cognitive_objects()
        c_id = f"contra_{uuid.uuid4().hex[:8]}"
        contra = Contradiction(id=c_id, description=description, related_claims=related_claims or [])
        objects.setdefault("contradictions", []).append(contra.model_dump())

        # Decay confidence of related claims
        for claim_id in (related_claims or []):
            for claim in objects.get("claims", []):
                if claim["id"] == claim_id:
                    old_conf = claim.get("confidence", 0.5)
                    new_conf = max(0.0, old_conf - 0.3)
                    claim["confidence"] = new_conf
                    self._add_revision(claim, f"Confidence decayed due to contradiction {c_id}")

        self._save_cognitive_objects(objects)
        return c_id

    def get_context_summary(self) -> str:
        """Generate a summary of the cognitive state for LLM context."""
        objects = self._get_cognitive_objects()
        lines = []
        
        hypotheses = [h for h in objects.get("hypotheses", []) if h["status"] == "active"]
        if hypotheses:
            lines.append("Active Hypotheses:")
            for h in hypotheses:
                lines.append(f"  - [{h['id']}] {h['description']} (confidence: {h.get('confidence', 0.5):.2f})")
                
        claims = objects.get("claims", [])
        if claims:
            lines.append("\nCurrent Claims:")
            for c in claims:
                lines.append(f"  - [{c['id']}] {c['description']} (confidence: {c.get('confidence', 0.5):.2f})")
                
        contradictions = [c for c in objects.get("contradictions", []) if not c.get("resolved", False)]
        if contradictions:
            lines.append("\nUnresolved Contradictions:")
            for c in contradictions:
                lines.append(f"  - [{c['id']}] {c['description']} (impacts: {', '.join(c.get('related_claims', []))})")
                
        open_qs = objects.get("open_questions", [])
        if open_qs:
            lines.append("\nOpen Questions:")
            for q in open_qs:
                lines.append(f"  - {q}")
                
        dead_ends = objects.get("dead_ends", [])
        if dead_ends:
            lines.append("\nDead Ends (Do not pursue):")
            for d in dead_ends[-3:]: # Only show last 3
                lines.append(f"  - {d}")

        return "\n".join(lines) if lines else "No semantic cognitive state established yet."


class StuckLoopException(Exception):
    """Raised when the agent gets stuck in a loop of identical errors."""
    pass

class ExecutionStuckDetector:
    """Detects if the agent is stuck in an execution loop."""
    def __init__(self):
        self.error_counts = {}

    def report_error(self, tool_name: str, parameters: dict, error_message: str):
        import hashlib
        # Hash the tool call and error message to detect identical loops
        param_str = str(sorted(parameters.items())) if parameters else ""
        error_sig = f"{tool_name}:{param_str}:{error_message}"
        sig_hash = hashlib.sha256(error_sig.encode()).hexdigest()
        
        count = self.error_counts.get(sig_hash, 0) + 1
        self.error_counts[sig_hash] = count
        
        if count >= 3:
            # We hit the loop threshold. Clear the count and raise.
            self.error_counts[sig_hash] = 0
            raise StuckLoopException(f"Stuck in execution loop with tool '{tool_name}'. Repeated error: {error_message}")
