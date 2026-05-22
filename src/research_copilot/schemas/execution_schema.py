"""Schema definitions for execution results and tool availability."""

from pydantic import ConfigDict, BaseModel, Field
from typing import List, Optional


class ExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    """Structured result from any runtime execution."""

    runtime: str = Field(..., description="Runtime used (python, r, bash, etc.)")
    script_path: str = Field(..., description="Path to executed script or command")
    exit_code: int = Field(..., description="Process exit code")
    stdout: str = Field(default="", description="Captured stdout")
    stderr: str = Field(default="", description="Captured stderr")
    duration_seconds: float = Field(..., description="Execution duration in seconds")
    container_used: Optional[str] = Field(default=None, description="Container image or runtime used")
    artifacts_produced: List[str] = Field(default=[], description="Artifacts produced by the execution")


class ToolStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")
    """Availability status for a single tool."""

    tool_id: str = Field(..., description="Tool registry ID")
    status: str = Field(..., description="AVAILABLE/INSTALLABLE/MISSING_REQUIRES_CONTAINER")
    version: Optional[str] = Field(default=None, description="Detected version string")
    install_cmd: Optional[str] = Field(default=None, description="Installation command")


class ToolAvailabilityReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    """Report of tool availability for a given analysis blueprint."""

    generated_at: str = Field(..., description="ISO 8601 timestamp")
    blueprint: str = Field(..., description="Path to analysis blueprint")
    tools: List[ToolStatus] = Field(default=[], description="Tool availability entries")
