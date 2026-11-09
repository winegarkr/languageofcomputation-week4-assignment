# Agreed rules for loading `books.csv` / `books-batch2.csv`

This is the **one shared `rules.md`** for the group (Kristina, Anthony,
Abigail), merged from the three independent versions per the decisions made
in the 2026-11-06 rules-merge meeting. Every rule below traces back to one
of two places:

- a numbered **Decision** from the meeting (see
  [`rules-comparison.md`](rules-comparison.md) for the full three-way
  comparison those decisions were made against), or
- an **Open item** the group voted to implement or skip.

One pair of decisions from the meeting directly conflicted with each other
— that's called out and resolved explicitly rather than silently, see
**Resolved conflict** below, instead of just picking a side with no record
of it.

## 0. What changed from each person's original rules.md

| Area | Decision | Outcome |
|---|---|---|
| Book identity | Decision 1 | **`goodreads_book_id`** (Abigail's model) — not ISBN |
| Bad-but-isolated ISBN problems | Decision 2 | **Load, warn, null the field** (Kristina's model) — never reject the row for this alone |
| No usable ISBN at all | Decision 3 | **Load with a warning** (Abigail's model) — not silent, not rejected |
| Update semantics | Decision 4 | **Abigail's two-camp split**: volatile metadata updates freely; identity-relevant fields reject + flag on conflict |
| Database schema | Decision 5 | **Kristina's two-table schema** (`books` + `warnings`), with `goodreads_book_id` added and indexed as the identity field — see [`erd.md`](erd.md) |
| Title comparison | Decision 6 | **Case-insensitive** (Kristina's/Anthony's model) — Abigail's case-sensitive comparison is not adopted |
| Report format | Decision 7 | **Abigail's three-tier run status** (SUCCESS / COMPLETED WITH ISSUES / FAILED), plus Kristina's existing report-content requirements |
| Anthony's extra ISBN repairs + multi-code reporting | Open item | **Implement** |
| ISBN-13 prefix (978/979) check | Open item | **Implement** |
| Abigail's publication-year / missing-title / missing-author / language-code rules | Open item | **Skip** |
| Abigail's atomicity guarantee (failed run saves nothing) | Open item | **Skip** — `FAILED` is a status label only; see **Resolved conflict** below |
| Abigail's external lookup + human-approval correction workflow | Open item | **Skip** |

### Resolved conflict: Decision 7 vs. the Open Items atomicity vote

**Decision 7** adopts Abigail's reporting requirements wholesale, which
*include* a three-tier run status where **FAILED means nothing is
saved** — that's the same atomicity guarantee as her §4.2 rule. **The Open
Items vote separately, and explicitly, marked "Abigail's atomicity
guarantee" as "skip, do not implement."** As written, those two decisions
contradicted each other.

**Resolution:** the more specific, explicitly-named decision wins over the
broader one it's nested inside. Decision 7's "go with Abby's reporting
requirements" is a general adoption that happens to bundle several of her
rules together; the Open Items vote is a separate, targeted decision made
about this exact guarantee by name. So:

- The **three-tier status** (SUCCESS / COMPLETED WITH ISSUES / FAILED) is
  implemented, per Decision 7.
- The **atomicity guarantee behind FAILED is not implemented**, per the
  Open Items vote. `FAILED` is a status label describing what happened,
  not a promise about what's in `books.db` afterward — a `FAILED` run may
  have partially written rows before it stopped.
- To avoid the report making a claim nothing enforces, **the report must
  say so explicitly** whenever it reports `FAILED`: something like "Status:
  FAILED — the group did not implement an atomicity guarantee for this
  pipeline; rows from before the failure may already be saved." This is
  the same honesty principle Abigail's own rules.md uses elsewhere ("the
  report never claims an ISBN was verified unless it actually was") —
  applied here to not claim a safety property the code doesn't have.

This keeps both decisions true to what was actually voted on, without
silently picking one over the other or inventing a compromise nobody
agreed to.

---

## 1. For each kind of ISBN problem: repair, reject, or load with a warning?

The governing principle (Decision 2, Kristina's model, kept): **a repair is
only allowed when it is deterministic and checksum-verifiable.** A bad or
unusable ISBN **never rejects the row** — the row is always loaded (its
identity doesn't depend on having an ISBN at all; see §2). A bad ISBN only
nulls that one field and attaches a warning.

| Problem | Action | Why |
|---|---|---|
| Already a valid ISBN-10 or ISBN-13 (978/979-prefixed) | **Load, no warning** | Nothing to fix. |
| Valid, but formatted with hyphens/spaces | **Repair** (strip separators) | Cosmetic; checksum unaffected. |
| `isbn` with leading zero(s) stripped (7–9 digits) | **Repair**: zero-pad to 10 digits, only if the padded result passes the checksum | Deterministic; single possible correction. |
| 10-digit `isbn` fails its checksum, but `978 + those 10 digits` is a valid ISBN-13 | **Repair** *(new — Anthony's "stripped-978" repair, Open item: implement)*: recompute the correct ISBN-10 check digit from the ISBN-13 that does check out | Still deterministic — the ISBN-13 proves there's exactly one right ISBN-10 check digit. |
| `isbn13` stored as scientific notation / float **and** the row has a valid (or repaired) `isbn` | **Repair**: re-derive `isbn13` from `isbn` via the `978` + check-digit formula | One valid ISBN-10 → exactly one correct ISBN-13. |
| `isbn13` is simply **blank** (not corrupted) **and** the row has a valid (or repaired) `isbn` | **Repair**: derive `isbn13` from `isbn`, same formula as above *(found during implementation — needed for the collision check below to actually work: two rows sharing an ISBN must collide whether that ISBN was stored as `isbn` or `isbn13`, per Abigail's own §2 rule that ISBNs are "compared as normalized ISBN-13s")* | Same reasoning as the row above; this was simply a gap in how literally "scientific notation" was read. |
| `isbn` is empty or unusable, but `isbn13` resolves (directly, or via repair) to a valid 978-prefixed ISBN-13 | **Repair** *(new — Anthony's "Missing Counterpart," Open item: implement)*: derive `isbn` from the valid `isbn13` | Reverse of the row above; still exactly one right answer. Only applies once `isbn13` is a clean, checksum-verified value — never derived from the raw scientific-notation text directly, for the same reason the forward direction doesn't trust it either. 979-prefixed ISBN-13s have no ISBN-10 form and are skipped here. |
| `isbn13` stored as scientific notation / float, no usable `isbn`, and no 978-prefixed `isbn13` to derive from | **Load with a warning**; null `isbn13`; keep raw text in an audit column | Digits are permanently lost; nothing to verify a reconstruction against. |
| Right length/character set, wrong check digit | **Load with a warning**; null the field; keep raw value | Could be any digit — not safely correctable. |
| Invalid character (letter where only a digit/trailing `X` belongs) | **Load with a warning**; null the field | Same reasoning. |
| Wrong length that isn't a leading-zero case | **Load with a warning**; null the field | No single deterministic correction. |
| 13-digit value with a valid Mod-10 checksum but a prefix other than 978/979 | **Load with a warning**; null the field *(new — Open item: implement the prefix check)* | Not an ISBN-13 by definition, whatever its checksum says. Neither Kristina's nor Anthony's original rules checked this — it was a shared gap. |
| A valid ISBN-13 sitting in the `isbn` (ISBN-10) column | **Repair**: move the value into `isbn13`, null `isbn` | Structural fix, not a value guess. |
| Both `isbn` and `isbn13` empty | **Load, with a warning** *(changed by Decision 3 — Abigail's model; Kristina's original treated this as informational-only, not a warning)* | The row is still fully identified by `goodreads_book_id` (§2), so there's no reason to hide the missing ISBN from the report. |
| A valid ISBN matches a book already on file under a **different `goodreads_book_id`** | **Reject** the incoming row *(reframed under Decision 1 — collision is keyed on `goodreads_book_id`, not title, since identity is no longer ISBN-based)* | Abigail's §2 rule 3: one ISBN can't belong to two publications; the system won't choose between them. |
| A completely unparseable value (letters only, symbols, garbage) | **Load with a warning**; null the field | Not a repairable format. |
| The row itself fails to parse as CSV (wrong field count, broken quoting) | **Reject the row**, reason recorded | All three original rule sets agreed on this — the only row-level rejection. |
| A single field hits more than one of the above at once | **List every applicable reason, comma-separated** *(new — Anthony's rule, Open item: implement)* | e.g. a Nook code with no `isbn` to recover from both lost its digits and isn't a book identifier at all. |

**Explicitly not implemented** (Open items vote: skip) — Abigail's
publication-year validation (including the BC/negative-year rule and
year-later-than-import-date warning), her missing-title/missing-author
handling, and her language-code handling. These fields are passed through
without new validation.

## 2. What makes two rows the same book?

**Identity is `goodreads_book_id` alone** (Decision 1, Abigail's model).
Every row in this dataset carries one, it's never blank, and it's unique —
so unlike the ISBN-based identity in the original rules, there is no "row
with no usable identity" case anymore.

- **ISBN is a secondary, validated attribute, not the identity key.** It's
  repaired/warned per §1, and checked for collisions (above), but it never
  decides whether two rows are the same book.
- **No fuzzy title/author matching, ever** — this was already common ground
  across all three original rule sets and isn't touched by any decision.
- **Title normalization is case-insensitive** (Decision 6): lowercase, strip
  punctuation and extra whitespace. A capitalization-only difference is not
  a title change for any purpose in this document, including the
  identity-relevant-field check in §3.

## 3. What happens when a book already in the database arrives again?

Matching is by `goodreads_book_id` (§2). Once a match is found, Decision 4
(Abigail's model) splits every other field into two camps:

**Volatile metadata — always updated, no review needed:**
`average_rating`, `ratings_count`, `work_ratings_count`,
`work_text_reviews_count`, `ratings_1`–`ratings_5`, `books_count`,
`image_url`, `small_image_url`, `best_book_id`, `book_id`.

**Identity-relevant fields — frozen once set:**
`title` (beyond case/whitespace, per §2), `authors`,
`original_publication_year`, `work_id`, `language_code`, and any change to
an already-populated `isbn`/`isbn13`.

| What's different | What happens |
|---|---|
| Nothing | **Skip**, logged as `duplicate, no changes — skipped`. |
| A volatile-metadata field differs | **Update** that field; log the old → new diff. |
| An identity-relevant field was **empty** and the new row fills it | **Update** (fill-the-gap only) — validate the new value the same way as on first load. |
| An identity-relevant field was **already populated** and the new row disagrees | **Reject** the incoming row and flag it for manual review; the existing record is left untouched. |
| The incoming row's ISBN matches a different `goodreads_book_id` already on file | **Reject**, flagged as a collision (§1/§2). |
| The row itself fails to parse as CSV | **Reject**, reason recorded. |

## 4. What must the report say?

Decision 7 (Abigail's model): every run reports one of three states.

- **SUCCESS** — every row loaded with no warnings.
- **COMPLETED WITH ISSUES** — the run finished, but some rows were
  rejected or carry a warning. Never reported as a plain success.
- **FAILED** — the file couldn't be read, a required column is missing, or
  an error stopped the run partway through. This is a status label, not a
  rollback guarantee (see **Resolved conflict**, above): rows loaded
  before the failure may already be in `books.db`, and the report says so
  explicitly whenever it reports FAILED.

On top of the status, the report keeps Kristina's original content
requirements, which Abigail's reporting model is a superset of:

- **Headline counts**, broken out separately: rows processed, loaded
  clean, loaded with a warning, updated, skipped as duplicates, rejected.
- **A breakdown by problem category** (matching §1's rows) with a count
  for each.
- **Per-row detail** for every non-clean row: file, row number,
  title/`goodreads_book_id`, the original offending value, which rule it
  hit, and exactly what the system did about it.
- **Old → new diffs** for every updated field.
- **Rejections and anything needing a person today** kept visibly separate
  from routine warnings.
- **One unambiguous bottom line at the top** — which is now just "the run
  status," per Decision 7.

---

## Open items, voted

| Item | Vote |
|---|---|
| Anthony's extra ISBN repairs (reverse ISBN-10 derivation, "stripped-978," multi-code reporting) | **Implement** — folded into §1 above |
| ISBN-13 prefix (978/979) check | **Implement** — folded into §1 above |
| Abigail's publication-year / missing-title / missing-author / language-code rules | **Skip** |
| Abigail's atomicity guarantee | **Skip** — `FAILED` is a status label only, see **Resolved conflict** |
| Abigail's external lookup + human-approval correction workflow (`lookup_isbns.py`, Open Library, `isbn-corrections.csv`) | **Skip** — out of scope for this assignment |

## Action items (not yet assigned at the meeting)

The working doc's action-items checklist was left blank at the end of the
call — still open:

- [ ] Who writes the implementation against this agreed `rules.md`?
- [ ] By when?
- [ ] Who builds which test suite?
- [ ] Confirm the group agrees with the Decision 7 / atomicity resolution above before implementation starts.
