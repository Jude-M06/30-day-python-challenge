import random

CHOICES = ("rock", "paper", "scissors")
BEATS   = {"rock": "scissors", "scissors": "paper", "paper": "rock"}
SHORTS  = {"r": "rock", "p": "paper", "s": "scissors"}
EMOJI   = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}

def get_player_choice():
    while True:
        raw = input("  Your move [r]ock / [p]aper / [s]cissors: ").strip().lower()
        choice = SHORTS.get(raw, raw)   # expand shorthand
        if choice in CHOICES:
            return choice
        print("  Invalid — type rock, paper, scissors (or r/p/s).")

def get_computer_choice():
    return random.choice(CHOICES)

def determine_winner(player, computer):
    if player == computer:
        return "draw"
    if BEATS[player] == computer:
        return "player"
    return "computer"

def print_scoreboard(wins, losses, draws):
    total = wins + losses + draws
    rate  = (wins / total * 100) if total else 0
    print(f"\n  Score — You: {wins}  CPU: {losses}  Draws: {draws}  "
          f"(win rate: {rate:.0f}%)")

def main():
    print("=== Rock Paper Scissors ===")
    wins = losses = draws = 0

while True:
        print()
        player   = get_player_choice()
        computer = get_computer_choice()

        print(f"\n  You: {EMOJI[player]} {player}")
        print(f"  CPU: {EMOJI[computer]} {computer}")

        result = determine_winner(player, computer)
        if result == "player":
            print("  ✅ You win!")
            wins += 1
        elif result == "computer":
            print("  ❌ Computer wins!")
            losses += 1
        else:
            print("  🤝 Draw!")
            draws += 1

        print_scoreboard(wins, losses, draws)

        again = input("\n  Play again? (y/n): ").strip().lower()
        if again != "y":
            print("\nFinal score:")
            print_scoreboard(wins, losses, draws)
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()
