from src.smart_input import parse_unstructured_transaction


def test_parse_unstructured_transaction_basic():
    parsed = parse_unstructured_transaction(
        "2026/04/21 spent $65.5 on food CYM roast goose rice"
    )
    assert parsed["date"] == "2026-04-21"
    assert parsed["amount"] == "65.5"
    assert parsed["category"] == "Dining"
    assert "CYM roast goose rice" in parsed["description"]


def test_parse_unstructured_transaction_with_hkd_keyword():
    parsed = parse_unstructured_transaction(
        "2026-04-22 hkd 48 transport MTR back home"
    )
    assert parsed["date"] == "2026-04-22"
    assert parsed["amount"] == "48"
    assert parsed["category"] == "Transport"


def test_parse_unstructured_transaction_with_dot_date():
    parsed = parse_unstructured_transaction("2007.2.17 spent 60 for food")
    assert parsed["date"] == "2007-02-17"
    assert parsed["amount"] == "60"
    assert parsed["category"] == "Dining"


def test_parse_unstructured_transaction_missing_fields():
    parsed = parse_unstructured_transaction("just some random text without numbers")
    assert parsed["date"] is None
    assert parsed["amount"] is None
    assert parsed["category"] is None
