import random
from pathlib import Path

HANGMAN_STAGES = [
   
    """
   -----
   |   |
   |
   |
   |
   |
==========""",

    """
   -----
   |   |
   |   O
   |
   |
   |
==========""",

    """
   -----
   |   |
   |   O
   |   |
   |
   |
==========""",

    """
   -----
   |   |
   |   O
   |  /|
   |
   |
==========""",

    """
   -----
   |   |
   |   O
   |  /|\
   |
   |
==========""",

    """
   -----
   |   |
   |   O
   |  /|\
   |  /
   |
==========""",

    """
   -----
   |   |
   |   O
   |  /|\
   |  / \
   |
==========""",
]

MAX_WRONG = len(HANGMAN_STAGES) - 1   

def load_words (path="words.txt"):
    p=Path(path)
    if not p.exists():
        return ["python", "hangman", "computer", "keyboard",
                "function", "variable", "algorithm", "database"]
    with open(p, "r", encoding="utf-8") as f:
        words = [line.strip().lower() for line in f if line.strip()]
    return words or ["python", "hangman"]

def get_display(word, guessed):
    return " ".join(c if c in guessed else "_" for c in word)

def print_state(word, guessed, wrong_count):
    print(HANGMAN_STAGES[wrong_count])
    print(f"  Word:    {get_display(word, guessed)}")
    wrong_letters = sorted(c for c in guessed if c not in word)
    if wrong_letters:
        print(f"  Wrong:   {' '.join(wrong_letters)}")
    print(f"  Lives:   {MAX_WRONG - wrong_count} remaining")

def get_guess(guessed):
    while True:
        raw = input("\n Guess a letter: ").strip().lower()
        if len(raw) != 1 or not raw.isalpha():
            print("please enter a single letter")
        elif raw in guessed:
            print(f" you already guessed '{raw} - try another")
        else:
            return raw
        
def play_game(word):
    guessed = set()
    wrong_count = 0

    print(f"\n New game, the word has {len(word)} letters")

    while True:
        print_state(word, guessed, wrong_count)

        if all(c in guessed for c in word):
            print(f"\n you won, the word was '{word}")
            return True
        
        if wrong_count == MAX_WRONG:
            print(f"\n game over, the word was '{word}' ")
            return False
        
        letter = get_guess(guessed)
        guessed.add(letter)

        if letter in word:
            print(f" '{letter}' is in the word")
        else:
            wrong_count += 1
            print(f" '{letter}' is not in the word")

def main():
    print("=== Hangman ===")
    words  = load_words()
    wins   = 0
    losses = 0

    while True:
        word   = random.choice(words)
        result = play_game(word)
        if result:
            wins += 1
        else:
            losses += 1

        print(f"\n  Record — Wins: {wins}  Losses: {losses}")
        again = input("  Play again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()


