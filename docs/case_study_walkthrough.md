# FinanceBIO Case Study Walkthrough

"""
This document provides step-by-step instructions on how to run the pre-defined 
case studies for FinanceBIO. It explains the scenario goals, the data involved, 
and the expected output for evaluation purposes.
"""

## 📋 Prerequisites
Before running these cases, ensure your project structure is as follows:
- `src/main.py` (and all supporting modules)
- `data/` folder containing all `.json` files provided.

---

## 🥪 Case Study 1: Student Daily Food Budget
**Scenario:** A student aims to limit daily lunch spending to HK$50.00 at CYM (Chiu Yuen Meng).

### Execution Steps:
1. Run the application: `python src/main.py`
2. Select **Option 5** (Load Data).
3. Select **Sub-option 1** (Load Transactions) and enter: `case1_student_cym_food.json`
4. Select **Sub-option 2** (Load Budget Profile) and enter: `case1_budgets.json`
5. Select **Option 4** (Check Alerts).

### Expected Result:
The system should trigger a **CAP ALERT** for April 21st, as the spending ($65.50) exceeds the HK$50.00 threshold.
* **Analysis:** This proves the system's ability to handle high-frequency daily spending checks.

---

## 🚇 Case Study 2: Transport Tracking (Weekly)
**Scenario:** Monitoring if commuting costs (MTR, Bus, Uber) stay within a HK$75.00 weekly limit.

### Execution Steps:
1. Run the application and select **Option 5**.
2. Load Transactions: `case2_transport_monthly.json`
3. Load Budget Profile: `case2_budgets.json`
4. Select **Option 4** (Check Alerts) and **Option 3** (Summary Statistics).

### Expected Result:
- **Summary:** Total spending will show HK$91.50.
- **Alert:** A warning will appear because the weekly total exceeds the HK$75.00 cap.
* **Analysis:** Demonstrates the system's "Weekly Grouping" logic and its effectiveness in identifying expensive transport choices (like Uber).

---

## 📺 Case Study 3: Subscription Creep (Percentage)
**Scenario:** Detecting if small digital subscriptions (Netflix, Spotify) are taking up too much of the total budget (Limit: 5%).

### Execution Steps:
1. Run the application and select **Option 5**.
2. Load Transactions: `case3_subscription_creep.json`
3. Load Budget Profile: `case3_budgets.json`
4. Select **Option 4** (Check Alerts).

### Expected Result:
The system will trigger a **BUDGET ALERT** showing that Subscriptions represent ~43% of total spending.
* **Analysis:** This validates the **Percentage-based logic**, proving that even small amounts ($15, $58) can become problematic if the total income/spending is low.

---

## 🛠️ Troubleshooting for Team Members
- **File Not Found:** Ensure you are running `main.py` from the root directory, not from inside the `src/` folder.
- **Wrong Format:** When entering filenames, always include the `.json` extension.
- **No Alerts:** Check if the `enabled` field in the budget JSON file is set to `true`.
