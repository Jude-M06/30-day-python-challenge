#---------------------------------
# you need to install flask first
# python -m pip install flask
#---------------------------------
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, request, redirect, render_template, url_for, abort

app = Flask(__name__)
DB  = Path("urls.db")

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                code       TEXT    UNIQUE NOT NULL,
                long_url   TEXT    NOT NULL,
                created_at TEXT    NOT NULL,
                clicks     INTEGER DEFAULT 0
            )
        """)

def generate_code():
    while True:
        code = secrets.token_urlsafe(4)[:6]
        with get_db() as conn:
            row = conn.execute("SELECT id FROM urls WHERE code = ?", (code,)).fetchone()
            if not row:
                return code

def insert_url(code, long_url):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with get_db() as conn:
        conn.execute("INSERT INTO urls (code, long_url, created_at) VALUES (?, ?, ?)",
                     (code, long_url, now))

def get_url(code):
    with get_db() as conn:
        return conn.execute("SELECT * FROM urls WHERE code = ?", (code,)).fetchone()

def increment_clicks(code):
    with get_db() as conn:
        conn.execute("UPDATE urls SET clicks = clicks + 1 WHERE code = ?", (code,))

def get_all_urls():
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM urls ORDER BY clicks DESC, created_at DESC"
        ).fetchall()

def validate_url(url):
    return url.startswith(("http://", "https://"))

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/shorten", methods=["POST"])
def shorten():
    long_url = request.form.get("url", "").strip()
    if not long_url:
        return render_template("index.html", error="Please enter a URL.")
    if not validate_url(long_url):
        return render_template("index.html",
                               error="URL must start with http:// or https://",
                               url=long_url)
    code      = generate_code()
    insert_url(code, long_url)
    short_url = url_for("redirect_to", code=code, _external=True)
    return render_template("index.html", short_url=short_url, long_url=long_url)

@app.route("/<code>")
def redirect_to(code):
    row = get_url(code)
    if not row:
        abort(404)
    increment_clicks(code)
    return redirect(row["long_url"], code=302)

@app.route("/stats")
def stats():
    return render_template("stats.html", urls=get_all_urls())

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Short URL not found."), 404

if __name__ == "__main__":
    init_db()
    app.run(debug=True)