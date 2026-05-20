"""Schema definitions for the global research state ledger."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict


class TokenBudget(BaseModel):
    """Token budget tracking for context window management."""

    used: int = Field(..., ge=0, description="Tokens used so far")
    remaining: int = Field(..., ge=0, description="Tokens remaining")
    limit: int = Field(..., gt=0, description="Total token limit")

    @field_validator("remaining")
    @classmethod
    def remaining_must_match(cls, v: int, info) -> int:
        if "used" in info.data and "limit" in info.data:
            expected = info.data["limit"] - info.data["used"]
            if v != expected:
                raise ValueError(f"Remaining ({v}) must equal limit - used ({expected})")
        return v


class ContextTransferMemo(BaseModel):
    """Context Transfer Memorandum — generated at 90% token budget to preserve
    latent context that cannot be transferred via structured state alone.

    Captures abandoned paths, micro-decisions, and immediate tactical goals
    so a new conversation can resume with full situational awareness.
    """

    ctm_id: str = Field(..., description="Unique ID for this CTM (format: ctm_<timestamp>)")
    phase: str = Field(..., description="Pipeline phase when CTM was generated")
    token_usage_pct: float = Field(..., ge=0.9, le=1.0, description="Token budget percentage at generation (>=0.9)")
    generated_at: str = Field(..., description="ISO 8601 timestamp of generation")

    abandoned_paths: List[Dict[str, str]] = Field(
        default=[],
        description="Paths/approaches abandoned during this conversation with reasons"
    )
    micro_decisions: List[Dict[str, str]] = Field(
        default=[],
        description="Micro-decisions made during analysis (what, why, alternatives considered)"
    )
    immediate_goals: List[str] = Field(
        default=[],
        description="Immediate tactical goals right before the cutoff"
    )
    partial_results: List[Dict[str, str]] = Field(
        default=[],
        description="Incomplete results or computations in progress"
    )
    open_questions: List[str] = Field(
        default=[],
        description="Unresolved questions the next conversation should address"
    )
    state_file_refs: List[str] = Field(
        default=[],
        description="Paths to relevant state files, checkpoints, and outputs"
    )
    handoff_notes: str = Field(
        default="",
        description="Free-form notes for the next conversation to understand context"
    )


class DAGNode(BaseModel):
    """A single node in the execution DAG representing a script run."""

    node_id: str = Field(..., description="Unique node ID (format: <script_name>_<iteration_id>_<run_index>)")
    script_path: str = Field(..., description="Path to the script that was executed")
    iteration_id: Optional[str] = Field(default=None, description="Iteration ID if this was part of an iteration (e.g., 001, 002)")
    depends_on: List[str] = Field(default=[], description="List of node_ids this execution depends on")
    input_files: List[str] = Field(default=[], description="Input data files consumed by this script")
    output_files: List[str] = Field(default=[], description="Output files produced by this script")
    status: str = Field(default="pending", description="Execution status: pending, running, complete, failed")
    timestamp: str = Field(..., description="ISO 8601 timestamp of execution")
    data_hash_in: Dict[str, str] = Field(default={}, description="SHA-256 hashes of input files at execution time")
    data_hash_out: Dict[str, str] = Field(default={}, description="SHA-256 hashes of output files at execution time")


class ExecutionDAG(BaseModel):
    """Directed Acyclic Graph tracking script execution lineage across iterations.

    Maintains a complete record of which scripts ran, in what order, what data
    they consumed/produced, and how iterations branch from prior executions.
    """

    schema_version: str = Field(default="7.0.0", description="Schema version")
    project: str = Field(default="", description="Project title")
    nodes: Dict[str, DAGNode] = Field(default={}, description="All execution nodes keyed by node_id")
    edges: List[Dict[str, str]] = Field(
        default=[],
        description="Directed edges: [{from: node_id, to: node_id}]"
    )
    last_updated: str = Field(..., description="ISO 8601 timestamp of last update")


class ResearchState(BaseModel):
    """Global research state ledger — single source of truth."""

    run_id: str = Field(..., description="UUID for this research run")
    project: str = Field(..., description="Project title")
    phase: str = Field(..., description="Current pipeline phase")
    step: int = Field(..., ge=0, description="Current step within phase")
    checkpoints: Dict[str, str] = Field(
        default={}, description="Phase completion status: {phase: status}"
    )
    active_hypotheses: List[dict] = Field(default=[], description="Active hypotheses being tested")
    dead_ends: List[str] = Field(default=[], description="Approaches tried and abandoned")
    loaded_data: List[str] = Field(default=[], description="Paths to loaded data files")
    domain_classification: Optional[str] = Field(
        default=None, description="Leaf-node domain classification from domain registry"
    )
    required_containers: List[str] = Field(
        default=[], description="Containers required for this project"
    )
    tool_availability: Dict[str, str] = Field(
        default={}, description="Tool availability map: tool_id -> AVAILABLE/INSTALLABLE/MISSING"
    )
    format_manifest_path: Optional[str] = Field(
        default=None, description="Path to data format manifest JSON"
    )
    execution_runtimes: List[str] = Field(
        default=[], description="Execution runtimes used (python, r, bash, etc.)"
    )
    token_budget: TokenBudget = Field(...)
    last_checkpoint: str = Field(..., description="ISO 8601 timestamp of last checkpoint")
    errors: List[str] = Field(default=[], description="List of error messages")
    resumable_from: Optional[str] = Field(default=None, description="Phase:step to resume from")
    context_transfer_memos: List[ContextTransferMemo] = Field(
        default=[], description="History of CTMs generated at token budget thresholds"
    )
    execution_dag_path: Optional[str] = Field(
        default=None, description="Path to the execution DAG JSON file"
    )
    data_scale_profile: Optional[Dict[str, str]] = Field(
        default=None, description="Data scale profile: {file_path: 'small'|'medium'|'large'|'massive'}"
    )
