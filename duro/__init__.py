from __future__ import annotations

import json
import os
from typing import Any

__version__ = "0.1.0-alpha"


def _install_cli_contract_enforcement() -> None:
    """Install lightweight JSON output contract enforcement for CLI paths.

    This patches click.echo globally (package import occurs before `duro.cli` module execution),
    so all command output paths pass through here.

    Behavior:
    - If output is non-JSON text: pass through unchanged.
    - If output is JSON object: normalize status/reason and validate contract.
    - On contract failure: emit deterministic error JSON and exit non-zero.

    Controlled by env:
    - DURO_ENFORCE_CONTRACT=0 disables enforcement.
    """

    if os.getenv("DURO_ENFORCE_CONTRACT", "1") == "0":
        return

    try:
        import click  # type: ignore
        from duro.contracts import normalize_status_reason, validate_cli_output_contract
        from duro.hardening import ErrorCode
    except Exception:
        return

    original_echo = click.echo

    def wrapped_echo(message: Any = None, *args: Any, **kwargs: Any):
        if isinstance(message, str):
            s = message.strip()
            if s.startswith("{") and s.endswith("}"):
                try:
                    payload = json.loads(s)
                    if isinstance(payload, dict):
                        payload = normalize_status_reason(payload)
                        issues = validate_cli_output_contract(payload)
                        if issues:
                            err = {
                                "ok": False,
                                "code": ErrorCode.SCHEMA_ERROR.value,
                                "message": "cli output contract validation failed",
                                "issues": [
                                    {"field": i.field, "message": i.message}
                                    for i in issues
                                ],
                            }
                            return original_echo(json.dumps(err, indent=2), *args, **kwargs)
                        return original_echo(json.dumps(payload, indent=2), *args, **kwargs)
                except Exception:
                    # Non-JSON or JSON we cannot safely normalize -> pass through
                    pass
        return original_echo(message, *args, **kwargs)

    click.echo = wrapped_echo


_install_cli_contract_enforcement()
