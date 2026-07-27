import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("tasks.json")

def load_tasks():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)

def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1

def add_task(tasks, title):
    task = {
        "id":      next_id(tasks),
        "title":   title.strip(),
        "done":    False,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),  # fixed: - not _
    }
    tasks.append(task)
    print(f"  Added: \"{task['title']}\"")

def list_tasks(tasks):
    if not tasks:
        print("  No tasks yet — add one!")
        return
    print()
    print(f"  {'#':<4} {'':2} {'Task':<30} {'Created'}")
    print("  " + "-" * 52)
    for task in tasks:
        status = "✅" if task["done"] else "❌"
        title  = task["title"]
        if task["done"]:
            title = f"--{title}--"
        print(f"  {task['id']:<4} {status}  {title:<30} {task['created']}")
    done_count = sum(1 for t in tasks if t["done"])
    print(f"\n  {done_count}/{len(tasks)} tasks complete")

def find_task(tasks, task_id):
    return next((t for t in tasks if t["id"] == task_id), None)

def complete_task(tasks, task_id):
    task = find_task(tasks, task_id)  # fixed: removed stray space
    if not task:
        print(f"  No task with id {task_id}.")
        return
    task["done"] = True
    print(f"  Marked done: \"{task['title']}\"")

def delete_task(tasks, task_id):
    task = find_task(tasks, task_id)
    if not task:
        print(f"  No task with id {task_id}.")
        return
    confirm = input(f"  Delete \"{task['title']}\"? (y/n): ").strip().lower()
    if confirm == "y":
        tasks.remove(task)
        print("  Deleted.")

def show_menu():
    print("\n--- To-Do List ---")
    print("  a) Add task")
    print("  l) List tasks")
    print("  c) Complete task")
    print("  d) Delete task")
    print("  q) Quit")

def get_id(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("  Please enter a task number.")

def main():
    print("=== To-Do List ===")
    tasks = load_tasks()
    while True:
        show_menu()
        choice = input("Choice: ").strip().lower()
        if choice == "a":
            title = input("  Task title: ").strip()
            if title:
                add_task(tasks, title)
                save_tasks(tasks)
            else:
                print("  Title can't be empty.")
        elif choice == "l":
            list_tasks(tasks)
        elif choice == "c":
            list_tasks(tasks)
            task_id = get_id("  Enter task # to complete: ")
            complete_task(tasks, task_id)
            save_tasks(tasks)
        elif choice == "d":
            list_tasks(tasks)
            task_id = get_id("  Enter task # to delete: ")
            delete_task(tasks, task_id)
            save_tasks(tasks)
        elif choice == "q":
            print("Goodbye!")
            break
        else:
            print("  Invalid choice — try again.")

if __name__ == "__main__":
    main()