def get_words():
    noun = input("Give me a noun: ")
    verb = input("Give me a verb: ")
    adjective = input("Give me a adjective: ")
    place = input("Give me a place: ")
    number = input("Give me a number: ")
    return noun, verb, adjective, place, number

def tell_story(noun, verb, adjective, place, number):
    story = (
        f"Once upon a time, a {adjective} {noun} "
        f"{verb} all the way to {place}."
        f"It took exectly {number} days,"
        f" and nobody believed the {noun} when it came back."
    )
    print("\n--- Your Mad Lib ---")
    print(story)

if __name__ == "__main__":
    print("=== Mad LIbs Generator ===\n")
    words = get_words()
    tell_story(*words)