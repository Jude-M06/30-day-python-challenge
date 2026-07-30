#---------------------------------------------------
# you need to install aiohttp beautifulsoup4 first
# python -m pip install aiohttp beautifulsoup4
#---------------------------------------------------

import argparse
import asyncio
import json
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

import aiohttp
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "PythonCrawler/1.0 (educational; +https://github.com)"
}



def normalise(url: str, base: str) -> str:
    url, _ = urldefrag(url)              
    url     = urljoin(base, url)         
    return url.rstrip("/")

def same_domain(url: str, base: str) -> bool:
    return urlparse(url).netloc == urlparse(base).netloc

def is_crawlable(url: str) -> bool:
    skip_exts = {".pdf", ".jpg", ".jpeg", ".png", ".gif",
                 ".svg", ".zip", ".mp4", ".mp3", ".css", ".js"}
    return not any(url.lower().endswith(e) for e in skip_exts)



async def fetch_page(session: aiohttp.ClientSession,
                     url: str,
                     semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:
        t0 = time.time()
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10),
                                   headers=HEADERS, ssl=False) as resp:
                elapsed = round(time.time() - t0, 2)
                if resp.content_type and "html" not in resp.content_type:
                    return {"url": url, "status": resp.status,
                            "html": None, "elapsed": elapsed}
                html = await resp.text(errors="replace")
                return {"url": url, "status": resp.status,
                        "html": html, "elapsed": elapsed}
        except asyncio.TimeoutError:
            return {"url": url, "status": "timeout", "html": None, "elapsed": 10}
        except Exception as e:
            return {"url": url, "status": f"error: {e}", "html": None, "elapsed": 0}

def extract_links(html: str, base_url: str) -> list[str]:
    soup  = BeautifulSoup(html, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        norm = normalise(href, base_url)
        if same_domain(norm, base_url) and is_crawlable(norm):
            links.add(norm)
    return list(links)

def extract_title(html: str) -> str:
    soup  = BeautifulSoup(html, "html.parser")
    title = soup.find("title")
    return title.get_text(strip=True) if title else ""



async def crawl(seed_url: str, max_pages: int = 50,
                concurrency: int = 10, delay: float = 0.5) -> dict:
    seed_url  = normalise(seed_url, seed_url)
    visited   = set()
    queue     = deque([seed_url])
    sitemap   = {}
    semaphore = asyncio.Semaphore(concurrency)
    start     = time.time()

    print(f"\n  Crawling: {seed_url}")
    print(f"  Max pages: {max_pages}  Concurrency: {concurrency}\n")

    connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        while queue and len(visited) < max_pages:
            
            batch = []
            while queue and len(batch) < concurrency:
                url = queue.popleft()
                if url not in visited:
                    visited.add(url)
                    batch.append(url)

            if not batch:
                break

            
            tasks   = [fetch_page(session, url, semaphore) for url in batch]
            results = await asyncio.gather(*tasks)

            for r in results:
                url     = r["url"]
                status  = r["status"]
                elapsed = r["elapsed"]
                icon    = "✔" if status == 200 else "✖"
                print(f"  {icon} [{len(sitemap)+1:>3}] {status}  "
                      f"{elapsed:.2f}s  {url}")

                title   = ""
                links   = []
                if r["html"]:
                    title = extract_title(r["html"])
                    links = extract_links(r["html"], url)
                    for link in links:
                        if link not in visited and link not in [u for u in queue]:
                            queue.append(link)

                sitemap[url] = {
                    "status":   status,
                    "title":    title,
                    "links":    links,
                    "elapsed":  elapsed,
                    "crawled_at": datetime.now().isoformat(),
                }

            
            if delay and queue:
                await asyncio.sleep(delay)

    elapsed_total = round(time.time() - start, 1)
    print(f"\n  Crawled {len(sitemap)} page(s) in {elapsed_total}s")
    return sitemap



def export_sitemap(sitemap: dict, base_path: str = "sitemap"):
    
    json_path = Path(base_path + ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sitemap, f, indent=2)
    print(f"  JSON sitemap → {json_path}")


    txt_path = Path(base_path + ".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        for url, data in sitemap.items():
            if data["status"] == 200:
                f.write(url + "\n")
    print(f"  URL list    → {txt_path}")

def print_report(sitemap: dict):
    pages      = list(sitemap.values())
    ok         = [p for p in pages if p["status"] == 200]
    broken     = [p for p in pages if isinstance(p["status"], int)
                  and p["status"] >= 400]
    errors     = [p for p in pages if isinstance(p["status"], str)]
    avg_time   = sum(p["elapsed"] for p in ok) / len(ok) if ok else 0
    all_links  = {l for p in pages for l in p.get("links", [])}
    external   = {l for l in all_links
                  if sitemap and not same_domain(l, list(sitemap.keys())[0])}

    print("\n" + "=" * 50)
    print("  CRAWL REPORT")
    print("=" * 50)
    print(f"  Pages crawled  : {len(pages)}")
    print(f"  OK (200)       : {len(ok)}")
    print(f"  Broken (4xx)   : {len(broken)}")
    print(f"  Errors/timeouts: {len(errors)}")
    print(f"  Unique links   : {len(all_links)}")
    print(f"  Avg response   : {avg_time:.2f}s")

    if broken:
        print(f"\n  Broken links:")
        for p in broken[:10]:
            print(f"    {p['status']}  {list(sitemap.keys())[0]}")

    print("=" * 50)


def build_parser():
    p = argparse.ArgumentParser(description="Async web crawler / sitemapper.")
    p.add_argument("url",           help="Seed URL to start crawling")
    p.add_argument("--max",         type=int, default=50,
                   help="Max pages to crawl (default: 50)")
    p.add_argument("--concurrency", type=int, default=10,
                   help="Simultaneous requests (default: 10)")
    p.add_argument("--delay",       type=float, default=0.5,
                   help="Delay between batches in seconds (default: 0.5)")
    p.add_argument("--output",      default="sitemap",
                   help="Output filename base (default: sitemap)")
    return p

def main():
    parser = build_parser()
    args   = parser.parse_args()

    sitemap = asyncio.run(crawl(
        seed_url    = args.url,
        max_pages   = args.max,
        concurrency = args.concurrency,
        delay       = args.delay,
    ))

    print_report(sitemap)
    export_sitemap(sitemap, args.output)

if __name__ == "__main__":
    main()