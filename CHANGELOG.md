# Changelog

All notable changes to DURO will be documented in this file.

## [0.1.0-alpha] - 2026-02-22

### Added
- DURO CLI scaffolding with branded UX and command structure.
- Core commands: `init`, `doctor`, `run`, `show`, `report export`, `verify`, `guard`, `ls`.
- LLM provider abstraction and adapters:
  - `mock`
  - `openai`
  - `gemini`
  - `ollama`
  - `anthropic`
  - `openrouter`
- `duro llm` commands:
  - `list-providers`
  - `test` (with `--json` and fallback support)
  - `stats`
- Scenario templates for 6 DeFi vulnerability classes:
  - access control
  - oracle manipulation
  - read-only reentrancy
  - signature/approval abuse
  - upgradeable proxy issues
  - governance attacks
- Safety policy gate for exploit steps (validation + denylist + limits).
- Confidence scoring and confidence breakdown in run artifacts.
- Reason code taxonomy in run results.
- Artifact integrity manifest generation and verification.
- CI replay workflow and fixture expectations.
- `duro verify --all` for bulk integrity checks.

### Improved
- Robust CI run-id parsing in replay checker.
- Manifest verification now supports relative-path hashing for nested artifacts.
- Report output includes confidence and telemetry details.

### Notes
- This is an **alpha** release intended for evaluation and iterative hardening.
- Recommended usage: authorized testing environments only.
