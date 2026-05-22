# MCP Integration

Research OS is built natively on the **Model Context Protocol (MCP)**, treating external AI clients and agents as first-class citizens. The MCP implementation provides a highly extensible and dynamic interface for execution and capability management.

## Dynamic Execution Workflow

Agents connect to the daemonized MCP server (`research-os start --daemon`) and execute tools via standard JSON-RPC over `stdio` or `HTTP`.

```mermaid
sequenceDiagram
    participant AI Agent
    participant MCP Server
    participant ToolRegistry
    participant SafetyGater
    participant PlanMutationEngine

    AI Agent->>MCP Server: Call Tool (route_intent)
    MCP Server->>PlanMutationEngine: Build DAG from Intake
    PlanMutationEngine-->>MCP Server: Execution Plan
    
    AI Agent->>MCP Server: Register New Tool
    MCP Server->>ToolRegistry: Add capability dynamically
    
    AI Agent->>MCP Server: Execute High-Risk Tool
    MCP Server->>SafetyGater: ToolCapabilityCheck (>0.85 confidence)
    SafetyGater-->>MCP Server: Approved / Blocked
    MCP Server-->>AI Agent: Tool Response / Error
```

## AI-Driven Extensibility
By exposing the `ToolRegistry` directly via MCP, external AI instances can hot-plug newly authored tools into the OS runtime without restarting the daemon. This establishes an autonomous loop where the OS seamlessly expands its operational surface area in real-time.
