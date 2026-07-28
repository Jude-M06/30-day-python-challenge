#------------------------------------------------
# you need to install reportlab matplotlib first
# python -m pip install reportlab matplotlib
#------------------------------------------------

import argparse
import json
import io
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")          
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    HRFlowable, Image, PageBreak, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)


BLUE   = colors.HexColor("#2563eb")
LIGHT  = colors.HexColor("#eff6ff")
GREY   = colors.HexColor("#6b7280")
WHITE  = colors.white
BLACK  = colors.black



def get_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle", parent=base["Title"],
            fontSize=26, textColor=BLUE, spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle", parent=base["Normal"],
            fontSize=13, textColor=GREY, spaceAfter=4,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"],
            fontSize=14, textColor=BLUE, spaceBefore=14, spaceAfter=6,
        ),
        "body": base["Normal"],
        "bold": ParagraphStyle(
            "Bold", parent=base["Normal"], fontName="Helvetica-Bold"
        ),
    }



def load_data(path: str) -> dict:
    p = Path(path)
    if p.suffix == ".json":
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    
    import csv
    with open(p, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["amount"] = float(row["amount"])
    return {
        "report_title": p.stem.replace("_", " ").title(),
        "period": "All time",
        "generated_by": "Python",
        "expenses": rows,
    }

def summarise(expenses: list) -> dict:
    by_cat   = defaultdict(float)
    by_date  = defaultdict(float)
    total    = 0.0
    for e in expenses:
        amt = float(e["amount"])
        by_cat[e["category"]] += amt
        by_date[e["date"][:7]] += amt   # YYYY-MM
        total += amt
    return {
        "by_category": dict(sorted(by_cat.items(), key=lambda x: x[1], reverse=True)),
        "by_date":     dict(sorted(by_date.items())),
        "total":       total,
        "count":       len(expenses),
        "avg":         total / len(expenses) if expenses else 0,
    }



def fig_to_image(fig, width=7*cm, height=6*cm) -> Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width, height=height)

def make_bar_chart(by_category: dict) -> Image:
    fig, ax = plt.subplots(figsize=(4.5, 3))
    cats    = list(by_category.keys())
    vals    = list(by_category.values())
    bars    = ax.bar(cats, vals, color="#2563eb", edgecolor="white", width=0.6)
    ax.set_title("Spending by Category", fontsize=11, pad=8)
    ax.set_ylabel("Amount (£)")
    ax.tick_params(axis="x", rotation=30, labelsize=8)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"£{val:.0f}", ha="center", va="bottom", fontsize=7)
    fig.tight_layout()
    return fig_to_image(fig)

def make_pie_chart(by_category: dict) -> Image:
    fig, ax = plt.subplots(figsize=(3.5, 3.5))
    ax.pie(
        list(by_category.values()),
        labels=list(by_category.keys()),
        autopct="%1.0f%%",
        startangle=140,
        textprops={"fontsize": 8},
    )
    ax.set_title("Spending Proportion", fontsize=11, pad=8)
    fig.tight_layout()
    return fig_to_image(fig, width=6*cm, height=6*cm)



def make_expense_table(expenses: list, styles: dict) -> Table:
    header = ["Date", "Category", "Description", "Amount"]
    rows   = [header]
    total  = 0.0

    for e in sorted(expenses, key=lambda x: x["date"]):
        amt = float(e["amount"])
        total += amt
        rows.append([
            e["date"],
            e["category"],
            e.get("description", "")[:40],
            f"£{amt:.2f}",
        ])

    rows.append(["", "", "TOTAL", f"£{total:.2f}"])

    col_widths = [2.5*cm, 3.5*cm, 8*cm, 2.5*cm]
    table = Table(rows, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        
        ("BACKGROUND",  (0, 0), (-1, 0),  BLUE),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),  9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        
        ("FONTSIZE",    (0, 1), (-1, -2), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [WHITE, LIGHT]),
        ("GRID",        (0, 0), (-1, -1), 0.3, colors.HexColor("#d1d5db")),
        
        ("FONTNAME",    (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND",  (0, -1), (-1, -1), colors.HexColor("#f3f4f6")),
        ("TOPPADDING",  (0, -1), (-1, -1), 6),
    ]
    table.setStyle(TableStyle(style_cmds))
    return table


def build_report(data: dict, output_path: str):
    styles   = get_styles()
    expenses = data["expenses"]
    summary  = summarise(expenses)
    doc      = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm,  bottomMargin=2*cm,
    )
    story = []
    S = Spacer

    
    story += [
        Paragraph(data.get("report_title", "Expense Report"), styles["title"]),
        Paragraph(f"Period: {data.get('period', '')}  |  "
                  f"Generated: {datetime.now().strftime('%d %b %Y')}  |  "
                  f"By: {data.get('generated_by', 'Python')}", styles["subtitle"]),
        HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=12),
    ]

    
    stats_data = [
        ["Total Spent", "Transactions", "Avg per Transaction", "Top Category"],
        [
            f"£{summary['total']:.2f}",
            str(summary["count"]),
            f"£{summary['avg']:.2f}",
            list(summary["by_category"].keys())[0] if summary["by_category"] else "—",
        ],
    ]
    stats_table = Table(stats_data, colWidths=[4*cm]*4)
    stats_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 9),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE",      (0, 1), (-1, 1), 14),
        ("FONTNAME",      (0, 1), (-1, 1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 1), (-1, 1), BLUE),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("GRID",          (0, 0), (-1, -1), 0.3, GREY),
    ]))
    story += [stats_table, S(1, 0.4*inch)]

    
    story.append(Paragraph("Spending Breakdown", styles["h1"]))
    bar = make_bar_chart(summary["by_category"])
    pie = make_pie_chart(summary["by_category"])
    chart_table = Table([[bar, pie]], colWidths=[10*cm, 7*cm])
    chart_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story += [chart_table, S(1, 0.3*inch)]

    
    story.append(Paragraph("Transaction Detail", styles["h1"]))
    story.append(make_expense_table(expenses, styles))

    
    doc.build(story)
    print(f"  Report saved: {output_path}")



def main():
    parser = argparse.ArgumentParser(description="Generate a PDF expense report.")
    parser.add_argument("--data",   default="data.json",   help="Input JSON or CSV")
    parser.add_argument("--output", default="report.pdf",  help="Output PDF filename")
    args = parser.parse_args()

    print(f"  Loading data from '{args.data}'...")
    data = load_data(args.data)
    print(f"  Building report with {len(data['expenses'])} entries...")
    build_report(data, args.output)

if __name__ == "__main__":
    main()