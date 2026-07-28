import random

def play_game():
    secret = random.randint(1, 100)
    attempts = 0

    print("\nI'm thinking of a number between 1 and 100.")

    while True:
        try:
            guess = int(input("Your guess: "))
        except ValueError:
            print("Please enter a whole number.")
            continue

        attempts += 1

        if guess < secret:
            print("Too low!")
        elif guess > secret:
            print("Too high!")
        else:
            print(f"\nCorrect! You got it in {attempts} attempt(s).")
            break

def main():
    print("=== Number Guessing Game ===")

    while True:
        play_game()
        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()