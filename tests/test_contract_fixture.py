import json
from pathlib import Path


def test_expected_fixture_contract_shape():
    p = Path("scenarios/fixtures/expected.json")
    assert p.exists(), "missing expected fixture"
    data = json.loads(p.read_text())
    assert isinstance(data, dict)
    # permissive contract checks
    assert any(k in data for k in ["status", "result", "findings", "summary"])
