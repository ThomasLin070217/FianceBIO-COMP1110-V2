import os
import json
import requests

OPENROUTER_API_KEY = "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"

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
"""

def analyze_spending(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_data = file.read()
    except FileNotFoundError:
        return "Err: CSV file not found"
    except Exception as e:
        return f"Err: Could not read file - {str(e)}"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "liquid/lfm-2.5-1.2b-instruct:free",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze these transactions for spending habits:\n\n{csv_data}"}
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            return "Err: Invalid API Key or insufficient permissions."
        elif response.status_code == 429:
            return f"Err: Key quota exceeded / Rate limited."
        else:
            return f"Err: HTTP Error - {response.status_code}: {response.text}"
    except Exception as e:
        return f"Err: {str(e)}"
