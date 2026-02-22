# DURO v0.1.0-alpha Release Notes

## Title
DURO v0.1.0-alpha — Exploitability, proven.

## Summary
This alpha release introduces DURO as a CLI-first DeFi exploit confirmation toolkit focused on reproducible fork-state validation, evidence integrity, and provider-agnostic AI step generation.

## Highlights
- CLI workflow for initialization, diagnostics, scenario execution, reporting, and verification.
- Criteria-to-Solidity assertion injection for exploit confirmation harnesses.
- Multi-provider LLM integration with runtime selection and fallback.
- Step safety policy to block unsafe generated plans before execution.
- Confidence scoring, reason codes, and telemetry in run artifacts.
- Integrity manifests plus single-run and bulk verification.
- CI replay suite with expected classification checks.

## Included commands
- `duro init`
- `duro doctor`
- `duro run <scenario.yaml> [--llm-provider ... --llm-model ... --llm-fallback ...]`
- `duro show <run_id>`
- `duro report export <run_id>`
- `duro verify <run_id>`
- `duro verify --all`
- `duro guard <run_id>`
- `duro ls`
- `duro llm list-providers`
- `duro llm test --provider ... [--fallback ...] [--json]`
- `duro llm stats`

## LLM providers in alpha
- mock
- openai
- gemini
- ollama
- anthropic
- openrouter

## Security / Safety notes
- DURO enforces a safety validation gate on generated exploit steps.
- Plans that violate policy are blocked with explicit safety errors.
- Use DURO only for authorized testing.

## CI and reproducibility
- Replay workflow: `.github/workflows/replay.yml`
- Replay checker: `scripts/ci_replay_check.py`
- Fixtures and expectations: `scenarios/fixtures/expected.json`

## Known limitations (alpha)
- Classification confidence model is baseline and will be refined.
- Some provider token/usage telemetry is not yet normalized.
- Scenario templates are starter references and need broader real-world corpora.

## Upgrade guidance
- Fresh install recommended for alpha users.
- Ensure provider API keys and RPC env vars are configured before `duro run`.

## Suggested GitHub release text
"DURO v0.1.0-alpha is our first public alpha for deterministic DeFi exploit confirmation workflows. This release ships the core CLI, multi-provider LLM integrations, safety gating, confidence-aware classifications, integrity verification, and CI replay checks."
