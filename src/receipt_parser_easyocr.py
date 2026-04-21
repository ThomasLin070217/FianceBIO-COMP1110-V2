import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import os
import re
import csv
from pathlib import Path
import easyocr
import pandas as pd
from datetime import datetime

# ================== CONFIGURATION ==================
ALLOWED_CATEGORIES = [
    "Food", "Transportation", "Subscription", "Groceries",
    "Entertainment", "Rent", "Water and electricity", "Savings"
]

# Keyword mapping for category detection (lowercase)
CATEGORY_KEYWORDS = {
    "Food": ["restaurant", "cafe", "coffee", "starbucks", "mcdonald", "kfc", "pizza", "burger", "dinner", "lunch", "breakfast", "food", "meal", "eatery", "bistro"],
    "Transportation": ["uber", "lyft", "taxi", "bus", "train", "subway", "metro", "gas", "fuel", "petrol", "diesel", "toll", "parking", "lyft", "grab", "gojek"],
    "Subscription": ["netflix", "spotify", "amazon prime", "disney+", "hulu", "hbo", "subscription", "monthly fee", "membership"],
    "Groceries": ["walmart", "target", "kroger", "safeway", "aldi", "trader joe", "whole foods", "costco", "sam's", "groceries", "supermarket", "market", "produce", "dairy"],
    "Entertainment": ["cinema", "movie", "theatre", "concert", "event", "game", "steam", "playstation", "xbox", "netflix", "spotify", "hulu", "disney+"],
    "Rent": ["rent", "lease", "apartment", "housing", "monthly rent", "landlord"],
    "Water and electricity": ["water bill", "electricity", "power bill", "utility", "gas bill", "sewage", "trash"],
    "Savings": ["savings", "deposit", "transfer to savings", "investment"]
}

# ================== OCR INITIALIZATION ==================
# Initialize EasyOCR reader (only once)
reader = easyocr.Reader(['en'])  # Add other languages if needed, e.g., ['en', 'fr']

# ================== PARSING FUNCTIONS ==================
def extract_date(text):
    """
    Extract a date from text and convert to YYYY-MM-DD.
    Supports: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, MM-DD-YYYY, etc.
    """
    patterns = [
        # Year first: 2024-12-31 or 2024/12/31 or 2024.12.31
        (r'(\d{4})[-/\.](\d{1,2})[-/\.](\d{1,2})', '%Y', '%m', '%d'),
        # US: MM/DD/YYYY or MM-DD-YYYY
        (r'(\d{1,2})[-/\.](\d{1,2})[-/\.](\d{4})', '%m', '%d', '%Y'),
        # European: DD/MM/YYYY
        (r'(\d{1,2})[-/\.](\d{1,2})[-/\.](\d{4})', '%d', '%m', '%Y'),
    ]
    
    for pattern, fmt1, fmt2, fmt3 in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                # Extract parts
                part1, part2, part3 = match.groups()
                # Determine which pattern actually matched by checking year range
                if len(part1) == 4:  # Year first
                    year, month, day = int(part1), int(part2), int(part3)
                elif len(part3) == 4:
                    # If third group is year, check if first group > 31 -> likely day
                    if int(part1) > 31:
                        # Could be year first? Already handled. Assume DD/MM/YYYY or MM/DD/YYYY
                        # Heuristic: if first > 12, it's day, so format = DD/MM/YYYY
                        if int(part1) > 12:
                            day, month, year = int(part1), int(part2), int(part3)
                        else:
                            # ambiguous, assume MM/DD/YYYY (US)
                            month, day, year = int(part1), int(part2), int(part3)
                    else:
                        month, day, year = int(part1), int(part2), int(part3)
                else:
                    continue
                
                # Basic validation
                if 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2100:
                    return f"{year:04d}-{month:02d}-{day:02d}"
            except:
                continue
    return ""

def extract_amount(text):
    """
    Extract the total amount from receipt text.
    Looks for patterns like $12.34, 12.34, 12,34 (European), etc.
    Returns float rounded to 1 decimal place.
    """
    # Patterns: $12.34, 12.34, 12,34 (with comma as decimal), TOTAL 12.34
    patterns = [
        r'(?:total|amount|due|sum|pay|balance)[^\d]*(\d+[.,]\d{2})',  # "Total 12.34"
        r'\$\s*(\d+[.,]\d{1,2})',                                     # "$12.34"
        r'(\d+[.,]\d{2})\s*$',                                       # ends with 12.34
        r'(\d+[.,]\d{1,2})',                                         # any decimal number
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Take the last match (often the total is at the end)
            amount_str = matches[-1]
            # Replace comma with dot if needed
            amount_str = amount_str.replace(',', '.')
            try:
                amount = float(amount_str)
                # Round to 1 decimal place
                return round(amount, 1)
            except:
                continue
    return 0.0

def extract_description(text):
    """
    Extract a short description: first line or merchant name.
    """
    lines = text.split('\n')
    # Remove empty lines
    lines = [line.strip() for line in lines if line.strip()]
    if lines:
        # Often the first non-empty line is the merchant name
        return lines[0][:100]  # Limit length
    return ""

def assign_category(text, description):
    """
    Assign a category based on keywords found in the text or description.
    """
    combined = (description + " " + text).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                return category
    return "Groceries"  # Default category

# ================== MAIN PROCESSING ==================
def process_receipt(image_path):
    """
    Process a single receipt image: OCR -> parse -> return dict.
    """
    print(f"Processing: {image_path}")
    
    # Run OCR
    result = reader.readtext(image_path, detail=0)  # detail=0 returns list of text strings
    if not result:
        print(f"  No text found in {image_path}")
        return None
    
    full_text = ' '.join(result)
    
    # Parse fields
    date_str = extract_date(full_text)
    amount = extract_amount(full_text)
    description = extract_description(full_text)
    category = assign_category(full_text, description)
    
    # Validate category
    if category not in ALLOWED_CATEGORIES:
        category = "Groceries"
    
    return {
        "date": date_str,
        "amount": amount,
        "category": category,
        "description": description
    }

def process_folder(input_folder, output_csv):
    """
    Process all images in a folder and save results to CSV.
    """
    # Supported image extensions
    exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    image_files = [f for f in Path(input_folder).iterdir() if f.suffix.lower() in exts]
    
    if not image_files:
        print(f"No images found in {input_folder}")
        return
    
    results = []
    for img_file in image_files:
        data = process_receipt(str(img_file))
        if data:
            results.append(data)
        else:
            print(f"  Skipped {img_file.name}")
    
    # Write CSV
    if results:
        df = pd.DataFrame(results)
        df.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"\n✅ Saved {len(results)} receipts to {output_csv}")
    else:
        print("\n❌ No valid receipts processed.")

def run_receipt_parser(project_root=None):
    """
    Process all receipt images in data/receipts and return list of transaction dicts.
    Also writes the CSV file to data/all_receipts.csv.
    """
    if project_root is None:
        script_dir = Path(__file__).parent.resolve()
        project_root = script_dir.parent

    input_folder = project_root / "data" / "receipts"
    output_csv = project_root / "data" / "all_receipts.csv"

    input_folder.mkdir(parents=True, exist_ok=True)

    # Supported image extensions
    exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    image_files = [f for f in input_folder.iterdir() if f.suffix.lower() in exts]

    if not image_files:
        print(f"No images found in {input_folder}")
        return []

    results = []
    for img_file in image_files:
        data = process_receipt(str(img_file))
        if data:
            results.append(data)

    # Write CSV
    if results:
        df = pd.DataFrame(results)
        df.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"\n✅ Saved {len(results)} receipts to {output_csv}")
    else:
        print("\n❌ No valid receipts processed.")

    return results

# ================== PATH CONFIGURATION FOR YOUR PROJECT ==================
if __name__ == "__main__":
    # Get the directory where this script is located (FinanceBIO-COMP1110-V2/src)
    script_dir = Path(__file__).parent.resolve()
    # Project root is one level up (FinanceBIO-COMP1110-V2)
    project_root = script_dir.parent
    
    # Define input folder: FinanceBIO-COMP1110-V2/data/receipts
    INPUT_FOLDER = project_root / "data" / "receipts"
    # Define output CSV: FinanceBIO-COMP1110-V2/data/all_receipts.csv
    OUTPUT_CSV = project_root / "data" / "all_receipts.csv"
    
    # Create the receipts folder if it doesn't exist
    INPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    
    print(f"Project root: {project_root}")
    print(f"Looking for receipt images in: {INPUT_FOLDER}")
    print(f"Results will be saved to: {OUTPUT_CSV}")
    print("-" * 50)
    
    process_folder(str(INPUT_FOLDER), str(OUTPUT_CSV))