import argparse

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

BASE_NAMES = {2: "Binary", 8: "Octal", 10: "Decimal", 16: "Hex"}

def validate_number(number_str, base):
    valid = DIGITS[:base]
    for ch in number_str.upper():
        if ch not in valid:
            raise ValueError(
                f"'{ch}' is not a valid digit in base {base}. "
                f"Valid digits: {valid}"
            )
        
def to_decimal(number_str, from_base):
    validate_number(number_str, from_base)
    return int(number_str, from_base)

def from_decimal_iterative(n, to_base):
    if n == 0:
        return "0"
    digits = []
    while n > 0:
        n, remainder = divmod(n, to_base)
        digits.append(DIGITS[remainder])
    return "".join(reversed(digits))

def from_decimal_recursive(n, to_base):
    if n < to_base:
        return DIGITS[n]
    return from_decimal_recursive(n // to_base, to_base) + DIGITS[n % to_base]

def convert(number_str, from_base, to_base):
    decimal = to_decimal(number_str, from_base)
    result  = from_decimal_iterative(decimal, to_base)
    return decimal, result

def show_working(n, to_base):
    if n == 0:
        print("  0 → 0")
        return

    steps    = []
    original = n
    while n > 0:
        n, rem = divmod(n, to_base)
        steps.append((n, rem, DIGITS[rem]))

    base_name = BASE_NAMES.get(to_base, f"base {to_base}")
    print(f"\n  Converting {original}₁₀ → {base_name} (base {to_base})")
    print(f"  {'Division':<20} {'Quotient':<12} {'Remainder':<12} Digit")
    print("  " + "-" * 52)

    for i, (quot, rem, digit) in enumerate(steps):
        dividend = original if i == 0 else steps[i-1][0]
        print(f"  {dividend} ÷ {to_base:<16} {quot:<12} {rem:<12} {digit}")

    remainders = [s[2] for s in reversed(steps)]
    result = "".join(remainders)
    print(f"\n  Read remainders bottom → top: {' '.join(remainders)}")
    print(f"  Result: {result}")

def convert_all(number_str, from_base):
    decimal = to_decimal(number_str, from_base)
    base_name = BASE_NAMES.get(from_base, f"base {from_base}")

    print(f"\n  {number_str.upper()} ({base_name}) = {decimal}₁₀\n")
    print(f"  {'Base':<14} {'Prefix':<8} Result")
    print("  " + "-" * 36)

    targets = [(2, "0b"), (8, "0o"), (10, ""), (16, "0x")]
    for base, prefix in targets:
        result  = from_decimal_iterative(decimal, base)
        marker  = BASE_NAMES.get(base, f"base {base}")
        active  = " ←" if base == from_base else ""
        print(f"  {marker:<14} {prefix:<8} {result}{active}")

   
    print(f"\n  Verified: bin={bin(decimal)}, oct={oct(decimal)}, hex={hex(decimal)}")

def get_base(prompt, label="base"):
    while True:
        try:
            b = int(input(prompt))
            if 2 <= b <= 36:
                return b
            print(f"  {label} must be between 2 and 36.")
        except ValueError:
            print("  Please enter a whole number.")

def get_number(prompt, base):
    while True:
        raw = input(prompt).strip().upper()
        try:
            validate_number(raw, base)
            return raw
        except ValueError as e:
            print(f"  {e}")

def interactive_menu():
    print("--- Number Base Converter ---\n")
    while True:
        print("  1) Convert between two bases")
        print("  2) Show all bases at once")
        print("  3) Step-by-step working")
        print("  q) Quit")
        choice = input("Choice: ").strip().lower()

        if choice == "1":
            from_base = get_base("  From base: ")
            number    = get_number(f"  Number (base {from_base}): ", from_base)
            to_base   = get_base("  To base  : ")
            try:
                decimal, result = convert(number, from_base, to_base)
                fname = BASE_NAMES.get(from_base, f"base {from_base}")
                tname = BASE_NAMES.get(to_base, f"base {to_base}")
                print(f"\n  {number.upper()} ({fname}) = {result} ({tname})")
                print(f"  (via decimal: {decimal})")
            except ValueError as e:
                print(f"  Error: {e}")
        
        elif choice == "2":
            from_base = get_base("  From base: ")
            number    = get_number(f"  Number (base {from_base}): ", from_base)
            try:
                convert_all(number, from_base)
            except ValueError as e:
                print(f"  Error: {e}")

        elif choice == "3":
            print("  Enter a decimal number to see step-by-step conversion.")
            try:
                n       = int(input("  Decimal number: ").strip())
                to_base = get_base("  Convert to base: ")
                show_working(n, to_base)
            except ValueError:
                print("  Please enter a whole number.")

        elif choice == "q":
            print("  Goodbye!")
            break
        else:
            print("  Invalid choice — try again.")

def build_parser():
    parser = argparse.ArgumentParser(description="Number base converter")
    parser.add_argument("number", help="Number to convert")
    parser.add_argument("--from", dest="from_base", type=int, default=10,
                        help="Source base (default: 10)")
    parser.add_argument("--to", dest="to_base", type=int, default=None,
                        help="Target base (omit to show all bases)")
    parser.add_argument("--show-working", action="store_true",
                        help="Show step-by-step division")
    return parser

def main():
    parser = build_parser()

    # if no CLI args, drop into interactive menu
    if len(__import__("sys").argv) == 1:
        interactive_menu()
        return

    args = parser.parse_args()
    try:
        if args.to_base is None:
            convert_all(args.number, args.from_base)
        else:
            decimal, result = convert(args.number, args.from_base, args.to_base)
            print(f"  {args.number.upper()} (base {args.from_base}) "
                  f"= {result} (base {args.to_base})")
            if args.show_working:
                show_working(decimal, args.to_base)
    except ValueError as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    main()
