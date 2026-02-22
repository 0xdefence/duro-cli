# START HERE (Plain English)

## What DURO does

DURO checks whether a smart-contract issue can be exploited **for real** on forked chain state.

It does not just say "maybe vulnerable".
It runs a simulation and gives a practical answer.

## Output meanings

- **CONFIRMED** → exploit worked in simulation
- **NOT_REPRODUCIBLE** → exploit did not work with current assumptions
- **INCONCLUSIVE** → not enough signal yet
- **INFRA_FAILED** → environment/tooling issue

## Typical user flow

1. Pick a scenario (`scenarios/templates/*.yaml`)
2. Run `duro run <scenario>`
3. Read result + confidence
4. Export report
5. Verify artifact integrity

## Fast commands

```bash
duro init
duro doctor
duro run scenarios/templates/access-control.yaml --llm-provider mock
duro report export <RUN_ID>
duro verify <RUN_ID>
```

## Why this matters

Security teams waste time on false alarms.
DURO helps prioritize what is actually exploitable.
