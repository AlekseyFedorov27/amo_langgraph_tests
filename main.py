import os
import time
import requests
from typing import TypedDict, Callable
from langgraph.graph import StateGraph, START, END

class State(TypedDict, total=False):
    leads: list[dict]
    tasks: list[dict]
    result: list[dict]

def fetch(endpoint: str) -> list[dict]:
    base = f"https://{os.environ['AMO_SUBDOMAIN']}.amocrm.ru/api/v4"
    headers = {"Authorization": f"Bearer {os.environ['AMO_TOKEN']}"}
    items, page = [], 1
    while True:
        r = requests.get(f"{base}/{endpoint}", headers=headers,
                         params={"page": page, "limit": 250}, timeout=30)
        r.raise_for_status()
        embedded = r.json().get("_embedded", {})
        batch = embedded.get(endpoint, [])
        items.extend(batch)
        if len(batch) < 250:
            return items
        page += 1

from logic import filter_leads

def build_graph(load_leads: Callable[[], list[dict]] | None = None,
                load_tasks: Callable[[], list[dict]] | None = None):
    load_leads = load_leads or (lambda: fetch("leads"))
    load_tasks = load_tasks or (lambda: fetch("tasks"))
    graph = StateGraph(State)
    graph.add_node("leads", lambda state: {"leads": load_leads()})
    graph.add_node("tasks", lambda state: {"tasks": load_tasks()})
    graph.add_node("filter", filter_leads)
    graph.add_edge(START, "leads")
    graph.add_edge("leads", "tasks")
    graph.add_edge("tasks", "filter")
    graph.add_edge("filter", END)
    return graph.compile()

app = build_graph()

if __name__ == "__main__":
    print(app.invoke({})["result"])
