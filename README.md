```text                            
████▄  ██  ██ █████▄  ▄████▄ 
██  ██ ██  ██ ██▄▄██▄ ██  ██ 
████▀  ▀████▀ ██   ██ ▀████▀ 
                             
```

# DURO CLI

**Exploitability, proven.**

DURO is a DeFi exploit-confirmation CLI that moves security workflows from “possible issue” to **reproducible proof** on forked chain state.

It is designed for:
- protocol security teams
- auditors
- offensive security researchers
- DeFi studios shipping evidence-backed reports

---

## Why DURO

Most tools detect patterns. Few prove exploitability under realistic state.

DURO focuses on:
1. deterministic fork replay
2. criteria-based exploit confirmation
3. auditable evidence bundles
4. regression test generation for patch safety

---

## Core capabilities

- 🍴 Fork state at pinned block
- 🧪 Generate Foundry harnesses from scenarios
- ✅ Classify runs:
  - `CONFIRMED`
  - `NOT_REPRODUCIBLE`
  - `INCONCLUSIVE`
  - `INFRA_FAILED`
- 📦 Export report artifacts (`md`, `json`, logs, manifest)
- 🛡️ Generate regression guard tests from confirmed runs

---

## Installation

## Prerequisites
- Python 3.11+
- Foundry (`forge`, `anvil`)

Install Foundry:
```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

Install DURO (local dev mode):
```bash
git clone https://github.com/<your-org>/duro.git
cd duro
pip install -e .
```

---

## Quickstart (2 min)

```bash
duro init
duro doctor
duro scenario lint scenarios/oracle-manipulation-demo.yaml
duro run scenarios/oracle-manipulation-demo.yaml
duro report export <RUN_ID>
```

---

## Commands

```bash
duro init
duro doctor
duro run <scenario.yaml>
duro show <run_id>
duro report export <run_id>
duro guard generate --run-id <run_id>
duro ls
duro verify <run_id>
```

Use `--help` on every command for details.

### LLM providers
DURO supports provider selection at runtime:

```bash
duro llm list-providers
duro llm test --provider openai --model gpt-5
duro llm test --provider ollama --model qwen2.5-coder:7b
duro llm test --provider gemini --model gemini-2.5-pro
duro llm test --provider anthropic --model claude-sonnet-4-20250514
duro llm test --provider openai --model gpt-5 --fallback openrouter
duro llm test --provider openai --model gpt-5 --json

duro run scenarios/oracle-manipulation-demo.yaml --llm-provider mock
duro run scenarios/oracle-manipulation-demo.yaml --llm-provider ollama --llm-model qwen2.5-coder:7b
duro run scenarios/oracle-manipulation-demo.yaml --llm-provider gemini --llm-model gemini-2.5-pro
```

Environment variables:
- `OPENAI_API_KEY` (OpenAI)
- `ANTHROPIC_API_KEY` (Anthropic)
- `OPENROUTER_API_KEY` (OpenRouter)
- `OPENROUTER_SITE_URL` (optional, default `https://localhost`)
- `OPENROUTER_APP_NAME` (optional, default `duro-cli`)
- `OLLAMA_HOST` (default: `http://127.0.0.1:11434`)
- `GEMINI_API_KEY` or `GOOGLE_API_KEY` (Gemini)

---

## Scenario format (example)

```yaml
id: oracle-manipulation-demo
chain: ethereum
rpc_env: MAINNET_RPC_URL
block: 19750000

target:
  protocol: DemoProtocol
  contracts:
    - "0x0000000000000000000000000000000000000001"

tokens:
  USDC: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

attacker:
  address: "0x000000000000000000000000000000000000BEEF"

success_criteria:
  - type: balance_increase
    token: USDC
    min_amount_wei: "1000000"
  - type: call_succeeds
    label: exploit_path
```

---

## Output artifacts

Each run stores artifacts under `runs/<run_id>/` and `reports/<run_id>/`:

- `result.json`
- `forge.stdout.log`
- `forge.stderr.log`
- generated harness (`.t.sol`)
- `summary.md`
- `summary.json`
- `manifest.sha256`

---

## Classification semantics

- **CONFIRMED**: all success criteria passed on fork replay
- **NOT_REPRODUCIBLE**: exploit path/criteria failed with current assumptions
- **INCONCLUSIVE**: harness/criteria incomplete or ambiguous outcome
- **INFRA_FAILED**: RPC/toolchain/runtime failure blocked reliable execution

---

## Production hardening features (implemented)

- Safety policy gate for generated exploit steps (schema + denylist + limits)
- Deterministic artifact manifests with path-aware integrity verification
- Confidence scoring + confidence breakdown in run/report output
- Provider telemetry in run artifacts (`latency_ms`, attempts, fallback_used)
- Provider fallback in `duro run --llm-fallback ...`
- LLM provider stats command: `duro llm stats`
- 6 scenario templates for core DeFi classes in `scenarios/templates/`
- CI replay suite workflow: `.github/workflows/replay.yml`

## Project status

Current phase: **Alpha+ (hardening in progress)**

Roadmap and release gates:
- `docs/DURO_RELEASE_PLAN.md`
- `docs/GITHUB_ISSUES_P0_P1.md`
- `docs/PROJECT_BOARD.md`

---

## Security notice

DURO is for authorized security testing only.
Do not run against systems/contracts you do not own or have explicit permission to test.

---

## License

MIT (recommended)
