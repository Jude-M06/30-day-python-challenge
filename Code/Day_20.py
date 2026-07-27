import argparse
import sys
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def load_csv(path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print(f"  File not found: {path}")
        sys.exit(1)
    except Exception as e:
        print(f"  Error reading CSV: {e}")
        sys.exit(1)

    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df = df.dropna(subset=["amount"])
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df

def print_summary(df, path):
    print(f"\n{'-'*44}")
    print(f"  FILE: {Path(path).name}")
    print(f"{'-'*44}")
    print(f"  Rows       : {df.shape[0]}")
    print(f"  Columns    : {df.shape[1]}  → {', '.join(df.columns)}")

    numeric = df.select_dtypes(include="number")
    if not numeric.empty:
        print(f"\n  Numeric summary:")
        print(numeric.describe().to_string())

    print(f"\n  First 5 rows:")
    print(df.head().to_string(index=False))
    print(f"{'-'*44}")

def save_or_show(fig, save_path=None):
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Chart saved to '{save_path}'.")
    else:
        plt.show()
    plt.close(fig)

def annotate_bars(ax):
    for bar in ax.patches:
        h = bar.get_height()
        if h > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + ax.get_ylim()[1] * 0.01,
                f"{h:.0f}",
                ha="center", va="bottom", fontsize=9,
            )

def plot_bar(df, group_col="category", value_col="amount", save_path=None):
    if group_col not in df.columns or value_col not in df.columns:
        print(f"  Columns '{group_col}' or '{value_col}' not found.")
        return

    grouped = df.groupby(group_col)[value_col].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    grouped.plot(kind="bar", ax=ax, color="steelblue", edgecolor="white", width=0.7)
    ax.set_title(f"Total {value_col} by {group_col}", fontsize=14, pad=12)
    ax.set_xlabel(group_col.title())
    ax.set_ylabel(value_col.title())
    ax.tick_params(axis="x", rotation=45)
    annotate_bars(ax)
    save_or_show(fig, save_path)

def plot_line(df, date_col="date", value_col="amount", save_path=None):
    if date_col not in df.columns or value_col not in df.columns:
        print(f"  Columns '{date_col}' or '{value_col}' not found.")
        return
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        print(f"  Column '{date_col}' is not a date — can't plot line chart.")
        return

    monthly = df.groupby(df[date_col].dt.to_period("M"))[value_col].sum()
    monthly.index = monthly.index.astype(str)

    fig, ax = plt.subplots(figsize=(10, 5))
    monthly.plot(kind="line", ax=ax, marker="o", color="coral", linewidth=2)
    ax.set_title(f"Monthly {value_col} trend", fontsize=14, pad=12)
    ax.set_xlabel("Month")
    ax.set_ylabel(value_col.title())
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    save_or_show(fig, save_path)

def plot_pie(df, group_col="category", value_col="amount", save_path=None):
    if group_col not in df.columns or value_col not in df.columns:
        print(f"  Columns '{group_col}' or '{value_col}' not found.")
        return

    grouped = df.groupby(group_col)[value_col].sum()

    fig, ax = plt.subplots(figsize=(8, 8))
    grouped.plot(
        kind="pie", ax=ax,
        autopct="%1.1f%%", startangle=140,
        pctdistance=0.85, labeldistance=1.05,
    )
    ax.set_title(f"{value_col.title()} by {group_col}", fontsize=14, pad=12)
    ax.set_ylabel("")
    save_or_show(fig, save_path)

def plot_dashboard(df, save_path=None):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Data Dashboard", fontsize=16, y=1.02)

    # bar
    if "category" in df.columns and "amount" in df.columns:
        grouped = df.groupby("category")["amount"].sum().sort_values(ascending=False)
        grouped.plot(kind="bar", ax=axes[0], color="steelblue", edgecolor="white")
        axes[0].set_title("By category")
        axes[0].tick_params(axis="x", rotation=45)

    # line
    if "date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["date"]):
        monthly = df.groupby(df["date"].dt.to_period("M"))["amount"].sum()
        monthly.index = monthly.index.astype(str)
        monthly.plot(kind="line", ax=axes[1], marker="o", color="coral")
        axes[1].set_title("Monthly trend")
        axes[1].tick_params(axis="x", rotation=45)

    # pie
    if "category" in df.columns and "amount" in df.columns:
        grouped = df.groupby("category")["amount"].sum()
        grouped.plot(kind="pie", ax=axes[2], autopct="%1.0f%%", startangle=140)
        axes[2].set_title("Proportion")
        axes[2].set_ylabel("")

    save_or_show(fig, save_path)

def interactive_menu(df, path):
    print_summary(df, path)
    while True:
        print("\n  1) Bar chart (by category)")
        print("  2) Line chart (monthly trend)")
        print("  3) Pie chart (proportions)")
        print("  4) Full dashboard (all 3)")
        print("  5) Print summary stats")
        print("  q) Quit")
        choice = input("Choice: ").strip().lower()

        if choice == "1":
            save = input("  Save to file? (Enter filename or leave blank): ").strip() or None
            plot_bar(df, save_path=save)
        elif choice == "2":
            save = input("  Save to file? (Enter filename or leave blank): ").strip() or None
            plot_line(df, save_path=save)
        elif choice == "3":
            save = input("  Save to file? (Enter filename or leave blank): ").strip() or None
            plot_pie(df, save_path=save)
        elif choice == "4":
            save = input("  Save to file? (Enter filename or leave blank): ").strip() or None
            plot_dashboard(df, save_path=save)
        elif choice == "5":
            print_summary(df, path)
        elif choice == "q":
            print("  Goodbye!")
            break
        else:
            print("  Invalid choice.")

def build_parser():
    parser = argparse.ArgumentParser(description="CSV data visualiser")
    parser.add_argument("csv", help="Path to CSV file")
    parser.add_argument("--chart", choices=["bar","line","pie","dashboard"],
                        default="dashboard", help="Chart type (default: dashboard)")
    parser.add_argument("--group", default="category",
                        help="Column to group by (default: category)")
    parser.add_argument("--value", default="amount",
                        help="Numeric column (default: amount)")
    parser.add_argument("--save", metavar="FILE",
                        help="Save chart to file instead of displaying")
    return parser

def main():
    if len(sys.argv) == 1:
        path = input("  CSV file path: ").strip()
        if not path:
            print("  No file provided.")
            return
        df = load_csv(path)
        interactive_menu(df, path)
        return

    parser = build_parser()
    args   = parser.parse_args()
    df     = load_csv(args.csv)

    print_summary(df, args.csv)

    if args.chart == "bar":
        plot_bar(df, args.group, args.value, args.save)
    elif args.chart == "line":
        plot_line(df, save_path=args.save)
    elif args.chart == "pie":
        plot_pie(df, args.group, args.value, args.save)
    else:
        plot_dashboard(df, args.save)

if __name__ == "__main__":
    main()

