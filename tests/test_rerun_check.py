import json
from pathlib import Path

from duro import core


def test_rerun_check_validates_n():
    try:
        core.rerun_consistency_check("x.yaml", n=1)
        assert False, "expected ValueError"
    except ValueError:
        assert True


def test_rerun_check_aggregates_distribution(tmp_path, monkeypatch):
    # isolate RUNS dir
    monkeypatch.setattr(core, "RUNS", tmp_path / "runs")
    core.RUNS.mkdir(parents=True, exist_ok=True)

    seq = [
        ("a1", "confirmed", 0.9),
        ("a2", "confirmed", 0.8),
        ("a3", "not_reproducible", 0.7),
    ]

    def fake_run_scenario(*_args, **_kwargs):
        rid, cls, conf = seq.pop(0)
        d = core.RUNS / rid
        d.mkdir(parents=True, exist_ok=True)
        (d / "result.json").write_text(json.dumps({"classification": cls, "confidence": conf}))
        return rid

    monkeypatch.setattr(core, "run_scenario", fake_run_scenario)

    out = core.rerun_consistency_check("scenario.yaml", n=3)
    assert out["distribution"]["confirmed"] == 2
    assert out["majority_classification"] == "confirmed"
