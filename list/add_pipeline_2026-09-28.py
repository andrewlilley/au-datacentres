"""One-off (2026-09-28): move lodged/announced projects from excluded.csv into
master.csv with new statuses `lodged` and `announced`, merging duplicates, and
create minimal facility folders (suburb-centroid location) for the map.

Kept in the repo as a record of what was merged; do not re-run.
"""
import csv, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PC = os.environ["POSTCODES_CSV"]  # matthewproctor/australianpostcodes CSV

ex = list(csv.DictReader(open(f"{ROOT}/list/excluded.csv", encoding="utf-8")))
mrows = list(csv.DictReader(open(f"{ROOT}/list/master.csv", encoding="utf-8")))
mcols = list(mrows[0].keys())
ecols = list(ex[0].keys())

# (excluded row indices merged, id, name, operator, state, geocode suburb, status, mw, planning_ref, confidence)
L, A = "lodged", "announced"
MOVE = [
    # NSW
    ([0, 30], "nextdc-s5", "NEXTDC S5 Sydney", "NEXTDC", "NSW", "Macquarie Park", L, "80", "SSD-63168959", "high"),
    ([1, 31], "nextdc-s7", "NEXTDC S7 Sydney", "NEXTDC", "NSW", "Eastern Creek", L, "550", "", "medium"),
    ([2, 63], "airtrunk-mamre-road", "Mamre Road Data Centre Campus (AirTrunk SYD4)", "AirTrunk (ISPT site)", "NSW", "Kemps Creek", L, "1200", "SSD-92743706", "high"),
    ([4, 35], "cdc-kc1", "CDC Kemps Creek KC1", "CDC Data Centres", "NSW", "Kemps Creek", L, "144", "SSD-133677993", "high"),
    ([5, 37], "cdc-wagga", "CDC Wagga Wagga (Ashfords Road)", "CDC Data Centres", "NSW", "Gregadoo", L, "1400", "SSD-144289240", "high"),
    ([6, 47], "stack-syd01", "STACK SYD01 Erskine Park", "STACK Infrastructure", "NSW", "Erskine Park", L, "450", "SSD-82211208", "high"),
    ([7, 52], "microsoft-honeman-close", "Microsoft Honeman Close", "Microsoft", "NSW", "Huntingwood", L, "96", "SSD-58601963", "high"),
    ([8], "ispt-julius-avenue", "Julius Avenue Data Centre", "ISPT", "NSW", "Macquarie Park", L, "115.2", "SSD-80018208", "high"),
    ([9, 50], "goodman-project-mars", "Goodman Project Mars", "Goodman", "NSW", "Lane Cove West", L, "81", "SSD-82052708", "high"),
    ([10], "goodman-project-atlas", "Goodman Project Atlas", "Goodman", "NSW", "Eastern Creek", L, "", "SSD-101067971", "high"),
    ([11], "stockland-road-1", "Stockland Road 1 Data Centre", "Stockland", "NSW", "Macquarie Park", L, "34.3", "SSD-80814238", "high"),
    ([12, 56], "stockland-aldington-road", "90 Aldington Road (Kemps Creek)", "Stockland / Fife Capital (EdgeConneX)", "NSW", "Kemps Creek", L, "168", "", "medium"),
    ([13, 57], "stockland-project-a", "Stockland Project A (Macquarie Park)", "Stockland / EdgeConneX", "NSW", "Macquarie Park", L, "", "", "medium"),
    ([14], "greensquaredc-brookhollow", "GreenSquareDC Brookhollow Avenue Expansion", "GreenSquareDC", "NSW", "Norwest", L, "118.3", "SSD-81928961", "high"),
    ([15], "gateway-frederick-street", "Frederick Street Data Centre", "Gateway Capital", "NSW", "St Leonards", L, "81", "SSD-139545990", "high"),
    ([16], "knbdc-mamre-road", "Mamre Road Data Centre Campus (KNBDC)", "KNBDC", "NSW", "Orchard Hills", L, "", "", "low"),
    ([17], "aims-bella-vista", "Bella Vista Data Centre Campus", "AIMS Capital Management", "NSW", "Bella Vista", L, "", "", "low"),
    ([18], "lane-cove-dc-alliance", "Lane Cove Data Centre Development", "Lane Cove DC Alliance", "NSW", "Lane Cove West", L, "", "", "low"),
    ([40], "digitalrealty-syd13", "Digital Realty SYD13 (23-25 Waterloo Rd)", "Digital Realty", "NSW", "Macquarie Park", L, "70", "", "medium"),
    ([19, 74], "edgeconnex-macquarie-park", "EdgeConneX Macquarie Park SYD1", "EdgeConneX", "NSW", "Macquarie Park", A, "100", "", "low"),
    ([20], "markham-oriordan-street", "22 O'Riordan Street", "Markham Real Estate Partners", "NSW", "Alexandria", A, "38", "", "low"),
    ([46], "macquarie-sydney-150", "Macquarie Data Centres 150 MW Sydney facility", "Macquarie Data Centres", "NSW", "", A, "150", "", "low"),
    # VIC
    ([34, 105], "airtrunk-donnybrook-road", "45 Donnybrook Road campus (Mickleham)", "AirTrunk (reported)", "VIC", "Mickleham", L, "", "PA2604506", "medium"),
    ([51, 111], "goodman-mount-atkinson-road", "Goodman 433 Mount Atkinson Road", "Goodman", "VIC", "Truganina", L, "", "", "medium"),
    ([58, 109], "stockland-cherry-lane", "72-76 Cherry Lane / 413 Francis Street", "Stockland / EdgeConneX", "VIC", "Laverton North", L, "250", "", "medium"),
    ([108], "stockland-brooklyn", "Stockland Brooklyn Distribution Centre data centre", "Stockland", "VIC", "Brooklyn", L, "250", "", "medium"),
    ([59, 110], "greensquaredc-spotswood", "GreenSquareDC MEL1 Spotswood", "GreenSquareDC", "VIC", "Spotswood", L, "240", "", "medium"),
    ([67, 106], "zerra-campbellfield", "Zerra DC Melbourne Campus (former Ford site)", "Zerra DC", "VIC", "Campbellfield", L, "", "PA2604362", "medium"),
    ([68, 112], "galileo-clyde-north", "585 Berwick-Cranbourne Road", "Galileo Group (applicant)", "VIC", "Clyde North", L, "", "", "low"),
    ([113, 70], "centuria-dandenong-road", "Centuria 1822 Dandenong Road", "Centuria", "VIC", "Clayton", L, "40", "", "low"),
    ([107], "dover-sm1b", "Dover SM1B South Morang", "Dover DC", "VIC", "South Morang", L, "200", "", "medium"),
    ([104], "nextdc-m3-paramount-road", "NEXTDC M3 expansion (Paramount Road)", "NEXTDC", "VIC", "West Footscray", L, "", "PA2604231", "medium"),
    ([117], "aws-donnybrook-road", "AWS 55 Donnybrook Road", "Amazon Web Services", "VIC", "Mickleham", A, "", "", "low"),
    ([116, 54], "aws-ferris-road", "AWS 54-80 Ferris Road", "Amazon Web Services", "VIC", "Cobblebank", A, "", "", "low"),
    ([69, 120], "syncline-vic-ai-centre", "Victorian AI Centre", "Syncline Energy", "VIC", "Plumpton", A, "2400", "", "low"),
    ([114], "centuria-temple-drive", "Centuria 49 Temple Drive / 2 Keon Parade", "Centuria", "VIC", "Thomastown", A, "", "", "low"),
    ([115], "centuria-cawley-road", "Centuria 2-8 Cawley Road / 1 Hardie Road", "Centuria", "VIC", "Yarraville", A, "", "", "low"),
    ([32, 118], "nextdc-m5", "NEXTDC M5 Melbourne (Lovely Banks)", "NEXTDC", "VIC", "Lovely Banks", A, "1200", "", "medium"),
    ([121], "resetdata-ai-f1", "ResetData AI Factory AI-F1", "ResetData", "VIC", "Docklands", A, "", "", "low"),
    # QLD
    ([75, 66], "zerra-western-downs", "Western Downs Digital Park", "Zerra DC (WDDP Pty Ltd)", "QLD", "Kogan", L, "1440", "", "high"),
    ([76], "swanbank-six-leaf-street", "Swanbank data centre (Lot 5 Six Leaf Street)", "Northern Concept Swanb Pty Ltd", "QLD", "Swanbank", L, "", "2285/2026/MCU", "medium"),
    ([77, 29], "nextdc-gc1", "NEXTDC GC1 Gold Coast", "NEXTDC", "QLD", "Southport", A, "6", "", "medium"),
    ([164, 65], "supernode-brendale", "Supernode data centre campus", "Supernode (Quinbrook Infrastructure Partners)", "QLD", "Brendale", A, "500", "", "medium"),
    ([163], "digico-bne3", "DigiCo BNE3 Brisbane Airport", "DigiCo Infrastructure REIT", "QLD", "Brisbane Airport", A, "", "", "low"),
    # ACT
    ([85], "cdc-beard-be2", "CDC Beard 2 (BE2)", "CDC Data Centres", "ACT", "Beard", L, "", "DA 202645149", "high"),
    ([86, 49], "stack-can01", "STACK CAN01 Hume", "STACK Infrastructure", "ACT", "Hume", A, "28", "", "low"),
    # TAS
    ([92], "firmus-wesley-vale", "Firmus Wesley Vale", "Firmus Technologies", "TAS", "Wesley Vale", L, "52", "", "medium"),
    ([91], "firmus-southgate-stage2", "Firmus Project Southgate Stage 2", "Firmus Technologies", "TAS", "St Leonards", A, "300", "", "medium"),
    # SA
    ([95, 64], "iren-bundey", "IREN Bundey AI campus", "IREN", "SA", "Bundey", A, "800", "", "high"),
    ([96], "firmus-tailem-bend", "Firmus Tailem Bend AI Factory", "Firmus Technologies", "SA", "Tailem Bend", A, "", "", "medium"),
    ([97], "skylab-cooke-plains", "Skylab Australia Cooke Plains", "Skylab Australia", "SA", "Cooke Plains", A, "800", "", "medium"),
    ([98], "aurora-port-augusta", "Aurora Energy Precinct AI Campus", "1414 Degrees / unnamed developer", "SA", "Port Augusta", A, "", "", "low"),
    ([45], "digico-adl1-expansion", "DigiCo ADL1 expansion", "DigiCo Infrastructure REIT", "SA", "Edinburgh", A, "15", "", "low"),
    # NT
    ([102], "dci-drw01", "DCI DRW01 Darwin", "DCI Data Centers", "NT", "Wishart", A, "10", "", "low"),
    ([103], "beetaloo-weddell", "Beetaloo Digital Weddell campus", "Beetaloo Energy", "NT", "Weddell", A, "2000", "", "medium"),
    # WA
    ([129, 36], "cdc-hazelmere", "CDC Hazelmere Campus", "CDC Data Centres", "WA", "Hazelmere", A, "192", "", "medium"),
    ([131], "gingerah-meridien", "Project Meridien (Broome)", "Gingerah Energy", "WA", "Broome", A, "240", "", "low"),
]

# Suburb centroids
cent = {}
for r in csv.DictReader(open(PC, encoding="utf-8")):
    try:
        lat, lon = float(r["Lat_precise"] or r["lat"]), float(r["Long_precise"] or r["long"])
    except ValueError:
        continue
    if lat == 0:
        continue
    cent.setdefault((r["locality"].upper(), r["state"]), (lat, lon, r["postcode"]))

ids = {r["id"] for r in mrows}
used = set()
for idx, fid, name, op, state, sub, status, mw, ref, conf in MOVE:
    assert fid not in ids, fid
    for i in idx:
        assert i not in used, (i, fid)
        used.add(i)
    rows = [ex[i] for i in idx]
    srcs = ";".join(dict.fromkeys(s for r in rows for s in r["sources"].split(";") if s.strip()))
    notes = " | ".join(r["reason"] for r in rows)
    if len(idx) > 1:
        notes += f" | merged {len(idx)} duplicate excluded rows (2026-09-28)"
    mrows.append({c: "" for c in mcols} | {
        "id": fid, "name": name, "operator": op, "state": state, "suburb": sub,
        "status": status, "mw_it": mw, "planning_ref": ref, "confidence": conf,
        "sources": srcs, "notes": notes, "found_by": "excluded->pipeline 2026-09-28"})
    # minimal facility record
    c = cent.get((sub.upper(), state)) if sub else None
    d = f"{ROOT}/facilities/{fid}"
    if os.path.exists(f"{d}/data.json"):
        # already researched in Phase 2 (then excluded): keep the record, update status only
        rec = json.load(open(f"{d}/data.json", encoding="utf-8"))
        rec["status"] = status
        rec.setdefault("open_questions", []).append(f"status set to {status} on 2026-09-28 (pipeline listing)")
        json.dump(rec, open(f"{d}/data.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        continue
    os.makedirs(d, exist_ok=True)
    loc_note = (f"approximate: centroid of {sub} {state} (postcode {c[2]}) from matthewproctor/australianpostcodes; site location not geocoded"
                if c else "no location")
    nil = {"value": None, "source": None, "note": ""}
    rec = {
        "id": fid, "name": name, "operator": op, "status": status,
        "location": {"address": dict(nil), "suburb": sub, "state": state,
                     "postcode": {"value": c[2] if c else None, "source": None, "note": "suburb postcode" if c else ""},
                     "lat": {"value": round(c[0], 4) if c else None, "source": None, "note": loc_note},
                     "lon": {"value": round(c[1], 4) if c else None, "source": None, "note": ""}},
        "builder": dict(nil), "developer": {"value": op, "source": 1, "note": ""},
        "mw_it": {"value": float(mw) if mw else None, "source": 1 if mw else None,
                  "note": "headline figure from announcement or application; may be campus total or grid demand, not verified as IT load" if mw else ""},
        "mw_grid": dict(nil), "cost_aud_m": dict(nil),
        "planning": {"authority": dict(nil), "pathway": dict(nil),
                     "reference": {"value": ref or None, "source": 1 if ref else None, "note": ""},
                     "lodged": dict(nil), "determined": dict(nil), "url": None},
        "jobs_construction": dict(nil), "jobs_construction_other": [],
        "jobs_operational": dict(nil), "jobs_operational_other": [],
        "construction_start": dict(nil), "construction_end": dict(nil),
        "last_checked": "2026-09-28",
        "open_questions": ["pipeline record from discovery only; per-facility collection not yet done"],
    }
    json.dump(rec, open(f"{d}/data.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    with open(f"{d}/sources.md", "w", encoding="utf-8") as f:
        f.write(f"# Sources: {fid}\n\nFrom discovery agents (2026-09-27); status as found then: {notes}\n\n")
        for n, u in enumerate(srcs.split(";"), 1):
            if u.strip():
                f.write(f"{n}. {u.strip()}\n")
    if not c and sub:
        print("no centroid:", fid, sub, state)

# Rows left in excluded: annotate obvious duplicates of master rows
DUP_OF_MASTER = {55: "stockland-athena", 71: "pgim-truganina-b1", 61: "firmus-southgate-stage1", 48: "stack-per01a / stack-per02"}
kept = []
for i, r in enumerate(ex):
    if i in used:
        continue
    if i in DUP_OF_MASTER:
        r["reason"] += f" | duplicate of master row {DUP_OF_MASTER[i]} (2026-09-28)"
    kept.append(r)

w = csv.DictWriter(open(f"{ROOT}/list/master.csv", "w", newline="", encoding="utf-8"), fieldnames=mcols)
w.writeheader(); w.writerows(mrows)
w = csv.DictWriter(open(f"{ROOT}/list/excluded.csv", "w", newline="", encoding="utf-8"), fieldnames=ecols)
w.writeheader(); w.writerows(kept)
print(len(MOVE), "pipeline rows added from", len(used), "excluded rows;", len(mrows), "master;", len(kept), "excluded")
