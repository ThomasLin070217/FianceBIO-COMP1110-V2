"""
Evaluates transaction data against user-defined budget rules.
Fully supports percentage-based alerts for different financial profiles.
"""

class AlertEngine:
    def __init__(self, transactions, rules):
        self.transactions = transactions
        self.rules = rules

    def check_all_alerts(self):
        """Processes all rules and returns a list of specific financial warnings."""
        alerts = []
        expense_transactions = [t for t in self.transactions if t.get('category') != "Income"]

        # Calculate overall total for percentage-based rules
        total_spent = sum(t['amount'] for t in expense_transactions)

        if total_spent <= 0:
            return ["INFO: No spending recorded. Budget rules cannot be evaluated."]

        # Aggregate current spending per category
        cat_totals = {}
        for t in expense_transactions:
            cat = t['category']
            cat_totals[cat] = cat_totals.get(cat, 0) + t['amount']

        # Evaluate each rule from the JSON profile
        for rule in self.rules:
            if not rule.get('enabled', True):
                continue
            
            cat = rule['category']
            current_amt = cat_totals.get(cat, 0)
            
            # Type 1: Percentage-based (e.g., Food 15%)
            if rule.get('rule_type') == 'percentage':
                actual_pct = current_amt / total_spent
                limit_pct = rule['threshold'] # e.g., 0.15
                
                if actual_pct > limit_pct:
                    alerts.append(
                        f"BUDGET ALERT: {cat} represents {actual_pct:.1%} of total spending. "
                        f"(Limit: {limit_pct:.1%} based on your chosen profile)"
                    )
            
            # Type 2: Fixed Amount Cap (e.g., Daily HK$50)
            elif rule.get('rule_type') == 'cap':
                if current_amt > rule['threshold']:
                    alerts.append(
                        f"CAP ALERT: {cat} spending (${current_amt:.2f}) exceeds "
                        f"your fixed limit of ${rule['threshold']:.2f}!"
                    )
        
        # Rule 5: Uncategorized check (as per guidelines)
        other_count = sum(1 for t in expense_transactions if t['category'] == "Other")
        if other_count > 0:
            alerts.append(f"INFO: You have {other_count} transactions in 'Other'. Consider categorizing them.")
            
        return alerts
