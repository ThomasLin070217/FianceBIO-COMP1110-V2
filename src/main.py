"""
Entry point of the application. Manages the text-based menu loop 
and coordinates user interactions with different modules.
"""
import sys
import shutil
import math
import os
import re
from pathlib import Path
from datetime import datetime

from budget_model import Transaction
from file_io import FileIO
from validator import Validator, ALLOWED_CATEGORIES, MAX_AMOUNT_HKD
from analyzer import Analyzer
from alert_engine import AlertEngine
from visualizer import Visualizer
from smart_input import parse_unstructured_transaction
try:
    from voice_input import transcribe_from_microphone
except ModuleNotFoundError:
    transcribe_from_microphone = None
try:
    from receipt_parser_easyocr import run_receipt_parser
except ModuleNotFoundError:
    run_receipt_parser = None
try:
    from rich.console import Console
    from rich.table import Table
except ModuleNotFoundError:
    Console = None
    Table = None

IS_WINDOWS = os.name == "nt"
if IS_WINDOWS:
    import msvcrt
    termios = None
    tty = None
else:
    import termios
    import tty

# Default file paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
DATA_FILE = os.path.join(DATA_DIR, "transactions.json")
RULES_FILE = os.path.join(DATA_DIR, "default_budgets.json")

# Category mapping from receipt parser categories to app categories.
CATEGORY_MAP = {
    "Food": "Dining",
    "Transportation": "Transport",
    "Subscription": "Digital",
    "Groceries": "Dining",
    "Entertainment": "Social",
    "Rent": "Housing",
    "Water and electricity": "Housing",
    "Savings": "Other",
}

RICH_CONSOLE = Console() if Console is not None else None


def render_rich_table(title, columns, rows):
    """Render a table with Rich if available, else return False."""
    if RICH_CONSOLE is None or Table is None:
        return False
    table = Table(title=title)
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    RICH_CONSOLE.print(table)
    return True


class UI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"

    @staticmethod
    def title(text):
        return f"{UI.BOLD}{UI.CYAN}{text}{UI.RESET}"

    @staticmethod
    def info(text):
        return f"{UI.BLUE}{text}{UI.RESET}"

    @staticmethod
    def success(text):
        return f"{UI.GREEN}{text}{UI.RESET}"

    @staticmethod
    def warning(text):
        return f"{UI.YELLOW}{text}{UI.RESET}"

    @staticmethod
    def error(text):
        return f"{UI.RED}{text}{UI.RESET}"


def read_input(prompt):
    """
    Read user input and allow ESC to quit immediately.
    """
    if not sys.stdin.isatty():
        text = input(prompt)
        if text == "\x1b":
            print(UI.warning("\nESC detected. Exiting program."))
            raise SystemExit(0)
        return text

    print(prompt, end="", flush=True)
    buffer = []

    while True:
        ch = read_key()
        if ch == "ESC":
            print(UI.warning("\nESC detected. Exiting program."))
            raise SystemExit(0)
        if ch in ("\r", "\n", "ENTER"):
            print()
            return "".join(buffer)
        if ch in ("\x7f", "\b", "BACKSPACE"):
            if buffer:
                buffer.pop()
                print("\b \b", end="", flush=True)
            continue
        if ch in ("UP", "DOWN", "LEFT", "RIGHT"):
            continue
        buffer.append(ch)
        print(ch, end="", flush=True)


def read_key():
    """
    Read one logical key across platforms.
    Returns: "UP", "DOWN", "LEFT", "RIGHT", "ENTER", "BACKSPACE", "ESC",
    or a one-character string for normal input.
    """
    if IS_WINDOWS:
        first = msvcrt.getwch()
        if first in ("\x00", "\xe0"):
            second = msvcrt.getwch()
            return {
                "H": "UP",
                "P": "DOWN",
                "K": "LEFT",
                "M": "RIGHT",
            }.get(second, "")
        if first == "\r":
            return "ENTER"
        if first == "\x08":
            return "BACKSPACE"
        if first == "\x1b":
            return "ESC"
        return first

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        first = sys.stdin.read(1)
        if first == "\x1b":
            second = sys.stdin.read(1)
            if second != "[":
                return "ESC"
            third = sys.stdin.read(1)
            return {
                "A": "UP",
                "B": "DOWN",
                "D": "LEFT",
                "C": "RIGHT",
            }.get(third, "")
        if first in ("\r", "\n"):
            return "ENTER"
        if first in ("\x7f", "\b"):
            return "BACKSPACE"
        return first
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def select_from_list(title, options):
    """
    Select an option using arrow keys inline (no screen switching).
    Space selects the highlighted item, Enter confirms.
    Falls back to plain text input if raw key reading is unavailable.
    """
    if not sys.stdin.isatty():
        for i, option in enumerate(options, start=1):
            print(f"{i}) {option}")
        raw = read_input("Enter option number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        return None

    selected_idx = 0
    chosen_idx = None
    lines_rendered = 0

    def render():
        nonlocal lines_rendered
        if lines_rendered > 0:
            print(f"\033[{lines_rendered}A", end="")
            for _ in range(lines_rendered):
                print("\033[2K", end="\n")
            print(f"\033[{lines_rendered}A", end="")

        print(title)
        for idx, option in enumerate(options):
            cursor = ">" if idx == selected_idx else " "
            marker = "[x]" if idx == chosen_idx else "[ ]"
            print(f" {cursor} {marker} {option}")
        lines_rendered = len(options) + 1
        sys.stdout.flush()

    try:
        render()
        while True:
            key = read_key()
            if key == "UP":
                selected_idx = (selected_idx - 1) % len(options)
                render()
            elif key == "DOWN":
                selected_idx = (selected_idx + 1) % len(options)
                render()
            elif key == " ":
                chosen_idx = selected_idx
                render()
            elif key == "ENTER":
                if chosen_idx is None:
                    chosen_idx = selected_idx
                break
        print()
        return options[chosen_idx]
    except Exception:
        for i, option in enumerate(options, start=1):
            print(f"{i}) {option}")
        raw = read_input("Enter option number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        return None


def select_category():
    return select_from_list("Choose category (Up/Down + Space to select, Enter to confirm):", ALLOWED_CATEGORIES)


def prompt_for_missing_parsed_fields(parsed):
    """
    Ask user to fill missing date/amount/category from smart input parse result.
    """
    date = parsed.get("date")
    amount = parsed.get("amount")
    category = parsed.get("category")
    desc = parsed.get("description", "Quick entry")

    while not date or not Validator.validate_date(date):
        if date:
            print(UI.error(f"Invalid date: {date}. Use YYYY-MM-DD."))
        else:
            print(UI.warning("Date not detected. Please enter date (YYYY-MM-DD):"))
        date = read_input("Date: ").strip()

    while not amount or not Validator.validate_amount(amount):
        if amount:
            print(UI.error(f"Invalid amount: {amount}."))
        else:
            print(UI.warning("Amount not detected. Please enter amount (HKD):"))
        amount = read_input(f"Amount (HKD, max {MAX_AMOUNT_HKD:,}): ").strip()

    while not category or not Validator.validate_category(category):
        if category:
            print(UI.error(f"Invalid category: {category}."))
        else:
            print(UI.warning("Category not detected. Please choose category:"))
        category = select_category()
        print(UI.info(f"Selected category: {category}"))

    return date, amount, category, desc


def append_parsed_transaction(transactions, parsed):
    """Validate parsed fields, append transaction, and return success flag."""
    date, amount, category, desc = prompt_for_missing_parsed_fields(parsed)

    if not Validator.validate_date(date):
        print(UI.error(f"Error: Parsed date is invalid: {date}"))
        return False
    if not Validator.validate_amount(amount):
        print(UI.error(f"Error: Parsed amount is invalid: {amount}"))
        return False
    if not Validator.validate_category(category):
        print(UI.error(f"Error: Parsed category is invalid: {category}"))
        return False

    print(UI.info(f"Parsed -> date={date}, amount={amount}, category={category}, desc={desc}"))
    parsed_amount = Validator.parse_amount(amount)
    new_tx = Transaction(date, parsed_amount, category, desc)
    transactions.append(new_tx.to_dict())
    print(UI.success("Transaction added successfully! Returning to main menu..."))
    return True


def upload_receipt_images():
    """Copy user-provided receipt images into data/receipts folder."""
    receipts_dir = Path(DATA_DIR) / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

    print(UI.info("Enter image file paths separated by commas."))
    raw = read_input("Image paths: ").strip()
    if not raw:
        print(UI.warning("No paths entered."))
        return 0

    copied = 0
    for token in raw.split(","):
        src = token.strip().strip('"').strip("'")
        if not src:
            continue
        src_path = Path(src).expanduser()
        if not src_path.exists():
            print(UI.warning(f"Skip missing file: {src_path}"))
            continue
        if src_path.suffix.lower() not in exts:
            print(UI.warning(f"Skip unsupported format: {src_path.name}"))
            continue
        target = receipts_dir / src_path.name
        try:
            shutil.copy2(str(src_path), str(target))
            copied += 1
        except Exception as exc:
            print(UI.error(f"Failed to copy {src_path.name}: {exc}"))
    return copied


def build_dashboard_lines(transactions, rules):
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")

    def visible_len(text):
        return len(ansi_re.sub("", str(text)))

    total = Analyzer.get_total_spending(transactions)
    income = Analyzer.get_total_income(transactions)
    net_balance = Analyzer.get_net_balance(transactions)
    count = len(transactions)
    expense_count = sum(1 for t in transactions if t.get("category") != "Income")
    avg = (total / expense_count) if expense_count else 0.0
    category_totals = Analyzer.get_category_totals(transactions) if transactions else {}
    top_cat = max(category_totals.items(), key=lambda x: x[1])[0] if category_totals else "N/A"

    alerts = AlertEngine(transactions, rules).check_all_alerts() if rules is not None else []
    score = Visualizer.health_score(alerts, transactions)
    tree_lines = [f"Score: {score}/100"] + Visualizer.tree_lines_by_score(score)

    left_content = [
        f"Total: HKD {total:,.2f}",
        f"Income: HKD {income:,.2f}",
        f"Net: HKD {net_balance:,.2f}",
        f"Transactions: {count}",
        f"Avg expense/tx: HKD {avg:,.2f}",
        f"Top Category: {top_cat}",
        f"Alerts: {len(alerts)}",
        f"Budget Health: {'Stable' if score >= 80 else 'Watch' if score >= 50 else 'Risk'}",
        f"Spend Density: {((count / 30) if count else 0):.1f} tx/week",
    ]

    terminal_width = shutil.get_terminal_size(fallback=(120, 24)).columns
    gap = "    "
    min_inner_width = 26
    min_box_total_width = min_inner_width + 4
    min_total_width = (min_box_total_width * 3) + (len(gap) * 2)

    # Build a full-width dashboard canvas first, then split into 3 columns.
    effective_width = max(terminal_width, min_total_width)
    usable_for_boxes = effective_width - (len(gap) * 2)
    base_box_width = usable_for_boxes // 3
    remainder = usable_for_boxes % 3
    box_widths = [base_box_width + (1 if i < remainder else 0) for i in range(3)]

    # Keep the dashboard stable and aligned by using one common content width.
    box_total_width = min(box_widths)
    col_width = box_total_width - 2
    inner_width = col_width - 2
    content_rows = 10

    def fit_cell(text):
        # Keep each dashboard cell visually stable in fixed-width layout.
        raw = str(text)
        if visible_len(raw) > inner_width:
            if "\033[" in raw:
                # Fallback: keep layout stable even if a colored line is too long.
                return ansi_re.sub("", raw)[:inner_width]
            return raw[:inner_width]
        return raw

    def center_cell(text):
        raw = fit_cell(text)
        visual = visible_len(raw)
        if visual >= inner_width:
            return raw
        left_pad = (inner_width - visual) // 2
        right_pad = inner_width - visual - left_pad
        return f"{' ' * left_pad}{raw}{' ' * right_pad}"

    def build_ascii_pie_content():
        if not (total > 0 and category_totals):
            return [
                "No spending data",
                "",
                "         .-''''''-.",
                "       .'   N/A    '.",
                "      /   Add txs    \\",
                "      |   to render   |",
                "      \\   pie chart  /",
                "       '._        _.'",
                "           '----'",
            ]

        top_items = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:4]
        labels = "1234"
        portions = []
        for idx, (cat, amt) in enumerate(top_items):
            portions.append((labels[idx], cat, amt / total))

        # Build cumulative angle ranges [0, 2*pi)
        ranges = []
        cursor = 0.0
        for sym, cat, frac in portions:
            span = frac * (2 * math.pi)
            ranges.append((sym, cat, frac, cursor, cursor + span))
            cursor += span

        # 7x15 raster pie (ellipse corrected by x_scale)
        grid_rows, grid_cols = 7, 15
        cx, cy = (grid_cols - 1) / 2, (grid_rows - 1) / 2
        radius = 3.2
        x_scale = 0.6
        pie_rows = []
        for y in range(grid_rows):
            row_chars = []
            for x in range(grid_cols):
                dx = (x - cx) * x_scale
                dy = y - cy
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > radius:
                    row_chars.append(" ")
                    continue
                angle = math.atan2(dy, dx)
                if angle < 0:
                    angle += 2 * math.pi
                ch = "."
                for sym, _cat, _frac, start, end in ranges:
                    if start <= angle < end or (end >= 2 * math.pi and angle < end - 2 * math.pi):
                        ch = sym
                        break
                row_chars.append(ch)
            pie_rows.append("".join(row_chars))

        content = [center_cell(r) for r in pie_rows]
        # Legend fits remaining lines
        for sym, cat, frac, _s, _e in ranges[:3]:
            content.append(f"{sym}:{cat[:10]:<10} {frac * 100:>5.1f}%")
        if len(ranges) == 4:
            other_pct = ranges[3][2] * 100
            content.append(f"4:{ranges[3][1][:10]:<10} {other_pct:>5.1f}%")
        return content

    mid_content = build_ascii_pie_content()

    tree_lines = [fit_cell(tree_lines[0])] + [center_cell(line) for line in tree_lines[1:]]
    tree_lines += ["", center_cell("Financial posture"), center_cell("updates with alerts")]

    def make_box(title, rows, color=None):
        clean_rows = rows[:content_rows] + [""] * max(0, content_rows - len(rows))
        top = f"+{'-' * col_width}+"
        title_row = f"| {title:<{col_width - 2}} |"
        sep = f"+{'=' * col_width}+"
        body = []
        for row in clean_rows:
            if color and row:
                raw = str(row)
                pad = max(0, (col_width - 2) - visible_len(raw))
                body.append(f"| {color}{raw}{' ' * pad}{UI.RESET} |")
            else:
                raw = str(row)
                pad = max(0, (col_width - 2) - visible_len(raw))
                body.append(f"| {raw}{' ' * pad} |")
        return [top, title_row, sep] + body + [top]

    left_box = make_box("Spend Overview", left_content)
    mid_box = make_box("Category Pie (ASCII)", mid_content)
    right_box = make_box("Wealth Tree", tree_lines)

    combined = []
    for i in range(len(left_box)):
        combined.append(f"{left_box[i]}{gap}{mid_box[i]}{gap}{right_box[i]}")
    return combined


def generate_report(transactions, rules):
    total = Analyzer.get_total_spending(transactions)
    income = Analyzer.get_total_income(transactions)
    net_balance = Analyzer.get_net_balance(transactions)
    count = len(transactions)
    category_totals = Analyzer.get_category_totals(transactions) if transactions else {}
    top_categories = Analyzer.get_top_categories(transactions, n=3) if transactions else []
    alerts = AlertEngine(transactions, rules).check_all_alerts() if rules is not None else []
    score = Visualizer.health_score(alerts, transactions)

    lines = [
        "FinanceBIO Report",
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Transactions: {count}",
        f"Total Spending: HKD {total:,.2f}",
        f"Total Income: HKD {income:,.2f}",
        f"Net Balance: HKD {net_balance:,.2f}",
        f"Health Score: {score}/100",
        f"Alert Count: {len(alerts)}",
        "",
        "Top Categories:",
    ]
    if top_categories:
        for cat, amt in top_categories:
            lines.append(f"- {cat}: HKD {amt:,.2f}")
    else:
        lines.append("- No data")

    lines.append("")
    lines.append("Suggestion:")
    if score >= 80:
        lines.append("- Good control. Keep current habits and automate weekly tracking.")
    elif score >= 50:
        lines.append("- Moderate risk. Reduce top category by 10% next week.")
    elif score >= 20:
        lines.append("- High risk. Set a hard cap for your top category today.")
    else:
        lines.append("- Critical. Pause non-essential spending and review all alerts.")

    report_text = "\n".join(lines)
    report_path = os.path.join(REPORTS_DIR, "generated_report.txt")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(UI.title("\nGENERATED REPORT"))
    print(report_text)
    print(UI.success(f"\nSaved to {report_path}"))
    return report_text, report_path


def main_menu(transactions):
    options = [
        "Add Transaction",
        "View All Transactions",
        "View Summary Statistics",
        "Check Financial Alerts",
        "Load Data (Case Studies)",
        "Generate Report (Suggestion)",
        "More Tools",
        "Exit",
    ]

    print()
    print(UI.title("╔══════════════════════════════════════════════════╗"))
    print(UI.title("║      FinanceBIO - HKU Student Budget Assistant   ║"))
    print(UI.title("╚══════════════════════════════════════════════════╝"))
    print(UI.info("\nDashboard"))
    for line in build_dashboard_lines(transactions, main_menu.cached_rules):
        print(line)
    print(UI.info("\nRecommendation: choose 'Generate Report (Suggestion)' for a one-page summary."))
    print(f"{UI.GRAY}{'-' * 96}{UI.RESET}")
    print(UI.info("Operations"))

    selected = select_from_list("Select an option (Up/Down + Space to select, Enter to confirm):", options)
    if selected is None:
        return None
    return str(options.index(selected) + 1)


main_menu.cached_rules = []

def run():
    # Initial Data Load [cite: 127]
    transactions = FileIO.load_from_json(DATA_FILE, Transaction)
    rules = FileIO.load_from_json(RULES_FILE, dict)
    if not rules:
        # Fallback for older datasets or renamed files.
        rules = FileIO.load_from_json(os.path.join(DATA_DIR, "user_created_rules.json"), dict)

    while True:
        main_menu.cached_rules = rules
        choice = main_menu(transactions)

        if choice == '1':
            # Add Transaction with Validation [cite: 77, 118]
            mode = select_from_list(
                "Add Transaction mode (Up/Down + Space to select, Enter to confirm):",
                ["Guided Input", "Smart Text Input"],
            )

            if mode == "Smart Text Input":
                raw = read_input(
                    "Enter transaction text (e.g. 2026/04/21 spent $65.5 on food CYM roast goose): "
                )
                parsed = parse_unstructured_transaction(raw)
                if not parsed:
                    print(UI.error("Error: Unable to parse input text."))
                    continue
                append_parsed_transaction(transactions, parsed)
                continue
            else:
                date = read_input("Enter date (YYYY-MM-DD): ")
                while not Validator.validate_date(date):
                    print(UI.error("Error: Invalid date format."))
                    date = read_input("Enter date (YYYY-MM-DD): ")
                
                amount = read_input(f"Enter amount (HKD, max {MAX_AMOUNT_HKD:,}): ")
                while not Validator.validate_amount(amount):
                    print(UI.error(f"Error: Invalid amount. Use HKD value <= {MAX_AMOUNT_HKD:,}."))
                    amount = read_input(f"Enter amount (HKD, max {MAX_AMOUNT_HKD:,}): ")

                print(UI.info("Categories: use arrow keys to select."))
                category = select_category()
                print(UI.info(f"Selected category: {category}"))
                if not Validator.validate_category(category):
                    print(UI.error("Error: Category not recognized."))
                    continue

                # Keep quick-entry behavior for guided flow as requested.
                parsed_amount = Validator.parse_amount(amount)
                new_tx = Transaction(date, parsed_amount, category, "")

            transactions.append(new_tx.to_dict())
            print(UI.success("Transaction added successfully! Returning to main menu..."))
            continue

        elif choice == '2':
            print(UI.title("\nAll Transactions"))
            if not transactions:
                print(UI.warning("No transactions available."))
            else:
                rows = [
                    (
                        t.get("date", ""),
                        f"{t.get('amount', 0):.2f}",
                        t.get("category", "N/A"),
                        t.get("description", ""),
                    )
                    for t in transactions
                ]
                used_rich = render_rich_table(
                    "All Transactions",
                    ["Date", "Amount", "Category", "Description"],
                    rows,
                )
                if not used_rich:
                    print(f"{'Date':<12} | {'Amount':<12} | {'Category':<10} | Description")
                    print("-" * 72)
                    for date, amount, category, desc in rows:
                        print(f"{date:<12} | {amount:<12} | {category:<10} | {desc}")

        elif choice == '3':
            # Analyzer Statistics [cite: 118, 127]
            total = Analyzer.get_total_spending(transactions)
            print(UI.title(f"\nTotal Spending: HKD {total:.2f}"))
            
            top_cats = Analyzer.get_top_categories(transactions)
            rows = [(cat, f"HKD {amt:.2f}") for cat, amt in top_cats]
            used_rich = render_rich_table("Top Categories", ["Category", "Amount"], rows)
            if not used_rich:
                print(UI.info("Top Categories:"))
                for cat, amt in top_cats:
                    print(f"- {cat}: HKD {amt:.2f}")

        elif choice == '4':
            # Alert Engine Execution [cite: 118, 127]
            engine = AlertEngine(transactions, rules)
            alerts = engine.check_all_alerts()
            print(UI.info("\nWealth Tree:"))
            print(Visualizer.wealth_tree(alerts, transactions))
            if not alerts:
                print(UI.success("\nEverything looks good! No alerts triggered."))
            else:
                print(UI.warning("\n!!! FINANCIAL ALERTS !!!"))
                for msg in alerts:
                    print(UI.warning(msg))

        elif choice == '5':
            # Load specific files for Case Studies 
            if not os.path.isdir(DATA_DIR):
                print(UI.error(f"Data directory not found: {DATA_DIR}"))
                continue
            case_files = sorted(
                [
                    name
                    for name in os.listdir(DATA_DIR)
                    if name.startswith("case") and name.endswith(".json") and "budget" not in name
                ]
            )
            print(UI.info("Available case transaction files:"))
            for idx, name in enumerate(case_files, start=1):
                print(f"  {idx}. {name}")
            filename = read_input("Enter the filename from data/ (e.g., case1_student_cym_food.json): ")
            transactions = FileIO.load_from_json(os.path.join(DATA_DIR, filename), Transaction)
            print(UI.success(f"Loaded {len(transactions)} records from {filename}."))
            FileIO.save_to_json(transactions, DATA_FILE)

        elif choice == '6':
            generate_report(transactions, rules)

        elif choice == '7':
            tool = select_from_list(
                "More Tools (Up/Down + Space to select, Enter to confirm):",
                [
                    "AI Spending Analysis",
                    "Voice Input (Mic)",
                    "Upload Receipt Images",
                    "Run Receipt Parser (OCR)",
                    "Save Current Data",
                    "Back",
                ],
            )
            if tool == "AI Spending Analysis":
                result = Analyzer.analyze_spending(transactions)
                print(UI.title("\nAI SPENDING ANALYSIS"))
                print(result)
            elif tool == "Voice Input (Mic)":
                print(UI.info("\n--- Voice Input ---"))
                if transcribe_from_microphone is None:
                    print(UI.error("Voice module not found: src/voice_input.py"))
                    manual = read_input("Paste voice transcript manually? (y/n): ").strip().lower()
                    if manual != "y":
                        continue
                    content = read_input("Transcript: ").strip()
                    if not content:
                        print(UI.warning("No transcript entered."))
                        continue
                else:
                    ok, content = transcribe_from_microphone()
                    if not ok:
                        print(UI.warning(content))
                        manual = read_input("Microphone unavailable. Paste transcript manually? (y/n): ").strip().lower()
                        if manual != "y":
                            continue
                        content = read_input("Transcript: ").strip()
                        if not content:
                            print(UI.warning("No transcript entered."))
                            continue
                    else:
                        print(UI.info(f"Transcribed: {content}"))
                parsed = parse_unstructured_transaction(content)
                if not parsed:
                    print(UI.error("Could not parse transcribed text into transaction fields."))
                    continue
                append_parsed_transaction(transactions, parsed)
            elif tool == "Upload Receipt Images":
                print(UI.info("\n--- Upload Receipt Images ---"))
                copied = upload_receipt_images()
                if copied <= 0:
                    print(UI.warning("No receipt images uploaded."))
                else:
                    print(UI.success(f"Uploaded {copied} image(s) to data/receipts/."))
                    run_now = read_input("Run OCR parser now? (y/n): ").strip().lower()
                    if run_now == "y":
                        if run_receipt_parser is None:
                            print(UI.error("Receipt parser module not found: src/receipt_parser_easyocr.py"))
                            continue
                        parsed_transactions = run_receipt_parser()
                        if not parsed_transactions:
                            print(UI.warning("No receipts were processed after upload."))
                            continue
                        imported = 0
                        for tx in parsed_transactions:
                            orig_cat = tx.get("category", "Other")
                            mapped_cat = CATEGORY_MAP.get(orig_cat, "Other")
                            new_tx = {
                                "date": tx.get("date"),
                                "amount": tx.get("amount"),
                                "category": mapped_cat,
                                "description": tx.get("description", "Receipt import"),
                                "notes": f"Imported from receipt OCR (original category: {orig_cat})",
                            }
                            transactions.append(new_tx)
                            imported += 1
                        print(UI.success(f"Imported {imported} transactions into current session."))
                        if FileIO.save_to_json(transactions, DATA_FILE):
                            print(UI.success("Data automatically saved."))
            elif tool == "Run Receipt Parser (OCR)":
                print(UI.info("\n--- Running Receipt Parser ---"))
                if run_receipt_parser is None:
                    print(UI.error("Receipt parser module not found: src/receipt_parser_easyocr.py"))
                    continue

                parsed_transactions = run_receipt_parser()
                if not parsed_transactions:
                    print(UI.warning("No receipts were processed. Check images under data/receipts/."))
                    continue

                answer = read_input(
                    f"Found {len(parsed_transactions)} parsed receipts. Import into current data? (y/n): "
                ).strip().lower()
                if answer == "y":
                    imported = 0
                    for tx in parsed_transactions:
                        orig_cat = tx.get("category", "Other")
                        mapped_cat = CATEGORY_MAP.get(orig_cat, "Other")
                        new_tx = {
                            "date": tx.get("date"),
                            "amount": tx.get("amount"),
                            "category": mapped_cat,
                            "description": tx.get("description", "Receipt import"),
                            "notes": f"Imported from receipt OCR (original category: {orig_cat})",
                        }
                        transactions.append(new_tx)
                        imported += 1
                    print(UI.success(f"Imported {imported} transactions into current session."))
                    if FileIO.save_to_json(transactions, DATA_FILE):
                        print(UI.success("Data automatically saved."))
                else:
                    print(UI.info("Import cancelled. Parsed CSV remains available for manual review."))
            elif tool == "Save Current Data":
                if FileIO.save_to_json(transactions, DATA_FILE):
                    print(UI.success("Data saved successfully."))

        elif choice == '8':
            # Exit after saving
            FileIO.save_to_json(transactions, DATA_FILE)
            print(UI.success("Goodbye! Stay financially healthy."))
            break
        
        else:
            print(UI.error("Invalid selection. Please choose 1-8."))

if __name__ == "__main__":
    run()
