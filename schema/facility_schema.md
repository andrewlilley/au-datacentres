# Per-facility record (facilities/<id>/)

Each facility in `list/master.csv` gets a folder `facilities/<id>/` with:

- `data.json` — the structured record below
- `sources.md` — every source used, with URL, access date and what it supports
- `docs/` — optional: saved planning documents (PDF excerpts, EIS summaries)

## data.json

Example values below are illustrative only, not facts about the facility.

Every value field is an object `{ "value": ..., "source": <n>, "note": "" }`
where `source` indexes the numbered list in `sources.md`. Use `null` value
when not found. Never estimate without saying so in `note`.

```json
{
  "id": "nextdc-s4",
  "name": "NEXTDC S4 Sydney",
  "operator": "NEXTDC",
  "status": "under_construction",
  "location": {
    "address": {"value": "...", "source": 1},
    "suburb": "Horsley Park",
    "state": "NSW",
    "postcode": {"value": "2175", "source": 1},
    "lat": {"value": -33.84, "source": 2, "note": "geocoded from lot/address"},
    "lon": {"value": 150.85, "source": 2}
  },
  "builder": {"value": "Multiplex", "source": 3, "note": "head contractor"},
  "developer": {"value": "NEXTDC", "source": 1},
  "mw_it": {"value": 300, "source": 1, "note": "IT load at full build"},
  "mw_grid": {"value": null, "source": null, "note": "total facility / grid demand if stated"},
  "cost_aud_m": {"value": 1500, "source": 1, "note": "capital investment value in EIS"},
  "planning": {
    "authority": {"value": "NSW DPHI", "source": 1},
    "pathway": {"value": "SSD", "source": 1},
    "reference": {"value": "SSD-63741210", "source": 1},
    "lodged": {"value": "2023-11-01", "source": 1},
    "determined": {"value": "2024-10-15", "source": 1},
    "url": "https://..."
  },
  "jobs_construction": {"value": 800, "source": 1, "basis": "peak", "scope": "direct",
                        "note": "EIS: 'up to 800 workers at peak'"},
  "jobs_construction_other": [
    {"value": 1200, "source": 5, "basis": "fte_years", "scope": "direct", "note": "economic impact appendix"},
    {"value": 2100, "source": 5, "basis": "fte_years", "scope": "direct_indirect", "note": ""}
  ],
  "jobs_operational": {"value": 150, "source": 1, "basis": "ongoing_headcount", "scope": "direct"},
  "jobs_operational_other": [],
  "construction_start": {"value": "2024-12", "source": 4, "precision": "month"},
  "construction_end": {"value": "2026-06", "source": 4, "precision": "month", "note": "expected"},
  "last_checked": "2026-09-27",
  "open_questions": []
}
```

### Jobs

Planning documents report jobs on different bases, and they are not comparable.
Record **every** figure a source gives, each tagged:

- `basis`: `peak` (max on-site workforce), `average` (average workforce over
  the build), `total_headcount` (distinct workers over the build), `fte_years`
  (full-time-equivalent job-years), `ongoing_headcount` (operational staff),
  `unstated` (source gives a number with no definition; quote it in `note`)
- `scope`: `direct` (on-site / by the project), `direct_indirect` (includes
  flow-on or supply-chain jobs), `unstated`

Put the direct peak figure (construction) or direct ongoing figure
(operational) in the primary field when available; everything else goes in the
`_other` arrays. Quote the source's exact wording in `note`.

Dates are ISO strings at the precision known (`YYYY`, `YYYY-MM`, `YYYY-MM-DD`).
Costs in AUD millions, nominal, as stated by the source.
