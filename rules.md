# Rules for loading `books.csv` / `books-batch2.csv`

These are the rules Claude should build the loader from in Part 4. They're
based on the problems actually found and catalogued in
[`data-validation.md`](data-validation.md) and the correction work in
[`isbn-correction-notes.md`](isbn-correction-notes.md).

## 1. For each kind of problem: repair, reject, or load with a warning?

The one rule underneath all of these: **a repair is only allowed when it is
deterministic and checksum-verifiable — when there is exactly one possible
correct value, and the checksum proves we found it.** The moment fixing a
value means picking among several plausible originals, it stops being a
repair and becomes a guess, and guesses never get written into the data as
if they were facts.

| Problem | Action | Why |
|---|---|---|
| Already a valid ISBN-10 or ISBN-13 | **Load, no warning** | Nothing to fix. |
| Valid, but formatted with hyphens/spaces (e.g. `0-450-19827-8`) | **Repair** (strip separators, store the plain digit form) | Purely cosmetic; stripping separators doesn't change the value, and the checksum still passes before and after. |
| `isbn` with leading zero(s) stripped (7–9 digits, all-numeric) | **Repair**: zero-pad to 10 digits | Deterministic: there's only one way to get from a 9-digit number to a 10-digit ISBN-10 by padding, and the checksum confirms it's right. Only apply if the padded result actually passes the checksum — if it doesn't, fall through to the next row. |
| `isbn13` stored as scientific notation / float (e.g. `9.78e+12`) **and** that row has a valid (or repaired) `isbn` | **Repair**: re-derive `isbn13` from the `isbn` using the standard `978` + check-digit formula | The truncated float text is unrecoverable on its own — but a valid ISBN-10 deterministically produces exactly one correct ISBN-13, so deriving it is not a guess. The corrupted text is discarded, not patched. |
| `isbn13` stored as scientific notation / float **and** no usable `isbn` in that row | **Load with a warning**; set `isbn13` to null, keep the original raw text in an audit column | The real digits are permanently lost from this file; there is nothing to verify a reconstruction against. Flag it for a human to look up against an authoritative source rather than fabricate a value. |
| Right length/character set, wrong check digit (e.g. `1854433017`) | **Load with a warning**; null the field, keep the raw value in an audit column | A single mistyped digit could be any of several digits — there's no way to know which one without an outside source. Repairing this would be a guess. |
| Invalid character (a letter where only a digit/trailing `X` belongs, e.g. `04390A3483`) | **Load with a warning**; null the field | Same reasoning — could be any digit; not safely correctable. |
| Wrong length that isn't a leading-zero case (e.g. 11 digits) | **Load with a warning**; null the field | No single deterministic correction (don't know which digit is extra/missing). |
| A valid ISBN-13 sitting in the `isbn` (ISBN-10) column | **Repair**: move the value into `isbn13`, null `isbn` | This is a structural fix, not a value guess — the checksum proves the value really is a valid ISBN-13, so it belongs in that column, not the other one. |
| Empty `isbn`/`isbn13` | **Load**, informational only (not a warning) | Missing data isn't corruption. The row is always loaded as new — see §2 for why no automatic matching is attempted for it. |
| An incoming row's (valid) ISBN matches a book already on file, but the title is different | **Reject** the incoming row | A human needs to resolve which one is actually right — loading it anyway would mean two different books occupy the same ISBN identity in the database. The row already on file keeps that ISBN; anything that collides with it and doesn't match its title is rejected, not merged. *(See the Q&A appendix — this overrides an earlier draft of this rule that said "load both with a warning.")* |
| A completely unparseable value (letters only, symbols, garbage) | **Load with a warning**; null the field | Not a format we can repair at all; null it, keep the row, keep the raw value for review. |
| The row itself fails to parse as CSV (wrong number of fields, broken quoting) | **Reject the row**, with the reason recorded in a dedicated rejection-reason column | This is the one case that *does* reject a whole row — the row isn't readable as data at all, so there's no "rest of the row" to preserve. |

Across the board: **the row is never rejected just because one ISBN field is
bad on its own.** Rejecting the whole row throws away everything else we do
know about the book (title, author, ratings), so a bad `isbn`/`isbn13` value
only nulls that one field and loads the row with a warning attached. A row is
only ever rejected outright for the two reasons above: the CSV itself didn't
parse, or its ISBN collides with a different book already on file.

## 2. What makes two rows the same book? What if there's no usable ISBN?

Identity is decided by **a valid ISBN alone** — a valid ISBN-13, or a valid
ISBN-10 converted to its ISBN-13 form when that's all a row has. That's the
only thing the loader uses to automatically decide "this is a book I already
have."

**A book with no usable ISBN is never matched against anything
automatically — it is always loaded as a new row.** I considered falling
back to a normalized title + author match for these, and explicitly rejected
it: it's too easy for a fuzzy match like that to merge two different books
that happen to share a title and author, or to miss a real match because the
title was typed slightly differently. Rather than risk a silent wrong merge,
**cross-run matching for books with no ISBN is left entirely to a human.**

To make that manual review possible, every row still gets a normalized
**title + primary author** key stored alongside it (lowercased, punctuation
and extra whitespace stripped; author reformatted as `Surname, Given`) — but
that key is informational only. The loader never reads it back to decide
skip/update/reject for anything.

One consequence worth stating plainly: **re-running a file that contains
no-ISBN books will insert them again, every time, as new rows.** That's
accepted, not a bug — deduplicating those is a human's job, not the
script's.

## 3. What happens when a book already in the database arrives again?

- **Same identity key, identical data** → treat as a true duplicate: skip
  the insert, don't create a second row, log it as
  `duplicate, no changes — skipped` (not an error, not a warning — this is
  expected and fine).
- **Same identity key, some fields differ** (e.g. an updated rating count, a
  corrected title, or an ISBN that was previously missing and now has a
  value) → treat as an **update**, not a new row. Keep the existing row's
  internal ID, update only the fields that changed, validate any newly
  arriving ISBN the same way as on first load before accepting it, and log
  exactly what changed (`field, old value → new value`) so there's an audit
  trail.
- **Same ISBN, but the title is different** → this isn't treated as the
  "same book, something changed" case at all — it's a collision (§1), and
  the incoming row is rejected rather than merged or updated.
- **A book with no usable ISBN, seen again** → there's no comparison to make
  (§2) — it's always inserted as a brand-new row, every time, whether that's
  a genuine re-run of the same file or a real second copy of the book. No
  skip/update/reject decision happens for these; a human cleans up the
  duplicates later.

## 4. What must next-morning's report tell the reader?

It has to answer, without the reader needing to re-run anything:

- **The headline numbers**: rows processed, loaded clean, loaded with a
  warning, updated, skipped as duplicates, and rejected outright — each
  broken out separately, not lumped together. Rejection only ever happens
  for two reasons (a structural CSV parse failure, or an ISBN collision with
  a different title already on file), so each rejected row should carry
  which of those two it was.
- **A breakdown by problem category** (matching the categories in
  `data-validation.md`/§1 above) with a count for each — not just "37
  warnings," but "19 unrecoverable ISBN-10s, 12 bad checksums, 6 ISBN
  collisions," etc.
- **Enough detail to act on every non-clean row without re-running the
  pipeline**: file, row number, title/author, the original offending value,
  which rule it hit, and exactly what the system did about it (repaired to
  what value / nulled with what warning / rejected and why).
- **What changed on updates** — the old-value → new-value diff for every
  updated field, not just "12 rows updated."
- **Rejections and anything else that needs a person today, kept visibly
  separate from routine warnings** — e.g. a rejected ISBN collision between
  two titles, or a structurally unreadable row — versus things that are just
  FYI (a missing ISBN that was always missing).
- **One unambiguous bottom line at the top**: either "everything that could
  be safely loaded is loaded, nothing needs attention," or "N rows are in a
  holding area, here they are" — the reader should never have to infer
  completeness themselves from the counts.

## Example table (≥12 ISBNs and what the rules say happens to them)

| # | ISBN value | Source | What the rules say happens |
|---|---|---|---|
| 1 | `0439023483` | real (`books.csv`, *The Hunger Games*, already corrected) | Valid ISBN-10 → **load, no warning**. |
| 2 | `439023483` | real (`books.csv`, raw, 9 digits) | Leading zero lost, pads to a checksum-valid 10 digits → **repair** to `0439023483`, load clean, note "zero-padded." |
| 3 | `9.78043902348e+12` | real (`books.csv`, raw `isbn13`, same row as #2) | Float-corrupted, but row has a valid `isbn` → **repair**: derive `9780439023481` from the ISBN-10, load clean. |
| 4 | `9.78067172365e+12` | real (`books.csv`, *How to Win Friends and Influence People*, `isbn` empty on that row) | Float-corrupted, no ISBN-10 to derive from → **load with warning**, `isbn13` set to null, raw value kept in an audit column. |
| 5 | `04390A3483` | real (`books-batch2.csv`, *The Glass Aviary*) | Letter in a digit position → **load with warning**, `isbn` nulled, flagged `invalid-characters`. |
| 6 | `1854433017` | real (`books-batch2.csv`, *Small Hours*) | Right length/charset, wrong check digit → **load with warning**, `isbn` nulled, flagged `bad-checksum`. |
| 7 | `15287463097` | real (`books-batch2.csv`, *Borrowed Light*) | 11 digits, not a leading-zero case → **load with warning**, `isbn` nulled, flagged `wrong-length`. |
| 8 | `9781982147600` (found in the `isbn` column) | real (`books-batch2.csv`, *An Atlas of Small Kindnesses*) | Fails as ISBN-10, but passes as ISBN-13 → **repair**: move it into `isbn13`, null `isbn`, load clean, note "moved from isbn column." |
| 9 | `0-450-19827-8` | real (`books-batch2.csv`, *Salt and Ember*) | Valid once hyphens are stripped → **repair** (reformat only), load clean. |
| 10 | `` (empty) | real (many rows) | No ISBN → **load** as a new row; no automatic matching is attempted (§2) — a normalized title+author key is stored for a human to use later, but every re-run inserts this row again. |
| 11 | `9999999999999` | made up | 13 digits, fails the ISBN-13 checksum → **load with warning**, `isbn13` nulled, flagged `bad-checksum`. |
| 12 | `ABCDEFGHIJ` | made up | Not numeric at all → **load with warning**, `isbn` nulled, flagged `invalid-characters`. |
| 13 | `1416524797` arriving twice for two different titles | real (`books-batch2.csv`, rows 21 & 24, *Angels & Demons* vs *Paper Moons*) | Same valid ISBN already on file under *Angels & Demons* → **reject** the second arrival (*Paper Moons*), flagged `isbn-collision`; the first-loaded row is untouched. |
| 14 | `978-0-13-468599-1` | made up | Valid ISBN-13 with hyphens → **repair** (strip separators), load clean. |
| 15 | `9780439023481` on a row where that book's `ratings_count` is higher than what's already on file | made up, based on real row (*The Hunger Games*) | Same ISBN, same title, a substantive field changed → **update** the existing row (not a new insert), log the old → new diff for `ratings_count`. |
| 16 | a data row with 25 comma-separated fields where the header has 23 | made up | The row itself doesn't parse against the expected structure → **reject the whole row**, reason `structural-parse-error` (the one case where the *row*, not just an ISBN field, is rejected). |

## Appendix: clarifying Q&A (2026-11-05)

Before `ingest.py` was written, a round of questions resolved everything the
sections above don't spell out on their own. Recorded here verbatim (my
answers lightly trimmed for length) so the reasoning stays attached to the
rules instead of living only in chat history. Where an earlier answer below
was later overridden by a more specific one, the later answer is what's
reflected in sections 1–4 above; both are kept here for the full trail.

**Round 1**

- **Q: What should the database schema look like?**
  A: I want a `books` table and a separate `warnings` table. I want a
  column to hold the original raw value when a field gets nulled, to record
  why.
- **Q: Your rules never reject a whole row — but the log needs a "rejected"
  count. What causes a rejection?**
  A: Reject if my rules do not cover all of the structural problems.
  Provide a reason in a column dedicated to the rejection reason. You may
  group rejection reasons into themes.
- **Q: Which fields count as "something about it changed" for deciding
  skip vs. update?**
  A: Update on substantive columns like ratings/isbn/title.
- **Q: For a book with no usable ISBN, does matching happen automatically,
  or only the flag?**
  A: Flag only. A book with no ISBN is always loaded as a new row, with
  cross-run matching left entirely to a human.
- **Q: Where do ISBN-collision conflicts land in the log's five buckets?**
  A: Rejected bucket.
- **Q: How exactly is "primary author" defined?**
  A: Primary author should be last name, then comma, then first name or
  initials. In the title column, strip punctuation and whitespace.
- **Q: Timestamp format? Is the CSV path a CLI argument?**
  A: ISO 8601 UTC. The CSV file path is a fixed filename, not a
  command-line argument.

**Round 2** — these answers resolved a direct contradiction the round-1
answers left behind: "update on title changes" (round 1) vs. the worked
example of two different titles sharing one ISBN, which round 1 had already
sent to the rejected bucket. Round 2 is the deciding word on all four points
below.

- **Q: When an incoming row's ISBN matches an existing row's ISBN exactly,
  but the title is different — always a rejected collision, or always a
  title-update?**
  A: Always a rejected collision — the title mismatch overrides the
  "title changed → update" rule.
- **Q: For no-ISBN rows, is there ever automatic matching (e.g. an exact
  full-row match on a trivial re-run), or truly none at all?**
  A: Truly zero automatic matching, ever. Re-running a file with no-ISBN
  books is expected to pile up duplicates — that's the human's job to clean
  up, not the script's.
- **Q: Does "structural problem" mean only CSV-parse failures, or also any
  non-ISBN content problem (empty title, bad rating count, etc.)?**
  A: Only rows where the CSV itself fails to parse correctly — wrong number
  of fields, broken quoting.
- **Q: Confirm the exact primary-author parsing rule.**
  A: Take the first author listed in `authors` (before the first top-level
  comma), split that name on whitespace, treat the last token as the
  surname and everything before it as the given name/initials, and
  reformat as `Surname, Given`.
