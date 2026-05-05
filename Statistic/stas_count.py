import os
import json
from collections import defaultdict

base_dir = "output_async_react_google"

def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)

def walk_numbers(obj, path=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_numbers(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_numbers(v, path + (str(i),))
    else:
        if is_number(obj):
            yield path, float(obj)

def unflatten(avg_map):
    root = {}
    for path, val in avg_map.items():
        cur = root
        for seg in path[:-1]:
            cur = cur.setdefault(seg, {})
        cur[path[-1]] = val
    return root

sums = defaultdict(float)     # key: tuple path -> sum
counts = defaultdict(int)     # key: tuple path -> how many files had this key
num_files = 0

for folder in os.listdir(base_dir):
    stats_path = os.path.join(base_dir, folder, "stats.json")
    if os.path.isfile(stats_path):
        try:
            with open(stats_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        for path, val in walk_numbers(data):
            sums[path] += val
            counts[path] += 1

        num_files += 1

print(num_files)

# Compute averages per numeric key over files that contained that key
averages_flat = {}
for path, total in sums.items():
    n = counts[path]
    if n > 0:
        averages_flat[path] = total / n

averages = unflatten(averages_flat)

result = {
    "num_files": num_files,
    "averages": averages
}

with open("avg_stats.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("Averages written to avg_stats.json")
