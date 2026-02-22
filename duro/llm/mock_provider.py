from __future__ import annotations
from typing import Any, Dict
from .base import ExploitPlan, LLMProvider


class MockProvider(LLMProvider):
    name = "mock"

    def generate_exploit_steps(self, scenario: Dict[str, Any], context: str = "") -> ExploitPlan:
        # Deterministic fallback for local/dev without API keys.
        steps = [{
            "label": "exploit_path",
            "target": (scenario.get("target", {}).get("contracts") or ["0x0000000000000000000000000000000000000001"])[0],
            "calldata": "0x",
            "value": "0",
            "expect_success": True
        }]
        return ExploitPlan(steps=steps, raw="mock")
