import os, json, re, argparse, itertools, collections
import pandas as pd

DIMENSIONS = [
    "Factual Consistency",
    "Logical Consistency",
    "Importance",
    "Readability",
    "Objectivity",
    "Journalistic",
    "Information Density",
    "Overall",
]

# ---- robust JSON extraction (handles ```json ... ``` and partials) ----
FENCE_JSON_RE = re.compile(r"```(?:json|JSON)?\s*(\{.*?\})\s*```", re.S)

def _find_first_json_object(text: str):
    start = text.find('{')
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i, ch in enumerate(text[start:], start):
            if in_str:
                if esc: esc = False
                elif ch == '\\': esc = True
                elif ch == '"': in_str = False
            else:
                if ch == '"': in_str = True
                elif ch == '{': depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        return text[start:i+1]
        start = text.find('{', start + 1)
    return None

def _extract_json_text(content: str):
    m = FENCE_JSON_RE.search(content)
    if m: return m.group(1).strip()
    if content.strip().startswith('{'):
        obj = _find_first_json_object(content)
        if obj: return obj.strip()
    obj = _find_first_json_object(content)
    return obj.strip() if obj else None

def _safe_load_result(meta: dict):
    """
    Return {"ok": bool, "data": dict|None, "raw_text": str|None}
    Works with both 'new' (raw_text+parsed flag) and 'old' formats.
    """
    if "parsed" in meta:
        if meta.get("parsed") and isinstance(meta.get("result"), dict):
            return {"ok": True, "data": meta["result"], "raw_text": meta.get("raw_text")}
        raw = meta.get("raw_text")
        if raw:
            jt = _extract_json_text(raw)
            if jt:
                try:
                    return {"ok": True, "data": json.loads(jt), "raw_text": raw}
                except Exception:
                    pass
        return {"ok": False, "data": None, "raw_text": raw}
    res = meta.get("result")
    if isinstance(res, dict):
        return {"ok": True, "data": res, "raw_text": None}
    raw = meta.get("raw_text")
    if raw:
        jt = _extract_json_text(raw)
        if jt:
            try:
                return {"ok": True, "data": json.loads(jt), "raw_text": raw}
            except Exception:
                pass
    return {"ok": False, "data": None, "raw_text": raw}

# ---- label normalization / aliases ----
ALIASES = {
    # exact labels as saved by DISPLAY_NAME_MAP in your evaluator:
    "gpt-4o/1step": ["gpt-4o/1step", "gpt4o/1step", "gpt4o 1step"],
    "gemma-3-27b-it/1step": ["gemma/1step", "gemma", "gemma-1step", "gemma-3-27b-it/1step"],
    "reference": ["reference", "__reference__"],
}

def _canon(label: str) -> str:
    l = (label or "").strip().lower()
    for k, vals in ALIASES.items():
        for v in vals:
            if l == v.lower():
                return k
    return label  # fallback: leave as-is

def _canon_from_meta(label: str) -> str:
    # meta labels are already display labels; still normalize case/whitespace
    return _canon(label)

# ---- aggregation ----
def analyze_pairs(outdir: str, participants: list[str]):
    raw_root = os.path.join(outdir, "raw_judge_json")
    if not os.path.isdir(raw_root):
        raise SystemExit(f"raw folder not found: {raw_root}")

    # canonical target participants
    targets = [_canon(p) for p in participants]
    if len(set(targets)) != 3:
        raise SystemExit(f"Need exactly 3 distinct participants, got: {targets}")

    # prepare accumulators per pair & per dimension
    # stats[(A,B)][dim] = {"A":wins, "B":wins, "tie":ties, "files":[...]}
    stats = {}
    for a, b in itertools.combinations(targets, 2):
        key = (a, b)
        stats[key] = {dim: {"A":0, "B":0, "tie":0, "files": []} for dim in DIMENSIONS}

    detail_rows = []

    for report_dir in sorted(os.listdir(raw_root)):
        rpath = os.path.join(raw_root, report_dir)
        if not os.path.isdir(rpath): continue
        for fname in sorted(os.listdir(rpath)):
            if not fname.endswith(".json"): continue
            fpath = os.path.join(rpath, fname)

            try:
                meta = json.load(open(fpath, "r", encoding="utf-8"))
            except Exception:
                continue

            li = _canon_from_meta(meta.get("label_i", f"idx_{meta.get('i')}"))
            lj = _canon_from_meta(meta.get("label_j", f"idx_{meta.get('j')}"))
            flip = bool(meta.get("flipped_presentation", True))
            rep = meta.get("report_id")

            # Only keep files where both labels are among our 3 targets
            if li not in targets or lj not in targets: 
                continue

            # which ordered pair bucket?
            pair_key = tuple(sorted((li, lj), key=lambda x: targets.index(x)))
            if pair_key not in stats:
                # If sorting by targets order missed due to custom order, use alphabetical as fallback
                pair_key = tuple(sorted((li, lj)))
                if pair_key not in stats:
                    continue

            # load decision JSON
            load = _safe_load_result(meta)
            if not load["ok"] or not isinstance(load["data"], dict):
                continue
            data = load["data"]

            for dim in DIMENSIONS:
                entry = data.get(dim)
                if not isinstance(entry, dict):
                    continue
                winner = entry.get("winner")
                reasoning = entry.get("reasoning", "")

                # map winner to participant side A/B for this pair
                # flip==True  -> presented(first,second)==(i,j)
                # flip==False -> presented(first,second)==(j,i)
                if winner not in ("first", "second", "tie"):
                    continue

                a_label, b_label = pair_key[0], pair_key[1]
                # figure whether 'first' maps to li or lj, then to A/B accordingly
                if winner == "tie":
                    stats[pair_key][dim]["tie"] += 1
                    side = "tie"
                else:
                    # winner_label is li/lj depending on flip and 'first'/'second'
                    if (winner == "first" and flip) or (winner == "second" and not flip):
                        winner_label = li
                    else:
                        winner_label = lj
                    side = "A" if winner_label == a_label else "B"
                    stats[pair_key][dim][side] += 1

                # record detail row (per dimension, per file)
                detail_rows.append({
                    "report_id": rep,
                    "pair": f"{a_label} vs {b_label}",
                    "dimension": dim,
                    "winner": "tie" if side=="tie" else (a_label if side=="A" else b_label),
                    "file": fpath,
                    "reasoning": reasoning,
                })

                # keep file list for quick trace
                stats[pair_key][dim]["files"].append(fpath)

    # write outputs
    analysis_dir = os.path.join(outdir, "analysis")
    os.makedirs(analysis_dir, exist_ok=True)

    # details CSV (one row per file x dimension)
    pd.DataFrame(detail_rows).to_csv(os.path.join(analysis_dir, "pairwise_details.csv"), index=False)

    # per-pair summaries
    for pair_key, per_dim in stats.items():
        a_label, b_label = pair_key
        rows = []
        for dim in DIMENSIONS:
            A = per_dim[dim]["A"]
            B = per_dim[dim]["B"]
            T = per_dim[dim]["tie"]
            matches = A + B + T
            winrate_A = 100.0 * A / matches if matches else 0.0
            winrate_A_non_tie = 100.0 * A / (A + B) if (A + B) else 0.0
            rows.append({
                "dimension": dim,
                "wins_A": A,
                "wins_B": B,
                "ties": T,
                "matches": matches,
                "winrate_A_%": round(winrate_A, 2),
                "winrate_A_non_tie_%": round(winrate_A_non_tie, 2),
                "A_label": a_label,
                "B_label": b_label,
            })
        df = pd.DataFrame(rows)
        safe_a = a_label.replace("/", "_")
        safe_b = b_label.replace("/", "_")
        df.to_csv(os.path.join(analysis_dir, f"pairwise_summary__{safe_a}__vs__{safe_b}.csv"), index=False)

    # Combined convenience table: one CSV stacking all pairs
    stacks = []
    for pair_key, per_dim in stats.items():
        a_label, b_label = pair_key
        for dim in DIMENSIONS:
            A = per_dim[dim]["A"]; B = per_dim[dim]["B"]; T = per_dim[dim]["tie"]
            matches = A + B + T
            stacks.append({
                "pair": f"{a_label} vs {b_label}",
                "dimension": dim,
                "wins_A": A, "wins_B": B, "ties": T, "matches": matches,
                "winrate_A_%": round(100.0 * A / matches, 2) if matches else 0.0,
                "winrate_A_non_tie_%": round(100.0 * A / (A+B), 2) if (A+B) else 0.0,
                "A_label": a_label, "B_label": b_label,
            })
    pd.DataFrame(stacks).to_csv(os.path.join(analysis_dir, "pairwise_summary_all_pairs.csv"), index=False)

def main():
    ap = argparse.ArgumentParser(description="Trace pairwise winrates for selected participants across all dimensions.")
    ap.add_argument("--outdir", default="eval_results", help="Evaluator OUTDIR (default: eval_results)")
    ap.add_argument("--participants", nargs=3, required=True,
                    help='Exactly three participants (display names). Aliases supported: "gemma/1step" -> "gemma-3-27b-it/1step".')
    args = ap.parse_args()
    analyze_pairs(args.outdir, args.participants)

if __name__ == "__main__":
    main()
