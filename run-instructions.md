# Running the pipeline and reading the report

This is the one-stop reference for running `ingest.py` against the
**agreed rules** ([`rules-agreed.md`](rules-agreed.md)) and reading its
output. The code itself lives in `week3-assignment/` (that's where the
CSVs, the database, and the script are) — this document is the
week4-assignment deliverable that explains how to drive it.

## Parameters

`ingest.py` takes **no command-line parameters**. Every "parameter" is a
constant at the top of the file instead — by design, per the script's own
docstring, so that a given run is always exactly reproducible from the
file alone, with no way to silently pass the wrong flag on the command
line.

| Constant | Default | What it controls |
|---|---|---|
| `CSV_FILENAME` | `"books.csv"` | The input file to ingest, resolved relative to `week3-assignment/`. |
| `DB_FILENAME` | `"books.db"` | The SQLite database written to / read from. |
| `LOG_FILENAME` | `"ingestion-log.json"` | Where each run's report entry is appended (never overwritten). |

To ingest a different file, open `week3-assignment/ingest.py` in a text
editor, change `CSV_FILENAME` near the top, save, and run it again — see
below.

## Running it

```powershell
cd "C:\Users\Kristina\Workspace\language-of-computation\week3-assignment"
python ingest.py
```

This is safe to run as many times as you like: it updates `books.db` and
appends a new entry to `ingestion-log.json` each time, rather than
overwriting anything.

To ingest both `books.csv` and `books-batch2.csv` in one go, without
hand-editing `CSV_FILENAME` twice:

```powershell
python -c "import ingest, os; here = os.path.dirname(os.path.abspath('ingest.py')); [ingest.run(os.path.join(here, f), os.path.join(here, 'books.db'), os.path.join(here, 'ingestion-log.json')) for f in ['books.csv', 'books-batch2.csv']]"
```

Either way, it prints one summary line when it finishes, e.g.:

```
status=COMPLETED WITH ISSUES rows_read=10000 loaded=10000 updated=0 skipped=0 rejected=0 rows_with_warning=703
```

`status` is the three-tier run verdict from Decision 7:

- **SUCCESS** — every row loaded with no warnings.
- **COMPLETED WITH ISSUES** — the run finished, but something was rejected
  or carries a warning.
- **FAILED** — the file couldn't be read, the header didn't match, or an
  error stopped the run partway through. This is a status label, not a
  rollback guarantee — see `rules-agreed.md`'s *Resolved conflict* section
  for exactly what it does and doesn't promise about `books.db`.

## Reading the report

`week3-assignment/report.html` reads `ingestion-log.json` directly in your
browser — nothing is uploaded anywhere.

1. In File Explorer, go to `week3-assignment/` and double-click
   `report.html` (or run `start report.html` from the same terminal).
2. Click **"Open ingestion-log.json"** and select that file from the same
   folder.
3. Each run appears as a card, newest first, with a colored status pill
   (green SUCCESS / amber COMPLETED WITH ISSUES / red FAILED) plus counts
   for read / loaded / updated / skipped / rejected / warned. Click a card
   to expand it into the full row-by-row detail: every rejected or skipped
   row with its reason, and every updated row's old → new diff.

Older log entries from before this update (predating the three-tier
status) simply show no status pill rather than a guessed one.

## What the numbers mean, per the agreed rules

- **rejected** rows are rejected for exactly two reasons now:
  `structural-parse-error` (the CSV row itself didn't parse),
  `isbn-collision` (a valid ISBN already belongs to a different
  `goodreads_book_id`), or `identity-field-conflict` (an identity-relevant
  field — title/authors/year/`work_id`/language/ISBN — already had a
  different value on file). See `rules-agreed.md` §1 and §3.
- **updated** rows had either a volatile-metadata field change (ratings,
  counts, image URLs — always applied) or an identity-relevant field that
  was previously empty and got filled in. See `rules-agreed.md` §3.
- **rows_with_warning** counts rows that loaded successfully but have at
  least one entry in the `warnings` table — including the new
  `no-usable-isbn` reason (Decision 3: loaded with a warning, not silently)
  and comma-separated multi-reason warnings like `bad-checksum,bad-prefix`
  when more than one problem applies to the same field.
