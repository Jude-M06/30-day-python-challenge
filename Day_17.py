import json
from pathlib import Path
import copy

SAVE_FILE = Path("save.json")

WORLD = {
    "entrance": {
        "description": "You stand at the entrance to a crumbling tower.",
        "exits": {"north": "hallway"},
        "items": ["rusty key"],
        "enemies": [],
    },
    "hallway": {
        "description": "A dimly lit hallway. Torches flicker on the walls.",
        "exits": {"south": "entrance", "up": "library", "north": "dungeon"},
        "items": ["torch"],
        "enemies": ["goblin"],
    },
    "library": {
        "description": "Shelves of ancient books. A locked chest gleams.",
        "exits": {"down": "hallway"},
        "items": ["spell book"],
        "enemies": [],
        "locked": True,
        "key": "rusty key",
    },
    "dungeon": {
        "description": "A damp dungeon. A dragon sleeps in the corner.",
        "exits": {"south": "hallway"},
        "items": ["golden crown"],
        "enemies": ["dragon"],
    },
}

COMMANDS = ["go", "take", "drop", "inventory", "look",
            "use", "help", "save", "load", "quit"]

HELP_TEXT = """
  Commands:
    go [direction]     — move (north/south/east/west/up/down)
    take [item]        — pick up an item
    drop [item]        — drop an item from your inventory
    use [item]         — use an item in the current room
    look               — re-read the room description
    inventory (or i)   — show what you're carrying
    save / load        — save or restore your game
    quit               — exit the game
"""

class Player:
    def __init__(self):
        self.location  = "entrance"
        self.inventory = []
        self.health    = 100
        self.alive     = True

    def move(self, direction, world):
        room = world[self.location]
        if direction not in room["exits"]:
            print("  You can't go that way.")
            return

        dest      = room["exits"][direction]
        dest_room = world[dest]

        if dest_room.get("locked"):
            key = dest_room.get("key", "")
            if key not in self.inventory:
                print(f"  The way is locked. You need: {key}.")
                return

        self.location = dest
        print(f"\n  You move {direction}.\n")

    def take(self, item, world):
        room_items = world[self.location]["items"]
        if item not in room_items:
            print(f"  There's no '{item}' here.")
            return
        room_items.remove(item)
        self.inventory.append(item)
        print(f"  You pick up the {item}.")

    def drop(self, item, world):
        if item not in self.inventory:
            print(f"  You're not carrying '{item}'.")
            return
        self.inventory.remove(item)
        world[self.location]["items"].append(item)
        print(f"  You drop the {item}.")

    def use(self, item, world):
        if item not in self.inventory:
            print(f"  You don't have '{item}'.")
            return
        room = world[self.location]
        enemies = room["enemies"]

        if item == "spell book" and "dragon" in enemies:
            enemies.remove("dragon")
            self.inventory.remove("spell book")
            print("  You read the spell book aloud. The dragon vanishes in a puff of smoke!")
        elif item == "torch" and enemies:
            enemy = enemies[0]
            enemies.remove(enemy)
            self.inventory.remove("torch")
            print(f"  You brandish the torch. The {enemy} flees into the darkness!")
        else:
            print(f"  Nothing interesting happens with the {item} here.")

    def to_dict(self):
        return {
            "location":  self.location,
            "inventory": self.inventory,
            "health":    self.health,
        }
    
    @classmethod
    def from_dict(cls, data):
        p           = cls()
        p.location  = data["location"]
        p.inventory = data["inventory"]
        p.health    = data["health"]
        return p


def describe_room(room_name, world):
    room = world[room_name]
    print("\n" + "=" * 44)
    print(f"  [{room_name.upper()}]")
    print("=" * 44)
    print(f"  {room['description']}")

    exits = ", ".join(room["exits"].keys())
    print(f"\n  Exits   : {exits}")

    if room["items"]:
        print(f"  Items   : {', '.join(room['items'])}")
    if room["enemies"]:
        print(f"  Enemies : {', '.join(room['enemies'])}  ")

def parse_command(raw):
    parts = raw.strip().lower().split(maxsplit=1)
    if not parts:
        return None, None
    verb = parts[0]
    noun = parts[1] if len(parts) > 1 else None
    aliases = {"i": "inventory", "l": "look", "n": "go north",
                "s": "go south",  "e": "go east",  "w": "go west"}
    if verb in aliases:
        return parse_command(aliases[verb])
    return verb, noun

def check_win(player, world):
    room = world[player.location]
    if "golden crown" in player.inventory and player.location == "entrance":
        print("\n  You emerge from the tower clutching the golden crown.")
        print("  Sunlight warms your face. You have won!")
        return True
    if room["enemies"]:
        enemy = room["enemies"][0]
        print(f"\n  A {enemy} attacks you! You have no way to fight back.")
        print("  Your health drains away. Game over.")
        player.alive = False
        return True
    return False

def save_game(player, world):
    data = {"player": player.to_dict(), "world": world}
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("  Game saved.")

def load_game():
    if not SAVE_FILE.exists():
        print("  No save file found.")
        return None, None
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    player = Player.from_dict(data["player"])
    world  = data["world"]
    print("  Game loaded.")
    return player, world

def main():
    print("-" * 44)
    print("   THE TOWER — a text adventure")
    print("-" * 44)
    print("  Type 'help' for commands.\n")

    player = Player()
    world  = copy.deepcopy(WORLD)

    describe_room(player.location, world)

    while player.alive:
        try:
            raw = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Farewell.")
            break

        if not raw:
            continue

        verb, noun = parse_command(raw)
        
        if verb == "help":
            print(HELP_TEXT)
        elif verb == "look":
            describe_room(player.location, world)
        elif verb == "inventory":
            if player.inventory:
                print(f"  Carrying: {', '.join(player.inventory)}")
            else:
                print("  You're not carrying anything.")
        elif verb == "go":
            if not noun:
                print("  Go where?")
            else:
                player.move(noun, world)
                describe_room(player.location, world)
                if check_win(player, world):
                    break
        elif verb == "take":
            if not noun:
                print("  Take what?")
            else:
                player.take(noun, world)
        elif verb == "drop":
            if not noun:
                print("  Drop what?")
            else:
                player.drop(noun, world)
        elif verb == "use":
            if not noun:
                print("  Use what?")
            else:
                player.use(noun, world)
        elif verb == "save":
            save_game(player, world)
        elif verb == "load":
            loaded = load_game()
            if loaded[0]:
                player, world = loaded
                describe_room(player.location, world)
        elif verb == "quit":
            print("  Thanks for playing.")
            break
        else:
            print(f"  Unknown command '{verb}'. Type 'help' for a list.")

if __name__ == "__main__":
    main()






