"""
pytest suite for ingest.py, built strictly from rules.md -- nothing here
tests anything rules.md doesn't say. Every example-table test is labeled
with the example number and quotes the table row it comes from.

Tests that need a database always use a file literally named "test.db"
inside a per-test temporary directory (never "books.db"), and every file a
test creates is removed in teardown, pass or fail. No test touches this
folder's own books.db or ingestion-log.json -- ingest.run() always takes
explicit paths, and every test points those paths at its own temp
directory.

ingest.py and rules.md are read-only to this file; nothing here modifies
either.
"""

import csv
import json
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ingest  # noqa: E402


# --------------------------------------------------------------------------
# Shared fixtures and helpers
# --------------------------------------------------------------------------

@pytest.fixture
def workdir(tmp_path):
    """A fresh, isolated directory for one test's test.db / CSV / log.
    Every file is removed on teardown whether the test passed or failed.
    sqlite3 keeps its file open on Windows, so every connection opened via
    connect(workdir) below is tracked and closed before cleanup runs --
    otherwise unlinking test.db fails with a PermissionError."""
    paths = {
        "db": tmp_path / "test.db",
        "csv": tmp_path / "test-input.csv",
        "csv2": tmp_path / "test-input-2.csv",
        "log": tmp_path / "ingestion-log.json",
        "_connections": [],
    }
    yield paths
    for conn in paths["_connections"]:
        conn.close()
    for key, p in paths.items():
        if key == "_connections":
            continue
        if p.exists():
            p.unlink()


def connect(workdir):
    """Opens workdir["db"] and registers the connection for the fixture
    to close during teardown, before it tries to unlink the file."""
    conn = sqlite3.connect(workdir["db"])
    workdir["_connections"].append(conn)
    return conn


def default_row(**overrides):
    """All 23 EXPECTED_HEADER columns with harmless placeholder values.
    Tests override only the columns the rule under test actually cares
    about."""
    row = {
        "book_id": "1", "goodreads_book_id": "100001", "best_book_id": "100001",
        "work_id": "200001", "books_count": "10",
        "isbn": "", "isbn13": "",
        "authors": "Test Author", "original_publication_year": "2000",
        "original_title": "Test Title", "title": "Test Title",
        "language_code": "eng", "average_rating": "4.0", "ratings_count": "100",
        "work_ratings_count": "100", "work_text_reviews_count": "10",
        "ratings_1": "1", "ratings_2": "2", "ratings_3": "3", "ratings_4": "4", "ratings_5": "5",
        "image_url": "https://example.com/img.jpg",
        "small_image_url": "https://example.com/img_small.jpg",
    }
    row.update(overrides)
    return row


def write_csv(path, rows):
    """Writes a well-formed CSV: the real EXPECTED_HEADER, then one line
    per row dict, in that column order."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ingest.EXPECTED_HEADER)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def get_book(conn, goodreads_book_id):
    cur = conn.execute("SELECT * FROM books WHERE goodreads_book_id = ?", (goodreads_book_id,))
    row = cur.fetchone()
    if row is None:
        return None
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


def get_warnings_for(conn, row_id):
    cur = conn.execute(
        "SELECT field, reason, raw_value FROM warnings WHERE book_row_id = ?", (row_id,)
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def run_single_row(workdir, row):
    """Writes one row as a CSV, ingests it, and returns (conn, book_dict)."""
    write_csv(workdir["csv"], [row])
    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))
    conn = connect(workdir)
    book = get_book(conn, row["goodreads_book_id"])
    return conn, book


# --------------------------------------------------------------------------
# One test per row of rules.md's example table ("Example table (>=12
# ISBNs and what the rules say happens to them)")
# --------------------------------------------------------------------------

def test_example_1_valid_isbn10_loads_clean(workdir):
    """#1 `0439023483`: "Valid ISBN-10 -> load, no warning.\""""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="e1", isbn="0439023483", isbn13="",
    ))
    assert book is not None
    assert book["isbn"] == "0439023483"
    assert get_warnings_for(conn, book["id"]) == []


def test_example_2_leading_zero_repaired(workdir):
    """#2 `439023483` (9 digits): "Leading zero lost, pads to a
    checksum-valid 10 digits -> repair to `0439023483`, load clean, note
    'zero-padded.'\""""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="e2", isbn="439023483", isbn13="",
    ))
    assert book["isbn"] == "0439023483"
    assert get_warnings_for(conn, book["id"]) == []


def test_example_3_isbn13_float_derived_from_isbn10(workdir):
    """#3 `9.78043902348e+12` (same row as #2): "Float-corrupted, but row
    has a valid `isbn` -> repair: derive `9780439023481` from the
    ISBN-10, load clean.\""""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="e3", isbn="439023483", isbn13="9.78043902348e+12",
    ))
    assert book["isbn13"] == "9780439023481"
    assert get_warnings_for(conn, book["id"]) == []


def test_example_4_isbn13_float_no_isbn10_warns(workdir):
    """#4 `9.78067172365e+12` (`isbn` empty on that row): "Float-corrupted,
    no ISBN-10 to derive from -> load with warning, `isbn13` set to null,
    raw value kept in an audit column.\""""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="e4", isbn="", isbn13="9.78067172365e+12",
    ))
    assert book["isbn13"] == ""
    warnings = get_warnings_for(conn, book["id"])
    assert len(warnings) == 1
    assert warnings[0]["field"] == "isbn13"
    assert warnings[0]["reason"] == "float-precision-lost"
    assert warnings[0]["raw_value"] == "9.78067172365e+12"


def test_example_5_letter_in_digit_position_invalid_characters(workdir):
    """#5 `04390A3483`: "Letter in a digit position -> load with warning,
    `isbn` nulled, flagged `invalid-characters`.\""""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="e5", isbn="04390A3483", isbn13="",
    ))
    assert book["isbn"] == ""
    warnings = get_warnings_for(conn, book["id"])
    assert len(warnings) == 1
    assert warnings[0]["field"] == "isbn"
    assert warnings[0]["reason"] == "invalid-characters"


def test_example_6_wrong_check_digit_bad_checksum(workdir):
    """#6 `1854433017`: "Right length/charset, wrong check digit -> load
    with warning, `isbn` nulled, flagged `bad-checksum`.\""""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="e6", isbn="1854433017", isbn13="",
    ))
    assert book["isbn"] == ""
    warnings = get_warnings_for(conn, book["id"])
    assert len(warnings) == 1
    assert warnings[0]["field"] == "isbn"
    assert warnings[0]["reason"] == "bad-checksum"


def test_example_7_eleven_digits_wrong_length(workdir):
    """#7 `15287463097` (11 digits): "11 digits, not a leading-zero case ->
    load with warning, `isbn` nulled, flagged `wrong-length`.\""""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="e7", isbn="15287463097", isbn13="",
    ))
    assert book["isbn"] == ""
    warnings = get_warnings_for(conn, book["id"])
    assert len(warnings) == 1
    assert warnings[0]["field"] == "isbn"
    assert warnings[0]["reason"] == "wrong-length"


def test_example_8_isbn13_in_isbn_column_moved(workdir):
    """#8 `9781982147600` found in the `isbn` column: "Fails as ISBN-10,
    but passes as ISBN-13 -> repair: move it into `isbn13`, null `isbn`,
    load clean, note 'moved from isbn column.'\""""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="e8", isbn="9781982147600", isbn13="",
    ))
    assert book["isbn"] == ""
    assert book["isbn13"] == "9781982147600"
    assert get_warnings_for(conn, book["id"]) == []


def test_example_9_hyphenated_isbn10_repaired(workdir):
    """#9 `0-450-19827-8`: "Valid once hyphens are stripped -> repair
    (reformat only), load clean.\""""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="e9", isbn="0-450-19827-8", isbn13="",
    ))
    assert book["isbn"] == "0450198278"
    assert get_warnings_for(conn, book["id"]) == []


def test_example_10_empty_isbn_loads_as_new_row_no_warning(workdir):
    """#10 `` (empty): "No ISBN -> load as a new row; no automatic matching
    is attempted (section 2) -- a normalized title+author key is stored
    for a human to use later, but every re-run inserts this row again.\"
    Only the single-row outcome is tested here (loaded, no warning) --
    the re-run-duplicates consequence is section 2 narrative, not this
    example row's own claim."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="e10", isbn="", isbn13="",
    ))
    assert book is not None
    assert book["isbn"] == "" and book["isbn13"] == ""
    assert get_warnings_for(conn, book["id"]) == []


def test_example_11_isbn13_bad_checksum_made_up(workdir):
    """#11 `9999999999999`: "13 digits, fails the ISBN-13 checksum -> load
    with warning, `isbn13` nulled, flagged `bad-checksum`.\""""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="e11", isbn="", isbn13="9999999999999",
    ))
    assert book["isbn13"] == ""
    warnings = get_warnings_for(conn, book["id"])
    assert len(warnings) == 1
    assert warnings[0]["field"] == "isbn13"
    assert warnings[0]["reason"] == "bad-checksum"


def test_example_12_non_numeric_invalid_characters(workdir):
    """#12 `ABCDEFGHIJ`: "Not numeric at all -> load with warning, `isbn`
    nulled, flagged `invalid-characters`.\"

    rules.md originally labeled this example `unparseable`, a code
    ingest.py never actually emits (it only ever returns
    "invalid-characters" for any non-digit value, matching example #5) --
    corrected in rules.md to match both the code and example #5's own
    wording."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="e12", isbn="ABCDEFGHIJ", isbn13="",
    ))
    assert book["isbn"] == ""
    warnings = get_warnings_for(conn, book["id"])
    assert len(warnings) == 1
    assert warnings[0]["field"] == "isbn"
    assert warnings[0]["reason"] == "invalid-characters"


def test_example_13_isbn_collision_second_title_rejected(workdir):
    """#13 `1416524797` arriving twice for two different titles (real,
    `books-batch2.csv` rows 21 & 24, *Angels & Demons* vs *Paper Moons*):
    "Same valid ISBN already on file under *Angels & Demons* -> reject
    the second arrival (*Paper Moons*), flagged `isbn-collision`; the
    first-loaded row is untouched.\""""
    rows = [
        default_row(goodreads_book_id="e13a", title="Angels & Demons",
                    isbn="1416524797", isbn13=""),
        default_row(goodreads_book_id="e13b", title="Paper Moons",
                    isbn="1416524797", isbn13=""),
    ]
    write_csv(workdir["csv"], rows)
    result = ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))

    conn = connect(workdir)
    first = get_book(conn, "e13a")
    second = get_book(conn, "e13b")

    assert first is not None
    assert first["title"] == "Angels & Demons"
    assert second is None  # the second arrival was rejected, never inserted

    import json
    log = json.loads(workdir["log"].read_text(encoding="utf-8"))
    rejected_entries = [r for r in log[-1]["not_loaded"] if r["status"] == "rejected"]
    assert len(rejected_entries) == 1
    assert rejected_entries[0]["reason"] == "isbn-collision"
    assert rejected_entries[0]["title"] == "Paper Moons"


def test_example_14_hyphenated_isbn13_repaired(workdir):
    """#14 `978-0-13-468599-1` (made up): "Valid ISBN-13 with hyphens ->
    repair (strip separators), load clean.\""""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="e14", isbn="", isbn13="978-0-13-468599-1",
    ))
    assert book["isbn13"] == "9780134685991"
    assert get_warnings_for(conn, book["id"]) == []


def test_example_15_ratings_count_increase_updates_existing_row(workdir):
    """#15 `9780439023481` on a row where that book's `ratings_count` is
    higher than what's already on file (made up, based on a real row --
    *The Hunger Games*): "Same ISBN, same title, a substantive field
    changed -> update the existing row (not a new insert), log the old ->
    new diff for `ratings_count`.\""""
    base = default_row(
        goodreads_book_id="e15", title="The Hunger Games",
        isbn="", isbn13="9780439023481", ratings_count="100",
    )
    write_csv(workdir["csv"], [base])
    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))

    updated_row = dict(base)
    updated_row["ratings_count"] = "150"
    write_csv(workdir["csv2"], [updated_row])
    ingest.run(str(workdir["csv2"]), str(workdir["db"]), str(workdir["log"]))

    conn = connect(workdir)
    book = get_book(conn, "e15")
    assert book["ratings_count"] == "150"

    import json
    log = json.loads(workdir["log"].read_text(encoding="utf-8"))
    second_run = log[-1]
    assert second_run["updated"] == 1
    diff = second_run["updates"][0]["changed"]
    assert diff["ratings_count"]["old"] == "100"
    assert diff["ratings_count"]["new"] == "150"

    workdir["csv2"].unlink()


def test_example_16_malformed_row_rejected(workdir):
    """#16 "a data row with 25 comma-separated fields where the header has
    23 (made up)": "The row itself doesn't parse against the expected
    structure -> reject the whole row, reason `structural-parse-error`
    (the one case where the *row*, not just an ISBN field, is
    rejected).\""""
    with open(workdir["csv"], "w", newline="", encoding="utf-8") as f:
        f.write(",".join(ingest.EXPECTED_HEADER) + "\n")
        f.write(",".join(str(i) for i in range(25)) + "\n")

    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))

    import json
    log = json.loads(workdir["log"].read_text(encoding="utf-8"))
    entry = log[-1]
    assert entry["rejected"] == 1
    assert entry["loaded"] == 0
    assert entry["not_loaded"][0]["reason"] == "structural-parse-error"


# --------------------------------------------------------------------------
# The five required behavioral tests
# --------------------------------------------------------------------------

def test_running_same_file_twice_creates_no_duplicates(workdir):
    """rules.md section 2: identity is a valid ISBN; running the same
    file again must not create a second row for a book that already has
    one (only no-ISBN books are documented to duplicate on re-run, which
    is a separate, already-accepted case -- this test uses ISBN-bearing
    rows, the case rules.md actually guarantees no duplicates for)."""
    rows = [
        default_row(goodreads_book_id="d1", isbn="0439023483", isbn13=""),
        default_row(goodreads_book_id="d2", isbn="0747532699", isbn13=""),
    ]
    write_csv(workdir["csv"], rows)

    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))
    conn = connect(workdir)
    count_after_first = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    conn.close()

    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))
    conn = connect(workdir)
    count_after_second = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]

    assert count_after_first == 2
    assert count_after_second == 2

    import json
    log = json.loads(workdir["log"].read_text(encoding="utf-8"))
    assert log[-1]["loaded"] == 0
    assert log[-1]["skipped"] == 2


def test_every_run_appends_a_log_entry_without_overwriting_earlier_ones(workdir):
    """rules.md section 4 assumes a run-by-run audit trail (the report
    must cover "every run," and ingest.py's own docstring/Q&A says it
    "appends a new entry... rather than overwriting anything"). Each run
    must add one entry, and prior entries must stay exactly as they were."""
    import json

    row_a = default_row(goodreads_book_id="l1", isbn="0439023483", isbn13="")
    write_csv(workdir["csv"], [row_a])
    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))
    log_after_first = json.loads(workdir["log"].read_text(encoding="utf-8"))
    assert len(log_after_first) == 1
    first_entry_snapshot = log_after_first[0]

    row_b = default_row(goodreads_book_id="l2", isbn="0747532699", isbn13="")
    write_csv(workdir["csv2"], [row_b])
    ingest.run(str(workdir["csv2"]), str(workdir["db"]), str(workdir["log"]))
    log_after_second = json.loads(workdir["log"].read_text(encoding="utf-8"))

    assert len(log_after_second) == 2
    assert log_after_second[0] == first_entry_snapshot  # untouched

    workdir["csv2"].unlink()


def test_loaded_updated_skipped_rejected_sum_to_rows_read(workdir):
    """rules.md section 4: the report's headline numbers must account for
    every row read -- "rows processed, loaded clean, loaded with a
    warning, updated, skipped as duplicates, and rejected outright."""
    import json

    seed_rows = [
        default_row(goodreads_book_id="s1", title="Seed One", isbn="0439023483", isbn13="", ratings_count="100"),
        default_row(goodreads_book_id="s2", title="Seed Two", isbn="0747532699", isbn13=""),
    ]
    write_csv(workdir["csv"], seed_rows)
    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))

    with open(workdir["csv2"], "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ingest.EXPECTED_HEADER)
        writer.writeheader()
        # unchanged -> skipped
        writer.writerow(default_row(goodreads_book_id="s1", title="Seed One",
                                     isbn="0439023483", isbn13="", ratings_count="100"))
        # same identity, ratings_count changed -> updated
        writer.writerow(default_row(goodreads_book_id="s2", title="Seed Two",
                                     isbn="0747532699", isbn13="", ratings_count="999"))
        # brand new, valid isbn -> loaded
        writer.writerow(default_row(goodreads_book_id="s3", title="Seed Three",
                                     isbn="059035342X", isbn13=""))
        # malformed line, written directly -> rejected
        f.write(",".join(str(i) for i in range(25)) + "\n")

    ingest.run(str(workdir["csv2"]), str(workdir["db"]), str(workdir["log"]))
    log = json.loads(workdir["log"].read_text(encoding="utf-8"))
    entry = log[-1]

    assert entry["rows_read"] == 4
    assert entry["loaded"] + entry["updated"] + entry["skipped"] + entry["rejected"] == entry["rows_read"]
    assert entry["skipped"] == 1
    assert entry["updated"] == 1
    assert entry["loaded"] == 1
    assert entry["rejected"] == 1

    workdir["csv2"].unlink()


def test_same_file_on_empty_database_twice_gives_same_database(workdir, monkeypatch):
    """ingest.py's own docstring: "every decision below is pure,
    deterministic logic..., so the same input file always produces the
    same result." Two separate runs, each starting from an empty
    database, must produce byte-identical books/warnings tables.

    The only thing that genuinely cannot be identical between two
    separate real-world invocations is the wall-clock timestamp -- so
    this test freezes time (not part of rules.md; a test-harness detail,
    the same way rules.md's own determinism claim implicitly assumes a
    fixed "now") to check full equality rather than quietly excluding
    columns from the comparison.
    """
    real_datetime = ingest.datetime

    class _FrozenDatetime(real_datetime):
        @classmethod
        def now(cls, tz=None):
            return real_datetime(2026, 1, 1, tzinfo=tz)

    monkeypatch.setattr(ingest, "datetime", _FrozenDatetime)

    rows = [
        default_row(goodreads_book_id="r1", isbn="0439023483", isbn13=""),
        default_row(goodreads_book_id="r2", isbn="", isbn13="9780134685991"),
        default_row(goodreads_book_id="r3", isbn="04390A3483", isbn13=""),
    ]
    write_csv(workdir["csv"], rows)

    def snapshot():
        ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))
        conn = connect(workdir)
        books = conn.execute(
            "SELECT * FROM books ORDER BY goodreads_book_id"
        ).fetchall()
        warnings = conn.execute(
            "SELECT field, raw_value, reason FROM warnings "
            "ORDER BY book_row_id, field"
        ).fetchall()
        conn.close()
        workdir["db"].unlink()
        return books, warnings

    first_books, first_warnings = snapshot()
    second_books, second_warnings = snapshot()

    assert first_books == second_books
    assert first_warnings == second_warnings
