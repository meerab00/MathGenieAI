import json
import os
from datetime import datetime

HISTORY_FILE = "chat_history.json"

def load_chats() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_chat(question: str, messages: list) -> None:
    chats = load_chats()
    serializable = []
    for m in messages:
        entry = {"role": m["role"], "content": m.get("content", "")}
        if "graph_expr" in m:
            entry["graph_expr"] = m["graph_expr"]
        serializable.append(entry)

    chats.insert(0, {
        "question": question[:80],
        "messages": serializable,
        "timestamp": datetime.now().isoformat(),
    })
    chats = chats[:30]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(chats, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def clear_all_history() -> None:
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
