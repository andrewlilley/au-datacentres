# Instructions for Claude sessions working on this repo

This repo builds a database of Australian data centres (>= 5 MW; completed
since 2018-09-01, under construction, or planning-approved). Read
`README.md`, `schema/list_schema.md` and `schema/facility_schema.md` first.

## Phase 2: per-facility collection (current phase)

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
- Never guess. Unknown = `null`. Estimates only with an explicit `note`.
- Where sources disagree, record the best-supported value and put the
  alternative in `note`.
- If research shows a facility is out of scope (pre-2018, < 5 MW, not
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
- Phase 3: build `site/` (static searchable table + map from facilities/*/data.json).
- Phase 4: fact-check a sample against sources.
