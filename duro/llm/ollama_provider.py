from __future__ import annotations
import json
import os
import urllib.request
from typing import Any, Dict

from .base import ExploitPlan, LLMProvider


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.model = model

    def generate_exploit_steps(self, scenario: Dict[str, Any], context: str = "") -> ExploitPlan:
        host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
        url = f"{host}/api/generate"

        prompt = (
            "Return ONLY valid JSON with key 'steps' (array). "
            "Each step: {label,target,calldata,value,expect_success}. No markdown.\n"
            f"Scenario:\n{json.dumps(scenario)}\n"
            f"Context:\n{context}"
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        text = body.get("response", "")
        data = json.loads(text)
        steps = data.get("steps", [])
        if not isinstance(steps, list):
            raise RuntimeError("Ollama response missing 'steps' list")
        return ExploitPlan(steps=steps, raw=text)
