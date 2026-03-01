# P0 Hardening Done (Fast Pass)

This pass implements immediate hardening improvements without changing core behavior.

## Added
- `duro/hardening.py`
  - `ErrorCode` taxonomy
  - provider config validation helpers
  - exception normalization helper
- `scripts/preflight_check.py`
  - pre-run provider env validation
- `tests/test_hardening.py`
  - basic unit tests for taxonomy/config validation
- `tests/test_contract_fixture.py`
  - output fixture shape contract sanity check
- `.github/workflows/hardening.yml`
  - compile + preflight + unit tests
  - python matrix (3.10, 3.11, 3.12)

## Why
- deterministic error taxonomy foundation
- fail-fast config checks
- stronger CI gate coverage

## Still recommended next
- wire `ErrorCode` through CLI/core end-to-end for all exits
- add strict JSON output schema tests for each command
- add structured run logs with provider/latency/fallback reasons
