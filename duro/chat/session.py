"""Session context and follow-up resolution for duro chat REPL.

Tracks last run, scenario, provider across turns and resolves
anaphoric follow-ups like "again", "show it", "use claude".
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .parser import Intent, ParseResult, normalize_provider, parse, _extract_params, PROVIDER_ALIASES, KNOWN_PROVIDERS


@dataclass
class SessionContext:
    last_run_id: str | None = None
    last_scenario_path: str | None = None
    last_provider: str = "mock"
    last_model: str = ""
    last_fallback: str = ""
    last_intent: Intent | None = None
    last_classification: str | None = None
    command_history: list[str] = field(default_factory=list)
    run_id_history: list[str] = field(default_factory=list)

    def update_after_run(self, run_id: str, scenario_path: str | None = None, provider: str | None = None):
        """Update session state after a successful run."""
        self.last_run_id = run_id
        if run_id not in self.run_id_history:
            self.run_id_history.append(run_id)
        if scenario_path:
            self.last_scenario_path = scenario_path
        if provider:
            self.last_provider = provider

    def update_after_command(self, intent: Intent, raw_input: str):
        """Track command history."""
        self.last_intent = intent
        self.command_history.append(raw_input)


# ---------------------------------------------------------------------------
# Follow-up patterns — checked BEFORE normal parse
# ---------------------------------------------------------------------------

_AGAIN_RE = re.compile(r'\b(again|repeat|redo|rerun(\s+it)?)\b', re.I)
_SHOW_IT_RE = re.compile(r'\b(show\s+(it|the\s+result|what\s+happened))\b', re.I)
_EXPORT_IT_RE = re.compile(r'\b(export\s+it|report\s+on\s+that)\b', re.I)
_VERIFY_IT_RE = re.compile(r'\b(verify\s+it|check\s+integrity)\b', re.I)
_WHY_RE = re.compile(r'\b(why|explain|what\s+went\s+wrong)\b', re.I)
_USE_PROVIDER_RE = re.compile(
    r'\b(?:use|switch\s+to|try\s+with)\s+(\w+)\b', re.I
)


def _try_follow_up(text: str, session: SessionContext) -> ParseResult | None:
    """Detect follow-up patterns that reference session context."""
    stripped = text.strip()

    # "again" / "repeat" / "redo" / "rerun it"
    if _AGAIN_RE.search(stripped):
        if session.last_scenario_path:
            return ParseResult(
                intent=Intent.RUN,
                confidence=0.90,
                params={
                    "scenario_path": session.last_scenario_path,
                    "provider": session.last_provider,
                },
                raw_input=text,
                phase="follow_up",
            )
        # No context to repeat — fall through to normal parse
        return None

    # "show it" / "the result" / "what happened"
    if _SHOW_IT_RE.search(stripped):
        if session.last_run_id:
            return ParseResult(
                intent=Intent.SHOW,
                confidence=0.90,
                params={"run_id": session.last_run_id},
                raw_input=text,
                phase="follow_up",
            )
        return None

    # "export it" / "report on that"
    if _EXPORT_IT_RE.search(stripped):
        if session.last_run_id:
            return ParseResult(
                intent=Intent.REPORT_EXPORT,
                confidence=0.90,
                params={"run_id": session.last_run_id},
                raw_input=text,
                phase="follow_up",
            )
        return None

    # "verify it" / "check integrity"
    if _VERIFY_IT_RE.search(stripped):
        if session.last_run_id:
            return ParseResult(
                intent=Intent.VERIFY,
                confidence=0.90,
                params={"run_id": session.last_run_id},
                raw_input=text,
                phase="follow_up",
            )
        return None

    # "use X" / "switch to X" / "try with X"
    m = _USE_PROVIDER_RE.search(stripped)
    if m:
        raw_provider = m.group(1).lower()
        canonical = normalize_provider(raw_provider)
        if canonical in KNOWN_PROVIDERS:
            return ParseResult(
                intent=Intent.SET_PROVIDER,
                confidence=0.95,
                params={"provider": canonical},
                raw_input=text,
                phase="follow_up",
            )

    # "why" / "explain" / "what went wrong"
    if _WHY_RE.search(stripped):
        if session.last_run_id:
            return ParseResult(
                intent=Intent.SHOW,
                confidence=0.85,
                params={"run_id": session.last_run_id, "explain": True},
                raw_input=text,
                phase="follow_up",
            )
        return None

    return None


# ---------------------------------------------------------------------------
# Implicit param injection
# ---------------------------------------------------------------------------

def _inject_from_session(result: ParseResult, session: SessionContext) -> ParseResult:
    """Fill missing params from session context when intent needs them."""
    needs_run_id = {Intent.SHOW, Intent.VERIFY, Intent.REPORT_EXPORT, Intent.GUARD}
    needs_scenario = {Intent.RUN, Intent.RERUN_CHECK, Intent.SCENARIO_LINT}

    if result.intent in needs_run_id and "run_id" not in result.params:
        if session.last_run_id:
            result.params["run_id"] = session.last_run_id

    if result.intent in needs_scenario and "scenario_path" not in result.params:
        if session.last_scenario_path:
            result.params["scenario_path"] = session.last_scenario_path

    # Always inject provider from session if not explicitly set
    if "provider" not in result.params and session.last_provider != "mock":
        result.params["provider"] = session.last_provider

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def resolve(text: str, session: SessionContext) -> ParseResult:
    """Parse input with session-aware follow-up resolution.

    1. Try follow-up patterns (references to session context)
    2. Fall back to normal parse
    3. Inject missing params from session
    """
    # Try follow-up first
    result = _try_follow_up(text, session)
    if result:
        return result

    # Normal parse
    result = parse(text)

    # Inject session context for missing params
    result = _inject_from_session(result, session)

    return result
