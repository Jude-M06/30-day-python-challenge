import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

NOTES_DIR = Path("notes")

def slugify(title):
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)   # remove punctuation
    slug = re.sub(r"[\s_]+", "-", slug)     # spaces → hyphens
    slug = re.sub(r"-+", "-", slug)         # collapse multiple hyphens
    return slug.strip("-")

def build_front_matter(title, tags):
    now      = datetime.now().strftime("%Y-%m-%d %H:%M")
    tag_str  = ", ".join(t.strip() for t in tags) if tags else ""
    return f"---\ntitle: {title}\ndate: {now}\ntags: {tag_str}\n---\n\n"

def get_note_path(title):
    date = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(title)
    return NOTES_DIR / f"{date}_{slug}.md"

def parse_note(path):
    text = path.read_text(encoding="utf-8")

    front  = re.search(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    meta   = {}
    body   = text

    if front:
        raw  = front.group(1)
        body = text[front.end():]
        for line in raw.splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                meta[key.strip()] = val.strip()

    return {
        "title": meta.get("title", path.stem),
        "date":  meta.get("date", ""),
        "tags":  [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
        "body":  body.strip(),
        "path":  path,
    }

def load_all_notes():
    NOTES_DIR.mkdir(exist_ok=True)
    notes = [parse_note(p) for p in sorted(NOTES_DIR.glob("*.md"), reverse=True)]
    return notes

def create_note(title=None, tags_raw=None):
    NOTES_DIR.mkdir(exist_ok=True)

    if not title:
        title = input("  Title: ").strip()
    if not title:
        print("  Title can't be empty.")
        return

    if tags_raw is None:
        tags_raw = input("  Tags (comma-separated, optional): ").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    print("  Write your note below. Enter a blank line when done.\n")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    body = "\n".join(lines).strip()

    content  = build_front_matter(title, tags) + body
    out_path = get_note_path(title)

    counter = 1
    while out_path.exists():
        out_path = NOTES_DIR / f"{out_path.stem}-{counter}.md"
        counter += 1

    out_path.write_text(content, encoding="utf-8")
    print(f"\n  Note saved: {out_path.name}")

def view_note(note):
    print("\n" + "=" * 50)
    print(f"  {note['title']}")
    print(f"  {note['date']}  |  tags: {', '.join(note['tags']) or 'none'}")
    print("-" * 50)
    print(note["body"])
    print("-" * 50)

def delete_note(note):
    confirm = input(f"  Delete '{note['title']}'? (y/n): ").strip().lower()
    if confirm == "y":
        note["path"].unlink()
        print("  Deleted.")

def list_notes(notes=None):
    if notes is None:
        notes = load_all_notes()
    if not notes:
        print("  No notes yet — create one with 'n'.")
        return notes
    print(f"\n  {'#':<4} {'Title':<30} {'Date':<18} Tags")
    print("  " + "-" * 64)
    for i, n in enumerate(notes, 1):
        tags = ", ".join(n["tags"]) or "—"
        print(f"  {i:<4} {n['title']:<30} {n['date'][:10]:<18} {tags}")
    print(f"\n  {len(notes)} note(s).")
    return notes

def search_notes(query, notes=None):
    if notes is None:
        notes = load_all_notes()
    q = query.lower()
    results = [
        n for n in notes
        if q in n["title"].lower()
        or q in n["body"].lower()
        or any(q in t.lower() for t in n["tags"])
    ]
    print(f"\n  {len(results)} result(s) for '{query}':")
    return list_notes(results)

def filter_by_tag(tag, notes=None):
    if notes is None:
        notes = load_all_notes()
    results = [n for n in notes if tag.lower() in [t.lower() for t in n["tags"]]]
    print(f"\n  Notes tagged '{tag}':")
    return list_notes(results)

def pick_note(notes):
    if not notes:
        return None
    while True:
        try:
            idx = int(input("  Enter note number (0 to cancel): "))
            if idx == 0:
                return None
            if 1 <= idx <= len(notes):
                return notes[idx - 1]
            print(f"  Enter a number between 1 and {len(notes)}.")
        except ValueError:
            print("  Please enter a number.")

def interactive_menu():
    print("--- Markdown Note-taker ---")
    while True:
        print("\n  n) New note      l) List all")
        print("  s) Search        t) Filter by tag")
        print("  v) View note     d) Delete note")
        print("  q) Quit")
        choice = input("Choice: ").strip().lower()

        if choice == "n":
            create_note()
        elif choice == "l":
            list_notes()
        elif choice == "s":
            query = input("  Search: ").strip()
            if query:
                search_notes(query)
        elif choice == "t":
            tag = input("  Tag: ").strip()
            if tag:
                filter_by_tag(tag)
        elif choice == "v":
            notes = list_notes()
            note  = pick_note(notes)
            if note:
                                view_note(note)
        elif choice == "d":
            notes = list_notes()
            note  = pick_note(notes)
            if note:
                delete_note(note)
        elif choice == "q":
            print("  Goodbye!")
            break
        else:
            print("  Invalid choice — try again.")

def build_parser():
    parser = argparse.ArgumentParser(description="Markdown note-taker")
    sub    = parser.add_subparsers(dest="cmd")

    new_p = sub.add_parser("new", help="Create a new note")
    new_p.add_argument("title", nargs="?", help="Note title")
    new_p.add_argument("--tags", default="", help="Comma-separated tags")

    sub.add_parser("list", help="List all notes")

    search_p = sub.add_parser("search", help="Search notes")
    search_p.add_argument("query")

    tag_p = sub.add_parser("tag", help="Filter by tag")
    tag_p.add_argument("tag")

    return parser

def main():
    parser = build_parser()
    args   = parser.parse_args()

    if args.cmd == "new":
        create_note(title=args.title, tags_raw=args.tags)
    elif args.cmd == "list":
        list_notes()
    elif args.cmd == "search":
        search_notes(args.query)
    elif args.cmd == "tag":
        filter_by_tag(args.tag)
    else:
        interactive_menu()

if __name__ == "__main__":
    main()

