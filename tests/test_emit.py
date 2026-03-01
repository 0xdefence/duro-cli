import json

from duro.emit import emit_json_contract


def test_emit_json_contract_valid(capsys):
    emit_json_contract({"status": "ok", "result": {"x": 1}})
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert payload["status"] == "ok"
    assert payload["reason"] == "unspecified"


def test_emit_json_contract_invalid(capsys):
    emit_json_contract({"status": 1})
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert payload["ok"] is False
    assert payload["code"] == "schema_error"
