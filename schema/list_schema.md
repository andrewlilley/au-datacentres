# Master list schema (list/master.csv)

Scope
- Australian data centre facilities, >= 5 MW IT capacity (design/ultimate for that building or phase).
- One row per building or phase (e.g. NextDC S1, S2, S3 are separate rows).
- Status in scope:
  - `operational` — completed/commissioned on or after 2018-09-01
  - `under_construction`
  - `approved` — planning approval (DA/SSD/permit) granted, construction not started
- Also listed but not in scope:
  - `withdrawn` — application withdrawn (or approval surrendered) before construction; kept so the record and its sources are not lost. Exclude from in-scope counts.
- Out of scope: facilities completed before 2018-09-01 (unless a new in-scope phase/building), sub-5 MW sites, lodged-but-undetermined or merely announced projects (record these in `list/excluded.csv` with a reason).

Columns (candidate files use the same columns)
| column | notes |
|---|---|
| id | slug: `operator-sitecode`, lowercase, hyphens, e.g. `nextdc-s3`, `airtrunk-syd1-phase2` |
| name | public facility name |
| operator | owner/operator brand |
| state | NSW, VIC, QLD, WA, SA, TAS, ACT, NT |
| suburb | |
| address | street address if public |
| status | operational / under_construction / approved / withdrawn |
| mw_it | planned IT capacity for this building/phase, MW (number, blank if unknown) |
| year_complete | year completed or expected |
| planning_ref | DA / SSD / permit number if known |
| confidence | high / medium / low that it belongs on the list |
| sources | semicolon-separated URLs |
| notes | anything useful (campus, phase, parent project, ambiguity) |
