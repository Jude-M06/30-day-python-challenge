import secrets
import string

def build_pool(uppercase=True, lowercase=True, digits=True, symbols=True):
    pool = ""
    if uppercase: pool += string.ascii_uppercase
    if lowercase: pool += string.ascii_lowercase
    if digits: pool += string.digits
    if symbols: pool += string.punctuation
    if not pool:
        raise ValueError("At least one character type must be selected ")
    return pool

def generate_password(length, uppercase=True,lowercase=True, digits=True, symbols=True):
    if length < 4 :
        raise ValueError("Password length must be at least 4")
    
    pool = build_pool(uppercase,lowercase, digits, symbols)

    guarantee = []
    if uppercase: guarantee.append(secrets.choice(string.ascii_uppercase))
    if lowercase: guarantee.append(secrets.choice(string.ascii_lowercase))
    if digits: guarantee.append(secrets.choice(string.digits))
    if symbols: guarantee.append(secrets.choice(string.punctuation))

    remaining = [secrets.choice(pool) for _ in range(length- len(guarantee))]
    
    password_list = guarantee + remaining   
    secrets.SystemRandom().shuffle(password_list)
    return "".join(password_list)

def strength_score(password):
    score = 0
    if len(password) >= 12:                              score += 1
    if len(password) >= 16:                              score += 1
    if any(c in string.ascii_uppercase for c in password): score += 1
    if any(c in string.digits          for c in password): score += 1
    if any(c in string.punctuation     for c in password): score += 1

    labels = [
        (1, "Weak",        "🔴"),
        (2, "Fair",        "🟠"),
        (3, "Good",        "🟡"),
        (4, "Strong",      "🟢"),
        (5, "Very strong", "🟢"),
    ]
    for threshold, label, emoji in labels:
        if score <= threshold:
            return label, emoji
    return "Very strong", "🟢"

def ask_yes_no(prompt, default=True):
    hint ="(Y/n)" if default else "(y/N)"
    raw = input(prompt + hint + ": ").strip().lower()
    if raw == "":
        return default
    return raw.startswith("y")

def get_int(prompt, min_val=1, max_val=999):
    while True:
        try:
            val = int(input(prompt))
            if min_val <= val <= max_val:
                return val
            print(f"Pease enter a number between {min_val} and {max_val}")
        except ValueError:
            print("Please enter a whole number")

def main():
    print("--- Password Generator ---\n")

    while True:
        print("Configure your password: ")
        length = get_int("Length (4-128): ", 4, 128)
        uppercase = ask_yes_no("include uppercase (A-Z)")
        lowercase = ask_yes_no("include lowercase (a-z)")
        digits = ask_yes_no("Include digits (0-9)")
        symbols = ask_yes_no("include symbols (!@#...)")
        count = get_int("How many passwords to generate (1-20): ", 1, 20)

        print()
        try:
            for i in range(count):
                pwd = generate_password(length, uppercase, lowercase, digits, symbols)
                label, emoji = strength_score(pwd)
                print(f" {i+1: >2}. {pwd} {emoji} {label}")
        except ValueError as e:
            print(f"Error: {e}")

            print()
            again = input("Generate another batch? (y/n): ").strip().lower()
            if again != "y":
                print("Stay secure!")
                break

if __name__ == "__main__":
    main()



