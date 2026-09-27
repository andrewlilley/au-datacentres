"""Build site/index.html from list/master.csv and facilities/*/data.json.

Run from anywhere:  python3 site/build.py
Writes site/data.json (the rolled-up dataset) and site/index.html
(template.html with the dataset and coastline inlined, so the page is a
single self-contained file that works on GitHub Pages or as an artifact).
"""
import csv, json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def v(obj):
    """Unwrap {'value':..} objects; pass plain values through."""
    if isinstance(obj, dict):
        return obj.get("value")
    return obj


def vn(obj):
    if isinstance(obj, dict):
        return obj.get("note") or ""
    return ""


def num(x):
    try:
        return float(x) if x not in (None, "") else None
    except (TypeError, ValueError):
        return None


def jobs(obj):
    if not isinstance(obj, dict) or obj.get("value") is None:
        return None
    return {k: obj.get(k) for k in ("value", "basis", "scope", "note", "source")}


def date(obj):
    if not isinstance(obj, dict):
        return None
    return {"value": obj.get("value"), "precision": obj.get("precision"), "note": obj.get("note") or ""}


SRC_LINE = re.compile(r"^\s*(?:[-*]\s*)?\[?(\d+)[.)\]]\s+(.*)$")
URL = re.compile(r"https?://[^\s<>\"')\]]+")


def sources(path):
    """Parse numbered source lines; the formats vary by session, so take the
    first URL on the line and keep the rest as the description."""
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        m = SRC_LINE.match(line)
        if not m:
            continue
        text = m.group(2).strip()
        u = URL.search(text)
        url = u.group(0).rstrip(".,;:") if u else None
        desc = (text[:u.start()] + text[u.end():]) if u else text
        desc = re.sub(r"\s*[—–-]\s*[—–-]\s*", " — ", desc)
        desc = re.sub(r"^[\s—–:,-]+|[\s—–:,-]+$", "", desc)
        desc = re.sub(r"\s{2,}", " ", desc)
        out.append({"n": int(m.group(1)), "url": url, "desc": desc})
    return out


def main():
    master = list(csv.DictReader(open(os.path.join(ROOT, "list", "master.csv"), encoding="utf-8")))
    recs = []
    for row in master:
        fid = row["id"]
        p = os.path.join(ROOT, "facilities", fid, "data.json")
        d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        loc = d.get("location", {})
        pl = d.get("planning", {})
        recs.append({
            "id": fid,
            "name": d.get("name") or row["name"],
            "operator": d.get("operator") or row["operator"],
            "state": loc.get("state") or row["state"],
            "suburb": loc.get("suburb") or row["suburb"],
            "status": row["status"],  # master.csv is canonical for status
            "address": v(loc.get("address")) or row["address"],
            "postcode": v(loc.get("postcode")),
            "lat": num(v(loc.get("lat"))),
            "lon": num(v(loc.get("lon"))),
            "geo_note": vn(loc.get("lat")),
            "mw": num(v(d.get("mw_it"))) if d else num(row["mw_it"]),
            "mw_note": vn(d.get("mw_it")),
            "mw_grid": num(v(d.get("mw_grid"))),
            "mw_grid_note": vn(d.get("mw_grid")),
            "cost": num(v(d.get("cost_aud_m"))),
            "cost_note": vn(d.get("cost_aud_m")),
            "builder": v(d.get("builder")),
            "builder_note": vn(d.get("builder")),
            "developer": v(d.get("developer")),
            "planning": {
                "authority": v(pl.get("authority")),
                "pathway": v(pl.get("pathway")),
                "ref": v(pl.get("reference")) or row["planning_ref"] or None,
                "lodged": v(pl.get("lodged")),
                "determined": v(pl.get("determined")),
                "url": pl.get("url") if isinstance(pl.get("url"), str) else v(pl.get("url")),
            },
            "jobs_c": jobs(d.get("jobs_construction")),
            "jobs_c_other": [j for j in (jobs(x) for x in d.get("jobs_construction_other") or []) if j],
            "jobs_o": jobs(d.get("jobs_operational")),
            "jobs_o_other": [j for j in (jobs(x) for x in d.get("jobs_operational_other") or []) if j],
            "start": date(d.get("construction_start")),
            "end": date(d.get("construction_end")),
            "year": row["year_complete"] or None,
            "confidence": row["confidence"],
            "review": row.get("review") or "",
            "questions": d.get("open_questions") or [],
            "checked": d.get("last_checked"),
            "sources": sources(os.path.join(ROOT, "facilities", fid, "sources.md")),
        })

    built = datetime.date.today().isoformat()
    payload = {"built": built, "facilities": recs}
    json.dump(payload, open(os.path.join(SITE, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    coast = open(os.path.join(SITE, "australia.json"), encoding="utf-8").read()
    tpl = open(os.path.join(SITE, "template.html"), encoding="utf-8").read()
    data_js = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = tpl.replace("/*__DATA__*/null", data_js).replace("/*__COAST__*/null", coast)
    # site/index.html: full document for GitHub Pages
    full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '</head>\n<body>\n' + html + '\n</body>\n</html>\n')
    open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(full)
    # fragment for publishing as a claude.ai artifact (skeleton added at publish)
    frag = os.environ.get("ARTIFACT_OUT")
    if frag:
        open(frag, "w", encoding="utf-8").write(html)
    print(f"{len(recs)} facilities -> site/index.html ({len(html)//1024} KB)")


if __name__ == "__main__":
    main()
