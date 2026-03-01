# P3 CLI Emit Helper (Monkeypatch Removal)

This pass removes package-level `click.echo` monkeypatching and introduces explicit JSON emit enforcement.

## Changes
- Removed global import-time monkeypatch from `duro/__init__.py`.
- Added `duro/emit.py` with `emit_json_contract(payload)`.
- Updated `duro/cli.py` to use `emit_json_contract(...)` for JSON output paths.
- Added `tests/test_emit.py` for valid/invalid payload emission behavior.

## Why
- Avoid broad side effects from monkeypatching Click globally.
- Make output contract checks explicit at command emit sites.
- Reduce risk for non-CLI imports and third-party integrations.
