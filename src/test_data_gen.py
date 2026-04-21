"""
Generates realistic synthetic transaction datasets to test the system's 
edge cases and performance under various scenarios.
"""
import random
from datetime import datetime, timedelta

def generate_test_transactions(num_records=10):
    """
    Creates a list of random transactions for testing purposes.
    Categories: Dining, Transport, Academic, Social, Digital, Other
    """
    categories = ["Dining", "Transport", "Academic", "Social", "Digital", "Other"]
    descriptions = {
        "Dining": ["CYM Lunch", "Starbucks", "U-Canteen Dinner", "7-11 Snack"],
        "Transport": ["MTR Top-up", "Uber to HKU", "Bus to Central"],
        "Academic": ["Textbook", "Printing", "Stationery"],
        "Social": ["Movie Night", "Party", "KTV"],
        "Digital": ["Netflix", "Spotify", "iCloud Storage"]
    }
    
    test_data = []
    start_date = datetime.now() - timedelta(days=30)

    for i in range(num_records):
        # Pick a random date within the last 30 days
        current_date = (start_date + timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
        cat = random.choice(categories)
        
        # Get a realistic description or a default one
        desc_list = descriptions.get(cat, ["Miscellaneous Expense"])
        desc = random.choice(desc_list)
        
        # Random amount between HKD 10 and 500
        amount = round(random.uniform(10.0, 500.0), 2)
        
        test_data.append({
            "date": current_date,
            "amount": amount,
            "category": cat,
            "description": desc,
            "notes": "Auto-generated for testing"
        })
    
    return test_data

if __name__ == "__main__":
    # Example: Generate 5 samples and print them
    samples = generate_test_transactions(5)
    import json
    print(json.dumps(samples, indent=4))
