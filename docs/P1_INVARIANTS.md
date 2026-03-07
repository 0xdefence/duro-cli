# P1 Invariant Scaffold

DURO now supports lightweight scenario invariants for run-level checks.

Add to scenario YAML:

```yaml
invariants:
  - label: must-confirm
    type: classification_is
    expected: confirmed

  - label: max-steps-guard
    type: steps_max
    max: 20

  - label: safety-gate
    type: safety_ok
```

## Supported invariant types

1. `classification_is`
- Params: `expected` (`confirmed|not_reproducible|inconclusive|infra_failed`)

2. `steps_max`
- Params: `max` (integer)

3. `safety_ok`
- No extra params

## Output

`runs/<id>/result.json` includes:

```json
"invariants": {
  "defined": 3,
  "passed": 2,
  "failed": 1,
  "results": [
    {
      "label": "must-confirm",
      "type": "classification_is",
      "passed": false,
      "detail": "expected=confirmed got=not_reproducible"
    }
  ]
}
```

`duro report export <run_id>` includes invariant summary in `reports/<run_id>/summary.md`.
