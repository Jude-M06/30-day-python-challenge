import time
import random

DIFFICULTIES = {
    "1": ("Easy", 5),
    "2": ("Medium", 10),
    "3": ("Hard", 12),
}

def generate_question(max_factor):
    a = random.randint(1, max_factor)
    b = random.randint(1, max_factor)
    return a, b, a * b

def ask_question(number, total, a, b, correct):
    start = time.time()
    try:
        raw = input(f"\n Q{number}/{total}: {a} x {b} = ?  ")
        elapsed = time.time() - start
        guess = int(raw.strip())
    except ValueError:
        elapsed = time.time() - start
        print("  not a number, counted as wrong")
        return False, elapsed, None
    
    if guess == correct:
        print(f" Correct! ({elapsed:.2f}s)")
        return True, elapsed, guess
    else:
        print(f"  x  Wrong — the answer was {correct}. ({elapsed:.2f}s)")
        return False, elapsed, guess

def run_quiz(num_questions, max_factor):
    log = []
    quiz_start = time.time()

    for i in range(1, num_questions + 1):
        a, b, correct = generate_question(max_factor)
        is_correct, elapsed, guess = ask_question(i, num_questions, a, b, correct)

        log.append({
            "question": f"{a} × {b}",
            "correct":  correct,
            "guess":    guess,
            "right":    is_correct,
            "time":     round(elapsed, 2),
        })

    log.append({"_total_time": round(time.time() - quiz_start, 2)})
    return log

def print_summary(log):
    results     = [r for r in log if "question" in r]
    total_time  = log[-1].get("_total_time", 0)
    correct     = sum(1 for r in results if r["right"])
    total       = len(results)
    accuracy    = correct / total * 100 if total else 0
    avg_time    = sum(r["time"] for r in results) / total if total else 0

    print("\n" + "-" * 40)
    print("           QUIZ SUMMARY")
    print("-" * 40)
    print(f"  Score        : {correct}/{total}")
    print(f"  Accuracy     : {accuracy:.0f}%")
    print(f"  Total time   : {total_time:.1f}s")
    print(f"  Avg per Q    : {avg_time:.2f}s")

    wrong = [r for r in results if not r["right"]]
    if wrong:
        print(f"\n  ✖ Missed ({len(wrong)}):")
        for r in wrong:
            guess_str = str(r["guess"]) if r["guess"] is not None else "?"
            print(f"    {r['question']} = {r['correct']}  "
                  f"(you said {guess_str})")
    else:
        print("\n  🎉 Perfect score!")

    
    if accuracy == 100:  grade = "S"
    elif accuracy >= 80: grade = "A"
    elif accuracy >= 60: grade = "B"
    elif accuracy >= 40: grade = "C"
    else:                grade = "D"
    print(f"\n  Grade: {grade}")
    print("-" * 40)



def choose_difficulty():
    print("\n  Difficulty:")
    for key, (name, factor) in DIFFICULTIES.items():
        print(f"    {key}) {name}  (1–{factor})")
    while True:
        choice = input("  Choose (1/2/3): ").strip()
        if choice in DIFFICULTIES:
            return DIFFICULTIES[choice]
        print("  Please enter 1, 2, or 3.")

def get_question_count():
    while True:
        try:
            n = int(input("  Number of questions (5–30): ").strip())
            if 5 <= n <= 30:
                return n
            print("  Please enter a number between 5 and 30.")
        except ValueError:
            print("  Please enter a whole number.")



def main():
    print("--- Multiplication Quiz ---")

    while True:
        diff_name, max_factor = choose_difficulty()
        num_questions         = get_question_count()

        print(f"\n  Starting {diff_name} quiz — {num_questions} questions. Good luck!\n")
        log = run_quiz(num_questions, max_factor)
        print_summary(log)

        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("Great work — keep practising!")
            break

if __name__ == "__main__":
    main()