from __future__ import annotations
import json
import os
import urllib.request
from typing import Any, Dict

from .base import ExploitPlan, LLMProvider


class OpenRouterProvider(LLMProvider):
    name = "openrouter"

    def __init__(self, model: str = "openai/gpt-4.1-mini"):
        self.model = model

    def generate_exploit_steps(self, scenario: Dict[str, Any], context: str = "") -> ExploitPlan:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")

        prompt = (
            "Return ONLY valid JSON with key 'steps' (array). "
            "Each step: {label,target,calldata,value,expect_success}. No markdown.\n"
            f"Scenario:\n{json.dumps(scenario)}\n"
            f"Context:\n{context}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You produce strict JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "https://localhost"),
                "X-Title": os.getenv("OPENROUTER_APP_NAME", "duro-cli"),
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        text = body["choices"][0]["message"]["content"]
        data = json.loads(text)
        steps = data.get("steps", [])
        if not isinstance(steps, list):
            raise RuntimeError("OpenRouter response missing 'steps' list")
        return ExploitPlan(steps=steps, raw=text)
