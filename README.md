# Australian data centres database

Every data centre building or phase in Australia of 5 MW or more that was
completed since January 2016, is under construction, or has planning
approval.

- `schema/` — scope rules and field definitions
- `list/candidates/` — raw lists from the discovery agents (by state, plus a national operator sweep)
- `list/merge.py` — merges candidates into `list/master.csv` and `list/excluded.csv`
- `list/master.csv` — the working facility list; `conflicts` and `review` flag rows needing a decision
- `facilities/<id>/` — per-facility data and sources (see `schema/facility_schema.md`)
- `site/` — the web page: `python3 site/build.py` regenerates `index.html` from `template.html` and the facility records; deployed to GitHub Pages by `.github/workflows/pages.yml`
