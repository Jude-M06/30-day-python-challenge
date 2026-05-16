import string
import sys
from collections import Counter

# --- text loading ---

def load_text(source):
    try:
        with open(source, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"File '{source}' not found.")
        sys.exit(1)
    except OSError:
        # not a path — treat source as raw text
        return source
    
# --- cleaning ---

def clean_words(text):
    tokens = text.lower().split()
    words  = [t.strip(string.punctuation) for t in tokens]
    return [w for w in words if w]   # drop empty strings

# --- analysis ---

def analyse(text, words):
    return {
        "word_count":     len(words),
        "unique_words":   len(set(words)),
        "char_count":     len(text),
        "char_no_spaces": len(text.replace(" ", "")),
        "sentence_count": text.count(".") + text.count("!") + text.count("?"),
        "freq":           Counter(words),
    }

# --- report ---

def print_report(stats, top_n=5):
    print("\n" + "=" * 36)
    print("         WORD COUNTER REPORT")
    print("=" * 36)
    print(f"  Words          : {stats['word_count']:>8,}")
    print(f"  Unique words   : {stats['unique_words']:>8,}")
    print(f"  Characters     : {stats['char_count']:>8,}")
    print(f"  Chars (no spc) : {stats['char_no_spaces']:>8,}")
    print(f"  Sentences ~    : {stats['sentence_count']:>8,}")

    print(f"\n  Top {top_n} words:")
    top   = stats["freq"].most_common(top_n)
    max_c = top[0][1] if top else 1
    bar_w = 20
    for word, count in top:
        bar = "█" * int(count / max_c * bar_w)
        print(f"  {word:<15} {count:>4}  {bar}")
    print("=" * 36)

# --- main ---

def main():
    if len(sys.argv) > 1:
        text = load_text(sys.argv[1])
    else:
        print("=== Word Counter ===")
        print("Paste your text below (press Enter twice when done):\n")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        text = "\n".join(lines)

    words = clean_words(text)
    stats = analyse(text, words)
    print_report(stats, top_n=5)

if __name__ == "__main__":
    main()