import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("expenses.csv")
FIELDNAMES = ["date", "category", "amount", "description"]

def ensure_file():
    if not DATA_FILE.exists():
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def load_expenses():
    ensure_file()
    with open(DATA_FILE, "r", newline="", encoding="utf-8") as f:
        reader =csv.DictReader(f)
        expenses = []
        for row in reader:
            row["amount"] = float(row["amount"])
            expenses.append(row)
    return expenses

def add_expense(date, category, amount, description):
    ensure_file()
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)   
        writer.writerow({
            "date": date, "category": category,
            "amount": f"{amount:.2f}", "description": description,
        })

def total_by_category(expenses):
    totals = defaultdict(float)
    for e in expenses:
        totals[e["category"]] += e["amount"]
    return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))

def total_by_month(expenses):
    totals = defaultdict(float)
    for e in expenses:
        month = e["date"][:7]   # "2025-06-01" -> "2025-06"
        totals[month] += e["amount"]
    return dict(sorted(totals.items()))

def grand_total(expenses):
    return sum(e["amount"] for e in expenses)

def print_bar_chart(data, max_width=30):
    if not data:
        return
    max_val = max(data.values())
    for label, value in data.items():
        bar_len = int(value / max_val * max_width) if max_val else 0
        bar = "█" * bar_len
        print(f"  {label:<15} £{value:>8.2f}  {bar}")

def print_summary(expenses):
    if not expenses:
        print("  No expenses logged yet.")
        return

    print("\n" + "-" * 44)
    print("           EXPENSE SUMMARY")
    print("-" * 44)
    print(f"  Total spent : £{grand_total(expenses):.2f}")
    print(f"  Entries     : {len(expenses)}")

    print("\n  By category:")
    print_bar_chart(total_by_category(expenses))

    print("\n  By month:")
    print_bar_chart(total_by_month(expenses))
    print("-" * 44)

def list_expenses(expenses, limit=None):
    if not expenses:
        print("  No expenses logged yet.")
        return
    rows = sorted(expenses, key=lambda e: e["date"], reverse=True)
    if limit:
        rows = rows[:limit]
    print(f"\n  {'Date':<12} {'Category':<14} {'Amount':>9}  Description")
    print("  " + "-" * 60)
    for e in rows:
        print(f"  {e['date']:<12} {e['category']:<14} "
              f"£{e['amount']:>7.2f}  {e['description']}")
        
def get_date():
    today = datetime.now().strftime("%Y-%m-%d")
    raw = input(f"  Date (YYYY-MM-DD) [{today}]: ").strip()
    if not raw:
        return today
    try:
         datetime.strptime(raw, "%Y-%m-%d")
         return raw
    except ValueError:
        print("  Invalid format — using today's date.")
        return today

def get_amount():
    while True:
        try:
            val = float(input("  Amount: £"))
            if val > 0:
                return val
            print("  Amount must be positive.")
        except ValueError:
            print("  Please enter a valid number.")

def show_menu():
    print("\n=== Expense Tracker ===")
    print("  a) Add expense")
    print("  l) List recent expenses")
    print("  s) Summary")
    print("  q) Quit")

def main():
    while True:
        show_menu()
        choice = input("Choice: ").strip().lower()

        if choice == "a":
            date        = get_date()
            category    = input("  Category: ").strip().title()
            amount      = get_amount()
            description = input("  Description (optional): ").strip()
            add_expense(date, category, amount, description)
            print("  ✅ Expense logged.")

        elif choice == "l":
            expenses = load_expenses()
            list_expenses(expenses, limit=10)

        elif choice == "s":
            expenses = load_expenses()
            print_summary(expenses)

        elif choice == "q":
            print("Goodbye!")
            break

        else:
            print("  Invalid choice — try again.")

if __name__ == "__main__":
    main()
