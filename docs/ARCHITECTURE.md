# Research Copilot Architecture

The system has transitioned from a rigid pipeline to a dynamic, autonomous OS.

## Core Subsystems

```mermaid
flowchart LR
    subgraph Control Plane
        Supervisor[Supervisor Agent]
        Planner[Planner Agent]
    end

    subgraph Cognition & Agents
        Critic[Critic Agent]
        Skeptic[Skeptic Agent]
        Tracker[Cognitive Tracker]
    end

    subgraph Memory & State
        Ledger[State Ledger]
        Synthesizer[Memory Synthesizer]
        Compressor[State Compressor]
    end

    subgraph Execution
        Scheduler[DAG Scheduler]
        Graph[Mutation Engine]
    end

    Supervisor --> Planner
    Planner --> Graph
    Graph --> Scheduler
    Scheduler --> Ledger
    Ledger --> Tracker
    Ledger --> Synthesizer
    Tracker --> Critic
    Tracker --> Skeptic
```

### 1. Agents Layer (`src/research_copilot/agents/`)
Contains the LLM personas (Supervisor, Critic, Skeptic) that steer the research.

### 2. Cognition Layer (`src/research_copilot/cognition/`)
Tracks hypotheses, claims, contradictions, and evidence. Maintains the epistemic state of the project.

### 3. Memory Layer (`src/research_copilot/memory/`)
Synthesizes episodic memory into semantic project context.

### 4. Planning & Execution (`src/research_copilot/planning/`, `src/research_copilot/execution/`)
Builds and executes the directed acyclic graph (DAG) of research tasks.

### 5. Prompts (`src/research_copilot/prompts/`)
Modular, compressed system prompts injected dynamically based on cognitive state.
