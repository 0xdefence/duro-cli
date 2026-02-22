from __future__ import annotations
import json
import os
from typing import Any, Dict

from .base import ExploitPlan, LLMProvider


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, model: str = "gpt-5"):
        self.model = model

    def generate_exploit_steps(self, scenario: Dict[str, Any], context: str = "") -> ExploitPlan:
        # Optional dependency pattern so CLI works without provider SDK installed.
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:
            raise RuntimeError("openai package not installed. pip install openai") from e

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        client = OpenAI(api_key=key)
        prompt = (
            "Return ONLY valid JSON with key 'steps' (array). "
            "Each step: {label,target,calldata,value,expect_success}. "
            "No markdown.\n"
            f"Scenario:\n{json.dumps(scenario)}\n"
            f"Context:\n{context}"
        )

        resp = client.responses.create(model=self.model, input=prompt)
        text = resp.output_text
        data = json.loads(text)
        steps = data.get("steps", [])
        if not isinstance(steps, list):
            raise RuntimeError("LLM response missing 'steps' list")
        return ExploitPlan(steps=steps, raw=text)
