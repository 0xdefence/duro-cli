from __future__ import annotations

import json
from typing import Any

import click

from duro.contracts import normalize_status_reason, validate_cli_output_contract
from duro.hardening import ErrorCode


def emit_json_contract(payload: dict[str, Any]) -> None:
    """Emit JSON payload with contract normalization + validation."""
    normalized = normalize_status_reason(payload)
    issues = validate_cli_output_contract(normalized)
    if issues:
        err = {
            "ok": False,
            "code": ErrorCode.SCHEMA_ERROR.value,
            "message": "cli output contract validation failed",
            "issues": [{"field": i.field, "message": i.message} for i in issues],
        }
        click.echo(json.dumps(err, indent=2))
        return
    click.echo(json.dumps(normalized, indent=2))
