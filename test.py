from backend.player_api import process_player_input
import os
import json

PLAYER_ID = "test_player"
CHARACTER_ID = "Thorin"
PLAYER_INPUT = "Explain how combat initiatives work."

# Call the function directly
response = process_player_input(PLAYER_ID, PLAYER_INPUT, CHARACTER_ID)

# Print DM response
print("=== DM Response ===")
print(response)

# 3. check memory
memory_file = os.path.join("memory_logs", f"{PLAYER_ID}.json")
if os.path.exists(memory_file):
    with open(memory_file, "r", encoding="utf8") as f:
        events = json.load(f)
    print("\n=== Memory Log ===")
    for e in events[-5:]:  # show last 5 events
        print(f"{e['type']}: {e['description']}")
else:
    print("No memory found for player.")
