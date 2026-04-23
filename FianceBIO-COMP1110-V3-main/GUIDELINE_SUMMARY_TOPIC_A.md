# COMP1110 Project Guideline Summary (Topic A)

This document summarizes only the parts of the COMP1110 Project Guidelines that are directly relevant to our selected topic:
**A. Personal Budget and Spending Assistant**.

## 1) Core Course Intent

The project is evaluated mainly on computational thinking, not advanced engineering:

- Model a real daily-life problem in a clear and structured way.
- Explain assumptions, scope, and design choices with reasoning.
- Build a simple, testable implementation using text interaction and file I/O.

## 2) Deliverables We Must Align With

### Project Plan (15%)
- Define problem scope clearly.
- Provide team task breakdown and role assignment.
- Provide timeline/milestones.
- Include a brief scan of related existing tools.

### Final Code (25%)
- Text-based interaction is sufficient (GUI is optional, not required).
- Use simple file formats (JSON/CSV) for persistent data.
- Code should be readable and documented.
- README must explain setup, run steps, and file purposes.
- Include sample test cases for chosen topic.
- Submit code as public GitHub repository.

### Group Final Report (35%)
- Explain problem significance and modeling approach.
- Compare existing solutions and justify design trade-offs.
- Present system design and key functions.
- Include case studies with concrete inputs and outputs.
- Discuss evaluation, limitations, and future improvements.

### Individual Final Report (10%, individual)
- Detail personal contribution and reflection.
- Keep contribution consistent with group task breakdown.
- If AI tools are used: document tool name/version, prompts, and verification/modification process.

### Tutorial Participation (15%, individual)
- Attend required tutorial sessions for progress check-ins.

## 3) Topic A Functional Expectations (Code + Evidence)

For Topic A, the implementation should support:

- Transaction model (date, amount, category, description, optional notes).
- Budget rule model (category, period, threshold, rule type, enabled).
- File loading/saving with error handling (missing/empty/malformed files).
- Text menu for add/view/load/save and analysis workflows.
- Input validation (date/amount/category).
- Summary statistics (totals, category totals, top categories, trend-style views).
- Rule-based alerts (cap/percentage and related warnings).
- Case-study-ready test data.

## 4) Case Study Requirements

We should provide **3-4 realistic scenarios** with:

- Exact transaction files.
- Matching budget rule files.
- Program outputs (summary + alerts).
- Discussion of strengths, limitations, and comparison with existing tools.

Suggested examples (already aligned with Topic A):
- Daily food budget control.
- Monthly transport tracking.
- Subscription creep detection.

## 5) Report-Facing Quality Checklist

Before submission, make sure we can clearly show:

- Why our model is simple and justified.
- How each major feature maps to Topic A requirements.
- Where our solution works well and where it does not.
- That all run instructions and sample files are reproducible.

## 6) AI Usage Compliance (Important)

If AI-assisted coding/writing is used, each member should record:

- Tool and version.
- Prompts used.
- How outputs were checked, modified, and validated.

This is mandatory for individual reporting compliance.

