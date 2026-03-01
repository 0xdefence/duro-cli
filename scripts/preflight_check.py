#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys

from duro.hardening import validate_provider_config


def main() -> int:
    provider = os.getenv("DURO_PROVIDER", "mock")
    env = dict(os.environ)
    errs = validate_provider_config(provider, env)
    if errs:
        print(json.dumps({
            "ok": False,
            "provider": provider,
            "errors": [
                {"code": e.code.value, "message": e.message, "details": e.details}
                for e in errs
            ],
        }, indent=2))
        return 2
    print(json.dumps({"ok": True, "provider": provider}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
