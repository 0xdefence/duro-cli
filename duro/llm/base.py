from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ExploitPlan:
    steps: List[Dict[str, Any]]
    raw: str


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def generate_exploit_steps(self, scenario: Dict[str, Any], context: str = "") -> ExploitPlan:
        ...
