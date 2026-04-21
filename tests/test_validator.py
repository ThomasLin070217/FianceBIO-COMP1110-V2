from src.validator import Validator


def test_validate_date_accepts_iso_date():
    assert Validator.validate_date("2026-04-21") is True


def test_validate_date_rejects_invalid_format():
    assert Validator.validate_date("21/04/2026") is False


def test_validate_amount_accepts_positive_number():
    assert Validator.validate_amount("123.45") is True
    assert Validator.validate_amount("HKD 123.45") is True
    assert Validator.validate_amount("$1,234.56") is True


def test_validate_amount_rejects_zero_and_negative():
    assert Validator.validate_amount("0") is False
    assert Validator.validate_amount("-10") is False


def test_validate_amount_rejects_too_large_or_non_numeric():
    assert Validator.validate_amount("1000000000.01") is False
    assert Validator.validate_amount("abc") is False


def test_validate_category_accepts_known_category():
    assert Validator.validate_category("Dining") is True


def test_validate_category_rejects_unknown_category():
    assert Validator.validate_category("Travel") is False
