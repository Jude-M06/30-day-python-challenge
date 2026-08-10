# 🐍 30-Day Python Challenge

A self-directed Python project challenge completed over 30 days, progressing from CLI fundamentals to deployed web apps, async networking, and live APIs. Every project was written from scratch and is contained in a single file.

**Built by Jude Morgan Jude-M06**,  CS student at the University of Liverpool, cybersecurity focus.

---

## 📌 Overview

| Stat | Value |
|---|---|
| Duration | 30 days |
| Projects | 30 |
| Languages | Python 3.13 |
| Key libraries | Flask, FastAPI, Streamlit, pandas, aiohttp, Pillow, discord.py, yfinance, BeautifulSoup |


---

## 🗂️ Projects

### Week 1 — Fundamentals (Days 1–10)
Core Python: input/output, loops, functions, file I/O, stdlib only.

| Day | Project | Key concepts |
|---|---|---|
| 01 | [Mad Libs Generator](./Day_01.py) | `input()`, f-strings |
| 02 | [Number Guessing Game](./Day_02.py) | `random`, while loops, try/except |
| 03 | [Simple Calculator](./Day_03.py) | Functions, dispatch table, error handling |
| 04 | [Temperature Converter](./Day_04.py) | Unit conversion, argparse |
| 05 | [Rock Paper Scissors](./Day_05.py) | Game loop, score tracking, dict logic |
| 06 | [Word Counter](./Day_06.py) | File I/O, `collections.Counter`, bar chart |
| 07 | [BMI Calculator](./Day_07.py) | `namedtuple`, threshold lookup, validation |
| 08 | [To-Do List CLI](./Day_08.py) | JSON persistence, CRUD, `pathlib` |
| 09 | [Password Generator](./Day_09.py) | `secrets`, character pools, strength scoring |
| 10 | [Multiplication Quiz](./Day_10.py) | `time`, scoring, difficulty levels |

### Week 2 — Intermediate (Days 11–20)
Third-party libraries, APIs, OOP, data analysis.

| Day | Project | Key concepts |
|---|---|---|
| 11 | [Contact Book](./Day_11.py) | Dict-of-dicts, JSON, fuzzy search |
| 12 | [Hangman](./Day_12.py) | Sets, ASCII art, game loop |
| 13 | [Expense Tracker](./Day_13.py) | CSV, `defaultdict`, bar charts |
| 14 | [Flashcard Quiz App](./Day_14.py) | `@dataclass`, spaced repetition, OOP |
| 15 | [Web Scraper](./Day_15.py) | `requests`, BeautifulSoup, pagination |
| 16 | [Weather CLI App](./Day_16.py) | REST APIs, geocoding, caching, argparse |
| 17 | [Text Adventure Game](./Day_17.py) | OOP, dict-based world map, save/load |
| 18 | [Markdown Note-taker](./Day_18.py) | `pathlib`, regex, front matter parsing |
| 19 | [Number Base Converter](./Day_19.py) | Recursion, `divmod()`, step-by-step output |
| 20 | [Data Visualiser](./Day_20.py) | pandas, matplotlib, CSV analysis |

### Week 3 — Advanced (Days 21–30)
Web frameworks, networking, async, deployment.

| Day | Project | Key concepts |
|---|---|---|
| 21 | [URL Shortener](./Day_21.py) | Flask, SQLite, HTTP redirects, Jinja2 |
| 22 | [Chat App](./Day_22.py) | Sockets, threading, TCP, broadcast pattern |
| 23 | [File Organiser Bot](./Day_23.py) | watchdog, `shutil`, event-driven programming |
| 24 | [REST API — Bookshelf](./Day_24.py) | FastAPI, Pydantic, CRUD, Swagger docs |
| 25 | [PDF Report Generator](./Day_25.py) | ReportLab, matplotlib, BytesIO |
| 26 | [Streamlit Dashboard](./Day_26.py) | Streamlit, Plotly, reactive UI, file upload |
| 27 | [Portfolio Tracker](./Day_27.py) | yfinance, pandas, price alerts, `schedule` |
| 28 | [Image Processing Tool](./Day_28.py) | Pillow, batch processing, watermarking |
| 29 | [Async Web Crawler](./Day_29.py) | asyncio, aiohttp, BFS, sitemap export |
| 30 | [Discord Bot](./Day_30.py) | discord.py, slash commands, tasks, deployment |

---

## 🚀 Getting Started

**Clone the repo**
```bash
git clone https://github.com/your-username/30-day-python-challenge.git
cd 30-day-python-challenge
```

**Install all dependencies**
```bash
pip install flask fastapi uvicorn streamlit pandas matplotlib plotly \
            requests beautifulsoup4 aiohttp watchdog Pillow yfinance \
            schedule reportlab discord.py python-dotenv
```

Or install per-project — each file lists its imports at the top.

**Run any project**
```bash
python Day_01.py
python Day_16.py London
python Day_24.py  # then visit http://localhost:8000/docs
```

> **Note for Day 30 (Discord bot):** requires a `.env` file with `DISCORD_TOKEN=your_token`. See [Discord Developer Portal](https://discord.com/developers/applications).

---

## 🛠️ Tech Stack

```
Language    Python 3.13
Web         Flask · FastAPI · Streamlit
Data        pandas · matplotlib · plotly
Async       asyncio · aiohttp
Networking  socket · threading
Scraping    requests · BeautifulSoup4
Images      Pillow
Finance     yfinance
Bots        discord.py
Storage     SQLite · JSON · CSV
```

---

## 📚 What I Learned

Thirty consecutive projects across a wide range of Python, some things that stand out:

- **Async programming** fundamentally changes how I/O-bound code is structured. The mental model shift from sequential to concurrent took until Day 29 to fully click.
- **Data-driven logic** (dispatch tables, threshold lists, rules dicts) consistently produces cleaner code than long if/elif chains.
- **File format choices matter** — JSON for nested/variable data, CSV for flat tables, SQLite when you need queries.
- **Error handling at the boundary** — validate input and handle network/file errors at the edges of the system; keep core logic pure and simple.

---

## 📬 Contact

**Jude Morgan** — CS Student, University of Liverpool
[GitHub](https://github.com/Jude-M06) · [LinkedIn](www.linkedin.com/in/jude-morgan)
