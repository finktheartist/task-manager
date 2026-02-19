from __future__ import annotations

from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date

from models import create_task
from storage import load_tasks, save_tasks

app = Flask(__name__)


# --- helpers (reuse your CLI logic) ---

def normalize_priority(value: str) -> str:
    v = (value or "").strip().lower()
    return v if v in {"low", "med", "high"} else "med"

def normalize_due_date(value: str) -> str | None:
    v = (value or "").strip()
    if not v:
        return None
    try:
        datetime.strptime(v, "%Y-%m-%d")
        return v
    except ValueError:
        return None


def priority_rank(task: dict) -> int:
    order = {"high": 0, "med": 1, "low": 2}
    return order.get(task.get("priority", "med"), 1)

def due_sort_key(task: dict) -> date:
    due = task.get("due_date")
    if not due:
        return date.max
    try:
        return datetime.strptime(due, "%Y-%m-%d").date()
    except ValueError:
        return date.max

def is_overdue(task: dict) -> bool:
    if task.get("completed"):
        return False
    d = due_sort_key(task)
    return d != date.max and d < date.today()

def next_id(tasks: list[dict]) -> int:
    return max((t.get("id", 0) for t in tasks), default=0) + 1

def find_task(tasks: list[dict], task_id: int) -> dict | None:
    for t in tasks:
        if t.get("id") == task_id:
            return t
    return None


# --- routes ---

@app.get("/")
def index():
    tasks = load_tasks()

    # basic sort (priority -> due -> id)
    tasks_sorted = sorted(tasks, key=lambda t: (priority_rank(t), due_sort_key(t), t.get("id", 0)))

    return render_template(
        "index.html",
        tasks=tasks_sorted,
        today=date.today().isoformat(),
        is_overdue=is_overdue,
    )

@app.post("/add")
def add_task():
    title = (request.form.get("title") or "").strip()
    if not title:
        return redirect(url_for("index"))

    tasks = load_tasks()
    task = create_task(next_id(tasks), title)
    tasks.append(task)
    save_tasks(tasks)

    return redirect(url_for("index"))

@app.post("/complete/<int:task_id>")
def complete_task(task_id: int):
    tasks = load_tasks()
    t = find_task(tasks, task_id)
    if t and not t.get("completed"):
        t["completed"] = True
        save_tasks(tasks)
    return redirect(url_for("index"))

@app.post("/uncomplete/<int:task_id>")
def uncomplete_task(task_id: int):
    tasks = load_tasks()
    t = find_task(tasks, task_id)
    if t and t.get("completed"):
        t["completed"] = False
        save_tasks(tasks)
    return redirect(url_for("index"))

@app.post("/delete/<int:task_id>")
def delete_task(task_id: int):
    tasks = load_tasks()
    before = len(tasks)
    tasks[:] = [t for t in tasks if t.get("id") != task_id]
    if len(tasks) != before:
        save_tasks(tasks)
    return redirect(url_for("index"))

@app.post("/update/<int:task_id>")
def update_task(task_id: int):
    tasks = load_tasks()
    t = find_task(tasks, task_id)
    if not t:
        return redirect(url_for("index"))

    # Read inputs from the form
    new_priority = normalize_priority(request.form.get("priority"))
    new_due = normalize_due_date(request.form.get("due_date"))

    changed = False

    if t.get("priority", "med") != new_priority:
        t["priority"] = new_priority
        changed = True

    if t.get("due_date") != new_due:
        t["due_date"] = new_due
        changed = True

    if changed:
        save_tasks(tasks)

    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run()
