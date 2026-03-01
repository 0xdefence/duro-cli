#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from duro.contracts import validate_cli_output_contract


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: validate_output_contract.py <json_file>")
        return 2

    p = Path(sys.argv[1])
    if not p.exists():
        print(json.dumps({"ok": False, "error": f"missing file: {p}"}, indent=2))
        return 2

    try:
        payload = json.loads(p.read_text())
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"invalid json: {exc}"}, indent=2))
        return 2

    issues = validate_cli_output_contract(payload)
    if issues:
        print(
            json.dumps(
                {
                    "ok": False,
                    "issues": [{"field": i.field, "message": i.message} for i in issues],
                },
                indent=2,
            )
        )
        return 1

    print(json.dumps({"ok": True, "file": str(p)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
