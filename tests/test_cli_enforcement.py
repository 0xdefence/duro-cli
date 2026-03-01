import importlib
import os


def test_import_duro_with_enforcement_toggle(monkeypatch):
    monkeypatch.setenv("DURO_ENFORCE_CONTRACT", "0")
    m = importlib.import_module("duro")
    assert hasattr(m, "__version__")


def test_import_duro_enforcement_default(monkeypatch):
    monkeypatch.delenv("DURO_ENFORCE_CONTRACT", raising=False)
    m = importlib.reload(importlib.import_module("duro"))
    assert hasattr(m, "__version__")
