"""
Implements logic for computing summary statistics, including category totals, 
spending trends, and top spending areas.
"""
import json
import os

import requests

class Analyzer:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    SYSTEM_PROMPT = """
You are a blunt but supportive financial health coach. Your goal is to find leaks
in a user's spending by analyzing their CSV transaction data.
Task: Analyze the provided CSV (Columns: Location, Cost, Item Name).
Identify the top 3 behavioral trends where the user is spending unconsciously.
Output Requirements:
1. The Hook: Start with a specific stat that combines frequency and total cost
2. The Context: Compare this to a healthy benchmark.
3. The Call to Action: End with a Micro-Goal or a limit suggestion.
4. Tone: Personal, conversational, and direct.
5. Format: one short sentence.
"""

    @staticmethod
    def get_total_spending(transactions):
        """Calculate total expense amount (exclude income entries)."""
        return sum(t['amount'] for t in transactions if t.get('category') != "Income")

    @staticmethod
    def get_total_income(transactions):
        """Calculate total income amount from Income category."""
        return sum(t['amount'] for t in transactions if t.get('category') == "Income")

    @staticmethod
    def get_net_balance(transactions):
        """Income minus spending to show current net cash flow."""
        return Analyzer.get_total_income(transactions) - Analyzer.get_total_spending(transactions)

    @staticmethod
    def get_category_totals(transactions):
        """Group expense amounts by category (exclude income)."""
        totals = {}
        for t in transactions:
            if t.get('category') == "Income":
                continue
            cat = t['category']
            totals[cat] = totals.get(cat, 0) + t['amount']
        return totals

    @staticmethod
    def get_top_categories(transactions, n=3):
        """Identify the top N categories with the highest spending."""
        cat_totals = Analyzer.get_category_totals(transactions)
        # Sort by amount descending
        sorted_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
        return sorted_cats[:n]

    @staticmethod
    def get_daily_breakdown(transactions):
        """Group daily expense totals (exclude income)."""
        daily = {}
        for t in transactions:
            if t.get('category') == "Income":
                continue
            date = t['date']
            daily[date] = daily.get(date, 0) + t['amount']
        return daily

    @staticmethod
    def analyze_spending(transactions):
        """Analyze spending patterns using AI and return behavioral insights."""
        if not transactions:
            return "No transaction data available for AI analysis."

        if not Analyzer.OPENROUTER_API_KEY:
            return "Err: OPENROUTER_API_KEY is not set."

        csv_data = "Location,Cost,Item Name\n"
        for t in transactions:
            csv_data += (
                f"{t.get('description', 'N/A')},"
                f"{t.get('amount', 0)},"
                f"{t.get('category', 'N/A')}\n"
            )

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {Analyzer.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "liquid/lfm-2.5-1.2b-instruct:free",
            "messages": [
                {"role": "system", "content": Analyzer.SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze these transactions for spending habits:\n\n{csv_data}"},
            ],
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError:
            if response.status_code == 401:
                return "Err: Invalid API Key or insufficient permissions."
            if response.status_code == 429:
                return "Err: Key quota exceeded / Rate limited."
            return f"Err: HTTP Error - {response.status_code}: {response.text}"
        except Exception as e:
            return f"Err: {str(e)}"
