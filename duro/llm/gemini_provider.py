from __future__ import annotations
import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict

from .base import ExploitPlan, LLMProvider


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, model: str = "gemini-2.5-pro"):
        self.model = model

    def generate_exploit_steps(self, scenario: Dict[str, Any], context: str = "") -> ExploitPlan:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set")

        model_enc = urllib.parse.quote(self.model, safe="")
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model_enc}:generateContent"
            f"?key={urllib.parse.quote(api_key, safe='')}"
        )

        prompt = (
            "Return ONLY valid JSON with key 'steps' (array). "
            "Each step: {label,target,calldata,value,expect_success}. No markdown.\n"
            f"Scenario:\n{json.dumps(scenario)}\n"
            f"Context:\n{context}"
        )

        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        candidates = body.get("candidates", [])
        if not candidates:
            raise RuntimeError(f"Gemini returned no candidates: {body}")

        parts = candidates[0].get("content", {}).get("parts", [])
        text = ""
        for p in parts:
            if "text" in p:
                text += p["text"]

        data = json.loads(text)
        steps = data.get("steps", [])
        if not isinstance(steps, list):
            raise RuntimeError("Gemini response missing 'steps' list")
        return ExploitPlan(steps=steps, raw=text)
