import csv
import json
import random
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

CARDS_FILE = Path("cards.csv")
PROGRESS_FILE = Path("progress.json")
REVIEW_INTERVALS = [1, 3, 7, 14]

@dataclass
class Card:
    question: str
    answer: str
    deck: str = "default"
    correct: int = 0
    incorrect: int = 0
    next_review: str = ""

    @property
    def due(self):
        if not self.next_review:
            return True
        return datetime.now().date() >= \
               datetime.fromisoformat(self.next_review).date()
    
    @property
    def accuracy(self):
        total = self.correct + self.incorrect
        return self.correct / total * 100 if total else 0.0
    
def load_cards(path=CARDS_FILE):
    cards = []
    if not path.exists():
        print(f"  No cards file found at '{path}'. Create cards.csv first.")
        return cards
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cards.append(Card(
                question=row["question"],
                answer=row["answer"],
                deck=row.get("deck", "default"),
            ))
    return cards

def load_progress(cards, path=PROGRESS_FILE):
    if not path.exists():
        with open(path, "r", encoding="utf-8") as f:
         data = json.load(f)
    for card in cards:
        if card.question in data:
            p = data[card.question]
            card.correct     = p.get("correct", 0)
            card.incorrect   = p.get("incorrect", 0)
            card.next_review = p.get("next_review", "")

def save_progress(cards, path=PROGRESS_FILE):
    data = {
        c.question: {
            "correct":     c.correct,
            "incorrect":   c.incorrect,
            "next_review": c.next_review,
        }
                for c in cards
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def next_review_date(streak):
    idx  = min(streak - 1, len(REVIEW_INTERVALS) - 1)
    days = REVIEW_INTERVALS[max(idx, 0)]
    return (datetime.now().date() + timedelta(days=days)).isoformat()

def quiz_session(cards):
    due = [c for c in cards if c.due]
    if not due:
        print("\n  🎉 No cards due today — come back tomorrow!")
        return 0, 0
    
    random.shuffle(due)
    correct_count = 0

    print(f"\n  {len(due)} card(s) due. Press Enter to reveal the answer.\n")

    for i, card in enumerate(due, 1):
        print(f"  [{i}/{len(due)}]  Deck: {card.deck}")
        print(f"  Q: {card.question}")
        input("  (press Enter to reveal) ")
        print(f"  A: {card.answer}\n")

        while True:
            rating = input("  Did you get it? (y/n): ").strip().lower()
            if rating in ("y", "n"):
                break
            print("  Please enter y or n.")

        if rating == "y":
            card.correct += 1
            card.next_review = next_review_date(card.correct)
            correct_count += 1
            print(f"  ✅ Nice! Next review: {card.next_review}\n")
        else:
            card.incorrect += 1
            card.next_review = (
                datetime.now().date() + timedelta(days=1)
            ).isoformat()
            print(f"  ❌ Review again tomorrow.\n")

    return correct_count, len(due)

def print_stats(cards):
    if not cards:
        print("  No cards loaded.")
        return

    due_count = sum(1 for c in cards if c.due)
    decks     = sorted(set(c.deck for c in cards))

    print("\n" + "-" * 42)
    print("           FLASHCARD STATS")
    print("-" * 42)
    print(f"  Total cards : {len(cards)}")
    print(f"  Due today   : {due_count}")

    print("\n  By deck:")
    for deck in decks:
        deck_cards = [c for c in cards if c.deck == deck]
        deck_due   = sum(1 for c in deck_cards if c.due)
        avg_acc    = (sum(c.accuracy for c in deck_cards) /
                      len(deck_cards))
        print(f"  {deck:<18} {len(deck_cards):>3} cards  "
              f"{deck_due:>2} due  {avg_acc:.0f}% avg accuracy")
        
    print("\n  Weakest cards (most incorrect):")
    weak = sorted(cards, key=lambda c: c.incorrect, reverse=True)[:5]
    for c in weak:
        if c.incorrect > 0:
            print(f"  {c.question[:40]:<42} "
                  f"❌ {c.incorrect}  ✅ {c.correct}")
    print("-" * 42)

def add_card(cards):
    print("\n  --- Add Card ---")
    question = input("  Question: ").strip()
    answer   = input("  Answer  : ").strip()
    deck     = input("  Deck [default]: ").strip() or "default"
    if not question or not answer:
        print("  Question and answer are required.")
        return
    
    file_exists = CARDS_FILE.exists()
    with open(CARDS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "answer", "deck"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({"question": question, "answer": answer, "deck": deck})

    cards.append(Card(question=question, answer=answer, deck=deck))
    print(f"  ✅ Card added to deck '{deck}'.")

def main():
    print("--- Flashcard Quiz App ---")
    cards = load_cards()
    load_progress(cards)

    while True:
        due = sum(1 for c in cards if c.due)
        print(f"\n  {due} card(s) due today.")
        print("  s) Start session")
        print("  t) Stats")
        print("  a) Add card")
        print("  q) Quit")

        choice = input("Choice: ").strip().lower()

        if choice == "s":
            correct, total = quiz_session(cards)
            if total:
                print(f"\n  Session complete — {correct}/{total} correct "
                      f"({correct/total*100:.0f}%)")
            save_progress(cards)

        elif choice == "t":
            print_stats(cards)

        elif choice == "a":
            add_card(cards)

        elif choice == "q":
            save_progress(cards)
            print("Progress saved. Keep studying!")
            break

        else:
            print("  Invalid choice — try again.")

if __name__ == "__main__":
    main()




