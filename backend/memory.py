import os
import json
from datetime import datetime

# Memory folder relative to this script
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory_logs")
os.makedirs(MEMORY_DIR, exist_ok=True)

def _get_player_file(player_id):
    return os.path.join(MEMORY_DIR, f"{player_id}.json")

def add_event(player_id, event_type, description, metadata=None):
    """
    Add a new event to the player's memory.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type,
        "description": description,
        "metadata": metadata or {}
    }
    
    mem_file = _get_player_file(player_id)
    if os.path.exists(mem_file):
        with open(mem_file, "r", encoding="utf8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)
    with open(mem_file, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return entry

def get_recent_events(player_id, limit=5):
    """
    Get the last N events for a player.
    """
    mem_file = _get_player_file(player_id)
    if not os.path.exists(mem_file):
        return []

    with open(mem_file, "r", encoding="utf8") as f:
        data = json.load(f)

    return data[-limit:]

def summarise_memory(player_id):
    """
    Create a summary of all past events for context.
    """
    events = get_recent_events(player_id, limit=1000)
    summary = []
    for e in events:
        summary.append(f"[{e['timestamp']}] {e['type']}: {e['description']}")
    return "\n".join(summary)
