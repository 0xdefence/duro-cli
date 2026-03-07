from duro.core import evaluate_invariants


def test_evaluate_invariants_counts_pass_fail():
    inv = [
        {"label": "c", "type": "classification_is", "expected": "confirmed"},
        {"label": "s", "type": "steps_max", "max": 3},
        {"label": "safe", "type": "safety_ok"},
    ]
    ctx = {"classification": "confirmed", "steps_count": 2, "safety": {"ok": True}}
    out = evaluate_invariants(inv, ctx)
    assert out["defined"] == 3
    assert out["failed"] == 0


def test_evaluate_invariants_unsupported_type_fails():
    out = evaluate_invariants([{"type": "unknown"}], {})
    assert out["failed"] == 1
