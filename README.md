# languageofcomputation-week4-assignment

Ingests `books.csv` / `books-batch2.csv` into `books.db` per `rules.md` —
the rules Kristina and her partner agreed on. `ingest.py` implements them;
`test_ingest.py` is the pytest suite built from them.

## Running the tests

These commands assume a PowerShell terminal, starting from having no
terminal open at all.

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

Add `-v` to see every test by name instead of just a pass/fail summary
line. `test-results-before.txt` is the saved output of this same command
run against the version of `ingest.py` built from the original Module 3
rules, before it was updated to pass; `test-results.txt` is the final run,
with all tests passing.

## Running `ingest.py`

`ingest.py` takes no command-line parameters — `CSV_FILENAME`,
`DB_FILENAME`, and `LOG_FILENAME` are fixed constants at the top of the
file (by design — see the script's own docstring), so a run is always
exactly reproducible from the file alone.

```powershell
cd "C:\Users\Kristina\Workspace\language-of-computation\week4-assignment"
python ingest.py
```

Run that same command a second time to ingest `books.csv` again (it's
safe to re-run — see `rules.md` section 3 for what happens to
already-loaded rows):

```powershell
python ingest.py
```

Then ingest `books-batch2.csv`. Since the CSV path isn't a command-line
argument, this one-liner points `ingest.run()` at the other file without
editing `ingest.py`:

```powershell
python -c "import ingest; ingest.run('books-batch2.csv', 'books.db', 'ingestion-log.json')"
```

Each of these writes to `books.db` and appends one entry to
`ingestion-log.json` — open `report.html` and load that file to see every
run's status, counts, and per-row detail.

## Working notes

`working-notes/` holds the process work that led here but isn't itself a
required deliverable: the three-way comparison of the original
individually-written rules.md files, the meeting notes, the merged
rules-agreed.md and its ERD, a spreadsheet breakdown of the load results,
and the test suite + run instructions for the original (pre-agreement)
rules. Nothing in this folder is read by `ingest.py` or the tests.
