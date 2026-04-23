***

# COMP1110 Budget Assistant - Personal Finance Manager

> A text-based Python application for HKU students to track spending and manage budgets with rule-based financial alerts.

**Project Topic**: A. Personal Budget and Spending Assistant  
**Language**: Python 3.x  
**Dependencies**: Standard library + optional `rich` for prettier table output  
**Submission Deadline**: May 2, 2026, 11:59 PM  
**GitHub**: [budget-app-comp1110](https://github.com/zerubbabel42/budget-app-comp1110)

***

## 📋 Project Overview

FinanceBio is designed to answer critical personal finance questions:
- **"Where did my money go?"** → Category-based spending summaries
- **"When am I likely to overspend?"** → Rule-based alert system
- **"Can I afford this?"** → Daily/weekly/monthly budget tracking

This project fulfills COMP1110 Topic A requirements emphasizing **computational thinking**, **problem modeling**, and **research-driven design** — not commercial app features.

***

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/zerubbabel42/budget-app-comp1110.git
cd budget-app-comp1110
python3 -m pip install --user -r requirements.txt
```

### Run Application
```bash
python3 src/main.py

# Main Menu Options:
# 1. Add Transaction            5. Load Data (Case Studies)
# 2. View All Transactions      6. Generate Report (Suggestion)
# 3. View Summary Statistics    7. More Tools (AI/OCR/Save)
# 4. Check Financial Alerts     8. Exit
```

### Add Your First Transaction
```
Format: YYYY-MM-DD,amount,category,description[,notes]
Example: 2026-04-21,45.50,Dining,CYM lunch,overpriced

Available Categories: Dining, Housing, Transport, Academic, Social, Digital, Income, Other
```

***

## 📁 Project Structure

```
budget-app-comp1110/
│
├── README.md                          # This file
├── requirements.txt                   # Dependencies (minimal)
├── src/                               # ⭐ CORE APPLICATION
│   ├── __init__.py
│   ├── main.py                        # Entry point: menu loop & commands
│   ├── budget_model.py                # Transaction & BudgetRule classes
│   ├── file_io.py                     # Load/save JSON with error handling
│   ├── validator.py                   # Input validation (date, amount, etc)
│   ├── analyzer.py                    # Summary stats & trend analysis
│   ├── alert_engine.py                # 5 rule-based alert system
│   ├── visualizer.py                  # ASCII wealth tree and score visuals
│   ├── smart_input.py                 # Unstructured input parser
│   ├── receipt_parser_easyocr.py      # OCR import integration
│   └── test_data_gen.py               # Generate test transactions
│
├── data/                              # ⭐ CASE STUDY DATA
│   ├── case1_student_cym_food.json        # HKU student CYM lunch tracking
│   ├── case1_budgets.json                 # Budget rules for case 1
│   ├── case2_transport_monthly.json       # Monthly MTR tracking
│   ├── case2_budgets.json
│   ├── case3_subscription_creep.json      # Netflix/Spotify detection
│   ├── case3_budgets.json
│   ├── default_budgets.json
│   ├── balanced_rules.json
│   ├── saving_first_rules.json
│   ├── user_created_rules.json
│   └── transactions.json               # Runtime current data
│
├── tests/                             # ⭐ UNIT TESTS (Optional)
│   ├── test_budget_model.py
│   ├── test_file_io.py
│   ├── test_smart_input.py
│   ├── test_visualizer.py
│   └── test_validator.py
│
├── reports/                           # ⭐ SUBMISSION DOCUMENTS
│   ├── group_final_report.pdf         # Main deliverable (35pts)
│   ├── research_survey.md             # Tool comparison (YNAB/Mint/Excel)
│   ├── design_tradeoffs.md            # 5+ design decisions explained
│   └── individual_reports/            # Each member's contribution (10pts)
│
└── docs/                              # ⭐ DOCUMENTATION
    ├── system_design.md               # Architecture & data flow
    └── case_study_walkthrough.md      # How to run case studies
```

***

## 🔧 Core Features (25pts Code)

### 1. **Data Model** (`src/budget_model.py`)
```python
Transaction: {
  date: "2026-04-21",           # ISO 8601
  amount: 45.50,                # HK$ (positive)
  category: "Dining",           # 8 predefined categories
  description: "CYM lunch",     # Free text
  notes: "overpriced"           # Optional
}

BudgetRule: {
  category: "Dining",
  threshold: 50.0,              # HK$
  period: "daily",              # daily/weekly/monthly
  rule_type: "cap",             # cap/percentage/streak
  enabled: true
}
```

### 2. **File I/O** (`src/file_io.py`)
✅ Load transactions (handles missing files, malformed data, empty files)  
✅ Save transactions (atomic write with temp file + rename)  
✅ Load/save budget rules (JSON persistence)  
✅ Graceful error handling with informative messages  

### 3. **Text Menu Interface** (`src/main.py`)
**8 Menu Options:**
1. **Add Transaction** → Parse, validate, store
2. **View All** → Table-format display
3. **Filter** → By date range or category
4. **Summary** → Category totals, top 3, daily/weekly/monthly breakdowns
5. **Alerts** → Check all active alerts
6. **Configure Budgets** → Add/edit/delete rules
7. **Load/Save** → Manual data persistence
8. **Exit** → Save and quit

### 4. **Summary Statistics** (`src/analyzer.py`)
✅ Total spending  
✅ Category totals & top N categories  
✅ Daily/weekly/monthly spending breakdown  
✅ Spending trends (last N days)  
✅ Category-specific analysis  

### 5. **Rule-Based Alerts** (`src/alert_engine.py`) — 5 Rules
1. **Daily Category Cap**: "Dining exceeded HK$50/day. Today: HK$65"
2. **Weekly Category Cap**: "Transport exceeded HK$75/week"
3. **Percentage Threshold**: "Dining is 60% of budget (limit: 40%)"
4. **Consecutive Overspend Streak**: "Overspent 3 consecutive days"
5. **Uncategorized Warning**: "2 transactions missing category"

### 6. **Input Validation** (`src/validator.py`)
✅ Date format (ISO 8601)  
✅ Amount validation (positive, max HK$100,000)  
✅ Category check (predefined list)  
✅ Menu choice validation (1-8)  
✅ Complete transaction parsing  

### 7. **Test Data Generator** (`src/test_data_gen.py`)
✅ Generate N realistic random transactions  
✅ Edge case generation (zero spending, duplicates, large amounts)  

***

## 📊 Case Studies (Evidence for 35pts Report)

### Case Study 1: Student CYM Food Budget
**Scenario**: HKU Year 1 controls daily CYM lunch spending (limit: HK$50/day)

| File | Purpose |
|------|---------|
| `data/case1_student_cym_food.json` | 8 sample transactions |
| `data/case1_budgets.json` | Rule: Dining ≤ HK$50/day |

**Expected Results**:
- ✓ Daily cap alert triggered (actual: HK$65)
- ✓ Category summary shows overspent
- ✗ Limitation: Can't auto-distinguish CYM vs other restaurants
- 🔄 YNAB comparison: Uses "Favorite Payee" tags

***

### Case Study 2: Monthly Transport Tracking
**Scenario**: Student tracks MTR budget (limit: HK$75/week, HK$300/month)

| File | Purpose |
|------|---------|
| `data/case2_transport_monthly.json` | 14 transport transactions |
| `data/case2_budgets.json` | Weekly + monthly cap rules |

**Expected Results**:
- ✓ Weekly breakdown shows HK$82/week (exceeded)
- ✓ Spending trend analysis
- ✗ Limitation: Can't auto-classify MTR vs bus vs taxi
- 🔄 Google Maps: Automatic transaction history

***

### Case Study 3: Subscription Creep Detection
**Scenario**: Monitor recurring subscriptions (Netflix, Spotify, Adobe, etc.)

| File | Purpose |
|------|---------|
| `data/case3_subscription_creep.json` | 11 recurring transactions |
| `data/case3_budgets.json` | Digital ≤ HK$150/month |

**Expected Results**:
- ✓ Recurring pattern detection (monthly charges)
- ✓ Month-over-month increase visualization
- ✗ Limitation: Can't auto-detect new recurring charges
- 🔄 YNAB: "Recurring Transactions" module

***

## 📝 Implementation Roadmap

### Week 1 (Apr 21-27) — CRITICAL
- [ ] `budget_model.py` + `file_io.py` skeleton
- [ ] `main.py` menu loop + Add Transaction
- [ ] `validator.py` + input parsing
- [ ] `analyzer.py` + summary statistics (basic)

### Week 2 (Apr 28-May 4) — HIGH PRIORITY
- [ ] Complete `alert_engine.py` (all 5 rules)
- [ ] `test_data_gen.py` + edge cases
- [ ] Generate case study JSON files + test runs
- [ ] `research_survey.md` (tool comparison)
- [ ] `design_tradeoffs.md` (5+ decisions)

### Week 3 (May 5-11) — FINALIZATION
- [ ] Polish `main.py` error handling
- [ ] Unit tests in `tests/`
- [ ] Group Final Report (draft)
- [ ] Individual Reports (each member)
- [ ] Demo video (running 1 case study)

### Deadline: May 2, 11:59 PM
- [ ] Push to public GitHub
- [ ] All code files + README
- [ ] Group Report + Research docs
- [ ] Individual Reports
- [ ] Case study outputs
- [ ] Demo video

***

## ✅ COMP1110 Requirements Checklist

| Requirement | Implementation | File | Status |
|-------------|-----------------|------|--------|
| **Problem Modeling** | Transaction schema + BudgetRule class | `budget_model.py` | ✅ |
| **File I/O** | JSON load/save with error handling | `file_io.py` | ✅ |
| **Text-based Interaction** | 8-option menu loop | `main.py` | ✅ |
| **Summary Statistics** | Category totals, trends, periods | `analyzer.py` | ✅ |
| **Rule-based Alerts** | 5 configurable rules | `alert_engine.py` | ✅ |
| **Input Validation** | Date, amount, category, menu choice | `validator.py` | ✅ |
| **Sample Test Cases** | Test data generator + edge cases | `test_data_gen.py` | ✅ |
| **3-4 Case Studies** | With sample JSON files | `data/case*.json` | ✅ |
| **Research** | Tool survey + comparison table | `research_survey.md` | 🔄 |
| **Design Trade-offs** | 5+ decisions with pros/cons | `design_tradeoffs.md` | 🔄 |
| **GitHub Repository** | Public, with README | `/` | 🔄 |

***

## 🎯 Team Roles & Tasks

### Suggested Task Breakdown (4-6 people)

**Person A - Data & File I/O**
- [ ] `budget_model.py` (Transaction, BudgetRule classes)
- [ ] `file_io.py` (load/save with error handling)
- [ ] `__init__.py` package setup

**Person B - Menu & Interaction**
- [ ] `main.py` (8-option menu loop)
- [ ] `validator.py` (input validation)
- [ ] User interface flow

**Person C - Analytics**
- [ ] `analyzer.py` (summary stats, trends)
- [ ] `alert_engine.py` (5 rules)
- [ ] Data processing logic

**Person D - Testing & Docs**
- [ ] `test_data_gen.py` (test cases + edge cases)
- [ ] Generate case study JSONs
- [ ] `system_design.md`

**Person E - Research**
- [ ] `research_survey.md` (tool comparison: YNAB, Mint, Excel, etc.)
- [ ] `design_tradeoffs.md` (5+ decisions explained)

**Person F - Reports**
- [ ] Group Final Report (35pts)
- [ ] Individual Reports (10pts each)
- [ ] Demo video walkthrough

***

## 🧪 Running Tests

### Test Data Generator
```bash
python -c "from src.test_data_gen import generate_test_transactions; print(generate_test_transactions(10))"
```

### Unit Tests (Optional but +points)
```bash
pytest -q
```

### Run Case Study 1
```bash
python src/main.py
# Menu → 7 (Load/Save) → Load case1_student_cym_food.json
# Menu → 4 (Summary) → View results
# Menu → 5 (Alerts) → Trigger budget alert
```

***

## 📚 Design Decisions (Trade-offs)

| Trade-off | Pro | Con | Choice |
|-----------|-----|-----|--------|
| **Manual vs Auto Entry** | Accurate, educational | Tedious | Manual (COMP1110 focus) |
| **Few (5) vs Many (20+) Categories** | Simple, focused | Less granular | 8 categories (balanced) |
| **Daily vs Weekly vs Monthly** | Flexible | Complex | Support all 3 (configurable) |
| **Local JSON vs Cloud** | Private, offline | Data loss risk | Local JSON (simple) |
| **Simple Rules vs ML** | Interpretable, fast | Less intelligent | Simple thresholds |

***

## 🔍 Known Limitations & Future Work

### Current Limitations
- ❌ Cannot auto-classify transactions by vendor/location
- ❌ No machine learning for predictions
- ❌ No bank API integration
- ❌ No mobile app
- ❌ Manual category assignment required

### Future Enhancements
- 📱 Mobile app (Flutter/React Native)
- 🤖 ML-powered auto-categorization
- 🏦 Bank/credit card API sync
- 📊 Advanced forecasting & recommendations
- 📈 Data visualization (charts/graphs)

***

## 🔗 References

### Tools Evaluated
1. **YNAB**: Manual entry, custom categories, advanced rules
2. **Mint**: Auto-sync, fixed categories, basic alerts
3. **Money Manager EX**: Local app, rich reporting
4. **Excel/Google Sheets**: Manual, high customization
5. **HK Money**: Hong Kong-specific
6. **PocketGuard**: AI-powered suggestions

***

## 📋 Submission Checklist

- [ ] **GitHub Repository**
  - [ ] Public repo: `budget-app-comp1110`
  - [ ] All source code in `src/`
  - [ ] Case study data in `data/`
  - [ ] README.md complete
  - [ ] .gitignore configured

- [ ] **Code Quality**
  - [ ] All functions documented (docstrings)
  - [ ] Error handling for file I/O
  - [ ] Input validation comprehensive
  - [ ] No hardcoded paths or API keys
  - [ ] `python src/main.py` runs successfully

- [ ] **Documentation**
  - [ ] `group_final_report.pdf` (35pts)
  - [ ] `research_survey.md` (tool comparison)
  - [ ] `design_tradeoffs.md` (5+ decisions)
  - [ ] Individual Reports (10pts each)
  - [ ] System design document

- [ ] **Case Studies**
  - [ ] 3-4 JSON case files
  - [ ] Budget rule files for each case
  - [ ] Program output screenshots/logs
  - [ ] Written discussion (what works/fails)

- [ ] **Demo & Submission**
  - [ ] 5-min demo video (run case study end-to-end)
  - [ ] Tutorial attendance (4 sessions, no late)
  - [ ] All files uploaded to Moodle by May 2, 11:59 PM

***

## 🤝 Contributors

| Role | Name | Module |
|------|------|--------|
| Data Model | [Member 1] | `budget_model.py`, `file_io.py` |
| Menu & UI | [Member 2] | `main.py`, `validator.py` |
| Analytics | [Member 3] | `analyzer.py`, `alert_engine.py` |
| Testing | [Member 4] | `test_data_gen.py`, case studies |
| Research | [Member 5] | Research & trade-off docs |
| Reports | [Member 6] | Final reports & video |

***

## 📞 Support & Troubleshooting

### "File not found" error
```
Solution: Ensure data/ directory exists (auto-created on first run)
```

### Invalid date format
```
Format must be ISO 8601: YYYY-MM-DD
Example: 2026-04-21 ✓, 04/21/2026 ✗
```

### Alerts not triggering
```
1. Configure budget rules (Menu → 6)
2. Ensure rules are marked "enabled"
3. Check thresholds match transaction amounts
```

***

## 📄 License

Educational project for COMP1110 course at HKU (2025-2026).

***

## 📞 Project Metadata

- **Course**: COMP1110 Computing and Data Science in Everyday Life
- **Semester**: 2, 2025-2026
- **Group Size**: 4-6 students
- **Total Points**: 80 (Code 25 + Report 35 + Individual 10 + Tutorials 15)
- **Submission Deadline**: May 2, 2026, 11:59 PM
- **GitHub Link**: https://github.com/zerubbabel42/budget-app-comp1110

***

**Last Updated**: April 21, 2026 | **Version**: 1.0 (Skeleton)
