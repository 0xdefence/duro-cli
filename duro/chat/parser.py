"""3-phase NLP parser for duro chat REPL.

Phase 1: Exact command match (regex strips optional 'duro ' prefix)
Phase 2: Keyword/synonym AND/OR matching
Phase 3: Levenshtein fuzzy fallback (>0.65 threshold)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


# ---------------------------------------------------------------------------
# Intent enum — 24 intents
# ---------------------------------------------------------------------------

class Intent(Enum):
    VERSION = auto()
    INIT = auto()
    DOCTOR = auto()
    RUN = auto()
    RERUN_CHECK = auto()
    SHOW = auto()
    DIFF = auto()
    VERIFY = auto()
    LS = auto()
    DISCOVER = auto()
    SYNTHESIZE = auto()
    AUDIT_RUN = auto()
    AUDIT = auto()
    GUARD = auto()
    SCENARIO_LINT = auto()
    REPORT_EXPORT = auto()
    REPORT_CHECK_FORMAT = auto()
    LLM_LIST_PROVIDERS = auto()
    LLM_STATS = auto()
    LLM_TEST = auto()
    SET_PROVIDER = auto()
    HELP = auto()
    QUIT = auto()
    UNKNOWN = auto()


# ---------------------------------------------------------------------------
# Parse result
# ---------------------------------------------------------------------------

@dataclass
class ParseResult:
    intent: Intent
    confidence: float
    params: dict[str, Any] = field(default_factory=dict)
    raw_input: str = ""
    alternatives: list[tuple[Intent, float]] = field(default_factory=list)
    phase: str = ""


# ---------------------------------------------------------------------------
# Provider aliases
# ---------------------------------------------------------------------------

PROVIDER_ALIASES: dict[str, str] = {
    "claude": "anthropic",
    "gpt": "openai",
    "chatgpt": "openai",
    "google": "gemini",
    "llama": "ollama",
    "local": "ollama",
    "lm-studio": "lmstudio",
    "lm studio": "lmstudio",
}

KNOWN_PROVIDERS = {"mock", "openai", "gemini", "ollama", "anthropic", "openrouter", "lmstudio"}


def normalize_provider(name: str) -> str:
    """Resolve aliases to canonical provider name."""
    n = name.strip().lower()
    return PROVIDER_ALIASES.get(n, n)


# ---------------------------------------------------------------------------
# Parameter extractors
# ---------------------------------------------------------------------------

_RE_YAML_PATH = re.compile(r'([\w./_-]+\.ya?ml)')
_RE_UUID = re.compile(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', re.I)
_RE_PROVIDER = re.compile(r'\b(mock|openai|gemini|ollama|anthropic|openrouter|lmstudio)\b', re.I)
_RE_N_TIMES = re.compile(r'(\d+)\s*times?', re.I)
_RE_MODE = re.compile(r'\b(fast|deep\+adversarial|deep)\b', re.I)


def _extract_params(text: str) -> dict[str, Any]:
    """Extract structured parameters from free-text input."""
    params: dict[str, Any] = {}

    m = _RE_YAML_PATH.search(text)
    if m:
        params["scenario_path"] = m.group(1)

    uuids = _RE_UUID.findall(text)
    if len(uuids) >= 2:
        params["run_id_pair"] = (uuids[0], uuids[1])
    elif len(uuids) == 1:
        params["run_id"] = uuids[0]

    # Provider — skip if it looks like a known command word in context
    m = _RE_PROVIDER.search(text)
    if m:
        params["provider"] = m.group(1).lower()

    # Also check aliases
    lower = text.lower()
    for alias, canonical in PROVIDER_ALIASES.items():
        if re.search(r'\b' + re.escape(alias) + r'\b', lower):
            params["provider"] = canonical
            break

    m = _RE_N_TIMES.search(text)
    if m:
        params["n_times"] = int(m.group(1))

    m = _RE_MODE.search(text)
    if m:
        params["mode"] = m.group(1).lower()

    return params


# ---------------------------------------------------------------------------
# Phase 1: Exact command match
# ---------------------------------------------------------------------------

_EXACT_COMMANDS: list[tuple[re.Pattern, Intent]] = [
    (re.compile(r'^(?:duro\s+)?version$', re.I), Intent.VERSION),
    (re.compile(r'^(?:duro\s+)?init$', re.I), Intent.INIT),
    (re.compile(r'^(?:duro\s+)?doctor$', re.I), Intent.DOCTOR),
    (re.compile(r'^(?:duro\s+)?run\b', re.I), Intent.RUN),
    (re.compile(r'^(?:duro\s+)?rerun[- ]?check\b', re.I), Intent.RERUN_CHECK),
    (re.compile(r'^(?:duro\s+)?show(\s+[0-9a-f][\w-]*)?$', re.I), Intent.SHOW),
    (re.compile(r'^(?:duro\s+)?diff\b', re.I), Intent.DIFF),
    (re.compile(r'^(?:duro\s+)?verify\b', re.I), Intent.VERIFY),
    (re.compile(r'^(?:duro\s+)?ls$', re.I), Intent.LS),
    (re.compile(r'^(?:duro\s+)?discover\b', re.I), Intent.DISCOVER),
    (re.compile(r'^(?:duro\s+)?synthesize\b', re.I), Intent.SYNTHESIZE),
    (re.compile(r'^(?:duro\s+)?audit[- ]?run\b', re.I), Intent.AUDIT_RUN),
    (re.compile(r'^(?:duro\s+)?audit\b(?!.*\brun\b)', re.I), Intent.AUDIT),
    (re.compile(r'^(?:duro\s+)?guard\b', re.I), Intent.GUARD),
    (re.compile(r'^(?:duro\s+)?scenario\s+lint\b', re.I), Intent.SCENARIO_LINT),
    (re.compile(r'^(?:duro\s+)?report\s+export\b', re.I), Intent.REPORT_EXPORT),
    (re.compile(r'^(?:duro\s+)?report\s+check[- ]?format\b', re.I), Intent.REPORT_CHECK_FORMAT),
    (re.compile(r'^(?:duro\s+)?llm\s+list[- ]?providers$', re.I), Intent.LLM_LIST_PROVIDERS),
    (re.compile(r'^(?:duro\s+)?llm\s+stats$', re.I), Intent.LLM_STATS),
    (re.compile(r'^(?:duro\s+)?llm\s+test\b', re.I), Intent.LLM_TEST),
    (re.compile(r'^(?:duro\s+)?(?:help|\?)$', re.I), Intent.HELP),
    (re.compile(r'^(?:duro\s+)?(?:quit|exit|bye|q)$', re.I), Intent.QUIT),
]


def _phase1_exact(text: str) -> ParseResult | None:
    """Try exact command match against known patterns."""
    stripped = text.strip()
    for pattern, intent in _EXACT_COMMANDS:
        if pattern.match(stripped):
            params = _extract_params(stripped)
            return ParseResult(
                intent=intent,
                confidence=1.0,
                params=params,
                raw_input=text,
                phase="exact",
            )
    return None


# ---------------------------------------------------------------------------
# Phase 2: Keyword/synonym matching
# ---------------------------------------------------------------------------

# Each intent maps to a list of keyword groups.
# Within a group, ALL words must be present (AND).
# Across groups, any group matching is sufficient (OR).
KEYWORD_MAP: dict[Intent, list[list[str]]] = {
    Intent.DOCTOR: [
        ["health"],
        ["check", "environment"],
        ["preflight"],
        ["ready"],
        ["system", "check"],
        ["diagnostics"],
    ],
    Intent.RUN: [
        ["run"],
        ["execute"],
        ["confirm", "exploit"],
        ["launch", "scenario"],
        ["run", "scenario"],
    ],
    Intent.RERUN_CHECK: [
        ["rerun"],
        ["consistency", "check"],
        ["run", "times"],
        ["repeat", "run"],
    ],
    Intent.SHOW: [
        ["show", "run"],
        ["display", "result"],
        ["view", "result"],
        ["result", "for"],
        ["what", "happened"],
    ],
    Intent.DIFF: [
        ["compare", "runs"],
        ["diff"],
        ["difference", "between"],
    ],
    Intent.VERIFY: [
        ["verify"],
        ["integrity"],
        ["check", "integrity"],
        ["validate", "artifacts"],
    ],
    Intent.LS: [
        ["list", "runs"],
        ["history"],
        ["recent", "runs"],
        ["show", "all", "runs"],
        ["past", "runs"],
    ],
    Intent.DISCOVER: [
        ["discover"],
        ["scan", "for", "vulnerabilities"],
        ["find", "issues"],
        ["scan", "solidity"],
        ["scan", "contracts"],
        ["find", "vulnerabilities"],
    ],
    Intent.SYNTHESIZE: [
        ["synthesize"],
        ["generate", "scenarios"],
        ["create", "scenarios"],
    ],
    Intent.AUDIT_RUN: [
        ["vector", "scan"],
        ["parallel", "scan"],
        ["audit", "run"],
        ["scan", "mode"],
    ],
    Intent.AUDIT: [
        ["full", "audit"],
        ["fused", "audit"],
        ["end", "to", "end"],
        ["e2e"],
        ["audit", "from", "discovery"],
    ],
    Intent.GUARD: [
        ["guard"],
        ["regression", "test"],
        ["generate", "test"],
        ["foundry", "test"],
    ],
    Intent.SCENARIO_LINT: [
        ["lint", "scenario"],
        ["validate", "scenario"],
        ["check", "scenario"],
        ["scenario", "valid"],
    ],
    Intent.REPORT_EXPORT: [
        ["export", "report"],
        ["generate", "report"],
        ["create", "report"],
    ],
    Intent.REPORT_CHECK_FORMAT: [
        ["check", "format"],
        ["report", "format"],
        ["validate", "report"],
    ],
    Intent.LLM_LIST_PROVIDERS: [
        ["list", "providers"],
        ["available", "providers"],
        ["which", "providers"],
        ["show", "providers"],
    ],
    Intent.LLM_STATS: [
        ["llm", "stats"],
        ["provider", "stats"],
        ["telemetry"],
    ],
    Intent.LLM_TEST: [
        ["test", "provider"],
        ["test", "llm"],
        ["provider", "connectivity"],
    ],
    Intent.SET_PROVIDER: [
        ["use"],
        ["switch", "to"],
        ["change", "provider"],
        ["set", "provider"],
    ],
    Intent.INIT: [
        ["initialize"],
        ["setup", "workspace"],
        ["init", "workspace"],
    ],
    Intent.VERSION: [
        ["version"],
        ["what", "version"],
    ],
    Intent.HELP: [
        ["help"],
        ["commands"],
        ["what", "can"],
    ],
    Intent.QUIT: [
        ["quit"],
        ["exit"],
        ["bye"],
        ["goodbye"],
    ],
}


def _words(text: str) -> set[str]:
    return set(re.findall(r'[a-z0-9+]+', text.lower()))


def _phase2_keywords(text: str) -> ParseResult | None:
    """Try keyword/synonym matching."""
    tokens = _words(text)
    if not tokens:
        return None

    best_intent: Intent | None = None
    best_score = 0.0
    alternatives: list[tuple[Intent, float]] = []

    for intent, groups in KEYWORD_MAP.items():
        for group in groups:
            group_set = set(group)
            if group_set.issubset(tokens):
                # Score = fraction of input tokens matched, with bonus for specificity
                coverage = len(group_set) / max(len(tokens), 1)
                specificity = len(group_set) / 5.0  # normalize to ~0-1
                score = min(0.95, 0.60 + coverage * 0.2 + specificity * 0.15)

                if score > best_score:
                    if best_intent is not None:
                        alternatives.append((best_intent, best_score))
                    best_intent = intent
                    best_score = score
                elif score > 0.5:
                    alternatives.append((intent, score))

    if best_intent is not None:
        # SET_PROVIDER needs a provider in params to be meaningful
        params = _extract_params(text)
        if best_intent == Intent.SET_PROVIDER and "provider" not in params:
            # Try to find a provider alias in the text
            for alias in PROVIDER_ALIASES:
                if alias in text.lower():
                    params["provider"] = PROVIDER_ALIASES[alias]
                    break
            # Also try known providers
            for p in KNOWN_PROVIDERS:
                if p in text.lower():
                    params["provider"] = p
                    break

        return ParseResult(
            intent=best_intent,
            confidence=best_score,
            params=params,
            raw_input=text,
            alternatives=alternatives,
            phase="keyword",
        )

    return None


# ---------------------------------------------------------------------------
# Phase 3: Fuzzy Levenshtein fallback
# ---------------------------------------------------------------------------

def _levenshtein(s1: str, s2: str) -> int:
    """Compute Levenshtein edit distance (stdlib-only)."""
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            cost = 0 if c1 == c2 else 1
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = curr
    return prev[-1]


def _similarity(s1: str, s2: str) -> float:
    """Normalized similarity 0..1."""
    maxlen = max(len(s1), len(s2))
    if maxlen == 0:
        return 1.0
    return 1.0 - _levenshtein(s1, s2) / maxlen


# Flatten keyword groups into representative phrases for fuzzy matching
_FUZZY_PHRASES: list[tuple[str, Intent]] = []
for _intent, _groups in KEYWORD_MAP.items():
    for _group in _groups:
        _FUZZY_PHRASES.append((" ".join(_group), _intent))

# Add exact command names too
_FUZZY_PHRASES.extend([
    ("version", Intent.VERSION),
    ("init", Intent.INIT),
    ("doctor", Intent.DOCTOR),
    ("run", Intent.RUN),
    ("rerun check", Intent.RERUN_CHECK),
    ("show", Intent.SHOW),
    ("diff", Intent.DIFF),
    ("verify", Intent.VERIFY),
    ("ls", Intent.LS),
    ("discover", Intent.DISCOVER),
    ("synthesize", Intent.SYNTHESIZE),
    ("audit run", Intent.AUDIT_RUN),
    ("audit", Intent.AUDIT),
    ("guard", Intent.GUARD),
    ("scenario lint", Intent.SCENARIO_LINT),
    ("report export", Intent.REPORT_EXPORT),
    ("report check format", Intent.REPORT_CHECK_FORMAT),
    ("llm list providers", Intent.LLM_LIST_PROVIDERS),
    ("llm stats", Intent.LLM_STATS),
    ("llm test", Intent.LLM_TEST),
    ("help", Intent.HELP),
    ("quit", Intent.QUIT),
    ("exit", Intent.QUIT),
])

FUZZY_THRESHOLD = 0.65


def _phase3_fuzzy(text: str) -> ParseResult | None:
    """Levenshtein fuzzy match against known phrases."""
    cleaned = text.strip().lower()
    # Strip 'duro ' prefix
    if cleaned.startswith("duro "):
        cleaned = cleaned[5:]

    best_sim = 0.0
    best_intent: Intent | None = None
    alternatives: list[tuple[Intent, float]] = []

    for phrase, intent in _FUZZY_PHRASES:
        sim = _similarity(cleaned, phrase)
        if sim > best_sim:
            if best_intent is not None and best_sim >= FUZZY_THRESHOLD:
                alternatives.append((best_intent, best_sim))
            best_intent = intent
            best_sim = sim
        elif sim >= FUZZY_THRESHOLD:
            alternatives.append((intent, sim))

    if best_intent is not None and best_sim >= FUZZY_THRESHOLD:
        return ParseResult(
            intent=best_intent,
            confidence=best_sim,
            params=_extract_params(text),
            raw_input=text,
            alternatives=alternatives[:3],
            phase="fuzzy",
        )

    return None


# ---------------------------------------------------------------------------
# AUDIT vs AUDIT_RUN disambiguation
# ---------------------------------------------------------------------------

_AUDIT_RUN_SIGNALS = re.compile(r'\b(audit[- ]run|vector|scan|mode|parallel)\b', re.I)
_AUDIT_FUSED_SIGNALS = re.compile(r'\b(fused|e2e|end.to.end|full.audit|from.discovery)\b', re.I)


def _disambiguate_audit(result: ParseResult) -> ParseResult:
    """Refine AUDIT vs AUDIT_RUN when the parser picks one ambiguously."""
    if result.intent not in (Intent.AUDIT, Intent.AUDIT_RUN):
        return result

    text = result.raw_input.lower()

    # Hyphenated "audit-run" is unambiguous
    if "audit-run" in text or "audit_run" in text:
        result.intent = Intent.AUDIT_RUN
        result.confidence = max(result.confidence, 0.90)
        return result

    run_signals = len(_AUDIT_RUN_SIGNALS.findall(text))
    fused_signals = len(_AUDIT_FUSED_SIGNALS.findall(text))

    if run_signals > fused_signals:
        result.intent = Intent.AUDIT_RUN
    elif fused_signals > run_signals:
        result.intent = Intent.AUDIT
    # else: keep original pick (bare "audit" stays AUDIT by default)

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(text: str) -> ParseResult:
    """Parse natural-language input into an intent with parameters.

    Runs 3 phases in order: exact → keyword → fuzzy.
    Returns first match above confidence threshold.
    """
    if not text or not text.strip():
        return ParseResult(
            intent=Intent.UNKNOWN,
            confidence=0.0,
            raw_input=text or "",
            phase="none",
        )

    # Phase 1: exact command match
    result = _phase1_exact(text)
    if result:
        return _disambiguate_audit(result)

    # Phase 2: keyword/synonym match
    result = _phase2_keywords(text)
    if result:
        return _disambiguate_audit(result)

    # Phase 3: fuzzy fallback
    result = _phase3_fuzzy(text)
    if result:
        return _disambiguate_audit(result)

    # Nothing matched
    return ParseResult(
        intent=Intent.UNKNOWN,
        confidence=0.0,
        params=_extract_params(text),
        raw_input=text,
        phase="none",
    )
