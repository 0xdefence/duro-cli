# DURO v0.2 Architect Review — Smart Contract Audit Tooling

## Executive Summary
DURO is currently a strong **exploit confirmation engine** built around Foundry harness execution and reproducibility classification.

It is **not yet** a full multi-tool audit orchestrator.

## Current Capability (Shipped)

DURO can currently:
- run reproducibility checks via Foundry (`forge test`)
- generate exploit harnesses from scenario + steps
- classify outcomes:
  - `CONFIRMED`
  - `NOT_REPRODUCIBLE`
  - `INCONCLUSIVE`
  - `INFRA_FAILED`
- enforce safety gating on generated exploit steps
- use LLM providers for exploit-step drafting (OpenAI/Gemini/Anthropic/Ollama/OpenRouter/etc.)
- export reports and integrity manifests

This is suitable for:
- “Can this issue be reproduced/exploited on a fork-style harness?”

## Gap to Full Audit Stack

DURO does not yet orchestrate common audit tools such as:
- Slither
- Mythril
- Aderyn
- Echidna
- Medusa
- Semgrep custom Solidity rules
- Halmos/symbolic tooling
- Tenderly trace pipelines

## v0.2 Priority Roadmap

### 1) Tool Adapter Interface
Create `duro/tools/*.py` adapters with a common contract.

Proposed interface:
- `name()`
- `check_available()`
- `run(target, options) -> ToolRunResult`
- `parse(raw_output) -> list[Finding]`

### 2) First Adapters
Implement first-party adapters for:
- Slither (`slither . --json`)
- Echidna (bounded fuzz pass)
- Optional Mythril quick scan

### 3) Unified Finding Schema
Normalize all tool outputs into a DURO-native schema:
- `finding_id`
- `title`
- `severity`
- `confidence`
- `source_tool`
- `location`
- `evidence`
- `artifacts`

### 4) Correlation Layer
Use normalized findings to:
- map findings to scenario templates
- auto-generate candidate DURO scenarios
- run reproducibility confirmation loop

### 5) New Command Surface
Add:

```bash
duro audit run <target> --tools slither,echidna,forge
```

### 6) Artifact Expansion
Per-run artifacts should include:
- raw tool outputs
- normalized findings JSON
- scenario mapping log
- reproducibility outcomes linked to finding IDs

## Target Outcome
DURO evolves from:
- “exploit confirmation engine”

to:
- “audit toolchain aggregator + exploit confirmation + evidence fusion”.
