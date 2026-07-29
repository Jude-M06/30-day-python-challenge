#---------------------------------------------------
# you need to install yfinance pandas schedule first
# python -m pip install yfinance pandas schedule
#---------------------------------------------------

import json
import time
import schedule
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

PORTFOLIO_FILE = Path("portfolio.json")


GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def green(s):  return f"{GREEN}{s}{RESET}"
def red(s):    return f"{RED}{s}{RESET}"
def yellow(s): return f"{YELLOW}{s}{RESET}"
def bold(s):   return f"{BOLD}{s}{RESET}"



def load_portfolio() -> dict:
    if PORTFOLIO_FILE.exists():
        with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"holdings": {}, "alerts": {}}

def save_portfolio(portfolio: dict):
    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
        json.dump(portfolio, f, indent=2)



def fetch_prices(symbols: list[str]) -> dict[str, float]:
    if not symbols:
        return {}
    try:
        raw = yf.download(
            " ".join(symbols),
            period="2d",
            auto_adjust=True,
            progress=False,
        )
        prices = {}
        close = raw["Close"]
        
        if isinstance(close, pd.Series):
            if symbols:
                prices[symbols[0]] = float(close.iloc[-1])
        else:
            for sym in symbols:
                if sym in close.columns:
                    prices[sym] = float(close[sym].iloc[-1])
        return prices
    except Exception as e:
        print(f"  {yellow('Warning:')} Could not fetch prices: {e}")
        return {}

def fetch_prev_close(symbol: str) -> float | None:
    try:
        info = yf.Ticker(symbol).info
        return info.get("previousClose") or info.get("regularMarketPreviousClose")
    except Exception:
        return None



def calculate_portfolio(holdings: dict, prices: dict) -> list[dict]:
    positions = []
    for sym, h in holdings.items():
        price = prices.get(sym)
        if price is None:
            continue
        shares     = h["shares"]
        avg_cost   = h["avg_cost"]
        cost_basis = shares * avg_cost
        mkt_value  = shares * price
        pnl        = mkt_value - cost_basis
        pnl_pct    = (pnl / cost_basis * 100) if cost_basis else 0

        positions.append({
            "symbol":     sym,
            "shares":     shares,
            "avg_cost":   avg_cost,
            "price":      price,
            "mkt_value":  mkt_value,
            "cost_basis": cost_basis,
            "pnl":        pnl,
            "pnl_pct":    pnl_pct,
        })
    return sorted(positions, key=lambda p: p["mkt_value"], reverse=True)



def fmt_pnl(val: float, pct: float) -> str:
    sign  = "+" if val >= 0 else ""
    s     = f"{sign}£{val:,.2f} ({sign}{pct:.1f}%)"
    return green(s) if val >= 0 else red(s)

def print_portfolio(positions: list[dict]):
    if not positions:
        print("  No positions to display.")
        return

    total_value = sum(p["mkt_value"]  for p in positions)
    total_cost  = sum(p["cost_basis"] for p in positions)
    total_pnl   = total_value - total_cost
    total_pct   = (total_pnl / total_cost * 100) if total_cost else 0

    now = datetime.now().strftime("%H:%M:%S")
    print(f"\n  {bold('PORTFOLIO')}  —  as of {now}")
    print("  " + "─" * 72)
    print(f"  {'Symbol':<8} {'Shares':>7} {'Avg Cost':>10} "
          f"{'Price':>10} {'Value':>12} {'P&L':>22}")
    print("  " + "─" * 72)

    for p in positions:
        pnl_str = fmt_pnl(p["pnl"], p["pnl_pct"])
        print(f"  {p['symbol']:<8} {p['shares']:>7.2f} "
              f"£{p['avg_cost']:>9.2f} £{p['price']:>9.2f} "
              f"£{p['mkt_value']:>11,.2f}  {pnl_str}")

    print("  " + "-" * 72)
    print(f"  {'TOTAL':<8} {'':>7} {'':>10} {'':>10} "
          f"£{total_value:>11,.2f}  {fmt_pnl(total_pnl, total_pct)}")
    print(f"\n  Cost basis: £{total_cost:,.2f}")



def check_alerts(positions: list[dict], alerts: dict):
    triggered = False
    for p in positions:
        sym    = p["symbol"]
        price  = p["price"]
        thresholds = alerts.get(sym, {})

        above = thresholds.get("above")
        below = thresholds.get("below")

        if above and price >= above:
            print(yellow(f"   ALERT: {sym} is ABOVE £{above:.2f} (current: £{price:.2f})"))
            triggered = True
        if below and price <= below:
            print(yellow(f"   ALERT: {sym} is BELOW £{below:.2f} (current: £{price:.2f})"))
            triggered = True

    if not triggered:
        print("  No alerts triggered.")



def add_holding(portfolio: dict):
    sym    = input("  Ticker symbol (e.g. AAPL): ").strip().upper()
    if not sym:
        return
    try:
        shares   = float(input("  Number of shares: ").strip())
        avg_cost = float(input("  Average cost per share (£): ").strip())
    except ValueError:
        print("  Invalid number.")
        return
    portfolio["holdings"][sym] = {
        "shares": shares, "avg_cost": avg_cost, "currency": "USD"
    }
    save_portfolio(portfolio)
    print(f"   Added {shares} shares of {sym} at £{avg_cost:.2f}")

def remove_holding(portfolio: dict):
    sym = input("  Ticker to remove: ").strip().upper()
    if sym in portfolio["holdings"]:
        del portfolio["holdings"][sym]
        portfolio["alerts"].pop(sym, None)
        save_portfolio(portfolio)
        print(f"    Removed {sym}")
    else:
        print(f"  {sym} not in portfolio.")

def set_alert(portfolio: dict):
    sym = input("  Ticker for alert: ").strip().upper()
    if sym not in portfolio["holdings"]:
        print(f"  {sym} not in your portfolio.")
        return
    above_raw = input("  Alert above price (Enter to skip): ").strip()
    below_raw = input("  Alert below price (Enter to skip): ").strip()
    portfolio["alerts"][sym] = {
        "above": float(above_raw) if above_raw else None,
        "below": float(below_raw) if below_raw else None,
    }
    save_portfolio(portfolio)
    print(f"  Alert set for {sym}")

def show_history(portfolio: dict):
    sym = input("  Ticker for history: ").strip().upper()
    if sym not in portfolio["holdings"]:
        print(f"  {sym} not in your portfolio.")
        return
    period = input("  Period (1mo / 3mo / 6mo / 1y) [1mo]: ").strip() or "1mo"
    try:
        hist = yf.Ticker(sym).history(period=period)
        if hist.empty:
            print("  No data returned.")
            return
        
        closes = hist["Close"].tolist()
        lo, hi = min(closes), max(closes)
        rows, width = 8, 40
        print(f"\n  {sym} — {period} price history  (Lo: £{lo:.2f}  Hi: £{hi:.2f})")
        for row in range(rows, -1, -1):
            threshold = lo + (hi - lo) * row / rows
            line = ""
            step = max(1, len(closes) // width)
            for i in range(0, len(closes), step):
                line += "█" if closes[i] >= threshold else " "
            price_label = f"£{threshold:6.1f} |"
            print(f"  {price_label} {line}")
        print("  " + " " * 9 + "└" + "─" * width)
    except Exception as e:
        print(f"  Error: {e}")



def refresh_and_display(portfolio: dict):
    symbols   = list(portfolio["holdings"].keys())
    prices    = fetch_prices(symbols)
    positions = calculate_portfolio(portfolio["holdings"], prices)
    print_portfolio(positions)
    check_alerts(positions, portfolio.get("alerts", {}))

def auto_refresh(portfolio: dict, interval: int = 60):
    print(f"  Auto-refresh every {interval}s — Ctrl+C to stop.")
    refresh_and_display(portfolio)
    schedule.every(interval).seconds.do(refresh_and_display, portfolio)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        schedule.clear()
        print("\n  Stopped.")



def show_menu():
    print("\n=== Portfolio Tracker ===")
    print("  r) Refresh prices")
    print("  a) Add holding")
    print("  x) Remove holding")
    print("  l) Set price alert")
    print("  h) Price history chart")
    print("  w) Auto-refresh (watch mode)")
    print("  q) Quit")

def main():
    portfolio = load_portfolio()

    
    symbols   = list(portfolio["holdings"].keys())
    if symbols:
        print("  Fetching prices...")
        prices    = fetch_prices(symbols)
        positions = calculate_portfolio(portfolio["holdings"], prices)
        print_portfolio(positions)
        check_alerts(positions, portfolio.get("alerts", {}))
    else:
        print("  Portfolio is empty — add a holding with 'a'.")

    while True:
        show_menu()
        choice = input("Choice: ").strip().lower()

        if choice == "r":
            symbols   = list(portfolio["holdings"].keys())
            prices    = fetch_prices(symbols)
            positions = calculate_portfolio(portfolio["holdings"], prices)
            print_portfolio(positions)
            check_alerts(positions, portfolio.get("alerts", {}))
        elif choice == "a":
            add_holding(portfolio)
        elif choice == "x":
            remove_holding(portfolio)
        elif choice == "l":
            set_alert(portfolio)
        elif choice == "h":
            show_history(portfolio)
        elif choice == "w":
            try:
                interval = int(input("  Refresh every N seconds [60]: ").strip() or 60)
            except ValueError:
                interval = 60
            auto_refresh(portfolio, interval)
        elif choice == "q":
            print("Goodbye!")
            break
        else:
            print("  Invalid choice — try again.")

if __name__ == "__main__":
    main()