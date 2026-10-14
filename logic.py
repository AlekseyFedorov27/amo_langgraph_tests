import time

def filter_leads(state: dict) -> dict:
    now = int(time.time())
    tasks_by_lead: dict[int, list[dict]] = {}
    for task in state["tasks"]:
        if task.get("entity_type") == "leads":
            tasks_by_lead.setdefault(task["entity_id"], []).append(task)
    result = []
    for lead in state["leads"]:
        tasks = tasks_by_lead.get(lead["id"], [])
        overdue = [t for t in tasks if not t.get("is_completed")
                   and t.get("complete_till", now + 1) < now]
        if not tasks or overdue:
            result.append({"id": lead["id"], "name": lead["name"],
                           "reason": "no_tasks" if not tasks else "overdue_tasks",
                           "overdue_task_ids": [t["id"] for t in overdue]})
    return {"result": result}

