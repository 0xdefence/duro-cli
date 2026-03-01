from duro.hardening import ErrorCode, normalize_exception, validate_provider_config


def test_provider_config_missing_openai_key():
    errs = validate_provider_config("openai", {})
    assert errs
    assert errs[0].code == ErrorCode.CONFIG_ERROR


def test_provider_config_mock_ok():
    errs = validate_provider_config("mock", {})
    assert errs == []


def test_exception_normalization_timeout():
    e = normalize_exception(Exception("request timeout on provider"))
    assert e.code == ErrorCode.TIMEOUT
