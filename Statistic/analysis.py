# avg_words_per_report.py
import sys
import re
from pathlib import Path
from typing import Dict, List

# Count words: letters with optional internal hyphens/apostrophes
WORD_RE = re.compile(r"[^\W\d_]+(?:[-'][^\W\d_]+)*", re.UNICODE)

def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))

def is_report_root(root: Path) -> bool:
    if not root.is_dir():
        return False
    for sub in root.iterdir():
        if sub.is_dir() and (sub / "draft.txt").exists():
            return True
    return False

def avg_words_for_root(root: Path) -> Dict[str, float]:
    reports = 0
    total_words = 0
    for sub in sorted(root.iterdir()):
        if not sub.is_dir():
            continue
        draft = sub / "draft.txt"
        if draft.exists():
            text = draft.read_text(encoding="utf-8", errors="ignore")
            total_words += count_words(text)
            reports += 1
    avg = (total_words / reports) if reports else 0.0
    return {
        "root": str(root.resolve()),
        "reports": reports,
        "total_words": total_words,
        "avg_words_per_report": avg,
    }

def main(args: List[str]) -> None:
    # If roots passed as args, use them; else auto-detect in CWD
    roots = [Path(a) for a in args] if args else [
        p for p in Path(".").iterdir() if is_report_root(p)
    ]
    if not roots:
        print("No report roots found. Pass root paths as arguments or run in a directory containing report folders.")
        return

    results = [avg_words_for_root(r) for r in roots]

    # Pretty print
    print("\nAverage words per report (by root):")
    for r in results:
        print(f"- {r['root']}")
        print(f"  reports: {r['reports']}")
        print(f"  total_words: {r['total_words']}")
        print(f"  avg_words_per_report: {r['avg_words_per_report']:.2f}")

if __name__ == "__main__":
    main(sys.argv[1:])
