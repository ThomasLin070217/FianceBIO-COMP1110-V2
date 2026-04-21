from src.budget_model import BudgetRule, Transaction


def test_transaction_initialization_and_type_conversion():
    tx = Transaction("2026-04-21", "45.5", "Dining", "CYM lunch", "weekday")

    assert tx.date == "2026-04-21"
    assert tx.amount == 45.5
    assert tx.category == "Dining"
    assert tx.description == "CYM lunch"
    assert tx.notes == "weekday"


def test_transaction_to_dict_contains_expected_keys():
    tx = Transaction("2026-04-22", 20, "Transport", "MTR")
    tx_dict = tx.to_dict()

    assert tx_dict == {
        "date": "2026-04-22",
        "amount": 20.0,
        "category": "Transport",
        "description": "MTR",
        "notes": "",
    }


def test_budget_rule_defaults_and_type_conversion():
    rule = BudgetRule("Dining", "0.2")

    assert rule.category == "Dining"
    assert rule.threshold == 0.2
    assert rule.period == "monthly"
    assert rule.rule_type == "percentage"
    assert rule.enabled is True


def test_budget_rule_to_dict_with_custom_values():
    rule = BudgetRule(
        category="Transport",
        threshold=75,
        period="weekly",
        rule_type="cap",
        enabled=False,
    )
    rule_dict = rule.to_dict()

    assert rule_dict == {
        "category": "Transport",
        "threshold": 75.0,
        "period": "weekly",
        "rule_type": "cap",
        "enabled": False,
    }
