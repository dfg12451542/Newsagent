import os
import json
from collections import defaultdict

base_dir = "output_async_react_gpt-4o-mini"
total_prompt_tokens = 0
total_completion_tokens = 0
total_tokens = 0
action_sums = defaultdict(int)
num_files = 0

for folder in os.listdir(base_dir):
    stats_path = os.path.join(base_dir, folder, "stats.json")
    if os.path.isfile(stats_path):
        with open(stats_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            total_prompt_tokens += data.get("total_prompt_tokens", 0)
            total_completion_tokens += data.get("total_completion_tokens", 0)
            total_tokens += data.get("total_tokens", 0)
            for action, count in data.get("action_counts", {}).items():
                action_sums[action] += count
        num_files += 1
print(num_files)
# Calculate averages
avg_total_prompt_tokens = total_prompt_tokens // num_files if num_files else 0
avg_total_completion_tokens = total_completion_tokens // num_files if num_files else 0
avg_total_tokens = total_tokens // num_files if num_files else 0
avg_action_counts = {action: (action_sums[action] // num_files if num_files else 0) for action in action_sums}

result = {
    "avg_total_prompt_tokens": avg_total_prompt_tokens,
    "avg_total_completion_tokens": avg_total_completion_tokens,
    "avg_total_tokens": avg_total_tokens,
    "avg_action_counts": avg_action_counts
}

with open("avg_stats.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print("Averages written to avg_stats.json") 