"""
pytest suite for THIS folder's ingest.py, built strictly from
rules-final.md (the group's complete, final rules document, aligned with
your partner) -- nothing here tests anything rules-final.md doesn't say.

ingest.py here has been updated to implement rules-final.md (the same
implementation verified separately in week3-assignment/ingest.py, now
copied into this folder) -- these tests are expected to pass. See
test-results-before.txt for the prior run against the original,
not-yet-updated ingest.py, which failed 8 of these 20 as expected.

rules-final.md has no example table of its own (unlike the original
rules.md). Per instruction, the "one test per example" requirement reuses
the original rules.md's 16 ISBN examples, but each test asserts what
rules-final.md says should happen now -- which differs from the original
for several of them:
  - identity is goodreads_book_id now, not ISBN, so every test row is
    given a distinct goodreads_book_id and matching is keyed on that;
  - isbn13 is now derived whenever isbn is valid, even if isbn13 was
    simply blank (not just scientific-notation-corrupted) -- examples
    #1, #2, #9 now populate isbn13 where the original left it blank;
  - the reverse derivation (isbn10 from a valid isbn13) is new -- examples
    #8, #9, #14 now populate isbn where the original left it blank;
  - a bad isbn13 can now carry more than one reason, comma-separated
    (example #11: `bad-prefix,bad-checksum`, since 999... has neither a
    978/979 prefix nor a passing checksum);
  - example #10 (both ISBN fields empty) now gets a warning
    (`no-usable-isbn`) instead of loading silently;
  - example #13's collision is reported the same way, but is now keyed on
    goodreads_book_id disagreeing on a shared ISBN, not on a title
    mismatch at a shared ISBN-derived identity.

Expected ISBN/ISBN13 repair values below were computed by calling
ingest.fix_isbn()/fix_isbn13()/derive_isbn10_from_isbn13() directly against
the real functions (not hand-derived), then cross-checked against
rules-final.md section 1.

Tests that need a database always use a file literally named "test.db"
inside a per-test temporary directory (never "books.db"), and every file a
test creates is removed in teardown, pass or fail. No test touches this
folder's real books.db or ingestion-log.json -- ingest.run() always takes
explicit paths, and every test points those paths at its own temp
directory.

ingest.py and rules-final.md are read-only to this file; nothing here
modifies either.
"""

import csv
import importlib.util
import json
import os
import sqlite3

import pytest

# Loaded under a distinct module name (not "ingest") so this never collides
# with test_ingest.py's own "import ingest" if both test files are ever
# collected in the same pytest run -- even though, as of this version,
# they point at the very same file (this folder's ingest.py), tested
# against two different rules documents.
_SPEC = importlib.util.spec_from_file_location(
    "ingest_agreed",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ingest.py"),
)
ingest = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ingest)


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
    about. goodreads_book_id is the identity now (Decision 1), so every
    call site gives it an explicit, distinct value."""
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
# One test per row of the original rules.md example table, reinterpreted
# under rules-final.md
# --------------------------------------------------------------------------

def test_example_1_valid_isbn10_loads_clean_isbn13_now_derived(workdir):
    """#1 `0439023483`: still loads clean, no warning. New under the
    agreed rules: isbn13 is now derived too, since it's blank and isbn is
    valid (the collision check needs isbn13 populated whenever any valid
    ISBN exists -- see rules-final.md section 1's "isbn13 is simply
    blank" row)."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="ag1", isbn="0439023483", isbn13="",
    ))
    assert book["isbn"] == "0439023483"
    assert book["isbn13"] == "9780439023481"
    assert get_warnings_for(conn, book["id"]) == []


def test_example_2_leading_zero_repaired_isbn13_now_derived(workdir):
    """#2 `439023483` (9 digits): still zero-pads to `0439023483`. New:
    isbn13 is now also derived from it."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="ag2", isbn="439023483", isbn13="",
    ))
    assert book["isbn"] == "0439023483"
    assert book["isbn13"] == "9780439023481"
    assert get_warnings_for(conn, book["id"]) == []


def test_example_3_isbn13_float_derived_from_isbn10(workdir):
    """#3 `9.78043902348e+12` (same row as #2): unchanged -- repair:
    derive `9780439023481` from the ISBN-10, load clean."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="ag3", isbn="439023483", isbn13="9.78043902348e+12",
    ))
    assert book["isbn"] == "0439023483"
    assert book["isbn13"] == "9780439023481"
    assert get_warnings_for(conn, book["id"]) == []


def test_example_4_isbn13_float_no_isbn10_warns(workdir):
    """#4 `9.78067172365e+12` (`isbn` empty on that row): unchanged --
    load with warning, `isbn13` set to null, raw value kept."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="ag4", isbn="", isbn13="9.78067172365e+12",
    ))
    assert book["isbn13"] == ""
    warnings = get_warnings_for(conn, book["id"])
    assert len(warnings) == 1
    assert warnings[0]["field"] == "isbn13"
    assert warnings[0]["reason"] == "float-precision-lost"
    assert warnings[0]["raw_value"] == "9.78067172365e+12"


def test_example_5_letter_in_digit_position_invalid_characters(workdir):
    """#5 `04390A3483`: unchanged -- load with warning, `isbn` nulled,
    flagged `invalid-characters`."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="ag5", isbn="04390A3483", isbn13="",
    ))
    assert book["isbn"] == ""
    warnings = get_warnings_for(conn, book["id"])
    assert len(warnings) == 1
    assert warnings[0]["field"] == "isbn"
    assert warnings[0]["reason"] == "invalid-characters"


def test_example_6_wrong_check_digit_bad_checksum(workdir):
    """#6 `1854433017`: unchanged -- load with warning, `isbn` nulled,
    flagged `bad-checksum` (the stripped-978 repair was tried and did not
    apply here -- the first 9 digits don't prove out as an ISBN-13
    either)."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="ag6", isbn="1854433017", isbn13="",
    ))
    assert book["isbn"] == ""
    warnings = get_warnings_for(conn, book["id"])
    assert len(warnings) == 1
    assert warnings[0]["field"] == "isbn"
    assert warnings[0]["reason"] == "bad-checksum"


def test_example_7_eleven_digits_wrong_length(workdir):
    """#7 `15287463097` (11 digits): unchanged -- load with warning,
    `isbn` nulled, flagged `wrong-length`."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="ag7", isbn="15287463097", isbn13="",
    ))
    assert book["isbn"] == ""
    warnings = get_warnings_for(conn, book["id"])
    assert len(warnings) == 1
    assert warnings[0]["field"] == "isbn"
    assert warnings[0]["reason"] == "wrong-length"


def test_example_8_isbn13_in_isbn_column_moved_and_isbn_rederived(workdir):
    """#8 `9781982147600` found in the `isbn` column: still moves to
    `isbn13`, `isbn` nulled by the move. New under the agreed rules:
    Anthony's reverse derivation then fills `isbn` back in from that
    valid 978-prefixed `isbn13` (computed as `1982147601` by the real
    isbn10_check_digit function, not hand-derived) -- so `isbn` ends up
    populated again, not left blank."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="ag8", isbn="9781982147600", isbn13="",
    ))
    assert book["isbn13"] == "9781982147600"
    assert book["isbn"] == "1982147601"
    assert get_warnings_for(conn, book["id"]) == []


def test_example_9_hyphenated_isbn10_repaired_isbn13_now_derived(workdir):
    """#9 `0-450-19827-8`: still strips to `0450198278`. New: `isbn13` is
    now also derived from it."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="ag9", isbn="0-450-19827-8", isbn13="",
    ))
    assert book["isbn"] == "0450198278"
    assert book["isbn13"] == "9780450198274"
    assert get_warnings_for(conn, book["id"]) == []


def test_example_10_empty_isbn_now_loads_with_warning(workdir):
    """#10 `` (empty): CHANGED under Decision 3 -- the original rules.md
    loaded this informationally, with no warning at all; rules-final.md
    adopts Abigail's model instead: loaded, but with a `no-usable-isbn`
    warning."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="ag10", isbn="", isbn13="",
    ))
    assert book is not None
    assert book["isbn"] == "" and book["isbn13"] == ""
    warnings = get_warnings_for(conn, book["id"])
    assert len(warnings) == 1
    assert warnings[0]["field"] == "isbn"
    assert warnings[0]["reason"] == "no-usable-isbn"


def test_example_11_isbn13_bad_prefix_and_checksum_multi_code(workdir):
    """#11 `9999999999999`: CHANGED under the agreed rules -- the prefix
    check (Open item: implement) means this now fails on *two* grounds at
    once (no 978/979 prefix, and a failing Mod-10 checksum), reported as
    one comma-separated reason per Anthony's multi-code reporting (Open
    item: implement), rather than just `bad-checksum`."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="ag11", isbn="", isbn13="9999999999999",
    ))
    assert book["isbn13"] == ""
    warnings = get_warnings_for(conn, book["id"])
    assert len(warnings) == 1
    assert warnings[0]["field"] == "isbn13"
    assert warnings[0]["reason"] == "bad-prefix,bad-checksum"


def test_example_12_non_numeric_invalid_characters(workdir):
    """#12 `ABCDEFGHIJ`: unchanged -- load with warning, `isbn` nulled,
    flagged `invalid-characters` (matching the corrected wording in the
    original rules.md, and example #5's wording)."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="ag12", isbn="ABCDEFGHIJ", isbn13="",
    ))
    assert book["isbn"] == ""
    warnings = get_warnings_for(conn, book["id"])
    assert len(warnings) == 1
    assert warnings[0]["field"] == "isbn"
    assert warnings[0]["reason"] == "invalid-characters"


def test_example_13_isbn_collision_keyed_on_goodreads_book_id(workdir):
    """#13 `1416524797` arriving twice for two different titles (real,
    `books-batch2.csv` rows 21 & 24, *Angels & Demons* vs *Paper Moons*):
    still rejects the second arrival as a collision. CHANGED under
    Decision 1: the collision is now keyed on the ISBN already belonging
    to a *different `goodreads_book_id`*, not on a title mismatch at a
    shared ISBN-derived identity -- the two rows below are given distinct
    goodreads_book_id values, matching the real scenario (two different
    books)."""
    rows = [
        default_row(goodreads_book_id="ag13a", title="Angels & Demons",
                    isbn="1416524797", isbn13=""),
        default_row(goodreads_book_id="ag13b", title="Paper Moons",
                    isbn="1416524797", isbn13=""),
    ]
    write_csv(workdir["csv"], rows)
    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))

    conn = connect(workdir)
    first = get_book(conn, "ag13a")
    second = get_book(conn, "ag13b")

    assert first is not None
    assert first["title"] == "Angels & Demons"
    assert second is None  # the second arrival was rejected, never inserted

    log = json.loads(workdir["log"].read_text(encoding="utf-8"))
    rejected_entries = [r for r in log[-1]["not_loaded"] if r["status"] == "rejected"]
    assert len(rejected_entries) == 1
    assert rejected_entries[0]["reason"] == "isbn-collision"
    assert rejected_entries[0]["title"] == "Paper Moons"


def test_example_14_hyphenated_isbn13_repaired_isbn_now_derived(workdir):
    """#14 `978-0-13-468599-1` (made up): still strips to
    `9780134685991`. New: `isbn` is now also reverse-derived from it,
    instead of staying blank."""
    conn, book = run_single_row(workdir, default_row(
        goodreads_book_id="ag14", isbn="", isbn13="978-0-13-468599-1",
    ))
    assert book["isbn13"] == "9780134685991"
    assert book["isbn"] == "0134685997"
    assert get_warnings_for(conn, book["id"]) == []


def test_example_15_ratings_count_increase_updates_existing_row(workdir):
    """#15 `9780439023481` on a row where that book's `ratings_count` is
    higher than what's already on file (made up, based on a real row --
    *The Hunger Games*): still updates the existing row and logs the
    old -> new diff. `ratings_count` is volatile metadata under Decision
    4, so it updates freely; the match is now by `goodreads_book_id`
    (Decision 1), not by the shared ISBN."""
    base = default_row(
        goodreads_book_id="ag15", title="The Hunger Games",
        isbn="", isbn13="9780439023481", ratings_count="100",
    )
    write_csv(workdir["csv"], [base])
    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))

    updated_row = dict(base)
    updated_row["ratings_count"] = "150"
    write_csv(workdir["csv2"], [updated_row])
    ingest.run(str(workdir["csv2"]), str(workdir["db"]), str(workdir["log"]))

    conn = connect(workdir)
    book = get_book(conn, "ag15")
    assert book["ratings_count"] == "150"

    log = json.loads(workdir["log"].read_text(encoding="utf-8"))
    second_run = log[-1]
    assert second_run["updated"] == 1
    diff = second_run["updates"][0]["changed"]
    assert diff["ratings_count"]["old"] == "100"
    assert diff["ratings_count"]["new"] == "150"


def test_example_16_malformed_row_rejected(workdir):
    """#16 "a data row with 25 comma-separated fields where the header has
    23 (made up)": unchanged -- reject the whole row, reason
    `structural-parse-error`."""
    with open(workdir["csv"], "w", newline="", encoding="utf-8") as f:
        f.write(",".join(ingest.EXPECTED_HEADER) + "\n")
        f.write(",".join(str(i) for i in range(25)) + "\n")

    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))

    log = json.loads(workdir["log"].read_text(encoding="utf-8"))
    entry = log[-1]
    assert entry["rejected"] == 1
    assert entry["loaded"] == 0
    assert entry["not_loaded"][0]["reason"] == "structural-parse-error"


# --------------------------------------------------------------------------
# The five required behavioral tests
# --------------------------------------------------------------------------

def test_running_same_file_twice_creates_no_duplicates(workdir):
    """rules-final.md section 2/3: identity is `goodreads_book_id`, which
    every row has -- running the same file again must not create a second
    row for a book that already has one. Unlike the original rules.md
    (where only ISBN-bearing rows deduplicated), this now holds even for a
    row with no usable ISBN at all, so one row of each kind is used here."""
    rows = [
        default_row(goodreads_book_id="dup1", isbn="0439023483", isbn13=""),
        default_row(goodreads_book_id="dup2", isbn="", isbn13=""),  # no ISBN at all
    ]
    write_csv(workdir["csv"], rows)

    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))
    conn = connect(workdir)
    count_after_first = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]

    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))
    conn2 = connect(workdir)
    count_after_second = conn2.execute("SELECT COUNT(*) FROM books").fetchone()[0]

    assert count_after_first == 2
    assert count_after_second == 2

    log = json.loads(workdir["log"].read_text(encoding="utf-8"))
    assert log[-1]["loaded"] == 0
    assert log[-1]["skipped"] == 2


def test_every_run_appends_a_log_entry_without_overwriting_earlier_ones(workdir):
    """rules-final.md section 4 (report requirements, carried over from
    the original rules.md and Decision 7): each run must add one entry,
    and prior entries must stay exactly as they were."""
    row_a = default_row(goodreads_book_id="log1", isbn="0439023483", isbn13="")
    write_csv(workdir["csv"], [row_a])
    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))
    log_after_first = json.loads(workdir["log"].read_text(encoding="utf-8"))
    assert len(log_after_first) == 1
    first_entry_snapshot = log_after_first[0]

    row_b = default_row(goodreads_book_id="log2", isbn="0747532699", isbn13="")
    write_csv(workdir["csv2"], [row_b])
    ingest.run(str(workdir["csv2"]), str(workdir["db"]), str(workdir["log"]))
    log_after_second = json.loads(workdir["log"].read_text(encoding="utf-8"))

    assert len(log_after_second) == 2
    assert log_after_second[0] == first_entry_snapshot  # untouched


def test_loaded_updated_skipped_rejected_sum_to_rows_read(workdir):
    """rules-final.md section 4: the report's headline numbers must
    account for every row read."""
    seed_rows = [
        default_row(goodreads_book_id="sum1", title="Seed One", isbn="0439023483", isbn13="", ratings_count="100"),
        default_row(goodreads_book_id="sum2", title="Seed Two", isbn="0747532699", isbn13=""),
    ]
    write_csv(workdir["csv"], seed_rows)
    ingest.run(str(workdir["csv"]), str(workdir["db"]), str(workdir["log"]))

    with open(workdir["csv2"], "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ingest.EXPECTED_HEADER)
        writer.writeheader()
        # unchanged -> skipped
        writer.writerow(default_row(goodreads_book_id="sum1", title="Seed One",
                                     isbn="0439023483", isbn13="", ratings_count="100"))
        # same identity, ratings_count changed (volatile) -> updated
        writer.writerow(default_row(goodreads_book_id="sum2", title="Seed Two",
                                     isbn="0747532699", isbn13="", ratings_count="999"))
        # brand new, valid isbn -> loaded
        writer.writerow(default_row(goodreads_book_id="sum3", title="Seed Three",
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


def test_same_file_on_empty_database_twice_gives_same_database(workdir, monkeypatch):
    """ingest.py's own docstring: "every decision ... is pure,
    deterministic logic ..., so the same input file always produces the
    same result." Two separate runs, each starting from an empty
    database, must produce byte-identical books/warnings tables.

    The only thing that genuinely cannot be identical between two
    separate real-world invocations is the wall-clock timestamp -- so
    this test freezes time (a test-harness detail, not part of
    rules-final.md) to check full equality rather than quietly excluding
    columns from the comparison.
    """
    real_datetime = ingest.datetime

    class _FrozenDatetime(real_datetime):
        @classmethod
        def now(cls, tz=None):
            return real_datetime(2026, 1, 1, tzinfo=tz)

    monkeypatch.setattr(ingest, "datetime", _FrozenDatetime)

    rows = [
        default_row(goodreads_book_id="fr1", isbn="0439023483", isbn13=""),
        default_row(goodreads_book_id="fr2", isbn="", isbn13="9780134685991"),
        default_row(goodreads_book_id="fr3", isbn="04390A3483", isbn13=""),
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
