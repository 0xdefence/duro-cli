from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ContractIssue:
    field: str
    message: str


REQUIRED_TOP_LEVEL_ANY = (
    ("status",),
    ("result",),
    ("summary",),
    ("findings",),
)


def validate_cli_output_contract(payload: dict[str, Any]) -> list[ContractIssue]:
    issues: list[ContractIssue] = []
    if not isinstance(payload, dict):
        return [ContractIssue(field="$", message="payload must be an object")]

    if not any(all(k in payload for k in group) for group in REQUIRED_TOP_LEVEL_ANY):
        issues.append(
            ContractIssue(
                field="$",
                message="payload missing expected top-level contract keys (status/result/summary/findings)",
            )
        )

    if "status" in payload and not isinstance(payload.get("status"), str):
        issues.append(ContractIssue(field="status", message="status must be a string"))

    if "findings" in payload and not isinstance(payload.get("findings"), list):
        issues.append(ContractIssue(field="findings", message="findings must be an array when present"))

    return issues


def normalize_status_reason(payload: dict[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    status = out.get("status")
    reason = out.get("reason")

    if status is None:
        out["status"] = "ok" if out.get("result") else "unknown"

    if reason is None:
        out["reason"] = "unspecified"

    return out
