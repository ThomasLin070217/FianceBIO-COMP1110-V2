# FinanceBIO System Design Document

"""
This document outlines the architecture, data models, and logical flow of 
the FinanceBIO personal budget assistant. It explains how real-world 
financial problems are translated into a computational system.
"""

## 1. Problem Modeling
We model the daily life problem of "Personal Finance Management" as a set of structured data entities:
- **Transaction**: Represents a single spending event (What, When, How much).
- **BudgetRule**: Represents a financial constraint (Category, Threshold, Rule Type).
- **Alert Engine**: Represents the logic of comparing actual behavior against goals.

## 2. System Architecture
The system follows a **Modular Design** to ensure high maintainability and readability (as per COMP1110 guidelines).

### Component Overview:
- **`main.py` (Controller)**: Handles the UI loop and directs data flow between modules.
- **`budget_model.py` (Data Layer)**: Defines the internal representation of data using Python classes.
- **`file_io.py` (Storage Layer)**: Manages JSON persistence with robust error handling for missing/empty files.
- **`validator.py` (Integrity Layer)**: Ensures all user inputs (dates, amounts) are valid before processing.
- **`analyzer.py` (Logic Layer)**: Performs data aggregation (totals, top categories, averages).
- **`alert_engine.py` (Logic Layer)**: The "intelligence" of the system that triggers alerts based on 5 specific rules.

## 3. Data Flow Diagram
1. **Input**: User enters data via the CLI or loads a Case Study JSON.
2. **Validation**: `validator.py` checks format integrity.
3. **Storage**: Data is committed to `transactions.json` via `file_io.py`.
4. **Processing**: `analyzer.py` calculates current spending levels.
5. **Evaluation**: `alert_engine.py` compares current levels against `budget_rules.json`.
6. **Output**: System prints summary statistics and any triggered warnings.

## 4. Key Design Decisions (Trade-offs)
*Detailed discussions of these can be found in `reports/design_tradeoffs.md`.*
- **Local JSON vs Database**: We chose JSON for simplicity and portability, ensuring the TA can run the project without setting up a SQL server.
- **Pure Standard Library**: We avoided external libraries (like Pandas) to demonstrate core algorithmic thinking and ensure zero-dependency execution.
- **Percentage-based Rules**: Implemented to accommodate fluctuating student income, allowing a "flexible" budget model.

## 5. Implementation of Alert Rules
The system implements 5 rule-based alerts:
1. **Daily Category Cap**: Triggers if a single day's category spend exceeds limit.
2. **Weekly Category Cap**: Triggers if a rolling week's category spend is too high.
3. **Percentage Threshold**: Triggers if a category takes up more than X% of the total monthly budget.
4. **Spending Streak**: Detects if the user has spent "high amounts" for 3+ consecutive days.
5. **Uncategorized Warning**: Flags transactions in the "Other" category to encourage better data organization.
