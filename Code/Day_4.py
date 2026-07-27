# --- conversion functions ---

def c_to_f(c): return c * 9/5 + 32
def c_to_k(c): return c + 273.15
def f_to_c(f): return (f - 32) * 5/9
def f_to_k(f): return (f - 32) * 5/9 + 273.15

def k_to_c(k):
    if k < 0:
        raise ValueError("Kelvin cannot be negative.")
    return k - 273.15

def k_to_f(k):
    if k < 0:
        raise ValueError("Kelvin cannot be negative.")
    return (k - 273.15) * 9/5 + 32

# --- dispatch table ---

CONVERSIONS = {
    "1": ("Celsius    → Fahrenheit", "°C", "°F", c_to_f),
    "2": ("Celsius    → Kelvin",     "°C", "K",  c_to_k),
    "3": ("Fahrenheit → Celsius",    "°F", "°C", f_to_c),
    "4": ("Fahrenheit → Kelvin",     "°F", "K",  f_to_k),
    "5": ("Kelvin     → Celsius",    "K",  "°C", k_to_c),
    "6": ("Kelvin     → Fahrenheit", "K",  "°F", k_to_f),
}

# --- helpers ---

def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  Please enter a valid number.")

def show_menu():
    print("\n--- Temperature Converter ---")
    for key, (label, *_) in CONVERSIONS.items():
        print(f"  {key}) {label}")
    print("  q) Quit")

# --- main ---

def main():
    print("=== Temperature Converter ===")
    while True:
        show_menu()
        choice = input("Choose a conversion: ").strip().lower()

        if choice == "q":
            print("Goodbye!")
            break

        if choice not in CONVERSIONS:
            print("  Invalid choice — try again.")
            continue

        label, from_unit, to_unit, fn = CONVERSIONS[choice]
        value = get_number(f"  Enter temperature ({from_unit}): ")

        try:
            result = fn(value)
            print(f"  {value:g}{from_unit} = {result:.2f}{to_unit}")
        except ValueError as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    main()