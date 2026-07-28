def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("invalid, please enter a number")

def show_menu():
    print("\n-- Calculator --")
    print("  1) Add       (+)")
    print("  2) Subtract  (-)")
    print("  3) Multiply  (*)")
    print("  4) Divide    (/)")
    print("  q) Quit")

OPERATIONS = {
    "1": ("+", add),
    "2": ("-", subtract),
    "3": ("*", multiply),
    "4": ("/", divide),
}

def main():
    print("== Simple Calculator ==")
    while True:
        show_menu()
        choice = input("Choose an operation: ").strip().lower()

        if choice == "q":
            print("Goodbye!")
            break

        if choice not in OPERATIONS:
            print("  Invalid choice — try again.")
            continue

        symbol, operation = OPERATIONS[choice]
        a = get_number("  First number : ")
        b = get_number("  Second number: ")

        try:
            result = operation(a, b)
            print(f"  {a} {symbol} {b} = {result:g}")
        except ValueError as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    main()
