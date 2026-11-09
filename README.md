# languageofcomputation-week4-assignment

## Running the tests

These commands assume a PowerShell terminal, starting from having no
terminal open at all, same as the other READMEs in this project.

**Install what the tests need** (pytest; a one-time step):

```powershell
cd "C:\Users\Kristina\Workspace\language-of-computation\week4-assignment"
python -m pip install pytest
```

**Run the tests:**

```powershell
cd "C:\Users\Kristina\Workspace\language-of-computation\week4-assignment"
python -m pytest
```

This runs both `test_ingest.py` (against the original `rules.md` +
`ingest.py` in this folder) and `test_ingest_agreed.py` (against
`rules-agreed.md` + `week3-assignment/ingest.py`) — pytest finds any file
named `test_*.py` in the folder automatically. Add `-v` to see every test
by name instead of just a pass/fail summary line.

## Running `ingest.py` on the CSVs in this folder

```powershell
cd "C:\Users\Kristina\Workspace\language-of-computation\week4-assignment"
python ingest.py
```

Run that same command a second time to ingest `books.csv` again (it's
safe to re-run — see `rules.md` section 3 for what should happen to
already-loaded rows).

```powershell
python ingest.py
```

Then ingest `books-batch2.csv`. `CSV_FILENAME` is a fixed constant in
`ingest.py`, not a command-line argument (by design — see the script's own
docstring), so this one-liner points it at the other file without editing
`ingest.py`:

```powershell
python -c "import ingest; ingest.run('books-batch2.csv', 'books.db', 'ingestion-log.json')"
```

Each of these writes to `books.db` and appends an entry to
`ingestion-log.json` in this folder, same as `week3-assignment`'s script.

## Week 4: comparing rules.md across partners

This repo is shared by a group of partners (Kristina, Anthony, Abigail) who
each wrote their own `rules.md` independently in week 3. Week 4 starts with
agreeing on one shared `rules.md`, which requires finding out where the
partners' rules actually agree, disagree, or only one of them addresses a
given decision at all.

### Session log

- Cloned this repo locally and created an `assignment` branch off `main`.
- Confirmed `rules.md` in this repo is Kristina's own week3 rules
  (identical to `week3-assignment/rules.md` in the sibling project folder).
- Pulled Anthony's actual `rules.md` from his repo
  (`fme5034/language-of-computation-week3-assignment`, `assignment`
  branch) — the file previously saved locally as `rules (1).md` turned out
  to be a duplicate of Kristina's file, not Anthony's.
- Pulled Abigail's actual `rules.md` from her repo
  (`ACRuby/language-of-computation-week3-assignment`, `assignment` branch),
  saved locally as `rules-Abigail.md`.
- Wrote [`rules-comparison.md`](rules-comparison.md): a decision-by-decision,
  three-way comparison of Kristina's, Anthony's, and Abigail's rules (ISBN
  problem handling, book identity, re-arrival/update behavior, report
  requirements, schema, plus Abigail's unique external-lookup/human-approval
  workflow), tagged all-agree / all-differ / 2-agree-1-differs / 2-agree-1-
  silent / 2-disagree-1-silent / 1-only, with summary counts (63 total
  decisions identified; 40 overlapping, 23 unique — 2 Kristina, 4 Anthony,
  17 Abigail) and a prioritized list of what needs deciding in the group
  meeting, led by the biggest split: Kristina/Anthony use ISBN as the book's
  identity, Abigail uses `goodreads_book_id`.
- Added both example-table walkthroughs: Kristina's 16 examples run through
  Anthony's and Abigail's rules, and Abigail's 29 examples run through
  Kristina's and Anthony's rules (Anthony has no example table of his own).
  10 of Kristina's 16 and 12 of Abigail's 29 land differently depending on
  whose rules ingest the file — most strikingly, examples Ab#23/Ab#24 show
  the `goodreads_book_id`-vs-ISBN identity split catching (or missing) a
  conflict in opposite ways.
- Added `goodreads_book_id`/`identity_key` indexes to
  `week3-assignment/ingest.py` and the live `books.db` (the column already
  existed and was fully populated; it just had no index).
- After the 2026-11-06 meeting, read the group's decisions back out of the
  filled-in working doc (`Week 4 Rules-Merge Meeting ... AR.docx`) and wrote
  [`rules-agreed.md`](rules-agreed.md) — the one shared `rules.md` for the
  group, merged from all seven decisions plus the Open Items vote. It flags
  one real contradiction in the recorded decisions rather than silently
  resolving it: Decision 7 adopts Abigail's FAILED-means-nothing-saved
  status, but the Open Items vote separately said to skip her atomicity
  guarantee.
- Wrote [`erd.md`](erd.md): a Mermaid ERD for the agreed schema (Decision
  5 — Kristina's `books`/`warnings` tables, `goodreads_book_id` as the new
  identity field), annotated with which columns are freely updatable
  ("volatile metadata") versus frozen-once-set ("identity-relevant") per
  Decision 4.
- Resolved the Decision 7 / atomicity contradiction in `rules-agreed.md`
  rather than leaving it open: the specific "skip atomicity" vote wins over
  the broader "adopt Abby's reporting" decision it was nested inside, so
  `FAILED` is a status label only, and the report says so explicitly.
- Implemented `rules-agreed.md` in `week3-assignment/ingest.py`: identity
  is now `goodreads_book_id`; bad-isolated-ISBN problems load with a
  warning instead of rejecting; empty ISBNs load with a warning instead of
  silently; updates split into always-free (volatile metadata) vs.
  reject-on-conflict (identity-relevant fields); added the 978/979 prefix
  check, Anthony's reverse ISBN-10 derivation and stripped-978 repair, and
  comma-separated multi-reason warnings; added the SUCCESS / COMPLETED
  WITH ISSUES / FAILED status to both the run summary and `report.html`.
  Found and fixed a real bug along the way: `isbn13` wasn't being derived
  when it was simply blank (only when scientific-notation-corrupted),
  which silently broke the ISBN-collision check — confirmed fixed by
  reproducing the `Angels & Demons` / `Paper Moons` collision from
  `books-batch2.csv`, which now correctly rejects. Reset and rebuilt
  `books.db`/`ingestion-log.json` from scratch to get a clean result
  (10,013 books, down from 10,738 under the old per-row ISBN identity,
  since `goodreads_book_id` now actually deduplicates no-ISBN books).
- Built a second suite, `test_ingest_agreed.py`, against `rules-agreed.md`
  and `week3-assignment/ingest.py` (loaded under a distinct module name,
  `ingest_agreed`, so it can't collide with `test_ingest.py`'s `import
  ingest` if both run in one pytest session). Reused the same 16 examples
  from the original rules.md's table, but with expected outcomes
  recomputed for the agreed rules — several changed materially: isbn13 is
  now derived even when it was simply blank (examples #1/#2/#9), the
  reverse ISBN-10 derivation now fills in `isbn` for #8/#9/#14, #10 now
  warns instead of loading silently, #11 now reports a comma-separated
  `bad-prefix,bad-checksum`, and #13's collision is keyed on
  `goodreads_book_id` instead of title. 20/20 pass; both suites together
  (40 tests) also pass with no module-name collision.
- Added a "Running the tests" / "Running `ingest.py` on the CSVs in this
  folder" section to this README with the exact `pip install`/`pytest`
  commands and the exact commands to ingest `books.csv`, `books.csv`
  again, and `books-batch2.csv` against this folder's own `ingest.py` —
  then actually ran all three to confirm them. Result: 10,000 loaded from
  the first `books.csv` run, 723 more loaded (not skipped) on the second
  run of the same file — expected under the original rules.md, since a
  book with no usable ISBN is never matched and reloads every run — then
  15 loaded / 4 updated / 11 skipped / 1 rejected (the Angels & Demons /
  Paper Moons collision) from `books-batch2.csv`. 10,738 total rows,
  matching 10000 + 723 + 15.
- Wrote [`run-instructions.md`](run-instructions.md): the week4 deliverable
  explaining `ingest.py`'s parameters (all constants at the top of the
  file, no CLI flags), how to run it against one or both CSVs, how to read
  `report.html`'s new status pills, and what each report number means
  under the agreed rules.