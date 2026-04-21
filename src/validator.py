"""
Provides input validation logic to ensure data integrity for dates, amounts, 
and categories according to project specifications.
"""
import datetime
import re

ALLOWED_CATEGORIES = ["Dining", "Food", "Housing", "Transport", "Academic", "Social", "Digital", "Income", "Other"]
MAX_AMOUNT_HKD = 100000  # Keep student-budget scope practical

class Validator:
    @staticmethod
    def validate_date(date_str):
        """Check if date follows ISO 8601 format (YYYY-MM-DD)."""
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_amount(amount_str):
        """Ensure amount is a positive number and within reasonable limits (HKD)."""
        val = Validator.parse_amount(amount_str)
        return val is not None and 0 < val <= MAX_AMOUNT_HKD

    @staticmethod
    def parse_amount(amount_str):
        """
        Parse amount from user input.
        Accepts formats like:
        - 1234.56
        - 1,234.56
        - HKD 1234.56
        - $1234.56
        """
        if amount_str is None:
            return None
        text = str(amount_str).strip()
        if not text:
            return None

        text = text.replace(",", "")
        text = re.sub(r"(?i)\bHKD\b", "", text)
        text = text.replace("$", "").strip()

        try:
            return float(text)
        except ValueError:
            return None

    @staticmethod
    def validate_category(category_name):
        """Ensure the category is within the predefined list."""
        return category_name in ALLOWED_CATEGORIES
