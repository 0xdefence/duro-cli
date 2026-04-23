from pydantic import BaseModel, Field, field_validator
from typing import Any, Dict, List


class StepModel(BaseModel):
    label: str
    target: str
    calldata: str = "0x"
    value: str = "0"
    expect_success: bool = True


class SuccessCriterion(BaseModel):
    type: str
    params: dict = Field(default_factory=dict)


class InvariantModel(BaseModel):
    label: str
    type: str
    expected: str | None = None
    max: int | None = None


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
    invariants: List[dict] = Field(default_factory=list)

    @field_validator("steps", mode="before")
    @classmethod
    def _validate_steps(cls, v: Any) -> List[dict]:
        if not isinstance(v, list):
            return v
        out: List[dict] = []
        for item in v:
            d = item if isinstance(item, dict) else dict(item)
            StepModel.model_validate(d)
            out.append(d)
        return out

    @field_validator("success_criteria", mode="before")
    @classmethod
    def _validate_success_criteria(cls, v: Any) -> List[dict]:
        if not isinstance(v, list):
            return v
        out: List[dict] = []
        for item in v:
            d = item if isinstance(item, dict) else dict(item)
            SuccessCriterion.model_validate(d)
            out.append(d)
        return out

    @field_validator("invariants", mode="before")
    @classmethod
    def _validate_invariants(cls, v: Any) -> List[dict]:
        if not isinstance(v, list):
            return v
        out: List[dict] = []
        for item in v:
            d = item if isinstance(item, dict) else dict(item)
            InvariantModel.model_validate(d)
            out.append(d)
        return out
