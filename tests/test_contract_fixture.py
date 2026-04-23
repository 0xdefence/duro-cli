import json
from pathlib import Path

VALID_CLASSIFICATIONS = {"confirmed", "not_reproducible", "inconclusive", "infra_failed"}


def test_expected_fixture_contract_shape():
    p = Path("scenarios/fixtures/expected.json")
    assert p.exists(), "missing expected fixture"
    data = json.loads(p.read_text())
    assert isinstance(data, dict)
    assert len(data) > 0, "fixture must not be empty"
    # Each key is a scenario template ID, each value is an expected classification
    for scenario_id, classification in data.items():
        assert isinstance(scenario_id, str), f"key {scenario_id!r} must be a string"
        assert classification in VALID_CLASSIFICATIONS, (
            f"scenario {scenario_id!r}: classification {classification!r} "
            f"not in {VALID_CLASSIFICATIONS}"
        )
