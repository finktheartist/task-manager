def create_task(task_id, title):
    return {
        "id": task_id,
        "title": title,
        "completed": False,
        "priority": "med",
        "due_date": None
    }

