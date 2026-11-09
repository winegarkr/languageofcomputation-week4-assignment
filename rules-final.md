# Rules for loading `books.csv` / `books-batch2.csv` (final, as implemented)

This is the complete, standalone rules document for the ingestion pipeline
actually used to process `books.csv` and `books-batch2.csv` (the run
logged in `week3-assignment/ingestion-log.json`, implemented in
`week3-assignment/ingest.py`). It consolidates every decision from
`rules-agreed.md` into one normal rules document — written the same way
the original individual `rules.md` files were, not as a diff against
anyone's prior draft. `rules-agreed.md` remains the record of *how* the
group arrived at each rule, including the one conflict it resolved; this
document is *what the rules are*, full stop.

The one governing principle underneath all of it: **a repair is only
allowed when it is deterministic and checksum-verifiable** — when there is
exactly one possible correct value, and the math proves it. The moment
fixing a value means picking among several plausible originals, it stops
being a repair and becomes a guess, and guesses never get written into the
data as if they were facts.

## 1. For each kind of ISBN problem: repair, reject, or load with a warning?

**A bad or missing ISBN never rejects the row.** Identity doesn't depend on
having an ISBN at all (see section 2), so a bad ISBN only nulls that one
field and attaches a warning; the row is always loaded.

| Problem | Action | Why |
|---|---|---|
| Already a valid ISBN-10 or ISBN-13 (978/979-prefixed, correct checksum) | **Load, no warning** | Nothing to fix. |
| Valid, but formatted with hyphens/spaces | **Repair**: strip separators | Cosmetic; the checksum is unaffected. |
| `isbn` with leading zero(s) stripped (7–9 digits, all-numeric) | **Repair**: zero-pad to 10 digits, only if the padded result then passes the ISBN-10 checksum | Deterministic — there's exactly one way to reach 10 digits by padding. |
| A 10-digit `isbn` candidate fails its own checksum, but `978` + those same 10 characters passes the ISBN-13 checksum | **Repair**: recompute the correct ISBN-10 check digit from the first 9 digits ("stripped-978" repair) | The ISBN-13 proves the first 9 digits are right; only the check digit was wrong. |
| `isbn13` stored as scientific notation / float, and the row has (or just repaired to) a valid `isbn` | **Repair**: derive `isbn13` from `isbn` via the `978` + check-digit formula | One valid ISBN-10 determines exactly one correct ISBN-13. |
| `isbn13` is simply blank (not corrupted), and the row has a valid `isbn` | **Repair**: derive `isbn13` from `isbn`, same formula | `isbn13` must be populated whenever any valid ISBN exists, so the collision check below can actually compare ISBNs regardless of which column they started in. |
| `isbn` is blank or unusable, but `isbn13` resolves (directly, or via repair) to a valid 978-prefixed ISBN-13 | **Repair**: derive `isbn` from `isbn13` (reverse of the two rows above) | A valid 978-prefixed ISBN-13 determines exactly one ISBN-10. 979-prefixed ISBN-13s have no ISBN-10 form and are left blank. |
| `isbn13` stored as scientific notation / float, and no usable `isbn` to derive from | **Load with a warning**; null `isbn13`; keep the raw text in an audit column | The real digits are permanently lost; nothing to verify a reconstruction against. |
| Right length/character set, wrong check digit, and no repair above applies | **Load with a warning**; null the field | Could be any digit — not safely correctable. |
| Invalid character (a letter where only a digit/trailing `X` belongs) | **Load with a warning**; null the field | Same reasoning. |
| Wrong length that isn't a leading-zero case | **Load with a warning**; null the field | No single deterministic correction. |
| 13-digit value with a valid checksum but a prefix other than 978/979 | **Load with a warning**; null the field | Not an ISBN-13 by definition, whatever its checksum says. |
| A valid ISBN-13 sitting in the `isbn` (ISBN-10) column | **Repair**: move the value into `isbn13`, null `isbn` (then the reverse-derivation row above may re-populate `isbn`) | Structural fix, not a value guess. |
| Both `isbn` and `isbn13` blank | **Load, with a warning** (`no-usable-isbn`) | The row is still fully identified by `goodreads_book_id` (section 2); the missing ISBN is still worth a human's attention. |
| A valid ISBN already belongs to a different `goodreads_book_id` on file | **Reject** the incoming row (`isbn-collision`) | One ISBN can't belong to two different books; the system won't choose between them. |
| A completely unparseable value (letters only, symbols, garbage) | **Load with a warning**; null the field | Not a repairable format. |
| A single field hits more than one of the above problems at once | **List every applicable reason, comma-separated** (e.g. `bad-prefix,bad-checksum`) | Don't hide a second real problem behind the first one found. |
| The row itself fails to parse as CSV (wrong field count, broken quoting) | **Reject the row**, reason recorded | The only case where the row — not just an ISBN field — is rejected. |

## 2. What makes two rows the same book?

**Identity is `goodreads_book_id` alone.** Every row carries one, it's
never blank, and it's unique — there is no "row with no usable identity"
case.

- `isbn`/`isbn13` are secondary, validated attributes, never the identity
  key.
- **Collision rule:** if a row's valid ISBN already belongs to a different
  `goodreads_book_id` already on file, the incoming row is rejected
  (`isbn-collision`), regardless of whether this row's own
  `goodreads_book_id` matches an existing record.
- No fuzzy title/author matching is ever used to decide identity.
- Title comparison is **case-insensitive**: lowercased, punctuation and
  extra whitespace stripped. A capitalization-only difference is never
  treated as a change, anywhere in this document.

## 3. What happens when a book already in the database arrives again?

Matching is by `goodreads_book_id`. Every other field falls into exactly
one of two camps:

**Volatile metadata — always updated, no review needed:**
`average_rating`, `ratings_count`, `work_ratings_count`,
`work_text_reviews_count`, `ratings_1`–`ratings_5`, `books_count`,
`image_url`, `small_image_url`, `best_book_id`, `book_id`.

**Identity-relevant fields — frozen once set:**
`title` (beyond case/whitespace), `authors`, `original_publication_year`,
`work_id`, `language_code`, `isbn`, `isbn13`.

| What's different | What happens |
|---|---|
| Nothing | **Skip**, logged as `duplicate-unchanged`. |
| A volatile-metadata field differs | **Update** that field; log the old → new diff. |
| An identity-relevant field was **empty** and the new row fills it | **Update** (fill-the-gap only) — the new value is validated the same way as on first load. |
| An identity-relevant field was **already populated** and the new row disagrees | **Reject** the incoming row (`identity-field-conflict`) and flag it for manual review; the existing record is left untouched. |
| An identity-relevant field was already populated and the new row is **blank** | No-op — missing information never erases existing information. |
| The incoming row's ISBN matches a different `goodreads_book_id` | **Reject** (`isbn-collision`, section 1/2). |
| The row itself fails to parse as CSV | **Reject**, reason recorded. |

## 4. What must the report say?

Every run reports exactly one of three states:

- **SUCCESS** — every row loaded with no warnings.
- **COMPLETED WITH ISSUES** — the run finished, but something was
  rejected or carries a warning. Never reported as a plain success.
- **FAILED** — the file couldn't be read, the header didn't match, or an
  error stopped the run partway through. This is a status label, not a
  rollback guarantee: rows loaded before the failure may already be saved,
  and the report says so explicitly whenever it reports FAILED. No
  atomicity guarantee is implemented for this pipeline.

On top of the status, every report includes:

- **Headline counts**, broken out separately: rows read, loaded, updated,
  skipped, rejected, and how many carried a warning.
- **A breakdown by problem category**, matching section 1's rows.
- **Per-row detail** for every row that wasn't a clean load: file, row
  number, title, the original offending value, which rule it hit, and
  exactly what the system did about it.
- **Old → new diffs** for every updated field.
- **Rejections kept visibly separate** from routine warnings.
- Every run **appends** one entry to the log; no prior entry is ever
  overwritten.

## 5. Database schema

Two tables:

- **`books`** — one row per `goodreads_book_id`. Columns: the 23 fields
  from the source CSV (`book_id`, `goodreads_book_id`, `best_book_id`,
  `work_id`, `books_count`, `isbn`, `isbn13`, `authors`,
  `original_publication_year`, `original_title`, `title`,
  `language_code`, `average_rating`, `ratings_count`,
  `work_ratings_count`, `work_text_reviews_count`, `ratings_1`–`ratings_5`,
  `image_url`, `small_image_url`), plus `identity_key` (mirrors
  `goodreads_book_id`, indexed), `fallback_key` (an informational
  normalized title+author string, not used for matching), `source_file`,
  `first_loaded_at`, `last_updated_at`.
- **`warnings`** — one row per warning: `book_row_id` (references
  `books.id`), `field`, `raw_value` (the original value, for audit),
  `reason` (one or more comma-separated codes), `recorded_at`.

`goodreads_book_id` and `identity_key` are both indexed.

## Operational details

- The CSV path is a fixed constant in `ingest.py` (`CSV_FILENAME`), not a
  command-line argument, so a run is always exactly reproducible from the
  file alone.
- Timestamps are ISO 8601 UTC.
- No network access, no AI, no randomness anywhere in the pipeline —
  every decision is pure, deterministic logic, so the same input file
  always produces the same result.

## Not implemented (explicitly out of scope)

- Publication-year validation (including BC/negative years), missing
  title/author handling, and language-code handling beyond passthrough.
- An external ISBN/metadata lookup step or any human-approval correction
  workflow.
- An atomicity/rollback guarantee on `FAILED` runs (see section 4).
