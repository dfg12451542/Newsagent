import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.gridspec import GridSpec

metrics = [
    "Factual Consistency", "Logical Consistency", "Importance",
    "Readability", "Objectivity", "Journalistic Style"
]

rows = [
    "GPT-4o vs Qwen3-32B",
    "Qwen3-32B vs Human-Written",
    "GPT-4o vs Human-Written"
]

data = {
    ("GPT-4o vs Qwen3-32B", "Factual Consistency"): [4.4, 16.3, 79.3],
    ("GPT-4o vs Qwen3-32B", "Logical Consistency"): [15.7, 25.0, 59.3],
    ("GPT-4o vs Qwen3-32B", "Importance"):          [51.5, 25.7, 22.8],
    ("GPT-4o vs Qwen3-32B", "Readability"):         [64.2, 35.8, 0.0],
    ("GPT-4o vs Qwen3-32B", "Objectivity"):         [9.7, 18.4, 71.9],
    ("GPT-4o vs Qwen3-32B", "Journalistic Style"):  [17.7, 63.2, 19.1],

    ("Qwen3-32B vs Human-Written", "Factual Consistency"): [17.2, 16.1, 66.7],
    ("Qwen3-32B vs Human-Written", "Logical Consistency"): [76.3, 5.3, 18.4],
    ("Qwen3-32B vs Human-Written", "Importance"):          [73.1, 24.7, 2.2],
    ("Qwen3-32B vs Human-Written", "Readability"):         [81.7, 18.3, 0.0],
    ("Qwen3-32B vs Human-Written", "Objectivity"):         [8.6, 29.0, 62.4],
    ("Qwen3-32B vs Human-Written", "Journalistic Style"):  [81.7, 17.2, 1.1],

    ("GPT-4o vs Human-Written", "Factual Consistency"): [7.6, 8.8, 83.6],
    ("GPT-4o vs Human-Written", "Logical Consistency"): [67.3, 6.1, 26.2],
    ("GPT-4o vs Human-Written", "Importance"):          [67.6, 29.3, 3.1],
    ("GPT-4o vs Human-Written", "Readability"):         [83.6, 16.3, 0.1],
    ("GPT-4o vs Human-Written", "Objectivity"):         [6.5, 41.3, 52.2],
    ("GPT-4o vs Human-Written", "Journalistic Style"):  [71.7, 27.3, 1.0],
}

COLORS = ["#92c9d4", "#f1a6b6", "#f4cf9b"]
def autopct_fmt(values): return lambda pct: f"{pct:.1f}%"

# Figure + GridSpec: tiny header row, big pie rows, tight gaps
fig = plt.figure(figsize=(14.2, 7.2))
gs = GridSpec(
    4, 6, figure=fig,
    height_ratios=[0.12, 1, 1, 1],  # thin header row
    hspace=0.12, wspace=0.03        # very tight to enlarge circles
)

# Legend (very top)
handles = [Patch(color=COLORS[0], label="Win"),
           Patch(color=COLORS[1], label="Lose"),
           Patch(color=COLORS[2], label="Tie")]
fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False,
           bbox_to_anchor=(0.5, 0.985))

# Header axes: one per column so header width == pie column width
for c, metric in enumerate(metrics):
    axh = fig.add_subplot(gs[0, c])
    axh.axis("off")
    axh.text(0.5, 0.05, metric, ha="center", va="bottom",
             fontsize=10, fontweight="bold")  # low so it hugs the pies

# Pie axes
for r, row_label in enumerate(rows):
    for c, metric in enumerate(metrics):
        ax = fig.add_subplot(gs[r+1, c])
        vals = data[(row_label, metric)]
        ax.pie(vals, colors=COLORS, startangle=90, counterclock=False,
               wedgeprops=dict(width=1.0, edgecolor="white"),
               autopct=autopct_fmt(vals), pctdistance=0.75,
               textprops=dict(fontsize=8))
        ax.set(aspect="equal")
        ax.set_title(row_label, fontsize=8, pad=4)

plt.show()
