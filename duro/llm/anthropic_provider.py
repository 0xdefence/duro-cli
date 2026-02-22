from __future__ import annotations
import json
import os
from typing import Any, Dict

from .base import ExploitPlan, LLMProvider


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model

    def generate_exploit_steps(self, scenario: Dict[str, Any], context: str = "") -> ExploitPlan:
        try:
            from anthropic import Anthropic  # type: ignore
        except Exception as e:
            raise RuntimeError("anthropic package not installed. pip install anthropic") from e

        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")

        client = Anthropic(api_key=key)
        prompt = (
            "Return ONLY valid JSON with key 'steps' (array). "
            "Each step: {label,target,calldata,value,expect_success}. No markdown.\n"
            f"Scenario:\n{json.dumps(scenario)}\n"
            f"Context:\n{context}"
        )

        msg = client.messages.create(
            model=self.model,
            max_tokens=1400,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}],
        )

        text = ""
        for block in msg.content:
            if getattr(block, "type", "") == "text":
                text += block.text

        data = json.loads(text)
        steps = data.get("steps", [])
        if not isinstance(steps, list):
            raise RuntimeError("Anthropic response missing 'steps' list")
        return ExploitPlan(steps=steps, raw=text)
