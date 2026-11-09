# Rules Comparison — Kristina vs. Anthony vs. Abigail

Sources: Kristina's `rules.md` (= `rules (1).md`, a duplicate save of the
same file), Anthony's `rules.md` pulled from
`fme5034/language-of-computation-week3-assignment` (`assignment` branch),
and Abigail's `rules-Abigail.md` pulled from
`ACRuby/language-of-computation-week3-assignment` (`assignment` branch).

No judgment is made anywhere below about which rule is "better" — only
whether the three documents agree, disagree, or whether only some of them
address a given point at all. Every table row is tagged with exactly one of
six statuses, used consistently throughout:

- **ALL AGREE** — all three address it, same answer.
- **ALL DIFFER** — all three address it, three different answers.
- **2 agree, 1 differs** — all three address it; two land on the same
  answer, one takes a different stance (named each time).
- **2 agree, 1 silent** — two address it and agree; the third doesn't
  address it at all.
- **2 disagree, 1 silent** — two address it and disagree with each other;
  the third doesn't address it at all.
- **1 only** — only one of the three addresses it at all.

---

## Summary numbers

| # | Metric | Count |
|---|---|---|
| 1 | Total number of rules/decisions identified across all three files | **63** |
| 2 | Total overlapping rules (addressed by 2 or more of the three) | **40** — 22 addressed by all three (7 full agreement, 9 "2 agree/1 differs", 6 "all differ"), and 18 addressed by exactly two (13 where those two agree, 5 where they disagree) |
| 3 | Total unique rules (addressed by exactly one person) | **23** — 2 unique to Kristina, 4 unique to Anthony, **17 unique to Abigail** |
| 4 | Rules flagged for discussion | **20 direct disagreements** (6 "all differ" + 5 "2 disagree/1 silent" + 9 "2 agree/1 differs"), plus several structural additions worth a group decision even though only one person's rules currently cover them (see §7) |

Abigail's file brings in far more unique material than Kristina's or
Anthony's (17 vs. 2 vs. 4) — mainly because her rules document a larger
process (a human-approval correction workflow, a three-tier run status,
year/author/language handling) that the other two don't touch at all. These
counts come directly from the 63 numbered rows in §1–§6 below, so they can
be checked by counting tags rather than taken on faith.

---

## 1. ISBN problem handling (repair / reject / warn)

| # | Decision | Kristina | Anthony | Abigail | Status |
|---|---|---|---|---|---|
| 1.1 | Already-valid ISBN | Load, no warning | Load, no warning; derives isbn13 as PK | Load; ISBN-10 always converted to isbn13, isbn10 kept as alternate | ALL AGREE |
| 1.2 | Hyphens/spaces/"ISBN" label | Repair: strip | Repair: strip | Repair: strip (incl. literal "ISBN" label text) | ALL AGREE |
| 1.3 | Lowercase trailing `x` in ISBN-10 | Not addressed | Repair: uppercase to `X` | Repair: uppercase to `X` | 2 agree, 1 silent (K) |
| 1.4 | ISBN-10 missing 1–3 leading zeros (7–9 digits) | Repair, only if checksum then passes | Repair, validate Mod-11 | Repair, only if check digit passes; not allowed beyond 3 missing zeros | ALL AGREE |
| 1.5 | ISBN-10 right length/charset, wrong check digit | Load with warning, null field | **Reject** (`BAD_CHECKSUM`) | Load with warning (ISBN unusable) | 2 agree (K, Ab: load+warn), 1 differs (A: reject) |
| 1.6 | `isbn13` scientific notation + valid ISBN-10 present | Repair: derive isbn13 from isbn10, unconditionally | Repair: reconstruct from isbn10 | Repair: derive from isbn10, **but only if it matches the rounded sci-notation number** | ALL AGREE (Abigail adds an extra verification step the others don't state) |
| 1.7 | `isbn13` scientific notation, no usable ISBN-10 | Load with warning; null isbn13; keep raw | **Reject** (`UNRECOVERABLE_ISBN13`) | Load with warning (ISBN unusable) | 2 agree (K, Ab), 1 differs (A: reject) |
| 1.8 | `isbn13` holds a non-book identifier (Nook/barcode/ISMN) | Not addressed | **Reject** (`NON_BOOK_IDENTIFIER`) | Load with warning (if no other usable ISBN) | 2 disagree (A reject vs. Ab warn), 1 silent (K) |
| 1.9 | Truncated `.0` value, digits actually missing | Not addressed | `.0` + 11+ digits → **reject** (`INVALID_LENGTH`) | ISBN unusable → load with warning | 2 disagree, 1 silent (K) |
| 1.10 | Full 13-digit value written with trailing `.0` | Not addressed | `.0` + 10 digits → column-inversion repair | Repair: strip `.0`, no digit change | 2 agree (both repair/strip `.0`, different digit-length cases), 1 silent (K) |
| 1.11 | ISBN-13 wrong checksum/length/letters/prefix | Load with warning, null field | **Reject** (`BAD_CHECKSUM`/`INVALID_LENGTH`/`CORRUPT_CHARACTERS`) | Load with warning (unusable) | 2 agree (K, Ab), 1 differs (A: reject) |
| 1.12 | `isbn`/`isbn13` individually valid but describe different editions | Not addressed | Keep one as canonical, other as `secondary_isbn*`, warn | Load with warning + review; **no ISBN stored at all** | 2 disagree (different outcomes), 1 silent (K) |
| 1.13 | **No usable ISBN at all** | **Load**, informational only (not even a warning) | **Reject** (`MISSING_ISBN`) — row discarded | **Load with warning** — identified by `goodreads_book_id` | **ALL DIFFER** — three genuinely different treatments of what's probably the single most common condition in the file |
| 1.14 | Meta-rule: can a bad ISBN field alone sink the whole row? | No — explicit governing principle | Yes — five reject codes are ISBN-only problems | No — explicit governing principle (row still has `goodreads_book_id`) | 2 agree (K, Ab), 1 differs (A) |
| 1.15 | Derive a missing ISBN-10 from a valid ISBN-13 | Not addressed | Repair rule ("Missing Counterpart") | Not addressed as a general rule | **1 only** (Anthony) |
| 1.16 | "Stripped-978" repair (recompute ISBN-10 check digit via ISBN-13 validity) | Not addressed | Repair rule | Not addressed | **1 only** (Anthony) |
| 1.17 | Corrupt / unparseable / out-of-range publication year | Not addressed | `CORRUPT_YEAR` → **reject**, range [-4000, 2100] | Non-whole-number or year 0 → drop field + warn (not reject); negative/BC years explicitly accepted | 2 disagree on severity (reject vs. warn), 1 silent (K) — though A and Ab agree in *effect* that negative/BC years are valid |
| 1.18 | Missing title | Not addressed | `MISSING_REQUIRED_FIELD` → reject | Reject | 2 agree (A, Ab: reject), 1 silent (K) |
| 1.19 | Missing or invalid `goodreads_book_id` | Not addressed (no such field in her schema) | Not addressed (no such field in his schema) | **Reject** — essential to her whole identity model | **1 only** (Abigail) — structurally significant, see §2 |
| 1.20 | Missing author | Not addressed | `MISSING_REQUIRED_FIELD` → reject | Load with warning | 2 disagree, 1 silent (K) |
| 1.21 | Missing publication year | Not addressed | Not clearly addressed | Load with warning | **1 only** (Abigail) |
| 1.22 | Whitespace repair on the *stored* title/author value itself | Only normalizes a separate informational matching key, not the stored value | Not addressed | Repair: strip extra spaces from the stored field | **1 only** (Abigail, for the stored value specifically) |
| 1.23 | Special characters / capitalization in titles | Not addressed | Not addressed | Keep as written | **1 only** (Abigail) |
| 1.24 | Missing language code | N/A (not in her schema) | N/A (not in his schema) | Accept, no warning | **1 only** (Abigail — structural) |
| 1.25 | A row triggering more than one problem at once | Not addressed (one themed reason) | List all applicable codes, comma-separated | Not explicitly addressed | **1 only** (Anthony) |

---

## 2. What makes two rows the same book?

| # | Decision | Kristina | Anthony | Abigail | Status |
|---|---|---|---|---|---|
| 2.1 | **What is the identity key?** | A valid ISBN alone (ISBN-13, or ISBN-10 converted) | Canonical ISBN-13, SQL primary key | **`goodreads_book_id`** is primary; ISBN is a secondary, validated attribute | 2 agree (K, A: ISBN is identity), 1 differs (Ab) — **this is the single most consequential disagreement in the whole comparison** |
| 2.2 | Can a book with no usable ISBN still be loaded/identified? | Yes — always loaded as new row | No — rejected outright, no fallback identity | Yes — identified by `goodreads_book_id` instead | 2 agree on outcome (K, Ab: row survives), 1 differs (A: discarded) — via different mechanisms |
| 2.3 | Fuzzy title/author matching as an identity fallback | Explicitly considered and rejected | Not addressed | Explicitly rejected ("same title alone never means the same book") | 2 agree, 1 silent (A) |
| 2.4 | Is title comparison case-insensitive? | Yes — lowercased before comparing | Yes — lowercased before comparing | **No** — "differing capitalization... REJECT and review" (capitals matter) | 2 agree (K, A), 1 differs (Ab) |
| 2.5 | Different valid ISBNs = different publications, even same title/author | Implied by ISBN-as-identity, not stated | Implied, not stated | Explicit rule (paperback vs. ebook stay separate) | **1 only** (Abigail states it explicitly; consistent with, not contradicting, K/A) |
| 2.6 | No-ISBN book sharing title+author with an existing record | New row created; a normalized key is stored for a human to review later, no active flag | Moot (no-ISBN rows are rejected) | New row created, **actively flagged "possible duplicate"** | 2 agree on outcome (K, Ab: not auto-merged), 1 silent (A) — Abigail's is an active flag, Kristina's a passive key |
| 2.7 | Exact duplicate rows within the same incoming file | Loads once/skipped | Explicit within-batch dedup, skip | Loads once, later copies UNCHANGED | ALL AGREE |

---

## 3. What happens when a book arrives again?

| # | Decision | Kristina | Anthony | Abigail | Status |
|---|---|---|---|---|---|
| 3.1 | Identical row arrives again | Skip, "duplicate, no changes" | Skip (`rows_skipped_already_exists`) | UNCHANGED, existing record untouched | ALL AGREE |
| 3.2 | A previously-empty field is now filled | Update (part of the general "any substantive field" rule) | Update, but **only** fills a NULL field on a 3-column whitelist | Update after validation; broader — any of author/year/original title/language/ISBN | 2 agree broadly (K, Ab), 1 narrower (A: whitelist only) |
| 3.3 | A non-empty field changes to a different non-empty value (e.g. corrected title, increased rating) | **Update** — title and rating explicitly named as examples | Not really addressed — his whitelist only covers NULL-filling | **Split by field**: ratings/metadata → update; title/author/year/`work_id`/language → **reject + review** | **ALL DIFFER** |
| 3.4 | Can the ISBN on an existing record ever change? | Yes — explicitly an update trigger, re-validated like fresh input | Narrow — `isbn13` (PK) immutable, but `isbn10`/`secondary_isbn10` are updatable | **Never** — any ISBN change is reject + review, full stop | **ALL DIFFER** |
| 3.5 | Same ISBN, different title, on re-arrival | Collision, reject — not an update | `ISBN_COLLISION_DIFFERENT_TITLE`, reject | Title change (beyond whitespace) → reject + review | ALL AGREE (all three reject rather than silently update) |
| 3.6 | Within-batch duplicate vs. already-in-db duplicate as separate tracked categories | One bucket | Explicit two buckets, within-batch checked first | Not named as two buckets (though her idempotency guarantee implies it operationally) | **1 only** (Anthony, as an explicit rule) |
| 3.7 | Audit trail for every change | Required: log old→new per field (report requirement) | Only the `warning` column is append-only; no general change log | Full audit log: import id, row, field, old/new, reason, time, auto/manual, source file | 2 agree a full trail is required (K, Ab), 1 narrower (A) |
| 3.8 | No-ISBN book re-arriving a second time | Always a new row, no dedup decision | Moot (rejected both times) | Matched by `goodreads_book_id` if genuinely the same; flagged possible-duplicate if only title/author match | 2 agree (K, Ab: never silently merged), 1 silent (A) |
| 3.9 | Idempotency guarantee for re-running the same file, stated explicitly | Not named as a guarantee (implied) | Not named as a guarantee | Explicit, with a worked example ("200 UNCHANGED, 0 CREATED") | **1 only** (Abigail) |
| 3.10 | Rejected rows can be corrected and resubmitted, linked to the original | Not addressed | Not addressed | Explicit workflow | **1 only** (Abigail) |

---

## 4. What must the report say?

| # | Decision | Kristina | Anthony | Abigail | Status |
|---|---|---|---|---|---|
| 4.1 | One unambiguous top-level verdict | Required: "everything loaded" or "N rows in holding" | Not addressed | Required: three named states — SUCCESS / COMPLETED WITH ISSUES / **FAILED** | 2 agree on the requirement (K, Ab), 1 silent (A) — Abigail's is more elaborate |
| 4.2 | Whole-run failure (unreadable file, missing columns) — what happens to the database? | Not addressed | Not addressed | **Explicit**: FAILED status, nothing saved, db never left half-loaded | **1 only** (Abigail) — a real gap in both K's and A's rules |
| 4.3 | Headline counts broken out by outcome | Required: processed/clean/warned/updated/skipped/rejected | Only implied by counter names, not stated as a requirement | Required: CREATED/UPDATED/UNCHANGED/REJECTED with a stated sum invariant; warned/repaired counted as separate orthogonal tags | 2 agree on requirement (K, Ab), 1 silent (A) — bucket organization differs between K and Ab too |
| 4.4 | Breakdown by problem category with counts | Required | Not addressed as report requirement | Required | 2 agree, 1 silent (A) |
| 4.5 | Per-row actionable detail | File, row #, title/author, original value, rule hit, action taken | Not addressed | Same, plus **"what the librarian should do"** | 2 agree, 1 silent (A) — Abigail adds one more element |
| 4.6 | "What to do next" summary | Part of the bottom-line requirement | Not addressed | Explicit "Actions required" list | 2 agree, 1 silent (A) |
| 4.7 | Downloadable rejected-rows / all-issues files | Not addressed | Not addressed | Explicit — two CSVs | **1 only** (Abigail) |
| 4.8 | Update diff logging (old→new per field) | Required | Only implied by append-only warning column | Required, kept in a separate audit log | 2 agree, 1 silent/narrower (A) |
| 4.9 | Visual separation of urgent/rejected items from routine warnings | Required | Not addressed | Achieved differently (status tiers + separate export), not stated as its own rule | 2 address it in substance (K, Ab), 1 silent (A) |

---

## 5. Schema and other structural/operational rules

| # | Decision | Kristina | Anthony | Abigail | Status |
|---|---|---|---|---|---|
| 5.1 | What columns/tables exist? | `books` + `warnings` tables; clearly includes rating-type metadata | Single `books` table: isbn13 (PK), isbn10, title, authors, publication_year, secondary_isbn10/13, raw_isbn/13, warning — **no ratings/metadata, no goodreads_book_id** | Implies the full goodbooks-10k column set: `goodreads_book_id`, `book_id`, `work_id`, isbn/isbn13 (+alt), title, authors, original_title, language_code, year, ratings_count, average_rating, books_count, image URL, best_book_id | **ALL DIFFER** — needs deciding before anyone writes a `CREATE TABLE` |
| 5.2 | Primary key / identity column | No surrogate key; ISBN functions as identity | `isbn13` is the literal SQL primary key | `goodreads_book_id` is the primary key; isbn13 is secondary | **ALL DIFFER** (same split as §2.1, at the schema level) |
| 5.3 | Mechanism for tracking discarded/corrupted raw input | Generic raw-value audit column | Named `raw_isbn`/`raw_isbn13` columns | Separate audit-log table, not inline columns | ALL DIFFER on mechanism (all three agree provenance tracking is *needed*) |
| 5.4 | Timestamp format | ISO 8601 UTC | Not specified | Not specified | **1 only** (Kristina) |
| 5.5 | Is the CSV path fixed, or a CLI argument? | Fixed filename | Not specified | Not specified the same way (her separate lookup script does take a file) | **1 only** (Kristina) |

---

## 6. External lookup & human-approved correction workflow — unique to Abigail

Kristina's and Anthony's rules.md files have no equivalent of any of this —
there's no second script, no external API, and no human-approval step
anywhere in either document. All seven items below are **1 only
(Abigail)**.

| # | Decision | Abigail's rule |
|---|---|---|
| 6.1 | A separate, human-run lookup step (`lookup_isbns.py`) against Open Library for ISBN/year-warning rows | Rate-limited (1 req/sec), identifies itself, caches results, Amazon excluded (ToS); only ever *suggests* |
| 6.2 | Human-approval file (`isbn-corrections.csv`) | Named approval columns; a row with no `approved_by` name is ignored entirely |
| 6.3 | Scope of a correction | Only fills a gap, never overwrites a valid existing value; must itself pass the same ISBN/year validation rules as any other input |
| 6.4 | Approved correction collides with another book's ISBN | Same reject-and-review rule as any other ISBN collision (reuses §2's rule) |
| 6.5 | Ebook/self-published books with no ISBN | May be approved to pass without one, surfaced as a **"note"** — a new status tier that is neither a warning nor silent |
| 6.6 | Traceability | Every correction's source, approver, and old/new value recorded in the audit log |
| 6.7 | A broken/unreadable corrections file | Stops the whole run (FAILED), same as a broken book file |

---

## 7. Example-table walkthroughs

Kristina's `rules.md` has a 16-row example table; Abigail's has a 29-row
one; Anthony's has none (his worked examples live in `data-validation.md`,
cited by line number, not collected into a table). This section runs each
person's own examples through the *other* two people's rules.

### 7A. Kristina's 16 examples, under Anthony's and Abigail's rules

| # | ISBN example | Kristina's outcome | Anthony's outcome | Abigail's outcome | Same or different? |
|---|---|---|---|---|---|
| 1 | `0439023483` (valid ISBN-10) | Load, no warning | Load, no warning | Load, no warning | Same |
| 2 | `439023483` (9-digit, leading zero lost) | Repair → zero-pad, load clean | Repair → zero-pad, load clean | Repair → zero-pad, load clean | Same |
| 3 | `9.78043902348e+12` (isbn13 float, valid isbn present) | Repair → derive isbn13, load clean | Repair → reconstruct isbn13, load clean | Repair → derive isbn13 (matches rounded value), load clean | Same |
| 4 | `9.78067172365e+12` (isbn13 float, no usable isbn) | Load with warning; isbn13 nulled, raw kept | **Reject** the row | Load with warning; no ISBN stored | **Different** (Anthony only) |
| 5 | `04390A3483` (letter in digit position) | Load with warning; isbn nulled | **Reject** the row | Load with warning | **Different** (Anthony only) |
| 6 | `1854433017` (wrong check digit) | Load with warning; isbn nulled | **Reject** the row | Load with warning | **Different** (Anthony only) |
| 7 | `15287463097` (11 digits) | Load with warning; isbn nulled | **Reject** the row | Load with warning | **Different** (Anthony only) |
| 8 | `9781982147600` found in `isbn` column | Repair → move to isbn13, load clean | Repair → Column Inversion, load clean | **Not addressed** — her rules have no cross-column-inversion repair at all | **Different** (Abigail's rules have a gap here) |
| 9 | `0-450-19827-8` (valid, hyphenated) | Repair → strip, load clean | Repair → strip, load clean | Repair → strip, load clean | Same |
| 10 | `` (empty isbn/isbn13) | **Load**, informational only | **Reject** the row | **Load with warning** | **All three different** |
| 11 | `9999999999999` (fails isbn13 checksum) | Load with warning; isbn13 nulled | **Reject** the row | Load with warning | **Different** (Anthony only) |
| 12 | `ABCDEFGHIJ` (non-numeric) | Load with warning; isbn nulled | **Reject** the row | Load with warning | **Different** (Anthony only) |
| 13 | `1416524797` twice, two different titles | Reject the 2nd arrival | Reject the 2nd arrival | Reject the 2nd arrival (different `goodreads_book_id`, same reasoning path as a collision) | Same outcome |
| 14 | `978-0-13-468599-1` (valid, hyphenated) | Repair → strip, load clean | Repair → strip, load clean | Repair → strip, load clean | Same |
| 15 | Same isbn/title, `ratings_count` increased | **Update**; log old→new diff | Treated as unchanged → **skip** (`ratings_count` isn't even a column in his schema) | **Update**; logged (ratings-type fields are explicitly in her always-updatable bucket) | **Different** (Anthony only) |
| 16 | 25-field row against a 23-field header | Reject whole row | Reject whole row (`MALFORMED_ROW`) | **Not addressed** — no column-count-mismatch rule stated | Same outcome for K/A; gap in Abigail's rules |

**10 of Kristina's 16 examples land differently, or expose a gap, under at
least one other person's rules** (#4, 5, 6, 7, 8, 10, 11, 12, 15, 16); the
other 6 (#1, 2, 3, 9, 13, 14) land the same way under all three.

### 7B. Abigail's 29 examples, under Kristina's and Anthony's rules

Examples #25–29 test Abigail's human-approved-correction workflow (§6),
which simply doesn't exist in Kristina's or Anthony's rules — there's no
equivalent concept to apply, so those five are marked **N/A** rather than
"different."

| # | Example (abbreviated) | Abigail's outcome | Kristina's outcome | Anthony's outcome | Same or different? |
|---|---|---|---|---|---|
| 1 | `0439023483`, valid | Load clean | Load clean | Load clean | Same |
| 2 | `043965548X`, valid w/ `X` | Load clean | Load clean | Load clean | Same |
| 3 | `043965548x`, lowercase `x` | Repair → `X` | Not addressed — does her "already valid" rule accept lowercase `x`? Ambiguous | Repair → `X` | Possible gap (Kristina) |
| 4 | `439023483`, missing 1 zero | Repair → zero-pad | Repair → zero-pad | Repair → zero-pad | Same |
| 5 | `7442912`, missing 3 zeros | Repair → zero-pad | Repair → zero-pad (within her 7–9 digit range) | Repair → zero-pad | Same |
| 6 | `12345`, too short to repair | Load with warning | Load with warning (falls to "wrong length") | **Reject** (`INVALID_LENGTH`) | **Different** (Anthony) |
| 7 | `1847386823`, wrong check digit | Load with warning | Load with warning | **Reject** (`BAD_CHECKSUM`) | **Different** (Anthony) |
| 8 | `385535144`, fails after zero-restore | Load with warning | Load with warning (falls through after failed repair) | **Reject** (`BAD_CHECKSUM`) | **Different** (Anthony) |
| 9 | `ABC123`, invalid characters | Load with warning | Load with warning | **Reject** (`CORRUPT_CHARACTERS`) | **Different** (Anthony) |
| 10 | `978-0-439-02348-1`, hyphenated | Repair → strip | Repair → strip | Repair → strip | Same |
| 11 | `ISBN 978 0 439 02348 1`, label + spaces | Repair → strip label and spaces | Her rule only names "hyphens/spaces" — a text label isn't explicitly covered | His rule only names "whitespace and hyphens" — same gap | Possible gap (both K and A) |
| 12 | `9780439023482` in isbn13, wrong check digit | Load with warning | Load with warning | **Reject** (`BAD_CHECKSUM`) | **Different** (Anthony) |
| 13 | `9770439023481`, prefix 977 (not 978/979) | Explicitly flagged unusable (prefix check) | **No prefix check stated at all** — if the checksum happens to pass, her rules as written would treat it as a valid ISBN-13 and load it clean | No prefix check stated either — same gap | Notable gap shared by Kristina and Anthony |
| 14 | `9791032305690`, valid 979-prefix, no isbn10 form | Load clean, no isbn10 | Load clean | Load clean (his isbn10-derivation rule is correctly scoped to 978-prefix only, so it's skipped here) | Same |
| 15 | sci-notation isbn13 matching derived value | Repair | Repair | Repair | Same |
| 16 | sci-notation isbn13, naive rounding would mislead | Repair (derives from isbn10, sidesteps the misleading rounded digits) | Repair (same approach — derives from isbn10 directly) | Repair (same approach) | Same |
| 17 | sci-notation isbn13, isbn10 empty | Load with warning, no ISBN | Load with warning; isbn13 nulled | **Reject** (`UNRECOVERABLE_ISBN13`) | **Different** (Anthony) |
| 18 | Nook code in isbn13, isbn10 empty | Load with warning, no ISBN | Load with warning (via her generic "unusable sci-notation" rule — Kristina has no specific non-book-identifier category) | **Reject** (`NON_BOOK_IDENTIFIER`) | **Different** (Anthony) |
| 19 | Truncated `.0`, 11 digits visible | Load with warning | Load with warning (generic "wrong length") | **Reject** (`INVALID_LENGTH`) | **Different** (Anthony) |
| 20 | isbn/isbn13 describe different editions | Load with warning + review, no ISBN stored | **Not addressed at all** | Keeps one as canonical, other as secondary, loads with warning | **Different** (Anthony); gap (Kristina) |
| 21 | Both ISBN fields empty | Load with warning | **Load**, not even a warning | **Reject** the row | **All three different** |
| 22 | Same isbn again, identical data | UNCHANGED | Skip, duplicate | Skip, already-exists | Same |
| 23 | Same isbn13, **different** `goodreads_book_id`, title unstated/presumably unchanged | **Reject** + review (goodreads_book_id mismatch is itself the collision) | If the title is unchanged, her rules never look at `goodreads_book_id` at all — this would just be treated as an ordinary repeat/update, **not rejected** | Same — his rules don't check `goodreads_book_id` either, so an unchanged title means no collision is triggered | **Different** — Abigail's `goodreads_book_id`-based identity catches a conflict that Kristina's and Anthony's ISBN-only identity would miss entirely |
| 24 | Same isbn, same `goodreads_book_id`, **title changed** | **Reject** + review (identity-relevant field changed) | **Update** the title — it's explicitly named as a substantive, correctable field | **Reject** (`ISBN_COLLISION_DIFFERENT_TITLE`) — his rules don't distinguish "a correction" from "a different book" | **Different** — Kristina updates exactly the case Anthony and Abigail both reject |
| 25 | Correction fills a gap ISBN | Repair from approved correction | N/A — no correction workflow | N/A — no correction workflow | N/A |
| 26 | Approved "ebook, no ISBN needed" | Passes as a note, not a warning | N/A | N/A | N/A |
| 27 | Valid isbn + conflicting correction | Correction ignored, valid isbn kept | N/A | N/A | N/A |
| 28 | Malformed/Excel-mangled correction | Correction fails validation, ignored | N/A | N/A | N/A |
| 29 | Suggested isbn, no approver name | Ignored (not approved) | N/A | N/A | N/A |

**12 of Abigail's 29 examples (#6, 7, 8, 9, 12, 17, 18, 19, 20, 21, 23, 24)
land differently** under Kristina's and/or Anthony's rules; **3 more (#3,
11, 13) expose possible gaps** rather than a clean disagreement; and **5
(#25–29) don't apply at all**, since the correction-approval workflow they
test only exists in Abigail's rules.

Two of these are worth calling out by name for the meeting: **#23 and #24**
are a clean, concrete demonstration of the §2.1 identity-model split — #23
shows a conflict that only Abigail's `goodreads_book_id`-based identity
would catch; #24 shows Kristina updating exactly the case that both Anthony
and Abigail treat as a reject-worthy conflict.

## 8. Rules flagged for discussion

The goal of today's meeting is picking **one** shared rules.md. These are
grouped by how big a decision they are, not by document.

### The one that changes everything else
- **§2.1 / §5.1 / §5.2 — what identifies a book?** Kristina and Anthony both
  center identity on ISBN; Abigail centers it on `goodreads_book_id`, with
  ISBN as a secondary, validated attribute. This isn't one rule among many —
  it's upstream of almost every other decision (whether a no-ISBN book can
  be loaded at all, what counts as a duplicate, what the schema's primary
  key is, whether title changes get rejected or updated). Decide this one
  first; several of the items below are downstream of it.

### The ISBN-problem philosophy split
- **§1.5, 1.7, 1.11, 1.14 (and the pattern across 1.8/1.9/1.12/1.17/1.20)** —
  Kristina and Abigail agree that a bad-but-isolated ISBN problem should
  load the row with a warning, never reject it outright; Anthony's rules
  reject the row for several of those same situations. This single
  "repair/warn-and-keep vs. reject-and-discard" question drives most of the
  disagreements in this document.
- **§1.13 — no usable ISBN at all.** All three genuinely differ: Kristina
  loads it silently (not even a warning), Abigail loads it with a warning,
  Anthony rejects it outright. Given how common this condition likely is in
  the real dataset, this alone could make the three resulting databases
  wildly different sizes.

### Update semantics
- **§3.3 / §3.4 — what counts as "this book changed," and can ISBN ever
  change on an existing record?** Three different answers each. Needs a
  concrete, field-by-field decision (which fields are ever updatable, and
  under what condition) before anyone writes tests for this behavior.

### Schema
- **§5.1 — what columns exist at all?** Anthony's schema has no ratings/
  metadata columns and no `goodreads_book_id`; Abigail's implies the full
  source column set; Kristina's is in between. Settle this before writing a
  `CREATE TABLE` statement.

### Comparison mechanics
- **§2.4 — is title comparison case-insensitive?** Kristina and Anthony both
  lowercase before comparing; Abigail treats a capitalization change as a
  reportable conflict. Minor-sounding, but it changes how many rows get
  flagged for review.

### Worth adopting regardless of who "wins" the core splits
- Anthony's extra repair rules (§1.15, 1.16) and his multi-code reporting
  (§1.25) are additions, not conflicts.
- Abigail's handling of publication year, missing title/author, and
  language code (§1.17, 1.18, 1.20, 1.21, 1.24) covers real problem
  categories neither Kristina's nor Anthony's rules considered at all.
- Abigail's atomicity guarantee (§4.2 — a failed run saves nothing) is a
  real gap in both other documents, independent of any other disagreement.
- The external lookup/correction workflow (§6) is a substantial process
  addition, not a tweak — worth a clear yes/no from the group on whether
  it's in scope for this assignment at all, separate from the rules-merging
  discussion itself.
