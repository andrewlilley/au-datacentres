"""Merge list/candidates/*.csv into list/master.csv.

State files take precedence; the national operators file fills blanks.
Disagreements between sources are written to the `conflicts` column
rather than silently resolved.
"""
import csv, glob, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
CAND = os.path.join(HERE, "candidates")
COLS = ["id","name","operator","state","suburb","address","status","mw_it",
        "year_complete","planning_ref","confidence","sources","notes"]

# operators.csv id -> canonical (state file) id
ALIAS = {
    "airtrunk-mel1-phase4-6": "airtrunk-mel1-building2",
    "cdc-mp-dc1": "cdc-mp1", "cdc-mp-dc2": "cdc-mp2", "cdc-mp-dc3": "cdc-mp3",
    "cdc-mp-dc4": "cdc-mp4", "cdc-mp-dc5": "cdc-mp5", "cdc-mp-dc6": "cdc-mp6",
    "cdc-hu4": "cdc-hume-hu4", "cdc-hu5": "cdc-hume-hu5", "cdc-hu6": "cdc-hume-hu6",
    "cdc-fy2": "cdc-fyshwick-fy2", "cdc-be1": "cdc-beard-be1",
    "cdc-bk1": "cdc-brooklyn-bk1", "cdc-bk2": "cdc-brooklyn-bk2",
    "cdc-lv1": "cdc-laverton-lv1", "cdc-lv2": "cdc-laverton-lv2",
    "cdc-maddington": "cdc-maddington-dc1",   # campus row folded into DC1
    "bne-airport-dc-stage2": "digico-bne2",
    "macquarie-ic3-superwest": "macquarie-ic3-super-west",
    "goodman-syd01-artarmon": "goodman-artarmon",
    "goodman-macquarie-park": "goodman-apollo",
    "microsoft-syd07-kemps-creek": "microsoft-kemps-creek-b2",
    "stockland-edgeconnex-davis-road": "stockland-davis-road",
}

# Rows needing a human decision on scope (cutoff date or 5 MW floor)
REVIEW = {
    "cdc-ec1": "completion vs 2018-09-01 cutoff unconfirmed",
    "cdc-fy1": "likely completed before 2018-09-01",
    "cdc-fyshwick-fy2": "completed 2018, month unknown vs cutoff",
    "airtrunk-mel1-building1": "established 2017, likely pre-cutoff",
    "digitalrealty-syd11": "completed 2018, month unknown vs cutoff",
    "pulse-tw-dc1": "2018 opening month unknown; MW 7 vs 2.5",
    "equinix-pe3": "may be under 5 MW",
    "equinix-me2": "no MW published; may be under 5 MW or pre-cutoff",
    "nextdc-d1": "designed 7 MW, built ~1 MW",
    "digico-bne2": "6 MW design, ~1.7 MW installed",
    "dca-pier-perth": "aggregator-only source",
    "aws-smeaton-grange-station": "aggregator-only source",
    "greensquaredc-wai1-b1": "approval may have lapsed",
    "greensquaredc-wai1-b2": "approval may have lapsed",
    "stack-per01a": "approved 2022, never built; may have lapsed",
    "stack-per02": "approved 2022, never built; may have lapsed",
    "stockland-athena": "AWS link from aggregator only",
    "microsoft-kemps-creek-b2": "operators file SYD07 (96 MW) mapped here; check vs B1",
    "cdc-hume-hu6": "DA lodged Oct 2024, approval not found",
    "nextdc-b2-stage2": "DA decision not confirmed; may be fit-out only",
}

def read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def norm(v):
    return (v or "").strip()

rows = {}
order = []
state_files = [p for p in sorted(glob.glob(os.path.join(CAND, "*.csv")))
               if "excluded" not in p and not p.endswith("operators.csv")]
for p in state_files:
    for r in read(p):
        r = {c: norm(r.get(c)) for c in COLS}
        r["conflicts"] = ""
        r["found_by"] = os.path.basename(p)[:-4]
        rows[r["id"]] = r
        order.append(r["id"])

for r in read(os.path.join(CAND, "operators.csv")):
    r = {c: norm(r.get(c)) for c in COLS}
    cid = ALIAS.get(r["id"], r["id"])
    if cid not in rows:
        r["conflicts"] = ""
        r["found_by"] = "operators"
        r["id"] = cid
        rows[cid] = r
        order.append(cid)
        continue
    base = rows[cid]
    base["found_by"] += "+operators"
    diffs = []
    for c in ["status","mw_it","year_complete","suburb","planning_ref"]:
        a, b = base[c], r[c]
        if not a and b:
            base[c] = b
        elif a and b and a.lower() != b.lower():
            diffs.append(f"{c}: {a} vs {b}")
    for c in ["address"]:
        if not base[c] and r[c]:
            base[c] = r[c]
    srcs = [s.strip() for s in (base["sources"] + ";" + r["sources"]).split(";") if s.strip()]
    base["sources"] = ";".join(dict.fromkeys(srcs))
    if r["notes"]:
        base["notes"] = (base["notes"] + " | ops: " + r["notes"]).strip(" |")
    if diffs:
        base["conflicts"] = "; ".join(diffs)

# Operators file gave Davis Road SSD-10330, which is CDC EC4's number; drop it
if rows.get("stockland-davis-road", {}).get("planning_ref") == "SSD-10330":
    rows["stockland-davis-road"]["planning_ref"] = ""
    rows["stockland-davis-road"]["notes"] += " | SSD-10330 in operators file belongs to CDC EC4, removed"

# Special case: operators SYD2 campus row double counts initial + expansion
if "airtrunk-syd2" in rows:
    rows["airtrunk-syd2"]["conflicts"] = re.sub(r"mw_it: 50 vs 158;? ?", "",
        rows["airtrunk-syd2"]["conflicts"]).strip("; ")
    rows["airtrunk-syd2"]["notes"] += " | 158 MW in operators file is whole campus incl. expansion row"

out_cols = COLS + ["conflicts", "review", "found_by"]
with open(os.path.join(HERE, "master.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=out_cols)
    w.writeheader()
    for i in sorted(order, key=lambda k: (rows[k]["state"], rows[k]["operator"].lower(), k)):
        r = rows[i]
        r["review"] = REVIEW.get(i, "")
        w.writerow({c: r.get(c, "") for c in out_cols})

# Excluded: concatenate with source file
ex = []
for p in sorted(glob.glob(os.path.join(CAND, "*_excluded.csv"))):
    for r in read(p):
        r = {k: norm(v) for k, v in r.items() if k}
        r["found_by"] = os.path.basename(p).replace("_excluded.csv", "")
        ex.append(r)
with open(os.path.join(HERE, "excluded.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["name","operator","state","suburb","reason","sources","found_by"],
                       extrasaction="ignore")
    w.writeheader()
    w.writerows(ex)

print(len(order), "master rows;", len(ex), "excluded rows")
