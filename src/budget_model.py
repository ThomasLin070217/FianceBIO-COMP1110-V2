"""
Defines the data structures for the project, including Transaction and BudgetRule classes.
Updated to support both fixed-cap and percentage-based financial modeling.
"""

class Transaction:
    def __init__(self, date, amount, category, description, notes=""):
        self.date = date          # Format: YYYY-MM-DD
        self.amount = float(amount)
        self.category = category
        self.description = description
        self.notes = notes

    def to_dict(self):
        """Convert object to dictionary for JSON serialization."""
        return self.__dict__

class BudgetRule:
    def __init__(self, category, threshold, period="monthly", rule_type="percentage", enabled=True):
        """
        threshold: If rule_type is 'percentage', value is 0.0 to 1.0 (e.g. 0.15 for 15%).
                   If rule_type is 'cap', value is the HKD amount.
        """
        self.category = category
        self.threshold = float(threshold)
        self.period = period      # daily, weekly, monthly
        self.rule_type = rule_type # "cap" or "percentage"
        self.enabled = enabled

    def to_dict(self):
        return self.__dict__
