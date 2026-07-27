#--------------------------------
#use this command first:
#  python -m pip install requests beautifulsoup4 
#--------------------------------

import csv
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

BASE_URL   = "https://quotes.toscrape.com"
OUTPUT_CSV = Path("quotes.csv")
HEADERS    = {"User-Agent": "Mozilla/5.0 (educational scraper)"}


def fetch_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"  Error fetching {url}: {e}")
        return None
    
def parse_quotes(soup):
    quotes = []
    for div in soup.select("div.quote"):
        text   = div.select_one("span.text").get_text(strip=True)
        author = div.select_one("small.author").get_text(strip=True)
        tags   = [t.get_text(strip=True) for t in div.select("a.tag")]
        quotes.append({
            "text":   text,
            "author": author,
            "tags":   ", ".join(tags),
        })
    return quotes

def get_next_url(soup):
    next_li = soup.select_one("li.next a")
    if next_li:
        return BASE_URL + next_li["href"]
    return None

def scrape_all(max_pages=10):
    all_quotes = []
    url        = BASE_URL
    page       = 1

    while url and page <= max_pages:
        print(f"  Scraping page {page}...", end=" ")
        soup = fetch_page(url)
        if not soup:
            break

        quotes = parse_quotes(soup)
        all_quotes.extend(quotes)
        print(f"{len(quotes)} quotes found.")

        url = get_next_url(soup)
        page += 1

        if url:
            time.sleep(1)   # be polite — don't hammer the server

    return all_quotes

def save_to_csv(quotes, path=OUTPUT_CSV):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "author", "tags"])
        writer.writeheader()
        writer.writerows(quotes)
    print(f"  Saved {len(quotes)} quotes to '{path}'.")

def search_by_author(quotes, author):
    return [q for q in quotes
            if author.lower() in q["author"].lower()]

def search_by_tag(quotes, tag):
    return [q for q in quotes
            if tag.lower() in q["tags"].lower()]

def print_quotes(quotes, limit=None):
    shown = quotes[:limit] if limit else quotes
    for i, q in enumerate(shown, 1):
        print(f"\n  [{i}] {q['text']}")
        print(f"       — {q['author']}")
        if q["tags"]:
            print(f"       Tags: {q['tags']}")
    print(f"\n  {len(shown)} quote(s) shown.")

def main():
    print("--- Quotes Scraper ---\n")

    while True:
        print("\n  1) Scrape quotes.toscrape.com")
        print("  2) Load from saved CSV")
        print("  q) Quit")
        choice = input("Choice: ").strip().lower()

        if choice == "1":
            try:
                pages = int(input("  How many pages? (1-10): ").strip())
                pages = max(1, min(pages, 10))
            except ValueError:
                pages = 1
            quotes = scrape_all(max_pages=pages)
            print(f"\n  Total: {len(quotes)} quotes scraped.")
            save_to_csv(quotes)

        elif choice == "2":
            if not OUTPUT_CSV.exists():
                print("  No saved CSV found — scrape first.")
                continue
            with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
                quotes = list(csv.DictReader(f))
            print(f"  Loaded {len(quotes)} quotes from CSV.")

        elif choice == "q":
            break
        else:
            continue

        while True:
            print("\n  a) Show all    s) Search by author")
            print("  t) Search by tag              b) Back")
            sub = input("  Choice: ").strip().lower()
            if sub == "a":
                print_quotes(quotes, limit=5)
            elif sub == "s":
                author  = input("  Author name: ").strip()
                results = search_by_author(quotes, author)
                print_quotes(results)
            elif sub == "t":
                tag     = input("  Tag: ").strip()
                results = search_by_tag(quotes, tag)
                print_quotes(results)
            elif sub == "b":
                break

if __name__ == "__main__":
    main()




