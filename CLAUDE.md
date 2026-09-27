# Instructions for Claude sessions working on this repo

This repo builds a database of Australian data centres (>= 5 MW; completed
since 2016-01-01, under construction, or planning-approved). Read
`README.md`, `schema/list_schema.md` and `schema/facility_schema.md` first.

## Phase 2b: 2016 cutoff extension (current phase)

On 2026-09-27 the completion cutoff moved from 2018-09-01 back to
2016-01-01 (the 5 MW floor is unchanged). Batches 1-4 are done. One session
does this phase, in two steps:

1. **Collect** `list/batches/batch5_2016_2018.txt` exactly as in Phase 2
   below (about 5 facilities; check each against the 5 MW floor).
2. **Discover** facilities completed 2016-01-01 to 2018-08-31 that are
   missing from `list/master.csv`. The original discovery only logged
   older sites incidentally. Check `list/excluded.csv` first, then operator
   histories and 2016-2018 news. Unverified leads to check (from memory, not
   sourced; confirm or discard each): Equinix SY4 (Alexandria), Equinix SY6,
   Global Switch Sydney East later stages, Macquarie Intellicentre 2,
   Digital Realty MEL10/MEL12 (Deer Park), NEXTDC S2 (confirm 2018 vs 2020
   completion), Metronode/Leading Edge-era builds, Vocus builds, Canberra
   and Perth colo expansions. Add confirmed ones to `list/master.csv`
   (`found_by` = `discovery-2016`), create their facility folders, and log
   rejects in `list/excluded.csv` with a reason.

Do not re-run `list/merge.py`; `master.csv` is now edited by hand.

Pipeline statuses (added 2026-09-28): `lodged` and `announced` rows in
`master.csv` are the undetermined and announced projects moved out of
`excluded.csv` (duplicates merged). Their facility folders are minimal:
suburb-centroid location and the discovery sources only. They have not had
Phase 2 collection; a future batch can fill them. Promote a row to `approved`
only on evidence of a planning decision.

## Phase 2: per-facility collection (done for batches 1-4)

The facility list is `list/master.csv`. It is split into batches in
`list/batches/*.txt` (one facility id per line). Each cloud session has a
cap of 200 web searches, so **one session handles one batch**.

For each facility id in your batch, fill `facilities/<id>/data.json` and
`facilities/<id>/sources.md` following `schema/facility_schema.md`.

Fields wanted: exact location (address, postcode, lat/lon), builder (head
contractor), developer, IT MW (and grid MW if stated), cost (AUD m), planning
authority/pathway/reference/dates/URL, construction jobs, operational jobs,
construction start and end dates.

Method
- Budget about 6 web searches per facility. Prefer WebFetch on known URLs
  (the `sources` column in master.csv, planning portal pages) over new searches.
- Best sources for cost and jobs: planning documents. NSW SSD pages on
  planningportal.nsw.gov.au/major-projects (EIS and Assessment Report state
  capital investment value and jobs); VIC DFP/permit decisions; WA DAP
  reports; ACT DA notices. Operator ASX releases and contractor press
  releases (e.g. Multiplex, Built, Lendlease, Richard Crookes, Hansen Yuncken,
  FDC, Kane, Icon) give builder and dates.
- Latitude/longitude: geocode from the street address or lot; say how in `note`.
- Jobs: record every jobs figure a source gives, tagged with `basis` and
  `scope` (see the Jobs section of `schema/facility_schema.md`). Peak, average,
  FTE-years and direct+indirect figures are different measures; never merge them.
- Never guess. Unknown = `null`. Estimates only with an explicit `note`.
- Where sources disagree, record the best-supported value and put the
  alternative in `note`.
- If research shows a facility is out of scope (completed before 2016, < 5 MW, not
  approved) or is a duplicate, still write its folder, set
  `"open_questions": ["scope: ..."]`, and do not delete it from master.csv.
- Use subagents to work several facilities in parallel (e.g. 4-6 agents,
  each with 4-6 ids), but remember they share the session's search cap.

When done with the batch
- Append a line per facility to `list/collection_log.csv`
  (id, batch, fields_filled, open_questions, date).
- Commit with a clear message and push to `main`. Pull/rebase first; other
  batches may have pushed.

## Later phases
- Phase 3 (built 2026-09-27): `site/build.py` rolls `list/master.csv` and
  `facilities/*/data.json` into `site/data.json` and `site/index.html` from
  `site/template.html`. Edit the template, never index.html. The GitHub
  Actions workflow rebuilds and deploys to Pages on every push to main.
- Phase 4: fact-check a sample against sources.
