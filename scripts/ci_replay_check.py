#!/usr/bin/env python3
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED = json.loads((ROOT / "scenarios/fixtures/expected.json").read_text())
TEMPLATE_DIR = ROOT / "scenarios/templates"


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stdout)
        print(p.stderr)
        raise RuntimeError(f"command failed: {' '.join(cmd)}")
    return p.stdout.strip()


def main():
    failures = []
    has_rpc = bool(os.getenv("MAINNET_RPC_URL"))

    for sc in sorted(TEMPLATE_DIR.glob("*.yaml")):
        # run command
        out = run(["duro", "run", str(sc), "--llm-provider", "mock"])
        # robust parse of run id from stdout variants
        run_id = None
        for line in out.splitlines():
            line = line.strip()
            if "Run completed:" in line:
                run_id = line.split("Run completed:")[-1].strip()
            elif line.startswith("RUN_ID="):
                run_id = line.split("=", 1)[1].strip()
        if not run_id:
            raise RuntimeError(f"unable to parse run id from output:\n{out}")
        result_path = ROOT / "runs" / run_id / "result.json"
        if not result_path.exists():
            failures.append((sc.stem, "result.json exists", "missing", run_id))
            continue

        data = json.loads(result_path.read_text())
        got_raw = data.get("classification")
        got = str(got_raw or "").strip().lower()
        exp_raw = EXPECTED.get(data.get("scenario_id"))
        exp = str(exp_raw or "").strip().lower()

        # In smoke CI without MAINNET_RPC_URL, infra failures are expected.
        if not has_rpc and got == "infra_failed":
            continue

        if exp and got != exp:
            failures.append((data.get("scenario_id"), exp, got, run_id))

    if failures:
        for f in failures:
            print(f"FAIL scenario={f[0]} expected={f[1]} got={f[2]} run_id={f[3]}")
        print(f"Replay check failed: {len(failures)} mismatch(es)")
        sys.exit(1)

    print("Replay check passed")


if __name__ == "__main__":
    main()
