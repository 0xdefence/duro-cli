import json
from pathlib import Path

from duro.contracts import normalize_status_reason, validate_cli_output_contract


def test_contract_validator_accepts_expected_fixture():
    p = Path("scenarios/fixtures/expected.json")
    payload = json.loads(p.read_text())
    issues = validate_cli_output_contract(payload)
    assert issues == []


def test_normalize_status_reason_sets_defaults():
    payload = {"result": {"ok": True}}
    out = normalize_status_reason(payload)
    assert out["status"] in {"ok", "unknown"}
    assert out["reason"] == "unspecified"


def test_contract_validator_rejects_bad_payload():
    issues = validate_cli_output_contract({"status": 1})
    assert issues
