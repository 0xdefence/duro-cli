# DURO Release Plan (Alpha → Credible Public Release)

## P0 (Must-have before public alpha)

## 1) `duro doctor` real checks
**Goal:** Fast environment validation with actionable fixes.

**Tasks**
- [ ] Check `forge` exists and parse version
- [ ] Check `anvil` exists and parse version
- [ ] Check RPC URL reachable (timeout + status)
- [ ] Check chain ID and compare with scenario chain
- [ ] Check write permissions for `runs/`, `reports/`, `foundry/`

**Acceptance criteria**
- `duro doctor` exits `0` when healthy, non-zero otherwise
- Every failure includes `Fix:` guidance
- `--json` output includes per-check status and reason

---

## 2) Strict scenario schema
**Goal:** Reject ambiguous/malformed scenarios early.

**Tasks**
- [ ] Pydantic models for scenario v1
- [ ] Address validation (`0x` + 40 hex)
- [ ] Required fields enforced (`id`, `chain`, `rpc_env`, `block`, `success_criteria`)
- [ ] Criterion-specific validation (`balance_increase`, `call_succeeds`, etc.)
- [ ] `duro scenario lint` command

**Acceptance criteria**
- Invalid scenario returns clear line-level error
- Lint exits non-zero on errors
- Lint supports `--json`

---

## 3) Deterministic run metadata
**Goal:** Replayability and auditability.

**Tasks**
- [ ] Persist tool versions (`forge/anvil/duro`)
- [ ] Persist chain ID, block number, RPC host hash/fingerprint
- [ ] Persist scenario hash and harness hash
- [ ] Persist start/end timestamps + duration
- [ ] Persist full command invocation

**Acceptance criteria**
- `runs/<id>/result.json` contains all metadata fields
- Two re-runs on same block show identical metadata baseline (except timestamps/run_id)

---

## 4) Artifact manifest + integrity
**Goal:** Evidence tamper detection.

**Tasks**
- [ ] Generate `manifest.sha256` for all run artifacts
- [ ] Include scenario/harness/log/report hashes
- [ ] Add `duro verify <run_id>` command

**Acceptance criteria**
- `duro verify <run_id>` returns success on untouched artifacts
- Returns failure if any artifact is modified

---

## 5) Classification hardening
**Goal:** Trustworthy outcomes.

**Tasks**
- [ ] Enforce `confirmed` only when all success criteria pass
- [ ] Add distinct `infra_failed` state
- [ ] Add reason code taxonomy (e.g., `CRITERIA_FAIL`, `HARNESS_INCOMPLETE`, `RPC_TIMEOUT`)
- [ ] Include confidence score and derivation basis

**Acceptance criteria**
- Classifier outputs one of: `confirmed`, `not_reproducible`, `inconclusive`, `infra_failed`
- Every classification has reason code + human-readable reason

---

## 6) Exploit-step generation safety
**Goal:** Prevent unsafe generated execution.

**Tasks**
- [ ] Add generated-code static checks/denylist
- [ ] Sandbox execution path only under Foundry test harness
- [ ] Add `--manual-approve` mode before execution
- [ ] Save generated steps as artifact

**Acceptance criteria**
- Unsafe patterns are blocked and reported
- Manual mode prompts before execution

---

## 7) Regression suite in CI
**Goal:** Prevent silent behavior drift.

**Tasks**
- [ ] Add 3–5 deterministic scenario fixtures
- [ ] CI job runs `duro run` on fixtures
- [ ] Snapshot expected classifications
- [ ] Fail CI on unexpected diffs

**Acceptance criteria**
- CI green on default branch
- PRs fail when replay outcomes drift unexpectedly

---

## 8) Config system
**Goal:** Predictable defaults across local/dev/CI.

**Tasks**
- [ ] `.duro/config.yaml` support
- [ ] Env var overrides
- [ ] Profile support (`local`, `ci`)
- [ ] `duro config show` command

**Acceptance criteria**
- Config merge order documented and test-covered
- `duro config show --json` prints effective config

---

## 9) Great error UX
**Goal:** Fast user recovery.

**Tasks**
- [ ] Standard error formatter (`ERROR`, `Fix`, `Docs`)
- [ ] Exit code map
- [ ] Add `--verbose` stack traces

**Acceptance criteria**
- All common failure paths include fix hints
- Exit code table documented

---

## 10) Docs that convert
**Goal:** New user can run successful demo in <10 min.

**Tasks**
- [ ] 2-minute quickstart
- [ ] One end-to-end demo script
- [ ] Classification interpretation guide
- [ ] Troubleshooting section

**Acceptance criteria**
- Fresh machine test passes using docs only
- One external tester completes setup in <10 min

---

## P1 (Nice-to-have, post-alpha)

- [ ] `duro monitor` TUI dashboard
- [ ] `duro api serve` for studio integration
- [ ] Slither import → scenario bootstrap
- [ ] Multi-chain adapters (Base/Arbitrum/BSC)
- [ ] Signed report bundles (cosign/PGP)

---

## Launch Gate (ship when all true)

- [ ] `duro run demo.yaml` works on a fresh machine
- [ ] Same scenario on same block gives stable outcome twice
- [ ] Report + manifest generated every run
- [ ] CI replay suite is green
- [ ] Docs validated by someone else end-to-end

---

## Suggested Milestones

### M1 (48h)
- Doctor, schema lint, metadata, manifest, basic docs

### M2 (72h)
- Classification hardening, safety checks, CI replay suite

### M3 (Launch)
- Public alpha tag, release notes, demo artifacts
