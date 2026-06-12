import json
import re
from pathlib import Path

DATA_FILE = Path("contacts.json")
FIELDS = ["name", "phone", "email", "address", "notes"]

def load_contacts():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_contacts(contacts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2)

def print_contact(contact):
    print("\n  " + "─" * 34)
    print(f"  👤  {contact['name']}")
    print("  " + "─" * 34)
    if contact.get("phone"):
        print(f"  📞  {contact['phone']}")
    if contact.get("email"):
        print(f"  ✉️   {contact['email']}")
    if contact.get("address"):
        print(f"  📍  {contact['address']}")
    if contact.get("notes"):
        print(f"  📝  {contact['notes']}")
    print("  " + "─" * 34)

def list_all(contacts):
    if not contacts:
        print("not contatcs yet")
        return
    print(f"\n {'Name':<25} {'Phone':<15} {'Email'}")
    print(" " + "-" * 60)
    for c in sorted(contacts.values(), key=lambda x: x["name"].lower()):
        print(f" {c['name']:<25} {c.get('phone',''):<15} {c.get('email','')}")
    print(f"\n {len(contacts)} contacts(s) total")

def validate_email(email):
    if not email:
        return True
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def validate_phone(phone):
    if not phone:
        return True 
    digits = re.sub(r"[\s\-\(\)]", "", phone)
    return digits.isdigit() and 7 <= len(digits) <= 15

def add_contact(contacts):
    print("\n  --- Add Contact ---")
    name = input("  Name (required): ").strip()
    if not name:
        print("  Name cannot be empty.")
        return
    
    key = name.lower()
    if key in contacts:
        print(f" '{name}' already exists, use edit to update")

    while True:
        phone = input("  Phone (optional): ").strip()
        if validate_phone(phone):
            break
        print("  Invalid phone number — try again or leave blank.")

    while True:
        email = input("  Email (optional): ").strip()
        if validate_email(email):
            break
        print("  Invalid email — try again or leave blank.")

    address = input("Address (optional): ").strip()
    notes = input("Notes (optional): ").strip()

    contacts[key] = {
        "name": name, "phone": phone,
        "email": email, "address": address, "notes": notes
    }
    print(f"Added: {name}")

def find_contact(contacts, query):
    key = query.strip().lower()
    if key in contacts:
        return contacts[key]
    return None

def searchg_contacts(contacts, query):
    q = query.strip().lower()
    results = [
        c for c in contacts.values()
        if q in c["name"].lower()
        or q in c.get("phone", "")
        or q in c.get("email", "").lower()
    ]
    if not results:
        print(f"not contacts matching '{query}'")
        return
    print(f"{len(results)} results(s) for '{query}'")
    for c in sorted(results, key=lambda x: x["name"].lower()):
        print_contact(c)

def edit_contact(contacts, query):
    contact = find_contact(contacts, query)
    if not contact:
        print(f"  Contact '{query}' not found.")
        return

    print(f"\n  Editing '{contact['name']}' — press Enter to keep current value.")
    updated = dict(contact)   # copy so we only save on success

    for field in FIELDS:
        current = contact.get(field, "")
        new_val = input(f"  {field.capitalize()} [{current}]: ").strip()
        if new_val:
            updated[field] = new_val

    # re-key if name changed
    old_key = query.strip().lower()
    new_key = updated["name"].lower()
    del contacts[old_key]
    contacts[new_key] = updated
    print(f"  ✅ Updated: {updated['name']}")

def delete_contact(contacts, query):
    contact = find_contact(contacts, query)
    if not contact:
        print(f" Contact '{query}' not found")
        return
    confirm = input(f"Delete '{contact['name']}? (y/n): ").strip().lower()
    if confirm == "y":
        del contacts[contact["name"].lower()]
        print("contact deleted")

def show_menu():
    print("\n=== Contact Book ===")
    print("  a) Add contact")
    print("  l) List all")
    print("  s) Search")
    print("  v) View contact")
    print("  e) Edit contact")
    print("  d) Delete contact")
    print("  q) Quit")

def main():
    contacts = load_contacts()

    while True:
        show_menu()
        choice = input("Choice: ").strip().lower()

        if choice == "a":
            add_contact(contacts)
            save_contacts(contacts)

        elif choice == "l":
            list_all(contacts)

        elif choice == "s":
            query = input("  Search: ").strip()
            if query:
                search_contacts(contacts, query)
        
        elif choice == "v":
            query = input("  Contact name: ").strip()
            contact = find_contact(contacts, query)
            if contact:
                print_contact(contact)
            else:
                print(f"  '{query}' not found.")

        elif choice == "e":
            query = input("  Contact name to edit: ").strip()
            edit_contact(contacts, query)
            save_contacts(contacts)

        elif choice == "d":
            query = input("  Contact name to delete: ").strip()
            delete_contact(contacts, query)
            save_contacts(contacts)

        elif choice == "q":
            print("Goodbye!")
            break

        else:
            print("  Invalid choice — try again.")

if __name__ == "__main__":
    main()
