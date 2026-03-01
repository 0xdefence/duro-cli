#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys

from duro.hardening import ErrorCode, normalize_exception, validate_provider_config


def main() -> int:
    # wrapper for safer CLI invocation with deterministic error JSON
    provider = os.getenv("DURO_PROVIDER", "mock")
    errs = validate_provider_config(provider, dict(os.environ))
    if errs:
        e = errs[0]
        print(json.dumps({"ok": False, "code": e.code.value, "message": e.message, "details": e.details}, indent=2))
        return 2

    cmd = [sys.executable, "-m", "duro.cli", *sys.argv[1:]]
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True)
        if cp.returncode != 0:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "code": ErrorCode.INFRA_FAILED.value,
                        "message": "duro.cli returned non-zero",
                        "details": {
                            "returncode": cp.returncode,
                            "stderr": (cp.stderr or "")[-1500:],
                            "stdout": (cp.stdout or "")[-1500:],
                        },
                    },
                    indent=2,
                )
            )
            return cp.returncode

        # pass through successful output
        if cp.stdout:
            print(cp.stdout, end="")
        return 0
    except Exception as exc:
        n = normalize_exception(exc)
        print(json.dumps({"ok": False, "code": n.code.value, "message": n.message, "details": n.details}, indent=2))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
