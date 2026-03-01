# P1 Hardening Done (Follow-up)

This pass adds output-contract validation and a safer CLI wrapper for deterministic failures.

## Added
- `duro/contracts.py`
  - output contract validator
  - status/reason normalizer
- `scripts/validate_output_contract.py`
  - validates JSON output files against DURO contract checks
- `scripts/duro_safe.py`
  - preflight provider config + deterministic failure JSON wrapper around `duro.cli`
- `tests/test_contracts.py`
  - contract validator tests and defaults normalization tests

## Why
- stronger output stability guarantees
- safer external automation invocation path
- better deterministic failure behavior for orchestration systems

## Next recommended
- integrate contract validator into all CLI command emit paths directly
- enforce command-specific schema fixtures and snapshot tests
- include structured latency/provider/fallback logs in each run output
