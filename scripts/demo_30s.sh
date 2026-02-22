#!/usr/bin/env bash
set -euo pipefail

SCENARIO="scenarios/templates/access-control.yaml"

duro init >/dev/null || true

echo "[DURO] running quick demo..."
OUT=$(duro run "$SCENARIO" --llm-provider mock --no-banner)
echo "$OUT"
RUN_ID=$(echo "$OUT" | awk -F'Run completed: ' '/Run completed:/{print $2}' | tail -n1)

if [ -z "${RUN_ID:-}" ]; then
  echo "Failed to parse RUN_ID"
  exit 1
fi

echo "\n[DURO] run summary:"
duro show "$RUN_ID"

echo "\n[DURO] export report:"
duro report export "$RUN_ID"

echo "Done."
