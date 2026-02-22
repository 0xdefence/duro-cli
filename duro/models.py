from pydantic import BaseModel, Field
from typing import Dict, List

class Target(BaseModel):
    protocol: str
    contracts: List[str] = Field(default_factory=list)

class Scenario(BaseModel):
    id: str
    chain: str
    rpc_env: str
    block: int
    target: Target
    class_type: str | None = None
    tokens: Dict[str, str] = Field(default_factory=dict)
    attacker: Dict[str, str] = Field(default_factory=dict)
    success_criteria: List[dict] = Field(default_factory=list)
    steps: List[dict] = Field(default_factory=list)
