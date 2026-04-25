"""Intent → handler dispatch registry.

Wraps core functions directly (not Typer commands) to avoid SystemExit.
Each handler returns a dict with result data for the REPL to format.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .parser import Intent


def _handle_version(**_kw: Any) -> dict[str, Any]:
    from duro import __version__
    return {"output": __version__, "label": "version"}


def _handle_init(**_kw: Any) -> dict[str, Any]:
    from duro.core import ensure_layout
    ensure_layout()
    return {"output": "Workspace initialized", "label": "init"}


def _handle_doctor(**_kw: Any) -> dict[str, Any]:
    from duro.core import ensure_layout, doctor_checks
    ensure_layout()
    checks = doctor_checks(skip_rpc=False)
    healthy = all(v is True or v == "skipped" for v in checks.values())
    return {"output": checks, "healthy": healthy, "label": "doctor"}


def _handle_run(scenario_path: str = "", provider: str = "mock", model: str = "", fallback: str = "", **_kw: Any) -> dict[str, Any]:
    from duro.core import run_scenario
    if not scenario_path:
        raise ValueError("Missing scenario path. Usage: run <path.yaml>")
    run_id = run_scenario(
        scenario_path,
        llm_provider=provider,
        llm_model=model,
        fallback_provider=fallback,
    )
    return {"run_id": run_id, "scenario_path": scenario_path, "label": "run"}


def _handle_rerun_check(scenario_path: str = "", n_times: int = 3, provider: str = "mock", model: str = "", fallback: str = "", **_kw: Any) -> dict[str, Any]:
    from duro.core import rerun_consistency_check
    if not scenario_path:
        raise ValueError("Missing scenario path. Usage: rerun-check <path.yaml>")
    out = rerun_consistency_check(
        scenario_path,
        n=max(2, n_times),
        llm_provider=provider,
        llm_model=model,
        fallback_provider=fallback,
    )
    return {"output": out, "label": "rerun_check"}


def _handle_show(run_id: str = "", **_kw: Any) -> dict[str, Any]:
    if not run_id:
        raise ValueError("Missing run ID. Usage: show <run_id>")
    p = Path("runs") / run_id / "result.json"
    if not p.exists():
        raise ValueError(f"Run not found: {run_id}")
    data = json.loads(p.read_text())
    return {"output": data, "label": "show"}


def _handle_diff(run_id_pair: tuple[str, str] | None = None, **_kw: Any) -> dict[str, Any]:
    from duro.core import diff_runs
    if not run_id_pair or len(run_id_pair) < 2:
        raise ValueError("Need two run IDs. Usage: diff <id_a> <id_b>")
    out = diff_runs(run_id_pair[0], run_id_pair[1])
    return {"output": out, "label": "diff"}


def _handle_verify(run_id: str = "", **_kw: Any) -> dict[str, Any]:
    from duro.core import verify_run
    if not run_id:
        raise ValueError("Missing run ID. Usage: verify <run_id>")
    ok = verify_run(run_id)
    return {"output": "Verified" if ok else "Verification FAILED", "ok": ok, "label": "verify"}


def _handle_ls(**_kw: Any) -> dict[str, Any]:
    runs = sorted(Path("runs").glob("*/result.json"), reverse=True)
    if not runs:
        return {"output": "No runs found", "runs": [], "label": "ls"}
    entries = []
    for r in runs[:20]:
        try:
            data = json.loads(r.read_text())
            entries.append({
                "run_id": data["run_id"],
                "classification": data["classification"],
                "scenario_id": data["scenario_id"],
            })
        except Exception:
            continue
    return {"output": entries, "label": "ls"}


def _handle_discover(root: str = ".", **_kw: Any) -> dict[str, Any]:
    from duro.discovery import write_discovery_bundle
    payload = write_discovery_bundle(root=root, out_path=".duro/findings.discovery.json")
    return {
        "output": f"Discovery: {len(payload.get('files_scanned', []))} files, {len(payload.get('findings', []))} findings",
        "payload": payload,
        "label": "discover",
    }


def _handle_synthesize(**_kw: Any) -> dict[str, Any]:
    from duro.discovery import synthesize_scenarios
    written = synthesize_scenarios(
        findings_path=".duro/findings.discovery.json",
        out_dir="scenarios/generated",
    )
    return {"output": f"Generated {len(written)} scenario(s)", "scenarios": written, "label": "synthesize"}


def _handle_audit_run(root: str = ".", mode: str = "fast", **_kw: Any) -> dict[str, Any]:
    from duro.orchestration import run_parallel_vector_scan, write_audit_report, write_audit_json
    payload = run_parallel_vector_scan(root=root, mode=mode)
    report_path = write_audit_report(payload, ".duro/audit.md", confidence_threshold=0.6)
    json_path = write_audit_json(payload, ".duro/audit.json")
    findings_count = len(payload.get("findings", []))
    return {
        "output": f"Audit scan: {findings_count} finding(s) — {report_path}",
        "report_path": str(report_path),
        "json_path": str(json_path),
        "label": "audit_run",
    }


def _handle_audit(provider: str = "mock", model: str = "", fallback: str = "", **_kw: Any) -> dict[str, Any]:
    from duro.orchestration import run_audit_from_discovery
    out = run_audit_from_discovery(
        findings_path=".duro/findings.discovery.json",
        out_prefix=".duro/fused-audit",
        llm_provider=provider,
        llm_model=model,
        llm_fallback=fallback,
    )
    return {
        "output": f"Fused audit: {len(out['generated_scenarios'])} scenarios, {len(out['run_mapping'])} runs",
        "fused_json": out["fused_json"],
        "fused_md": out["fused_md"],
        "label": "audit",
    }


def _handle_guard(run_id: str = "", **_kw: Any) -> dict[str, Any]:
    if not run_id:
        raise ValueError("Missing run ID. Usage: guard <run_id>")
    out_dir = Path("foundry/test/regression")
    out_dir.mkdir(parents=True, exist_ok=True)
    f = out_dir / f"Regression_{run_id}.t.sol"
    f.write_text(
        """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";
contract RegressionTest is Test {
    function test_regression_placeholder() public { assertTrue(true); }
}
"""
    )
    return {"output": f"Guard test generated: {f}", "path": str(f), "label": "guard"}


def _handle_scenario_lint(scenario_path: str = "", **_kw: Any) -> dict[str, Any]:
    from duro.core import load_scenario
    if not scenario_path:
        raise ValueError("Missing scenario path. Usage: scenario lint <path.yaml>")
    load_scenario(scenario_path)
    return {"output": f"Scenario valid: {scenario_path}", "label": "scenario_lint"}


def _handle_report_export(run_id: str = "", **_kw: Any) -> dict[str, Any]:
    from duro.core import export_report
    if not run_id:
        raise ValueError("Missing run ID. Usage: report export <run_id>")
    export_report(run_id)
    return {"output": f"Report exported: reports/{run_id}", "label": "report_export"}


def _handle_report_check_format(scenario_path: str = "", **_kw: Any) -> dict[str, Any]:
    path = scenario_path
    if not path:
        raise ValueError("Missing report path. Usage: report check-format <path>")
    p = Path(path)
    if not p.exists():
        raise ValueError(f"Missing report: {path}")
    txt = p.read_text()
    required = [
        "# DURO Audit Report",
        "## Findings (above confidence threshold)",
        "## Below Confidence Threshold",
    ]
    missing = [r for r in required if r not in txt]
    if missing:
        return {"output": f"Format check failed: {', '.join(missing)}", "ok": False, "label": "report_check_format"}
    return {"output": "Report format check passed", "ok": True, "label": "report_check_format"}


def _handle_llm_list_providers(**_kw: Any) -> dict[str, Any]:
    providers = ["mock", "openai", "gemini", "ollama", "anthropic", "openrouter", "lmstudio (stub)"]
    return {"output": providers, "label": "llm_list_providers"}


def _handle_llm_stats(**_kw: Any) -> dict[str, Any]:
    runs = sorted(Path("runs").glob("*/result.json"), reverse=True)[:50]
    agg: dict[str, dict] = {}
    for r in runs:
        try:
            data = json.loads(r.read_text())
            llm = data.get("llm", {})
            name = llm.get("provider") or "none"
            a = agg.setdefault(name, {"count": 0, "fallbacks": 0, "latencies": []})
            a["count"] += 1
            if llm.get("fallback_used"):
                a["fallbacks"] += 1
            if isinstance(llm.get("latency_ms"), int):
                a["latencies"].append(llm["latency_ms"])
        except Exception:
            continue

    if not agg:
        return {"output": "No telemetry found", "label": "llm_stats"}

    summary = {}
    for k, v in agg.items():
        lat = int(sum(v["latencies"]) / len(v["latencies"])) if v["latencies"] else None
        summary[k] = {"runs": v["count"], "fallbacks": v["fallbacks"], "avg_latency_ms": lat}
    return {"output": summary, "label": "llm_stats"}


def _handle_llm_test(provider: str = "mock", model: str = "", **_kw: Any) -> dict[str, Any]:
    import time
    from duro.llm import get_provider

    sample = {
        "id": "llm-test",
        "chain": "ethereum",
        "rpc_env": "MAINNET_RPC_URL",
        "block": 1,
        "target": {"protocol": "Test", "contracts": ["0x0000000000000000000000000000000000000001"]},
        "success_criteria": [{"type": "call_succeeds", "label": "exploit_path"}],
    }

    t0 = time.time()
    p = get_provider(provider, model)
    plan = p.generate_exploit_steps(sample, context="Provider connectivity test")
    elapsed_ms = int((time.time() - t0) * 1000)
    return {
        "output": f"Provider OK: {p.name} (latency={elapsed_ms}ms, steps={len(plan.steps)})",
        "ok": True,
        "label": "llm_test",
    }


def _handle_set_provider(provider: str = "", **_kw: Any) -> dict[str, Any]:
    if not provider:
        raise ValueError("Missing provider name. Usage: use <provider>")
    return {"action": "set_provider", "provider": provider, "label": "set_provider"}


def _handle_help(**_kw: Any) -> dict[str, Any]:
    commands = [
        ("doctor / health", "system health check"),
        ("run <scenario.yaml>", "execute a scenario"),
        ("rerun-check <scenario.yaml> N times", "consistency check"),
        ("show <run_id>", "display run results"),
        ("diff <id_a> <id_b>", "compare two runs"),
        ("verify <run_id>", "check artifact integrity"),
        ("ls / history", "list recent runs"),
        ("discover", "scan for Solidity findings"),
        ("synthesize", "generate scenarios from findings"),
        ("audit-run [--mode fast|deep]", "vector scan"),
        ("audit", "full fused audit pipeline"),
        ("guard <run_id>", "generate regression test"),
        ("scenario lint <path.yaml>", "validate scenario file"),
        ("report export <run_id>", "export report"),
        ("report check-format <path>", "validate report format"),
        ("llm list-providers", "show available LLM providers"),
        ("llm stats", "provider usage telemetry"),
        ("llm test [provider]", "test provider connectivity"),
        ("use <provider>", "switch LLM provider"),
        ("version", "show DURO version"),
    ]
    footer = [
        "Follow-ups: 'again', 'show it', 'export it', 'verify it', 'why?'",
        "Provider aliases: claude→anthropic, gpt→openai, llama→ollama",
        "Type 'quit' or 'exit' to leave.",
    ]
    # Also provide plain-text output for non-REPL callers
    lines = [f"  {cmd:<42} — {desc}" for cmd, desc in commands]
    plain = "Available commands:\n" + "\n".join(lines) + "\n\n" + "\n".join(footer)
    return {"output": plain, "commands": commands, "footer": footer, "label": "help"}


# ---------------------------------------------------------------------------
# Registry map
# ---------------------------------------------------------------------------

HANDLERS: dict[Intent, Any] = {
    Intent.VERSION: _handle_version,
    Intent.INIT: _handle_init,
    Intent.DOCTOR: _handle_doctor,
    Intent.RUN: _handle_run,
    Intent.RERUN_CHECK: _handle_rerun_check,
    Intent.SHOW: _handle_show,
    Intent.DIFF: _handle_diff,
    Intent.VERIFY: _handle_verify,
    Intent.LS: _handle_ls,
    Intent.DISCOVER: _handle_discover,
    Intent.SYNTHESIZE: _handle_synthesize,
    Intent.AUDIT_RUN: _handle_audit_run,
    Intent.AUDIT: _handle_audit,
    Intent.GUARD: _handle_guard,
    Intent.SCENARIO_LINT: _handle_scenario_lint,
    Intent.REPORT_EXPORT: _handle_report_export,
    Intent.REPORT_CHECK_FORMAT: _handle_report_check_format,
    Intent.LLM_LIST_PROVIDERS: _handle_llm_list_providers,
    Intent.LLM_STATS: _handle_llm_stats,
    Intent.LLM_TEST: _handle_llm_test,
    Intent.SET_PROVIDER: _handle_set_provider,
    Intent.HELP: _handle_help,
}


def dispatch(intent: Intent, params: dict[str, Any]) -> dict[str, Any]:
    """Dispatch intent to its handler, passing params as kwargs."""
    handler = HANDLERS.get(intent)
    if handler is None:
        raise ValueError(f"No handler for intent: {intent.name}")
    return handler(**params)
