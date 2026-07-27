from collections import namedtuple

Category = namedtuple("Category", ["label", "emoji"])

BMI_Categories = [
    (18.5, Category("Underweight",      "🔵")),
    (25.0, Category("Normal weight",    "🟢")),
    (30.0, Category("Overweight",       "🟡")),
    (35.0, Category("Obese (Class I)",  "🟠")),
    (40.0, Category("Obese (Class II)", "🔴")),
    (float("inf"), Category("Obese (Class III)", "🔴")),
]

def get_positive_number(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Please enter a positive number.")
            else:
                return value 
        except ValueError:
            print("invalid, please eneter a number")

def lbs_to_kg(lbs): return lbs / 2.205
def inches_to_m(ins): return ins / 39.38
def ft_in_to_m(ft, inches): return inches_to_m(ft * 12 + inches)

def calculate_bmi(weight_kg, height_m):
    return weight_kg / (height_m ** 2)


def get_category(bmi):
    for threshold, category in BMI_Categories:
        if bmi < threshold:
            return category
    return BMI_Categories[-1][1]

def normal_weight_range(height_m):
    low = 18.5 * height_m ** 2
    high = 24.9 * height_m ** 2
    return low, high

def get_metric_inputs():
    weight_kg = get_positive_number("  Weight (kg): ")
    height_m  = get_positive_number("  Height (m) : ") / 1   # already metres
    
    if height_m > 3:   
        height_m /= 100
    return weight_kg, height_m

def get_imperial_inputs():
    weight_lbs = get_positive_number("  Weight (lbs)  : ")
    feet       = get_positive_number("  Height (feet) : ")
    inches     = get_positive_number("  Height (inches remaining): ")
    return lbs_to_kg(weight_lbs), ft_in_to_m(feet, inches)

def print_result(bmi, category, height_m, unit):
    low, high = normal_weight_range(height_m)
    if unit == "imperial":
        low_disp  = f"{low  * 2.205:.1f} lbs"
        high_disp = f"{high * 2.205:.1f} lbs"
    else:
        low_disp  = f"{low:.1f} kg"
        high_disp = f"{high:.1f} kg"

    print("\n" + "=" * 34)
    print("         BMI RESULT")
    print("=" * 34)
    print(f"  BMI        : {bmi:.1f}")
    print(f"  Category   : {category.emoji}  {category.label}")
    print(f"  Normal range: {low_disp} – {high_disp}")
    print("=" * 34)
    print("  Note: BMI is a screening tool only.")
    print("  Consult a doctor for health advice.")

def main():
    print("=== BMI Calculator ===\n")
    print("Unit system:")
    print("  1) Metric   (kg / m)")
    print("  2) Imperial (lbs / ft & in)")

    while True:
        choice = input("Choose (1/2): ").strip()
        if choice == "1":
            weight_kg, height_m = get_metric_inputs()
            unit = "metric"
            break
        elif choice == "2":
            weight_kg, height_m = get_imperial_inputs()
            unit = "imperial"
            break
        print("  Please enter 1 or 2.")

    bmi      = calculate_bmi(weight_kg, height_m)
    category = get_category(bmi)
    print_result(bmi, category, height_m, unit)

if __name__ == "__main__":
    main()

