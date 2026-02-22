# GitHub Issues Backlog (P0/P1)

Copy each issue into GitHub as-is.

---

## P0-01: Implement `duro doctor` environment checks
**Labels:** `P0`, `cli`, `ux`

### Scope
Implement robust environment diagnostics for forge/anvil/rpc/filesystem.

### Tasks
- Detect forge/anvil presence + version
- Check RPC reachability + timeout
- Validate chain ID compatibility
- Validate write paths (`runs/`, `reports/`, `foundry/`)
- Add `--json` output mode

### Acceptance Criteria
- Healthy env returns exit code 0
- Broken checks return non-zero and include `Fix:` guidance

---

## P0-02: Enforce strict scenario schema + lint command
**Labels:** `P0`, `validation`

### Scope
Create strict scenario schema using Pydantic and expose `duro scenario lint`.

### Tasks
- Add v1 schema model
- Validate addresses/criteria types
- Lint command with human + JSON modes

### Acceptance Criteria
- Invalid scenarios fail fast with clear errors
- Lint command exits non-zero on invalid input

---

## P0-03: Persist deterministic run metadata
**Labels:** `P0`, `engine`, `auditability`

### Scope
Store deterministic metadata required for replay and auditing.

### Tasks
- Save tool versions, chain ID, block
- Save scenario/harness hash
- Save command invocation + timing

### Acceptance Criteria
- `runs/<id>/result.json` includes all required metadata fields

---

## P0-04: Add artifact hashing + `duro verify`
**Labels:** `P0`, `security`, `auditability`

### Scope
Generate and verify artifact integrity manifest.

### Tasks
- Create `manifest.sha256`
- Implement `duro verify <run_id>`

### Acceptance Criteria
- Verification passes for untouched artifacts, fails for tampered artifacts

---

## P0-05: Harden classification states and reason codes
**Labels:** `P0`, `engine`

### Scope
Classification must be strict and explainable.

### Tasks
- Add states: `confirmed`, `not_reproducible`, `inconclusive`, `infra_failed`
- Add reason code taxonomy
- Gate `confirmed` on criteria pass only

### Acceptance Criteria
- Every run has classification + reason code + reason message

---

## P0-06: Add exploit-step generation safety guardrails
**Labels:** `P0`, `security`, `llm`

### Scope
Prevent unsafe generated code execution.

### Tasks
- Add denylist/static checks
- Add manual approval mode
- Save generated code artifacts

### Acceptance Criteria
- Unsafe patterns blocked before execution
- Manual mode prompts and logs approval

---

## P0-07: Add deterministic replay suite in CI
**Labels:** `P0`, `ci`, `quality`

### Scope
Run known scenario fixtures in CI and enforce expected outcomes.

### Tasks
- Add 3–5 replay fixtures
- Add GitHub Actions workflow
- Snapshot expected classifications

### Acceptance Criteria
- PR fails when classification drift occurs unexpectedly

---

## P0-08: Implement config system (`.duro/config.yaml`)
**Labels:** `P0`, `config`

### Scope
Support merged config with env overrides.

### Tasks
- Implement config load/merge order
- Add `duro config show`
- Add profiles (`local`, `ci`)

### Acceptance Criteria
- Effective config can be printed via JSON and is test-covered

---

## P0-09: Standardize error UX + exit code contract
**Labels:** `P0`, `ux`

### Scope
Consistent user-facing errors and documented exit codes.

### Tasks
- Add error formatter with `Fix:` hints
- Document and enforce exit codes
- Add `--verbose` detailed traces

### Acceptance Criteria
- Common failures always include recovery guidance

---

## P0-10: Publish conversion-focused docs
**Labels:** `P0`, `docs`

### Scope
Create docs that let new users run a complete scenario quickly.

### Tasks
- 2-minute quickstart
- Demo walkthrough
- Classification interpretation
- Troubleshooting

### Acceptance Criteria
- External tester succeeds in <10 minutes following docs only

---

## P1-01: Add `duro monitor` TUI
**Labels:** `P1`, `tui`

## P1-02: Add `duro api serve` for studio integration
**Labels:** `P1`, `api`

## P1-03: Slither import and finding-to-scenario bootstrap
**Labels:** `P1`, `integrations`

## P1-04: Multi-chain adapters (Base/Arbitrum/BSC)
**Labels:** `P1`, `multichain`

## P1-05: Signed evidence bundles (cosign/PGP)
**Labels:** `P1`, `security`
