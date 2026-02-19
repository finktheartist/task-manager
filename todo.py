# todo.py
from __future__ import annotations
from datetime import datetime, date, timedelta

import argparse

from app import priority_rank, due_sort_key
from models import create_task
from storage import load_tasks, save_tasks


# ----------------------------
# Helpers
# ----------------------------

def find_task(tasks: list[dict], task_id: int) -> dict | None:
    for task in tasks:
        if task.get("id") == task_id:
            return task
    return None

def format_task(task):
    status = "✅" if task.get("completed") else "⬜"
    priority = task.get("priority", "med").upper()
    due = task.get("due_date") or "-"
    return f"{status} [{task['id']}] {task['title']} | {priority} | due: {due}"

def is_overdue(task):
    if task.get("completed"):
        return False

    if not task.get("due_date"):
        return False


    try:
        due = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
    except ValueError:
        return False

    return due < date.today()

def sort_key(task: dict, mode: str):
    if mode == "due":
        return (due_sort_key(task), priority_rank(task), task["id"])
    if mode == "id":
        return (task["id"],)
    # default: priority
    return (priority_rank(task), due_sort_key(task), task["id"])


# ----------------------------
# Command functions
# Each returns True if tasks were changed
# ----------------------------

def cmd_add(args: argparse.Namespace, tasks: list[dict]) -> bool:
    next_id = max((task["id"] for task in tasks), default=0) + 1
    task = create_task(next_id, args.title)
    tasks.append(task)
    print(f"Added: [{task['id']}] {task['title']}")
    return True


def cmd_complete(args: argparse.Namespace, tasks: list[dict]) -> bool:
    task = find_task(tasks, args.id)

    if not task:
        print(f"No task found with id {args.id}")
        return False

    if task.get("completed"):
        print("Task already completed.")
        return False

    task["completed"] = True
    print(f"Task {args.id} marked complete.")
    return True


def cmd_delete(args: argparse.Namespace, tasks: list[dict]) -> bool:
    task = find_task(tasks, args.id)

    if not task:
        print(f"No task found with id {args.id}")
        return False

    tasks[:] = [t for t in tasks if t["id"] != args.id]
    print(f"Task {args.id} deleted.")
    return True

def cmd_list(args: argparse.Namespace, tasks: list[dict]) -> bool:
    filtered = tasks[:]

    if args.overdue:
        filtered = [t for t in filtered if is_overdue(t)]

    if args.priority:
        filtered = [t for t in filtered if t.get("priority", "med") == args.priority]

    if args.todo:
        filtered = [t for t in filtered if not t.get("completed")]

    if args.today:
        today = date.today()
        filtered = [t for t in filtered due_sort_key(t) == today]

    if args.week:
        start = day.today()
        end = start + timedelta(days=7)
        filtered = [t for t in filtered if start <= due_sort_key(t) <= end]

    filtered.sort(key=lambda t: sort_key(t, args.sort), reverse=args.reverse)

    if not filtered:
        print("No tasks found.")
        return False

    for task in filtered:
        print(format_task(task))

    if args.due:
        filtered = [t for t in filtered if t.get("due_date")]

    return False


# ----------------------------
# Argparse setup
# ----------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo",
        description="CLI task manager (argparse + JSON persistence).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title (use quotes if needed)")
    add_parser.set_defaults(func=cmd_add)

    # complete
    complete_parser = subparsers.add_parser("complete", help="Mark a task completed")
    complete_parser.add_argument("id", type=int, help="Task id")
    complete_parser.set_defaults(func=cmd_complete)

    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", type=int, help="Task id")
    delete_parser.set_defaults(func=cmd_delete)

    # list
    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--priority", choices=["low", "med", "high"], help="Filter tasks by priority")
    list_parser.add_argument("--todo", action="store_true", help="Show only incomplete tasks")
    list_parser.add_argument("--due", action="store_true", help="Show only tasks with a due date")
    list_parser.add_argument("--overdue", action="store_true", help="Show overdue tasks")
    list_parser.set_defaults(func=cmd_list)
    list_parser.add_argument("--today", action="store_true", help="Show tasks due today")
    list_parser.add_argument("--week". action="store_true", help="Show tasks due in the next 7 days")
    list_parser.add_argument(
        "--sort",
        choices=["priority", "due", "id"],
        default="priority",
        help="Sort order (default: priority)",
    )
    list_parser.add_argument(
        "--reverse",
        action="store_true",
        help="Reverse the sort order",
    )

    return parser


# ----------------------------
# Main entry
# ----------------------------

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return

    tasks = load_tasks()

    changed = args.func(args, tasks)

    if changed:
        save_tasks(tasks)


if __name__ == "__main__":
    main()
