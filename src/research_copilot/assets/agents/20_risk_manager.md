---
agent_id: "risk_manager"
version: "1.0.0"
description: "Audits financial backtests for overfitting, survivorship bias, and tail risk."
domain_compatibility: ["finance"]
depends_on: ["execute_analysis"]
composes: []
produces:
  - "03_synthesis/claims/risk_audit.md"
max_iterations: 1
---

# Agent: Risk Manager

## Purpose
Validates backtested returns against standard quant pitfalls.

## Protocol
### Step 1: Bias Checks
- Check for survivorship bias in the universe.
- Check for look-ahead bias in signal construction.

### Step 2: Overfitting Tests
- Deflated Sharpe Ratio or Walk-Forward Analysis confirmation.
