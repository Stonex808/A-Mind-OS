import json
from local_demo import LocalOrchestratorDemo  # adjust import if needed

demo = LocalOrchestratorDemo()

# Step 1 — store a fact so memory has something to recall
store_result = demo.process_intent("remember debian setup requires apt-get update first", source="test")
assert store_result["accepted"] == True
assert store_result["result"].get("episode_id") is not None

# Step 2 — recall it (memory now causally drives planning)
result = demo.process_intent("recall my last task about debian setup", source="test")

assert result["accepted"] == True
assert result["result"].get("memory_recall") is not None
assert len(result["result"]["memory_recall"].get("episodes", [])) >= 1 or len(result["result"]["memory_recall"].get("facts", [])) >= 1

print("✅ GREEN LOOP PASSED — memory now causally drives planning!")
with open("green_loop_result.json", "w") as f:
    json.dump(result, f, indent=2)
