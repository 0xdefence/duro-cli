# P2 CLI Contract Enforcement

This pass wires output-contract checks directly into CLI execution paths by installing
package-level `click.echo` JSON contract enforcement in `duro/__init__.py`.

## What it does
- Intercepts JSON object output emitted through `click.echo`.
- Normalizes `status`/`reason` fields.
- Validates output contract (`status/result/summary/findings` presence + type checks).
- Emits deterministic schema error payload on invalid contract.

## Control
- `DURO_ENFORCE_CONTRACT=1` (default): enabled
- `DURO_ENFORCE_CONTRACT=0`: disabled

## Why
Ensures all command output paths using Click echo are contract-guarded without requiring
manual edits per command function.
