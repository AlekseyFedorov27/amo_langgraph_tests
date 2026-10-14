import time
from logic import filter_leads


def sample_data():
    now = int(time.time())
    leads = [
        {"id": 1, "name": "Сделка без задач"},
        {"id": 2, "name": "Просроченная задача"},
        {"id": 3, "name": "Задача на будущее"},
        {"id": 4, "name": "Задача завершена"},
        {"id": 5, "name": "Задача другого типа сущности"},
    ]
    tasks = [
        {"id": 101, "entity_id": 2, "entity_type": "leads",
         "is_completed": False, "complete_till": now - 3600},
        {"id": 102, "entity_id": 3, "entity_type": "leads",
         "is_completed": False, "complete_till": now + 3600},
        {"id": 103, "entity_id": 4, "entity_type": "leads",
         "is_completed": True, "complete_till": now - 7200},
        {"id": 104, "entity_id": 5, "entity_type": "contacts",
         "is_completed": False, "complete_till": now - 3600},
    ]
    return leads, tasks


def test_filter_returns_only_leads_without_tasks_or_with_overdue_tasks():
    leads, tasks = sample_data()
    result = filter_leads({"leads": leads, "tasks": tasks})["result"]
    assert [item["id"] for item in result] == [1, 2, 5]
    assert result[0]["reason"] == "no_tasks"
    assert result[1]["reason"] == "overdue_tasks"
    assert result[1]["overdue_task_ids"] == [101]


def test_completed_overdue_task_is_not_reported_as_overdue():
    now = int(time.time())
    state = {
        "leads": [{"id": 10, "name": "Завершённая задача"}],
        "tasks": [{"id": 110, "entity_id": 10, "entity_type": "leads",
                   "is_completed": True, "complete_till": now - 100}],
    }
    assert filter_leads(state)["result"] == []
