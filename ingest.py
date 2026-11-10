"""
Ingest a books CSV into books.db, following rules.md exactly -- the rules
Kristina and her partner agreed on.

No AI, no network access: every decision below is pure, deterministic logic
(ISBN checksum math and plain string rules), so the same input file always
produces the same result. The CSV filename is fixed on purpose (not a
command-line argument) -- edit CSV_FILENAME below to point at a different
file.
"""

import csv
import json
import os
import re
import sqlite3
from datetime import datetime, timezone

CSV_FILENAME = "books.csv"
DB_FILENAME = "books.db"
LOG_FILENAME = "ingestion-log.json"

EXPECTED_HEADER = [
    "book_id", "goodreads_book_id", "best_book_id", "work_id", "books_count",
    "isbn", "isbn13", "authors", "original_publication_year", "original_title",
    "title", "language_code", "average_rating", "ratings_count",
    "work_ratings_count", "work_text_reviews_count",
    "ratings_1", "ratings_2", "ratings_3", "ratings_4", "ratings_5",
    "image_url", "small_image_url",
]

# rules.md section 3: on a match (by goodreads_book_id), every other
# field is one of two camps.
#
# Volatile metadata -- always updated, no review needed.
VOLATILE_FIELDS = [
    "average_rating", "ratings_count", "work_ratings_count",
    "work_text_reviews_count",
    "ratings_1", "ratings_2", "ratings_3", "ratings_4", "ratings_5",
    "books_count", "image_url", "small_image_url", "best_book_id", "book_id",
]

# Identity-relevant -- frozen once set: a fill (empty -> value) is an
# update, but a value that disagrees with an already-populated value is a
# conflict (reject + flag for review), never a silent overwrite.
IDENTITY_RELEVANT_FIELDS = [
    "title", "authors", "original_publication_year", "work_id",
    "language_code", "isbn", "isbn13",
]

# Columns read back from an existing row to compare against an incoming one
# (in addition to "id"), in the exact order the SELECT below lists them.
EXISTING_FIELDS = IDENTITY_RELEVANT_FIELDS + VOLATILE_FIELDS


# --------------------------------------------------------------------------
# ISBN checksum math (ISO 2108 for ISBN-10, EAN-13 algorithm for ISBN-13).
# --------------------------------------------------------------------------

def isbn10_check(s):
    if len(s) != 10:
        return False
    for c in s[:9]:
        if not c.isdigit():
            return False
    if not (s[9].isdigit() or s[9] in "Xx"):
        return False
    total = sum((10 - i) * int(c) for i, c in enumerate(s[:9]))
    total += 10 if s[9] in "Xx" else int(s[9])
    return total % 11 == 0


def isbn10_check_digit(nine_digits):
    """The one ISBN-10 check character that makes `nine_digits` + it pass
    isbn10_check -- used by the stripped-978 repair and the isbn13 -> isbn10
    reverse derivation (rules.md section 1)."""
    total = sum((10 - i) * int(c) for i, c in enumerate(nine_digits))
    check = (11 - (total % 11)) % 11
    return "X" if check == 10 else str(check)


def isbn13_checksum_ok(s):
    """Mod-10 check only, no prefix requirement -- used internally to tell
    a bad checksum apart from a bad prefix for multi-code reporting."""
    if len(s) != 13 or not s.isdigit():
        return False
    total = sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(s))
    return total % 10 == 0


def isbn13_check(s):
    """Full ISBN-13 validity: Mod-10 checksum AND a 978/979 prefix
    (rules.md section 1, the prefix check --
    a 977-prefixed value is an ISSN-style code, not an ISBN, whatever its
    checksum says)."""
    return isbn13_checksum_ok(s) and s[:3] in ("978", "979")


def isbn13_check_digit(twelve_digits):
    total = sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(twelve_digits))
    return (10 - (total % 10)) % 10


def try_stripped_978_repair(ten_digit_candidate):
    """Anthony's 'stripped-978' repair: if a 10-digit ISBN-10 candidate
    fails its own Mod-11 checksum, but '978' + those same 10 characters
    passes the ISBN-13 Mod-10 checksum, that proves the first 9 digits are
    right -- recompute the correct ISBN-10 check digit from them. Returns
    the repaired 10-digit string, or None if the repair doesn't apply."""
    if isbn13_checksum_ok("978" + ten_digit_candidate):
        repaired = ten_digit_candidate[:9] + isbn10_check_digit(ten_digit_candidate[:9])
        if isbn10_check(repaired):
            return repaired
    return None


def derive_isbn10_from_isbn13(isbn13_value):
    """Anthony's 'Missing Counterpart' reverse derivation: a valid
    978-prefixed ISBN-13 determines exactly one ISBN-10. 979-prefixed
    ISBN-13s have no ISBN-10 form and are skipped (returns None)."""
    if isbn13_value[:3] != "978":
        return None
    nine = isbn13_value[3:12]
    candidate = nine + isbn10_check_digit(nine)
    return candidate if isbn10_check(candidate) else None


def strip_separators(s):
    """Strip hyphens/spaces, and uppercase a lowercase trailing check digit
    ('x' -> 'X') so the same ISBN-10 value doesn't come out differently
    cased depending on how it was typed. rules.md doesn't say this
    explicitly, but Anthony's and Abigail's implementations both do it,
    so this aligns Kristina's outcomes with theirs (comparison.md,
    "Why our data differs" #1)."""
    s = re.sub(r"[-\s]", "", s)
    return s[:-1] + "X" if s.endswith("x") else s


def looks_like_float_artifact(raw):
    # scientific notation (9.78e+12) or a trailing .0-style float artifact
    return bool(re.search(r"[eE][+\-]?\d+$", raw)) or bool(re.fullmatch(r"\d+\.0+", raw))


# --------------------------------------------------------------------------
# Field-level repair / warning logic -- this is rules.md section 1,
# and nothing else. Every branch below maps to one row of that table.
# --------------------------------------------------------------------------

def fix_isbn(raw):
    """
    Returns a dict:
      value         -- final isbn10 value to store ("" if none)
      repaired      -- bool, whether the stored value differs from the raw input
      note          -- human-readable description of the repair, or None
      warning       -- reason code(s) if the value had to be nulled, or None
                        (comma-separated when more than one reason applies)
      warning_raw   -- the original raw text, if warning is set
      moved_isbn13  -- a valid ISBN-13 found in this column, to hand to isbn13
                       handling, or None
    """
    s = raw.strip()
    empty = {"value": "", "repaired": False, "note": None, "warning": None,
              "warning_raw": None, "moved_isbn13": None}
    if s == "":
        return empty

    stripped = strip_separators(s)

    # Already a valid ISBN-10 (possibly formatted with hyphens/spaces), or
    # repairable via the stripped-978 check digit recalculation.
    if re.fullmatch(r"[0-9]{9}[0-9Xx]", stripped):
        if isbn10_check(stripped):
            repaired = stripped != s
            return {"value": stripped, "repaired": repaired,
                    "note": "reformatted (separators stripped)" if repaired else None,
                    "warning": None, "warning_raw": None, "moved_isbn13": None}
        fixed = try_stripped_978_repair(stripped)
        if fixed:
            return {"value": fixed, "repaired": True,
                    "note": f"check digit recalculated via stripped-978 repair (978+{stripped} passed as an ISBN-13)",
                    "warning": None, "warning_raw": None, "moved_isbn13": None}
        return {"value": "", "repaired": False, "note": None,
                "warning": "bad-checksum", "warning_raw": s, "moved_isbn13": None}

    # A valid ISBN-13 sitting in the isbn (ISBN-10) column: structural repair.
    if re.fullmatch(r"[0-9]{13}", stripped) and isbn13_check(stripped):
        return {"value": "", "repaired": True,
                "note": "moved to isbn13 (was a valid ISBN-13 found in the isbn column)",
                "warning": None, "warning_raw": None, "moved_isbn13": stripped}

    # Leading zero(s) stripped by numeric storage: all-digit, short.
    if re.fullmatch(r"[0-9]+", stripped) and len(stripped) < 10:
        padded = stripped.zfill(10)
        if isbn10_check(padded):
            return {"value": padded, "repaired": True,
                    "note": f"zero-padded from {len(stripped)} to 10 digits",
                    "warning": None, "warning_raw": None, "moved_isbn13": None}
        fixed = try_stripped_978_repair(padded)
        if fixed:
            return {"value": fixed, "repaired": True,
                    "note": f"zero-padded from {len(stripped)} to 10 digits, then check digit "
                            f"recalculated via stripped-978 repair",
                    "warning": None, "warning_raw": None, "moved_isbn13": None}
        # The value pads to the right length but still fails the checksum --
        # treated as a bad checksum (the padded 10-digit candidate is what
        # failed), not a length problem, matching Anthony's and Abigail's
        # implementations (comparison.md, "Why our data differs" #2).
        return {"value": "", "repaired": False, "note": None,
                "warning": "bad-checksum", "warning_raw": s, "moved_isbn13": None}

    # All-digit but the wrong length in some other way (too long, or 13 digits
    # that don't check out as ISBN-13 either).
    if re.fullmatch(r"[0-9]+", stripped):
        return {"value": "", "repaired": False, "note": None,
                "warning": "wrong-length", "warning_raw": s, "moved_isbn13": None}

    # Anything else: letters/symbols in positions that can't be fixed blind.
    return {"value": "", "repaired": False, "note": None,
            "warning": "invalid-characters", "warning_raw": s, "moved_isbn13": None}


def fix_isbn13(raw, resolved_isbn10, moved_isbn13):
    """
    Returns a dict: value, repaired, note, warning, warning_raw.
    `resolved_isbn10` is the already-repaired isbn10 value for this row (or "").
    `moved_isbn13` is a value handed over from fix_isbn() if the isbn column
    held a valid ISBN-13 (column-swap case).
    """
    s = raw.strip()

    if moved_isbn13 is not None and s == "":
        return {"value": moved_isbn13, "repaired": True,
                "note": "moved from isbn column (was a valid ISBN-13 found there)",
                "warning": None, "warning_raw": None}
    # moved_isbn13 is not None and s != "": isbn13 already holds its own
    # value -- don't blindly overwrite it. Fall through and evaluate the
    # isbn13 cell on its own merits; the isbn-column value that would have
    # moved here is simply invalid (ambiguous), which fix_isbn's caller
    # already reflects by discarding it.

    if s == "":
        # isbn13 is simply blank (not corrupted) -- if isbn already resolved
        # to a valid ISBN-10, derive isbn13 from it the same way as the
        # scientific-notation case. Needed so isbn13 is always populated
        # whenever a valid ISBN exists at all, which the collision check in
        # run() (Decision 1 / Abigail's identity model) depends on: two rows
        # with the same ISBN but different goodreads_book_id must collide
        # whether the shared ISBN was stored as isbn10 or isbn13.
        if resolved_isbn10 and isbn10_check(resolved_isbn10):
            base12 = "978" + resolved_isbn10[:9]
            derived = base12 + str(isbn13_check_digit(base12))
            return {"value": derived, "repaired": True,
                    "note": f"derived from isbn ({resolved_isbn10}) since isbn13 was blank",
                    "warning": None, "warning_raw": None}
        return {"value": "", "repaired": False, "note": None, "warning": None, "warning_raw": None}

    if looks_like_float_artifact(s):
        if resolved_isbn10 and isbn10_check(resolved_isbn10):
            base12 = "978" + resolved_isbn10[:9]
            derived = base12 + str(isbn13_check_digit(base12))
            return {"value": derived, "repaired": True,
                    "note": f"derived from isbn ({resolved_isbn10}) via 978-prefix conversion",
                    "warning": None, "warning_raw": None}
        return {"value": "", "repaired": False, "note": None,
                "warning": "float-precision-lost", "warning_raw": s}

    stripped = strip_separators(s)
    if re.fullmatch(r"[0-9]{13}", stripped):
        reasons = []
        if stripped[:3] not in ("978", "979"):
            reasons.append("bad-prefix")
        if not isbn13_checksum_ok(stripped):
            reasons.append("bad-checksum")
        if not reasons:
            repaired = stripped != s
            return {"value": stripped, "repaired": repaired,
                    "note": "reformatted (separators stripped)" if repaired else None,
                    "warning": None, "warning_raw": None}
        return {"value": "", "repaired": False, "note": None,
                "warning": ",".join(reasons), "warning_raw": s}

    if stripped.isdigit():
        return {"value": "", "repaired": False, "note": None,
                "warning": "wrong-length", "warning_raw": s}

    return {"value": "", "repaired": False, "note": None,
            "warning": "invalid-characters", "warning_raw": s}


def normalize_title(s):
    """Lowercase, punctuation and extra whitespace stripped. Used both for
    the informational fallback key (section 2) and, per Decision 6, to
    decide whether an incoming title actually conflicts with an existing
    one (a capitalization-only difference is never a conflict)."""
    s = (s or "").strip().lower()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalize_primary_author(authors_raw):
    """First author listed, reformatted as 'Surname, Given'."""
    if not authors_raw or not authors_raw.strip():
        return ""
    primary = authors_raw.split(",")[0].strip()
    parts = primary.split()
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    surname = parts[-1]
    given = " ".join(parts[:-1])
    return f"{surname}, {given}"


def compute_fallback_key(title, authors_raw):
    """Informational only -- legacy from the pre-Decision-1 ISBN-based
    identity model, kept in the schema (see erd.md) but no longer used by
    this script to match/dedupe rows: identity is goodreads_book_id now."""
    return f"{normalize_title(title)}||{normalize_primary_author(authors_raw)}"


def compute_identity_key(goodreads_book_id):
    """Decision 1: identity is goodreads_book_id alone, not ISBN."""
    gid = (goodreads_book_id or "").strip()
    return gid if gid else None


# --------------------------------------------------------------------------
# Database setup
# --------------------------------------------------------------------------

def open_db(path):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(f"""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id TEXT, goodreads_book_id TEXT, best_book_id TEXT, work_id TEXT,
        books_count TEXT,
        isbn TEXT, isbn13 TEXT,
        authors TEXT, original_publication_year TEXT, original_title TEXT,
        title TEXT, language_code TEXT, average_rating TEXT, ratings_count TEXT,
        work_ratings_count TEXT, work_text_reviews_count TEXT,
        ratings_1 TEXT, ratings_2 TEXT, ratings_3 TEXT, ratings_4 TEXT, ratings_5 TEXT,
        image_url TEXT, small_image_url TEXT,
        identity_key TEXT,
        fallback_key TEXT,
        source_file TEXT,
        first_loaded_at TEXT,
        last_updated_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_books_identity_key ON books(identity_key);
    CREATE INDEX IF NOT EXISTS idx_books_goodreads_book_id ON books(goodreads_book_id);

    CREATE TABLE IF NOT EXISTS warnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_row_id INTEGER NOT NULL REFERENCES books(id),
        field TEXT NOT NULL,
        raw_value TEXT,
        reason TEXT NOT NULL,
        recorded_at TEXT NOT NULL
    );
    """)
    conn.commit()
    return conn


# --------------------------------------------------------------------------
# Row-level structural parsing: only a wrong field count or a quoting error
# causes a structural rejection. Nothing about the *content* of a field is
# a structural problem.
# --------------------------------------------------------------------------

def read_rows(path):
    """Yields (line_no, row_list_or_None, parse_error_or_None)."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        line_no = 1
        header = None
        while True:
            line_no += 1
            try:
                row = next(reader)
            except StopIteration:
                break
            except csv.Error as e:
                yield line_no, None, str(e)
                continue
            if header is None:
                header = row
                continue
            yield line_no, row, None


# --------------------------------------------------------------------------
# Main ingestion run
# --------------------------------------------------------------------------

def run(csv_path, db_path, log_path):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    rows_read = 0
    loaded = 0
    updated = 0
    skipped = 0
    rejected = 0
    rows_with_warning = 0
    not_loaded = []   # skipped + rejected rows, with reasons
    update_diffs = [] # field-level diffs for updated rows

    status = "SUCCESS"
    fatal_error = None
    conn = None

    try:
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"{csv_path} does not exist")

        with open(csv_path, newline="", encoding="utf-8") as f:
            header = next(csv.reader(f))
        if header != EXPECTED_HEADER:
            raise ValueError(
                f"header does not match the expected {len(EXPECTED_HEADER)} columns "
                f"{EXPECTED_HEADER}; found {header}"
            )

        conn = open_db(db_path)
        cur = conn.cursor()
        header_len = len(EXPECTED_HEADER)

        for line_no, raw_row, parse_error in read_rows(csv_path):
            rows_read += 1

            if parse_error is not None:
                rejected += 1
                not_loaded.append({
                    "line": line_no, "title": None, "status": "rejected",
                    "reason": "structural-parse-error", "detail": parse_error,
                })
                continue

            if len(raw_row) != header_len:
                rejected += 1
                not_loaded.append({
                    "line": line_no, "title": None, "status": "rejected",
                    "reason": "structural-parse-error",
                    "detail": f"expected {header_len} fields, found {len(raw_row)}",
                })
                continue

            row = dict(zip(EXPECTED_HEADER, raw_row))
            title = row["title"].strip()

            isbn_result = fix_isbn(row["isbn"])
            isbn13_result = fix_isbn13(row["isbn13"], isbn_result["value"], isbn_result["moved_isbn13"])

            final_isbn = isbn_result["value"]
            final_isbn13 = isbn13_result["value"]

            # Anthony's reverse derivation: isbn13 is good (978-prefixed)
            # but isbn never resolved to anything usable.
            if final_isbn == "" and final_isbn13 and final_isbn13[:3] == "978":
                derived10 = derive_isbn10_from_isbn13(final_isbn13)
                if derived10:
                    final_isbn = derived10

            identity_key = compute_identity_key(row["goodreads_book_id"])

            record = dict(row)
            record["isbn"] = final_isbn
            record["isbn13"] = final_isbn13
            record["fallback_key"] = compute_fallback_key(row["title"], row["authors"])

            field_warnings = []
            if isbn_result["warning"]:
                field_warnings.append(("isbn", isbn_result["warning_raw"], isbn_result["warning"]))
            if isbn13_result["warning"]:
                field_warnings.append(("isbn13", isbn13_result["warning_raw"], isbn13_result["warning"]))
            if (not field_warnings and final_isbn == "" and final_isbn13 == ""
                    and row["isbn"].strip() == "" and row["isbn13"].strip() == ""):
                field_warnings.append(("isbn", "", "no-usable-isbn"))
            if field_warnings:
                rows_with_warning += 1

            # ISBN collision: a valid isbn13 already belongs to a different
            # goodreads_book_id -- reject regardless of whether *this* row
            # matches an existing one of its own.
            if final_isbn13:
                cur.execute(
                    "SELECT goodreads_book_id FROM books WHERE isbn13 = ? AND goodreads_book_id != ? LIMIT 1",
                    (final_isbn13, identity_key or ""),
                )
                collision = cur.fetchone()
                if collision:
                    rejected += 1
                    not_loaded.append({
                        "line": line_no, "title": title, "status": "rejected",
                        "reason": "isbn-collision",
                        "detail": f"isbn13 {final_isbn13} already belongs to "
                                  f"goodreads_book_id {collision[0]}",
                    })
                    continue

            existing = None
            if identity_key is not None:
                cur.execute(
                    f"SELECT id, {', '.join(EXISTING_FIELDS)} "
                    f"FROM books WHERE goodreads_book_id = ?",
                    (identity_key,),
                )
                existing = cur.fetchone()

            if identity_key is not None and existing is not None:
                existing_id = existing[0]
                existing_fields = dict(zip(EXISTING_FIELDS, existing[1:]))

                conflicts = {}
                fills = {}
                for field in IDENTITY_RELEVANT_FIELDS:
                    old_val = (existing_fields.get(field) or "").strip()
                    new_val = (record.get(field) or "").strip()
                    if field == "title":
                        same = normalize_title(old_val) == normalize_title(new_val)
                    else:
                        same = old_val == new_val
                    if old_val == "" and new_val != "":
                        fills[field] = {"old": old_val, "new": new_val}
                    elif old_val != "" and new_val != "" and not same:
                        conflicts[field] = {"old": old_val, "new": new_val}
                    # old non-empty, new empty: keep the existing value, no-op.
                    # equal values: no-op.

                if conflicts:
                    rejected += 1
                    detail = ", ".join(
                        f"{f} ({v['old']!r} -> {v['new']!r})" for f, v in conflicts.items()
                    )
                    not_loaded.append({
                        "line": line_no, "title": title, "status": "rejected",
                        "reason": "identity-field-conflict",
                        "detail": f"existing goodreads_book_id {identity_key} "
                                  f"(row id {existing_id}) disagrees on: {detail}",
                    })
                    continue

                volatile_diffs = {}
                for field in VOLATILE_FIELDS:
                    old_val = existing_fields.get(field, "")
                    new_val = record.get(field, "")
                    if (old_val or "") != (new_val or ""):
                        volatile_diffs[field] = {"old": old_val, "new": new_val}

                diffs = {**fills, **volatile_diffs}

                if not diffs:
                    skipped += 1
                    not_loaded.append({
                        "line": line_no, "title": title, "status": "skipped",
                        "reason": "duplicate-unchanged",
                        "detail": f"matches existing row id {existing_id}, no changes",
                    })
                    continue

                update_fields = list(fills.keys()) + list(volatile_diffs.keys())
                set_clause = ", ".join(f"{f} = ?" for f in update_fields)
                cur.execute(
                    f"UPDATE books SET {set_clause}, source_file = ?, last_updated_at = ? WHERE id = ?",
                    [record[f] for f in update_fields] + [os.path.basename(csv_path), now, existing_id],
                )
                cur.execute("DELETE FROM warnings WHERE book_row_id = ?", (existing_id,))
                for field, raw_value, reason in field_warnings:
                    cur.execute(
                        "INSERT INTO warnings (book_row_id, field, raw_value, reason, recorded_at) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (existing_id, field, raw_value, reason, now),
                    )
                updated += 1
                update_diffs.append({"line": line_no, "title": title, "row_id": existing_id, "changed": diffs})
                continue

            # No match (new book, or no usable identity key at all) -> insert.
            columns = list(record.keys()) + ["identity_key", "source_file", "first_loaded_at", "last_updated_at"]
            values = list(record.values()) + [identity_key, os.path.basename(csv_path), now, now]
            placeholders = ", ".join("?" for _ in columns)
            cur.execute(
                f"INSERT INTO books ({', '.join(columns)}) VALUES ({placeholders})",
                values,
            )
            new_id = cur.lastrowid
            for field, raw_value, reason in field_warnings:
                cur.execute(
                    "INSERT INTO warnings (book_row_id, field, raw_value, reason, recorded_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (new_id, field, raw_value, reason, now),
                )
            loaded += 1

        conn.commit()

    except Exception as e:
        # rules.md section 4: FAILED is a status label,
        # not a rollback guarantee -- whatever was already committed stays.
        status = "FAILED"
        fatal_error = str(e)
        if conn is not None:
            conn.commit()
    finally:
        if conn is not None:
            conn.close()

    if status != "FAILED" and (rejected > 0 or rows_with_warning > 0):
        status = "COMPLETED WITH ISSUES"

    entry = {
        "run_at": now,
        "source_file": os.path.basename(csv_path),
        "status": status,
        "fatal_error": fatal_error,
        "rows_read": rows_read,
        "loaded": loaded,
        "updated": updated,
        "skipped": skipped,
        "rejected": rejected,
        "rows_with_warning": rows_with_warning,
        "not_loaded": not_loaded,
        "updates": update_diffs,
    }

    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []
    else:
        log = []
    log.append(entry)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

    print(f"status={status} rows_read={rows_read} loaded={loaded} updated={updated} "
          f"skipped={skipped} rejected={rejected} rows_with_warning={rows_with_warning}")
    if status == "FAILED":
        note = ("no rows were written" if rows_read == 0
                 else "rows loaded before the failure may already be saved -- "
                      "no atomicity guarantee was implemented (rules.md section 4)")
        print(f"FAILED: {fatal_error} ({note})")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    run(
        os.path.join(here, CSV_FILENAME),
        os.path.join(here, DB_FILENAME),
        os.path.join(here, LOG_FILENAME),
    )
