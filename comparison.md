# comparison.md -- Kristina vs. Anthony vs. Abigail's `books.db`

Compared using `goodreads_book_id` as the match key (per `rules.md` section 2 -- "identity is `goodreads_book_id` alone"), across the 19 data columns in `books` (everything except `id`, `identity_key`, `fallback_key`, `source_file`, `first_loaded_at`, `last_updated_at`, which were excluded as agreed), plus the `warnings` table joined back to each book.

## Summary

**All three databases hold the same 10013 books** -- identical sets of `goodreads_book_id`, no book present in one and missing from another.

They are **not byte-identical**, though. Every difference falls into one of four categories, in order of how much they actually matter:

1. **A genuine ISBN-casing difference on 1 book** -- a real, if tiny, data disagreement.
2. **A genuine warning-classification disagreement on 2 books** -- rules.md doesn't pin down which reason code applies, and the three implementations resolved it differently.
3. **A systematic warning-labeling difference affecting 706 books** -- not a disagreement about *which* books have a problem, only about the exact wording used to describe it, and (for 566 of them) which column the warning is filed under.
4. **A systematic `NULL`-vs-`''` storage convention affecting 3131 books across 7 columns** -- the same "this field is empty" fact, stored two different ways. Not a data disagreement.

## 1. Books only in one database

None. All three contain exactly the same 10,013 `goodreads_book_id` values.

## 2. Real differing values (category 1 above)

Every book-and-column pair where the three databases hold genuinely different non-empty values (i.e. not just one side storing `NULL` where another stores an empty string):

| goodreads_book_id | Title | Column | Kristina | Anthony | Abigail |
|---|---|---|---|---|---|
| 111220 | Eleanor of Aquitaine: A Life  | original_title | ` ` | `None` | `None` |
| 239107 | Sea of Swords (Forgotten Realms: Paths of Darkness, #4; Legend of Drizzt, #13) | original_title | ` ` | `None` | `None` |
| 826582 | If You Take a Mouse to School | original_title | ` ` | `None` | `None` |
| 90010004 | Winter Orchard | isbn | `031200009x` | `031200009X` | `031200009X` |
| 92871 | Brothers Majere (Dragonlance: Preludes, #3) | original_title | ` ` | `None` | `None` |
| 9549 | Shadows of the Empire (Star Wars) | original_title | ` ` | `None` | `None` |

**6 rows.** Five are `original_title`, where Kristina stored a single space `' '` instead of an empty value (same underlying fact -- no original title on file -- represented a third way). The one that actually matters: **`90010004`, *Winter Orchard*** -- Kristina's `isbn` is `031200009x` (lowercase check-digit `x`), Anthony's and Abigail's is `031200009X` (uppercase). `rules.md` never says to uppercase a lowercase ISBN-10 check digit, so this is a real gap in the agreed rules, not a bug in any one implementation -- each of us happened to preserve or normalize the case differently.

## 3. Genuine warning-classification disagreements (category 2 above)

Same book, same raw ISBN value, but a different reason code for *why* it's a problem -- not just different wording for the same reason:

| goodreads_book_id | Title | Raw value | Kristina | Anthony | Abigail |
|---|---|---|---|---|---|
| 11436 | Rejoice (Redemption, #4) | `84386874` | isbn/wrong-length | isbn/bad-checksum | isbn/bad-checksum |
| 7603 | Reading Lolita in Tehran | `812971060` | isbn/wrong-length | isbn/bad-checksum | isbn/bad-checksum |

**2 rows.** Both are 8-9 digit numeric ISBN-10 candidates that still fail the checksum *after* zero-padding to 10 digits. `rules.md` says a short numeric value gets zero-padded "only if the padded result then passes the ISBN-10 checksum" but never says what reason code applies when padding is tried and still fails -- Kristina's code kept the original `wrong-length` reason (the raw value was never 10 digits), Anthony's and Abigail's reported `bad-checksum` instead (treating the padded 10-digit value as the thing that failed). Both are defensible readings of an underspecified rule.

## 4. Warning-labeling differences -- same problem, different label (category 3)

**566 books** where Kristina files a "no usable ISBN" warning under the `isbn` field, while Anthony and Abigail file the identical warning under `isbn13` -- same book, same meaning ("this book has no usable ISBN at all"), different column chosen to attach it to. `rules.md` says both fields should be blank and warned; it doesn't say which field name the warning record itself should use.

**140 books** with a pure wording difference for the same reason -- `float-precision-lost` (mine) vs. `lost-precision` / `lost-precision,bad-prefix` (Anthony's and Abigail's), `invalid-characters` vs. `bad-characters`, `wrong-length` vs. `bad-length`. `rules.md` requires a warning here but never fixes the exact string to use, so each of us named our own reason codes.

A representative sample (first 10 of each):


**Field attribution (`isbn` vs. `isbn13`), sample:**

| goodreads_book_id | Title | Kristina field | Anthony/Abigail field | Reason |
|---|---|---|---|---|
| 10295484 | Heart on a Chain | isbn | isbn13 | no-usable-isbn |
| 10374 | Hard-Boiled Wonderland and the End of the World | isbn | isbn13 | no-usable-isbn |
| 10586539 | Wake (Watersong #1) | isbn | isbn13 | no-usable-isbn |
| 10599302 | Head Over Heels (Lucky Harbor, #3) | isbn | isbn13 | no-usable-isbn |
| 10664113 | A Dance with Dragons (A Song of Ice and Fire, #5) | isbn | isbn13 | no-usable-isbn |
| 10776793 | War Brides | isbn | isbn13 | no-usable-isbn |
| 10790376 | A Modern Witch (A Modern Witch, #1) | isbn | isbn13 | no-usable-isbn |
| 10813469 | Rock Chick Renegade (Rock Chick, #4) | isbn | isbn13 | no-usable-isbn |
| 10813480 | For You (The 'Burg, #1) | isbn | isbn13 | no-usable-isbn |
| 10830444 | Guilty Wives | isbn | isbn13 | no-usable-isbn |

**Wording only, sample:**

| goodreads_book_id | Title | Kristina reason | Anthony/Abigail reason |
|---|---|---|---|
| 10088913 | مخطوطة بن إسحاق: مدينة الموتى | float-precision-lost | lost-precision |
| 10169662 | Never Knowing | float-precision-lost | lost-precision |
| 10468258 | The Finding (Law of the Lycans, #5) | float-precision-lost | lost-precision,bad-prefix |
| 105189 | The Story of a Shipwrecked Sailor | float-precision-lost | lost-precision |
| 10706934 | بيكاسو وستاربكس | float-precision-lost | lost-precision |
| 10801027 | Cross My Heart (Cross My Heart, #1) | float-precision-lost | lost-precision,bad-prefix |
| 11201007 | Hearts in Darkness (Hearts in Darkness, #1) | float-precision-lost | lost-precision,bad-prefix |
| 11239856 | Maid for the Billionaire (Legacy Collection, #1) | float-precision-lost | lost-precision,bad-prefix |
| 11382346 | That Boy (That Boy, #1) | float-precision-lost | lost-precision |
| 11436 | Rejoice (Redemption, #4) | float-precision-lost | lost-precision |

## 5. `NULL` vs. empty-string storage convention (category 4 above)

Counts by column -- same underlying fact ("this field has no value"), stored as an empty string `''` in Kristina's database and as SQL `NULL` in Anthony's and Abigail's, for every one of these:

| Column | Books affected |
|---|---|
| language_code | 1084 |
| isbn | 708 |
| isbn13 | 707 |
| original_title | 585 |
| original_publication_year | 21 |
| image_url | 13 |
| small_image_url | 13 |

**Total: 3131 books affected across these 7 columns.** This is not a data disagreement -- every one of these rows has the exact same real-world information in all three databases, just represented two different ways at the SQL level. `rules.md` doesn't say whether a missing text field should be stored as `NULL` or `''`.

## Appendix A: every `NULL`-vs-`''` row, in full

| goodreads_book_id | Title | Column | Kristina | Anthony | Abigail |
|---|---|---|---|---|---|
| 1001896 | The Real Mother Goose | language_code | `''` | `None` | `None` |
| 10058 | Flags of Our Fathers | language_code | `''` | `None` | `None` |
| 10088913 | مخطوطة بن إسحاق: مدينة الموتى | isbn | `''` | `None` | `None` |
| 10088913 | مخطوطة بن إسحاق: مدينة الموتى | isbn13 | `''` | `None` | `None` |
| 10092 | Sea of Silver Light (Otherland, #4) | language_code | `''` | `None` | `None` |
| 1009996 | Artisan Bread in Five Minutes a Day: The Discovery That Revolutionizes Home Baking | original_title | `''` | `None` | `None` |
| 10111087 | Turn Right at Machu Picchu: Rediscovering the Lost City One Step at a Time | original_title | `''` | `None` | `None` |
| 10155 | The Lost World (Professor Challenger, #1) | language_code | `''` | `None` | `None` |
| 10161216 | Mr. Churchill's Secretary (Maggie Hope Mystery, #1) | original_title | `''` | `None` | `None` |
| 10169662 | Never Knowing | isbn | `''` | `None` | `None` |
| 10169662 | Never Knowing | isbn13 | `''` | `None` | `None` |
| 10209997 | The Night Strangers | original_title | `''` | `None` | `None` |
| 10211494 | Stories I Only Tell My Friends | original_title | `''` | `None` | `None` |
| 102954 | Preacher, Volume 7: Salvation | language_code | `''` | `None` | `None` |
| 10295484 | Heart on a Chain | isbn | `''` | `None` | `None` |
| 10295484 | Heart on a Chain | isbn13 | `''` | `None` | `None` |
| 102958 | Preacher, Volume 9: Alamo | original_title | `''` | `None` | `None` |
| 10305231 | The Next Always (Inn BoonsBoro, #1) | language_code | `''` | `None` | `None` |
| 103111 | X-Men: The Dark Phoenix Saga | original_title | `''` | `None` | `None` |
| 10327303 | Uncommon Criminals (Heist Society, #2) | language_code | `''` | `None` | `None` |
| 10335318 | Destiny of the Republic: A Tale of Madness, Medicine and the Murder of a President | original_title | `''` | `None` | `None` |
| 1034605 | The Country Mouse and the City Mouse; The Fox and the Crow; The Dog and His Bone | language_code | `''` | `None` | `None` |
| 10365 | Where the Red Fern Grows | language_code | `''` | `None` | `None` |
| 10365343 | Zone One | original_title | `''` | `None` | `None` |
| 10374 | Hard-Boiled Wonderland and the End of the World | isbn | `''` | `None` | `None` |
| 10374 | Hard-Boiled Wonderland and the End of the World | isbn13 | `''` | `None` | `None` |
| 103902 | Gustav Klimt: 1862-1918 | language_code | `''` | `None` | `None` |
| 10395 | How Soccer Explains the World | language_code | `''` | `None` | `None` |
| 10421530 | Kiss of Frost (Mythos Academy, #2) | language_code | `''` | `None` | `None` |
| 1044141 | The 8th Habit: From Effectiveness to Greatness | original_publication_year | `''` | `None` | `None` |
| 1044141 | The 8th Habit: From Effectiveness to Greatness | original_title | `''` | `None` | `None` |
| 1045757 | Once (Once, #1) | language_code | `''` | `None` | `None` |
| 10468258 | The Finding (Law of the Lycans, #5) | isbn | `''` | `None` | `None` |
| 10468258 | The Finding (Law of the Lycans, #5) | isbn13 | `''` | `None` | `None` |
| 10473214 | 13 Gifts (Willow Falls, #3) | original_title | `''` | `None` | `None` |
| 104734 | The Vagina Monologues | language_code | `''` | `None` | `None` |
| 10506 | The Island of the Day Before | language_code | `''` | `None` | `None` |
| 10508526 | The Chronicles of Harris Burdick: 14 Amazing Authors Tell the Tales | original_title | `''` | `None` | `None` |
| 105189 | The Story of a Shipwrecked Sailor | isbn | `''` | `None` | `None` |
| 105189 | The Story of a Shipwrecked Sailor | isbn13 | `''` | `None` | `None` |
| 1052 | The Richest Man in Babylon | original_title | `''` | `None` | `None` |
| 10537195 | The Last Council (Amulet, #4) | original_title | `''` | `None` | `None` |
| 10538 | The Life and Times of the Thunderbolt Kid | language_code | `''` | `None` | `None` |
| 1055617 | The Miracle of Forgiveness | language_code | `''` | `None` | `None` |
| 1056627 | Become a Better You: 7 Keys to Improving Your Life Every Day | original_publication_year | `''` | `None` | `None` |
| 1056627 | Become a Better You: 7 Keys to Improving Your Life Every Day | original_title | `''` | `None` | `None` |
| 1056627 | Become a Better You: 7 Keys to Improving Your Life Every Day | language_code | `''` | `None` | `None` |
| 105760 | Zodiac | language_code | `''` | `None` | `None` |
| 10586539 | Wake (Watersong #1) | isbn | `''` | `None` | `None` |
| 10586539 | Wake (Watersong #1) | isbn13 | `''` | `None` | `None` |
| 10592 | Carrie | language_code | `''` | `None` | `None` |
| 10594929 | Out of Oz (The Wicked Years, #4) | original_title | `''` | `None` | `None` |
| 1059680 | Veganomicon: The Ultimate Vegan Cookbook | language_code | `''` | `None` | `None` |
| 10599302 | Head Over Heels (Lucky Harbor, #3) | isbn | `''` | `None` | `None` |
| 10599302 | Head Over Heels (Lucky Harbor, #3) | isbn13 | `''` | `None` | `None` |
| 10604115 | Happy Accidents: A Memoir | original_title | `''` | `None` | `None` |
| 10604115 | Happy Accidents: A Memoir | language_code | `''` | `None` | `None` |
| 106131 | Charlie Bone and the Castle of Mirrors (The Children of the Red King, #4) | language_code | `''` | `None` | `None` |
| 10618 | Apt Pupil | original_title | `''` | `None` | `None` |
| 10659536 | Every Thing on It | language_code | `''` | `None` | `None` |
| 10661081 | Vampire Academy: The Ultimate Guide (Vampire Academy) | original_title | `''` | `None` | `None` |
| 10664113 | A Dance with Dragons (A Song of Ice and Fire, #5) | isbn | `''` | `None` | `None` |
| 10664113 | A Dance with Dragons (A Song of Ice and Fire, #5) | isbn13 | `''` | `None` | `None` |
| 10706934 | بيكاسو وستاربكس | isbn | `''` | `None` | `None` |
| 10706934 | بيكاسو وستاربكس | isbn13 | `''` | `None` | `None` |
| 10710392 | Chopsticks | original_title | `''` | `None` | `None` |
| 107195 | I Kissed Dating Goodbye | language_code | `''` | `None` | `None` |
| 107291 | Needful Things | language_code | `''` | `None` | `None` |
| 10762697 | The Farseer Trilogy (Farseer Trilogy #1-3) | original_title | `''` | `None` | `None` |
| 107664 | Raven's Gate (The Gatekeepers, #1) | language_code | `''` | `None` | `None` |
| 107670 | Evil Star (The Gatekeepers, #2) | language_code | `''` | `None` | `None` |
| 10776793 | War Brides | isbn | `''` | `None` | `None` |
| 10776793 | War Brides | isbn13 | `''` | `None` | `None` |
| 10778410 | The Fire (Witch & Wizard, #3) | original_title | `''` | `None` | `None` |
| 10778410 | The Fire (Witch & Wizard, #3) | language_code | `''` | `None` | `None` |
| 107821 | Bridge of Sighs | language_code | `''` | `None` | `None` |
| 10785687 | Harry Potter Page to Screen: The Complete Filmmaking Journey | language_code | `''` | `None` | `None` |
| 10790276 | Courageous | language_code | `''` | `None` | `None` |
| 10790376 | A Modern Witch (A Modern Witch, #1) | isbn | `''` | `None` | `None` |
| 10790376 | A Modern Witch (A Modern Witch, #1) | isbn13 | `''` | `None` | `None` |
| 10801027 | Cross My Heart (Cross My Heart, #1) | isbn | `''` | `None` | `None` |
| 10801027 | Cross My Heart (Cross My Heart, #1) | isbn13 | `''` | `None` | `None` |
| 10813469 | Rock Chick Renegade (Rock Chick, #4) | isbn | `''` | `None` | `None` |
| 10813469 | Rock Chick Renegade (Rock Chick, #4) | isbn13 | `''` | `None` | `None` |
| 10813469 | Rock Chick Renegade (Rock Chick, #4) | original_title | `''` | `None` | `None` |
| 10813480 | For You (The 'Burg, #1) | isbn | `''` | `None` | `None` |
| 10813480 | For You (The 'Burg, #1) | isbn13 | `''` | `None` | `None` |
| 10830444 | Guilty Wives | isbn | `''` | `None` | `None` |
| 10830444 | Guilty Wives | isbn13 | `''` | `None` | `None` |
| 10868182 | The Hidden Child (Patrik Hedström, #5) | language_code | `''` | `None` | `None` |
| 10875239 | Lethal | language_code | `''` | `None` | `None` |
| 10907 | The Pursuit of Happyness | language_code | `''` | `None` | `None` |
| 10913 | Keeping Faith | language_code | `''` | `None` | `None` |
| 109515 | How I Raised Myself from Failure to Success in Selling | language_code | `''` | `None` | `None` |
| 10960383 | A Grown-Up Kind of Pretty | original_title | `''` | `None` | `None` |
| 10970532 | The Siren (The Original Sinners, #1) | language_code | `''` | `None` | `None` |
| 10975 | The Sound and the Fury | isbn | `''` | `None` | `None` |
| 10975 | The Sound and the Fury | isbn13 | `''` | `None` | `None` |
| 1099097 | The Tiger Who Came to Tea | language_code | `''` | `None` | `None` |
| 11051889 | The Fallen Star (Fallen Star, #1) | original_title | `''` | `None` | `None` |
| 11051889 | The Fallen Star (Fallen Star, #1) | language_code | `''` | `None` | `None` |
| 110692 | The Redemption of Althalus | language_code | `''` | `None` | `None` |
| 1107001 | The Silver Palate Cookbook | language_code | `''` | `None` | `None` |
| 11076177 | The Cat's Table | original_title | `''` | `None` | `None` |
| 11096647 | Flat-Out Love (Flat-Out Love, #1) | isbn | `''` | `None` | `None` |
| 11096647 | Flat-Out Love (Flat-Out Love, #1) | isbn13 | `''` | `None` | `None` |
| 11101772 | The Scrapbook of Frankie Pratt | original_title | `''` | `None` | `None` |
| 11104030 | MWF Seeking BFF: My Yearlong Search For A New Best Friend | original_title | `''` | `None` | `None` |
| 11104933 | Willpower: Rediscovering the Greatest Human Strength | language_code | `''` | `None` | `None` |
| 111126 | Hateship, Friendship, Courtship, Loveship, Marriage: Stories | language_code | `''` | `None` | `None` |
| 1111600 | The Wheel of Time: Boxed Set  (Wheel of Time, #1-8) | language_code | `''` | `None` | `None` |
| 1113545 | The Candy Shop War (The Candy Shop War, #1) | language_code | `''` | `None` | `None` |
| 11198480 | Not a Fan: Becoming a Completely Committed Follower of Jesus | original_title | `''` | `None` | `None` |
| 11201007 | Hearts in Darkness (Hearts in Darkness, #1) | isbn | `''` | `None` | `None` |
| 11201007 | Hearts in Darkness (Hearts in Darkness, #1) | isbn13 | `''` | `None` | `None` |
| 11227040 | Sweet Dreams (Colorado Mountain, #2) | isbn | `''` | `None` | `None` |
| 11227040 | Sweet Dreams (Colorado Mountain, #2) | isbn13 | `''` | `None` | `None` |
| 11227041 | The Gamble (Colorado Mountain, #1) | isbn | `''` | `None` | `None` |
| 11227041 | The Gamble (Colorado Mountain, #1) | isbn13 | `''` | `None` | `None` |
| 11227043 | Rock Chick Revenge (Rock Chick, #5) | isbn | `''` | `None` | `None` |
| 11227043 | Rock Chick Revenge (Rock Chick, #5) | isbn13 | `''` | `None` | `None` |
| 11227043 | Rock Chick Revenge (Rock Chick, #5) | original_title | `''` | `None` | `None` |
| 112292 | Dauntless (The Lost Fleet, #1) | language_code | `''` | `None` | `None` |
| 11237412 | Six's Legacy (Lorien Legacies: The Lost Files, #1) | isbn | `''` | `None` | `None` |
| 11237412 | Six's Legacy (Lorien Legacies: The Lost Files, #1) | isbn13 | `''` | `None` | `None` |
| 11239856 | Maid for the Billionaire (Legacy Collection, #1) | isbn | `''` | `None` | `None` |
| 11239856 | Maid for the Billionaire (Legacy Collection, #1) | isbn13 | `''` | `None` | `None` |
| 11239856 | Maid for the Billionaire (Legacy Collection, #1) | original_title | `''` | `None` | `None` |
| 11260526 | The Twilight Saga Breaking Dawn Part 1: The Official Illustrated Movie Companion (The Twilight Saga: The Official Illustrated Movie Companion, #4) | original_title | `''` | `None` | `None` |
| 11262424 | Between the Lines (Between the Lines, #1) | isbn | `''` | `None` | `None` |
| 11262424 | Between the Lines (Between the Lines, #1) | isbn13 | `''` | `None` | `None` |
| 11266880 | It Chooses You | original_title | `''` | `None` | `None` |
| 11281852 | Kisses from Katie: A Story of Relentless Love and Redemption | original_title | `''` | `None` | `None` |
| 112872 | A Light in the Window (Mitford Years, #2) | language_code | `''` | `None` | `None` |
| 112874 | These High, Green Hills (Mitford Years, #3) | language_code | `''` | `None` | `None` |
| 1129315 | The Berenstain Bears' Trouble at School | original_title | `''` | `None` | `None` |
| 11306337 | EntreLeadership: 20 Years of Practical Business Wisdom from the Trenches | original_title | `''` | `None` | `None` |
| 11306337 | EntreLeadership: 20 Years of Practical Business Wisdom from the Trenches | language_code | `''` | `None` | `None` |
| 11312 | Over Sea, Under Stone (The Dark Is Rising, #1) | language_code | `''` | `None` | `None` |
| 11318 | Trouble Is My Business | original_publication_year | `''` | `None` | `None` |
| 11324166 | Timeless (Parasol Protectorate, #5) | isbn | `''` | `None` | `None` |
| 11324166 | Timeless (Parasol Protectorate, #5) | isbn13 | `''` | `None` | `None` |
| 11337912 | The Prisoner of Cell 25 (Michael Vey, #1) | language_code | `''` | `None` | `None` |
| 113429 | No One Belongs Here More Than You | language_code | `''` | `None` | `None` |
| 11350430 | The Mystery Knight (The Tales of Dunk and Egg, #3) | isbn | `''` | `None` | `None` |
| 11350430 | The Mystery Knight (The Tales of Dunk and Egg, #3) | isbn13 | `''` | `None` | `None` |
| 113576 | The Smartest Guys in the Room: The Amazing Rise and Scandalous Fall of Enron | language_code | `''` | `None` | `None` |
| 11381910 | Heft | language_code | `''` | `None` | `None` |
| 11382346 | That Boy (That Boy, #1) | isbn | `''` | `None` | `None` |
| 11382346 | That Boy (That Boy, #1) | isbn13 | `''` | `None` | `None` |
| 11389341 | The Meaning of Marriage: Facing the Complexities of Commitment with the Wisdom of God | original_title | `''` | `None` | `None` |
| 11391817 | Drawing from Memory | original_title | `''` | `None` | `None` |
| 11395597 | Why Be Happy When You Could Be Normal? | language_code | `''` | `None` | `None` |
| 11401915 | The Ripper (The Vampire Diaries: Stefan's Diaries, #4) | language_code | `''` | `None` | `None` |
| 11408650 | The Unbecoming of Mara Dyer (Mara Dyer, #1) | isbn | `''` | `None` | `None` |
| 11408650 | The Unbecoming of Mara Dyer (Mara Dyer, #1) | isbn13 | `''` | `None` | `None` |
| 11413 | Captivating: Unveiling the Mystery of a Woman's Soul | original_title | `''` | `None` | `None` |
| 114170 | Then Came You (The Gamblers, #1) | isbn | `''` | `None` | `None` |
| 114170 | Then Came You (The Gamblers, #1) | isbn13 | `''` | `None` | `None` |
| 11422 | Redeeming Love | original_title | `''` | `None` | `None` |
| 114345 | The Little House Collection (Little House, #1-9) | language_code | `''` | `None` | `None` |
| 11436 | Rejoice (Redemption, #4) | isbn | `''` | `None` | `None` |
| 11436 | Rejoice (Redemption, #4) | isbn13 | `''` | `None` | `None` |
| 11445880 | Midnight in Austenland (Austenland, #2) | original_title | `''` | `None` | `None` |
| 11450591 | The Mill River Recluse | isbn | `''` | `None` | `None` |
| 11450591 | The Mill River Recluse | isbn13 | `''` | `None` | `None` |
| 11479285 | Breathe (Sea Breeze, #1) | isbn | `''` | `None` | `None` |
| 11479285 | Breathe (Sea Breeze, #1) | isbn13 | `''` | `None` | `None` |
| 1149440 | Heavier Than Heaven: A Biography of Kurt Cobain | language_code | `''` | `None` | `None` |
| 114954 | The Opal Deception  (Artemis Fowl, #4) | isbn | `''` | `None` | `None` |
| 114954 | The Opal Deception  (Artemis Fowl, #4) | isbn13 | `''` | `None` | `None` |
| 11505797 | Beautiful Disaster (Beautiful, #1) | isbn | `''` | `None` | `None` |
| 11505797 | Beautiful Disaster (Beautiful, #1) | isbn13 | `''` | `None` | `None` |
| 11512688 | The Dead of Night (The 39 Clues: Cahills vs. Vespers, #3) | original_title | `''` | `None` | `None` |
| 11525 | 1,000 Places to See Before You Die | language_code | `''` | `None` | `None` |
| 11561469 | Reason to Breathe (Breathing, #1) | isbn | `''` | `None` | `None` |
| 11561469 | Reason to Breathe (Breathing, #1) | isbn13 | `''` | `None` | `None` |
| 11564 | The Girl Who Loved Tom Gordon | language_code | `''` | `None` | `None` |
| 116020 | Walden & Civil Disobedience | original_title | `''` | `None` | `None` |
| 116236 | The Education of Little Tree | language_code | `''` | `None` | `None` |
| 116295 | Guards! Guards!: The Play | original_title | `''` | `None` | `None` |
| 116356 | Footfall | language_code | `''` | `None` | `None` |
| 116494 | Anastasia Krupnik (Anastasia Krupnik, #1) | language_code | `''` | `None` | `None` |
| 11665750 | At Peace (The 'Burg, #2) | isbn | `''` | `None` | `None` |
| 11665750 | At Peace (The 'Burg, #2) | isbn13 | `''` | `None` | `None` |
| 11713 | The English Patient | language_code | `''` | `None` | `None` |
| 117251 | Hamlet: Screenplay, Introduction And Film Diary | original_title | `''` | `None` | `None` |
| 11737313 | Three Times Lucky (Tupelo Landing, #1) | original_title | `''` | `None` | `None` |
| 11742691 | The Hunger Games: Official Illustrated Movie Companion | original_title | `''` | `None` | `None` |
| 11757975 | The Look of Love (San Francisco Sullivans, #1; The Sullivans, #1) | isbn | `''` | `None` | `None` |
| 11757975 | The Look of Love (San Francisco Sullivans, #1; The Sullivans, #1) | isbn13 | `''` | `None` | `None` |
| 117835 | Nourishing Traditions: The Cookbook That Challenges Politically Correct Nutrition and the Diet Dictocrats | language_code | `''` | `None` | `None` |
| 11784281 | Take This Regret (Take This Regret, #1) | isbn | `''` | `None` | `None` |
| 11784281 | Take This Regret (Take This Regret, #1) | isbn13 | `''` | `None` | `None` |
| 11808919 | Maid for Love (Gansett Island Series, #1) | isbn | `''` | `None` | `None` |
| 11808919 | Maid for Love (Gansett Island Series, #1) | isbn13 | `''` | `None` | `None` |
| 11821514 | Long Time Coming | isbn | `''` | `None` | `None` |
| 11821514 | Long Time Coming | isbn13 | `''` | `None` | `None` |
| 11851522 | The Complete Works of H.P. Lovecraft | isbn | `''` | `None` | `None` |
| 11851522 | The Complete Works of H.P. Lovecraft | isbn13 | `''` | `None` | `None` |
| 11851522 | The Complete Works of H.P. Lovecraft | original_title | `''` | `None` | `None` |
| 11873368 | The World of the Hunger Games (Hunger Games Trilogy) | original_title | `''` | `None` | `None` |
| 11908 | The Adventures of Augie March | language_code | `''` | `None` | `None` |
| 119091 | Taltos (Lives of the Mayfair Witches, #3) | language_code | `''` | `None` | `None` |
| 1191 | Giada's Family Dinners | language_code | `''` | `None` | `None` |
| 11913681 | The Boyfriend Thief (Stolen Kiss, #1) | isbn | `''` | `None` | `None` |
| 11913681 | The Boyfriend Thief (Stolen Kiss, #1) | isbn13 | `''` | `None` | `None` |
| 11913681 | The Boyfriend Thief (Stolen Kiss, #1) | original_title | `''` | `None` | `None` |
| 1192 | Everyday Italian: 125 Simple and Delicious Recipes | language_code | `''` | `None` | `None` |
| 11942408 | شاب كشك في رحلة البحث عن الجادون | isbn | `''` | `None` | `None` |
| 11942408 | شاب كشك في رحلة البحث عن الجادون | isbn13 | `''` | `None` | `None` |
| 11947156 | Prince of Wolves (The Grey Wolves, #1) | isbn | `''` | `None` | `None` |
| 11947156 | Prince of Wolves (The Grey Wolves, #1) | isbn13 | `''` | `None` | `None` |
| 11970096 | Twenty-Eight and a Half Wishes (Rose Gardner Mystery, #1) | isbn | `''` | `None` | `None` |
| 11970096 | Twenty-Eight and a Half Wishes (Rose Gardner Mystery, #1) | isbn13 | `''` | `None` | `None` |
| 11970096 | Twenty-Eight and a Half Wishes (Rose Gardner Mystery, #1) | original_title | `''` | `None` | `None` |
| 11970747 | The Hedge Knight (The Tales of Dunk and Egg, #1) | isbn | `''` | `None` | `None` |
| 11970747 | The Hedge Knight (The Tales of Dunk and Egg, #1) | isbn13 | `''` | `None` | `None` |
| 119760 | The Seat of the Soul | original_title | `''` | `None` | `None` |
| 11981168 | The One You Love (Emma Holden Suspense Mystery, #1) | isbn | `''` | `None` | `None` |
| 11981168 | The One You Love (Emma Holden Suspense Mystery, #1) | isbn13 | `''` | `None` | `None` |
| 11981168 | The One You Love (Emma Holden Suspense Mystery, #1) | original_title | `''` | `None` | `None` |
| 11985631 | The Sworn Sword (The Tales of Dunk and Egg, #2) | isbn | `''` | `None` | `None` |
| 11985631 | The Sworn Sword (The Tales of Dunk and Egg, #2) | isbn13 | `''` | `None` | `None` |
| 11995136 | محال | isbn | `''` | `None` | `None` |
| 11995136 | محال | isbn13 | `''` | `None` | `None` |
| 11996019 | The King's Agent | original_title | `''` | `None` | `None` |
| 12000020 | Aristotle and Dante Discover the Secrets of the Universe (Aristotle and Dante Discover the Secrets of the Universe, #1) | language_code | `''` | `None` | `None` |
| 12002819 | The Flight of Gemma Hardy | original_title | `''` | `None` | `None` |
| 12017 | Inversions (Culture, #6) | language_code | `''` | `None` | `None` |
| 12019355 | Infamous (Chronicles of Nick, #3) | language_code | `''` | `None` | `None` |
| 120230 | Barefoot Contessa at Home: Everyday Recipes You'll Make Over and Over Again | language_code | `''` | `None` | `None` |
| 12037026 | Come Home | language_code | `''` | `None` | `None` |
| 12039943 | Capital | language_code | `''` | `None` | `None` |
| 120461 | Oscar et la dame rose | language_code | `''` | `None` | `None` |
| 12063467 | Fury (New Species, #1) | original_title | `''` | `None` | `None` |
| 12065943 | Extra Yarn (E. B. White Read-Aloud Award. Picture Books) | original_title | `''` | `None` | `None` |
| 12067972 | Where You Are (Between the Lines, #2) | isbn | `''` | `None` | `None` |
| 12067972 | Where You Are (Between the Lines, #2) | isbn13 | `''` | `None` | `None` |
| 12072362 | The Pioneer Woman Cooks: Food from My Frontier  | original_title | `''` | `None` | `None` |
| 1207980 | Helmet for My Pillow | language_code | `''` | `None` | `None` |
| 120840 | David Gets In Trouble | language_code | `''` | `None` | `None` |
| 12107920 | Shatterproof (The 39 Clues: Cahills vs. Vespers, #4) | original_title | `''` | `None` | `None` |
| 12107920 | Shatterproof (The 39 Clues: Cahills vs. Vespers, #4) | language_code | `''` | `None` | `None` |
| 12107925 | Day of Doom (The 39 Clues: Cahills vs. Vespers, #6) | original_title | `''` | `None` | `None` |
| 12107927 | Trust No One (The 39 Clues: Cahills vs. Vespers, #5) | original_title | `''` | `None` | `None` |
| 12158480 | Why Nations Fail: The Origins of Power, Prosperity, and Poverty | language_code | `''` | `None` | `None` |
| 12171769 | 7: An Experimental Mutiny Against Excess | original_title | `''` | `None` | `None` |
| 121792 | The Revenge of the Baby-Sat | language_code | `''` | `None` | `None` |
| 1219103 | Five Weeks in a Balloon (Extraordinary Voyages, #1) | language_code | `''` | `None` | `None` |
| 12191246 | Second Son (Jack Reacher, #15.5) | isbn | `''` | `None` | `None` |
| 12191246 | Second Son (Jack Reacher, #15.5) | isbn13 | `''` | `None` | `None` |
| 12191246 | Second Son (Jack Reacher, #15.5) | language_code | `''` | `None` | `None` |
| 12204 | The Road Not Taken and Other Poems | language_code | `''` | `None` | `None` |
| 122212 | Waiting to Exhale (Waiting To Exhale #1) | language_code | `''` | `None` | `None` |
| 12254379 | 1Q84 #1-2 (1Q84, #1-2) | isbn | `''` | `None` | `None` |
| 12254379 | 1Q84 #1-2 (1Q84, #1-2) | isbn13 | `''` | `None` | `None` |
| 122574 | Getting Stoned with Savages: A Trip Through the Islands of Fiji and Vanuatu | language_code | `''` | `None` | `None` |
| 12287209 | Wool (Wool, #1) | isbn | `''` | `None` | `None` |
| 12287209 | Wool (Wool, #1) | isbn13 | `''` | `None` | `None` |
| 12288282 | Gunmetal Magic (Kate Daniels, #5.5) | isbn | `''` | `None` | `None` |
| 12288282 | Gunmetal Magic (Kate Daniels, #5.5) | isbn13 | `''` | `None` | `None` |
| 122967 | The Ugly Duckling | original_title | `''` | `None` | `None` |
| 12299419 | Mystery Man (Dream Man, #1) | isbn | `''` | `None` | `None` |
| 12299419 | Mystery Man (Dream Man, #1) | isbn13 | `''` | `None` | `None` |
| 123063 | Under the Skin | language_code | `''` | `None` | `None` |
| 1231511 | Dark River (Warriors: Power of Three, #2) | original_title | `''` | `None` | `None` |
| 1231511 | Dark River (Warriors: Power of Three, #2) | language_code | `''` | `None` | `None` |
| 123170 | Big Red (Big Red, #1) | language_code | `''` | `None` | `None` |
| 12326627 | The White Princess (The Plantagenet and Tudor Novels, #5) | isbn | `''` | `None` | `None` |
| 12326627 | The White Princess (The Plantagenet and Tudor Novels, #5) | isbn13 | `''` | `None` | `None` |
| 12331767 | High-Rise | language_code | `''` | `None` | `None` |
| 12341557 | The Wind Through the Keyhole (The Dark Tower, #4.5) | isbn | `''` | `None` | `None` |
| 12341557 | The Wind Through the Keyhole (The Dark Tower, #4.5) | isbn13 | `''` | `None` | `None` |
| 12351649 | Perfection (Neighbor from Hell, #2) | isbn | `''` | `None` | `None` |
| 12351649 | Perfection (Neighbor from Hell, #2) | isbn13 | `''` | `None` | `None` |
| 12357 | Take the Cannoli | language_code | `''` | `None` | `None` |
| 12389310 | Crow's Row (Crow's Row, #1) | original_title | `''` | `None` | `None` |
| 12390650 | Wildest Dreams (Fantasyland, #1) | isbn | `''` | `None` | `None` |
| 12390650 | Wildest Dreams (Fantasyland, #1) | isbn13 | `''` | `None` | `None` |
| 12413836 | Avatar: The Last Airbender (The Promise, #1) | original_title | `''` | `None` | `None` |
| 12413836 | Avatar: The Last Airbender (The Promise, #1) | language_code | `''` | `None` | `None` |
| 12413949 | White Girl Problems | original_title | `''` | `None` | `None` |
| 12415695 | كخه يا بابا | isbn | `''` | `None` | `None` |
| 12415695 | كخه يا بابا | isbn13 | `''` | `None` | `None` |
| 12458287 | The Golden Dynasty (Fantasyland, #2) | isbn | `''` | `None` | `None` |
| 12458287 | The Golden Dynasty (Fantasyland, #2) | isbn13 | `''` | `None` | `None` |
| 12458287 | The Golden Dynasty (Fantasyland, #2) | original_title | `''` | `None` | `None` |
| 12475019 | Some Assembly Required: A Journal of My Son's First Son | original_title | `''` | `None` | `None` |
| 12499 | Belly Laughs: The Naked Truth About Pregnancy and Childbirth | language_code | `''` | `None` | `None` |
| 12513614 | Captive in the Dark (The Dark Duet, #1) | isbn | `''` | `None` | `None` |
| 12513614 | Captive in the Dark (The Dark Duet, #1) | isbn13 | `''` | `None` | `None` |
| 12535 | Plan B: Further Thoughts on Faith | language_code | `''` | `None` | `None` |
| 12543 | Bird by Bird: Some Instructions on Writing and Life | language_code | `''` | `None` | `None` |
| 125540 | One Day at Horrorland (Goosebumps, #16) | language_code | `''` | `None` | `None` |
| 125542 | Stay Out of the Basement  (Goosebumps, #2) | language_code | `''` | `None` | `None` |
| 125564 | Night of the Living Dummy (Goosebumps, #7) | language_code | `''` | `None` | `None` |
| 12583975 | The Billionaire Wins the Game (Billionaire Bachelors, #1) | isbn | `''` | `None` | `None` |
| 12583975 | The Billionaire Wins the Game (Billionaire Bachelors, #1) | isbn13 | `''` | `None` | `None` |
| 125955 | White: The Great Pursuit (The Circle, #3) | language_code | `''` | `None` | `None` |
| 125958 | Skin | language_code | `''` | `None` | `None` |
| 125963 | Thr3e | language_code | `''` | `None` | `None` |
| 12598982 | Afterwards | language_code | `''` | `None` | `None` |
| 12602078 | The Tycoon's Revenge (Baby for the Billionaire, #1) | isbn | `''` | `None` | `None` |
| 12602078 | The Tycoon's Revenge (Baby for the Billionaire, #1) | isbn13 | `''` | `None` | `None` |
| 12602078 | The Tycoon's Revenge (Baby for the Billionaire, #1) | original_title | `''` | `None` | `None` |
| 12605157 | The $100 Startup: Reinvent the Way You Make a Living, Do What You Love, and Create a New Future | original_title | `''` | `None` | `None` |
| 12611073 | The Harbinger: The Ancient Mystery that Holds the Secret of America's Future | original_title | `''` | `None` | `None` |
| 12611073 | The Harbinger: The Ancient Mystery that Holds the Secret of America's Future | language_code | `''` | `None` | `None` |
| 126185 | The Christmas Train | language_code | `''` | `None` | `None` |
| 126381 | Purple Hibiscus | language_code | `''` | `None` | `None` |
| 12647642 | Love Unrehearsed (Love, #2) | isbn | `''` | `None` | `None` |
| 12647642 | Love Unrehearsed (Love, #2) | isbn13 | `''` | `None` | `None` |
| 12652457 | The Broken Eye (Lightbringer, #3) | isbn | `''` | `None` | `None` |
| 12652457 | The Broken Eye (Lightbringer, #3) | isbn13 | `''` | `None` | `None` |
| 12659 | Texas | language_code | `''` | `None` | `None` |
| 12667194 | Accordance (Significance, #2) | isbn | `''` | `None` | `None` |
| 12667194 | Accordance (Significance, #2) | isbn13 | `''` | `None` | `None` |
| 12675109 | Great by Choice: Uncertainty, Chaos, and Luck--Why Some Thrive Despite Them All | isbn | `''` | `None` | `None` |
| 12675109 | Great by Choice: Uncertainty, Chaos, and Luck--Why Some Thrive Despite Them All | isbn13 | `''` | `None` | `None` |
| 12675109 | Great by Choice: Uncertainty, Chaos, and Luck--Why Some Thrive Despite Them All | original_title | `''` | `None` | `None` |
| 1268348 | The Secret Between Us | language_code | `''` | `None` | `None` |
| 1268479 | Warbreaker (Warbreaker, #1) | isbn | `''` | `None` | `None` |
| 1268479 | Warbreaker (Warbreaker, #1) | isbn13 | `''` | `None` | `None` |
| 12706435 | Defiance (Significance, #3) | isbn | `''` | `None` | `None` |
| 12706435 | Defiance (Significance, #3) | isbn13 | `''` | `None` | `None` |
| 12712435 | Seating Arrangements | language_code | `''` | `None` | `None` |
| 12716010 | Rapture (Fallen, #4) | isbn | `''` | `None` | `None` |
| 12716010 | Rapture (Fallen, #4) | isbn13 | `''` | `None` | `None` |
| 12716613 | The Witness | language_code | `''` | `None` | `None` |
| 12737118 | Wife 22 | language_code | `''` | `None` | `None` |
| 127451 | Don't Die, My Love | language_code | `''` | `None` | `None` |
| 1275105 | A Charlie Brown Christmas | language_code | `''` | `None` | `None` |
| 12755792 | A Hidden Fire (Elemental Mysteries, #1) | isbn | `''` | `None` | `None` |
| 12755792 | A Hidden Fire (Elemental Mysteries, #1) | isbn13 | `''` | `None` | `None` |
| 12755792 | A Hidden Fire (Elemental Mysteries, #1) | language_code | `''` | `None` | `None` |
| 12758317 | In One Person | language_code | `''` | `None` | `None` |
| 127586 | The White Dragon (Pern, #3) | language_code | `''` | `None` | `None` |
| 12760903 | The Vision (Fallen Star, #3) | isbn | `''` | `None` | `None` |
| 12760903 | The Vision (Fallen Star, #3) | isbn13 | `''` | `None` | `None` |
| 12760903 | The Vision (Fallen Star, #3) | original_title | `''` | `None` | `None` |
| 127970 | The Prize Winner of Defiance, Ohio: How My Mother Raised 10 Kids on 25 Words or Less | language_code | `''` | `None` | `None` |
| 12799058 | Summerland | isbn | `''` | `None` | `None` |
| 12799058 | Summerland | isbn13 | `''` | `None` | `None` |
| 128066 | The Pianist: The Extraordinary Story of One Man's Survival in Warsaw, 1939–45 | language_code | `''` | `None` | `None` |
| 12839 | A Separate Reality | language_code | `''` | `None` | `None` |
| 12842134 | Just One Year (Just One Day, #2) | isbn | `''` | `None` | `None` |
| 12842134 | Just One Year (Just One Day, #2) | isbn13 | `''` | `None` | `None` |
| 12867423 | Girl Walks into a Bar . . .: Comedy Calamities, Dating Disasters, and a Midlife Miracle | original_title | `''` | `None` | `None` |
| 12867423 | Girl Walks into a Bar . . .: Comedy Calamities, Dating Disasters, and a Midlife Miracle | language_code | `''` | `None` | `None` |
| 128711 | The Yacoubian Building | isbn | `''` | `None` | `None` |
| 128711 | The Yacoubian Building | isbn13 | `''` | `None` | `None` |
| 128755 | Cross Bones (Temperance Brennan, #8) | language_code | `''` | `None` | `None` |
| 128759 | Fatal Voyage (Temperance Brennan, #4) | language_code | `''` | `None` | `None` |
| 12878300 | Fearless: The Heroic Story of One Navy SEAL's Sacrifice in the Hunt for Osama Bin Laden and the Unwavering Devotion of the Woman Who Loved Him | original_title | `''` | `None` | `None` |
| 12878300 | Fearless: The Heroic Story of One Navy SEAL's Sacrifice in the Hunt for Osama Bin Laden and the Unwavering Devotion of the Woman Who Loved Him | language_code | `''` | `None` | `None` |
| 12881141 | Wild Man (Dream Man, #2) | isbn | `''` | `None` | `None` |
| 12881141 | Wild Man (Dream Man, #2) | isbn13 | `''` | `None` | `None` |
| 12900174 | The Vincent Boys (The Vincent Boys, #1) | isbn | `''` | `None` | `None` |
| 12900174 | The Vincent Boys (The Vincent Boys, #1) | isbn13 | `''` | `None` | `None` |
| 12902549 | An Invisible Thread: The True Story of an 11-Year-Old Panhandler, a Busy Sales Executive, and an Unlikely Meeting with Destiny | isbn | `''` | `None` | `None` |
| 12902549 | An Invisible Thread: The True Story of an 11-Year-Old Panhandler, a Busy Sales Executive, and an Unlikely Meeting with Destiny | isbn13 | `''` | `None` | `None` |
| 12922320 | Criminal (Will Trent, #6) | isbn | `''` | `None` | `None` |
| 12922320 | Criminal (Will Trent, #6) | isbn13 | `''` | `None` | `None` |
| 12923 | The Castle of Otranto | original_title | `''` | `None` | `None` |
| 12924261 | This Book Is Full of Spiders: Seriously, Dude, Don't Touch It (John Dies at the End, #2) | original_title | `''` | `None` | `None` |
| 12926804 | One for the Murphys | original_title | `''` | `None` | `None` |
| 129510 | Empire of Ivory (Temeraire, #4) | language_code | `''` | `None` | `None` |
| 129565 | Financial Peace Revisited | language_code | `''` | `None` | `None` |
| 12958487 | Lady Luck (Colorado Mountain, #3) | isbn | `''` | `None` | `None` |
| 12958487 | Lady Luck (Colorado Mountain, #3) | isbn13 | `''` | `None` | `None` |
| 1298171 | Finding Nemo | language_code | `''` | `None` | `None` |
| 1298205 | Dumbo: A Little Golden Book | language_code | `''` | `None` | `None` |
| 12987640 | Imagine: How Creativity Works | original_title | `''` | `None` | `None` |
| 129947 | The Water is Wide: A Memoir | language_code | `''` | `None` | `None` |
| 13023 | Alice in Wonderland | original_title | `''` | `None` | `None` |
| 130260 | Birdman (Jack Caffery, #1) | language_code | `''` | `None` | `None` |
| 13027304 | The Hunger Games Tribute Guide | original_title | `''` | `None` | `None` |
| 1303 | The 48 Laws of Power | language_code | `''` | `None` | `None` |
| 13031445 | The Hunger Pains: A Parody | original_title | `''` | `None` | `None` |
| 1305 | Gates of Fire: An Epic Novel of the Battle of Thermopylae | language_code | `''` | `None` | `None` |
| 13051316 | The Misremembered Man (Tailorstown #1) | isbn | `''` | `None` | `None` |
| 13051316 | The Misremembered Man (Tailorstown #1) | isbn13 | `''` | `None` | `None` |
| 13057939 | In the Shadow of the Banyan | language_code | `''` | `None` | `None` |
| 13063 | Basket Case | original_title | `''` | `None` | `None` |
| 13063 | Basket Case | language_code | `''` | `None` | `None` |
| 13065142 | Rock Chick Reckoning (Rock Chick, #6) | isbn | `''` | `None` | `None` |
| 13065142 | Rock Chick Reckoning (Rock Chick, #6) | isbn13 | `''` | `None` | `None` |
| 13065142 | Rock Chick Reckoning (Rock Chick, #6) | original_title | `''` | `None` | `None` |
| 13069213 | Yes, Chef | original_title | `''` | `None` | `None` |
| 13070346 | Blood Rites (The Grey Wolves, #2) | isbn | `''` | `None` | `None` |
| 13070346 | Blood Rites (The Grey Wolves, #2) | isbn13 | `''` | `None` | `None` |
| 13096848 | Avatar: The Last Airbender (The Promise, #2) | original_title | `''` | `None` | `None` |
| 13125947 | Reached (Matched, #3) | language_code | `''` | `None` | `None` |
| 13129925 | Horrorstör | language_code | `''` | `None` | `None` |
| 131304 | Big Bang: The Origin of the Universe | language_code | `''` | `None` | `None` |
| 13132 | 3rd Degree (Women's Murder Club, #3) | language_code | `''` | `None` | `None` |
| 13132816 | Emmy & Oliver | isbn | `''` | `None` | `None` |
| 13132816 | Emmy & Oliver | isbn13 | `''` | `None` | `None` |
| 13146214 | Because of Low (Sea Breeze, #2) | isbn | `''` | `None` | `None` |
| 13146214 | Because of Low (Sea Breeze, #2) | isbn13 | `''` | `None` | `None` |
| 13151283 | بضع ساعات في يوم ما | isbn | `''` | `None` | `None` |
| 13151283 | بضع ساعات في يوم ما | isbn13 | `''` | `None` | `None` |
| 13151637 | طه الغريب | isbn | `''` | `None` | `None` |
| 13151637 | طه الغريب | isbn13 | `''` | `None` | `None` |
| 13152194 | Tiny Beautiful Things: Advice on Love and Life from Dear Sugar | language_code | `''` | `None` | `None` |
| 13152998 | Home | language_code | `''` | `None` | `None` |
| 13153693 | Ghettoside: A True Story of Murder in America | language_code | `''` | `None` | `None` |
| 13154952 | Calico Joe | language_code | `''` | `None` | `None` |
| 13167062 | Spring Fever | original_title | `''` | `None` | `None` |
| 13167847 | Most Talkative: Stories from the Front Lines of Pop Culture | original_title | `''` | `None` | `None` |
| 13167847 | Most Talkative: Stories from the Front Lines of Pop Culture | language_code | `''` | `None` | `None` |
| 13168 | Runaway Ralph (Ralph S. Mouse, #2) | language_code | `''` | `None` | `None` |
| 1317181 | Harry Potter and the Order of the Phoenix (Harry Potter, #5, Part 1) | original_title | `''` | `None` | `None` |
| 1317181 | Harry Potter and the Order of the Phoenix (Harry Potter, #5, Part 1) | language_code | `''` | `None` | `None` |
| 13178410 | Proper Gauge (Wool, #2) | isbn | `''` | `None` | `None` |
| 13178410 | Proper Gauge (Wool, #2) | isbn13 | `''` | `None` | `None` |
| 131830 | Women's Bodies, Women's Wisdom: Creating Physical and Emotional Health and Healing | language_code | `''` | `None` | `None` |
| 13184572 | The Next Best Thing | isbn | `''` | `None` | `None` |
| 13184572 | The Next Best Thing | isbn13 | `''` | `None` | `None` |
| 13184572 | The Next Best Thing | language_code | `''` | `None` | `None` |
| 13184992 | Rock Chick Regret (Rock Chick, #7) | isbn | `''` | `None` | `None` |
| 13184992 | Rock Chick Regret (Rock Chick, #7) | isbn13 | `''` | `None` | `None` |
| 13184992 | Rock Chick Regret (Rock Chick, #7) | original_title | `''` | `None` | `None` |
| 13188676 | Ignite Me (Shatter Me, #3) | isbn | `''` | `None` | `None` |
| 13188676 | Ignite Me (Shatter Me, #3) | isbn13 | `''` | `None` | `None` |
| 132152 | Streams in the Desert | language_code | `''` | `None` | `None` |
| 13223520 | Existence (Existence Trilogy, #1) | isbn | `''` | `None` | `None` |
| 13223520 | Existence (Existence Trilogy, #1) | isbn13 | `''` | `None` | `None` |
| 13223520 | Existence (Existence Trilogy, #1) | original_title | `''` | `None` | `None` |
| 13226173 | The Infernal Devices: Clockwork Angel (The Infernal Devices: Manga, #1) | original_title | `''` | `None` | `None` |
| 13230263 | Mrs. Kennedy and Me: An Intimate Memoir | original_title | `''` | `None` | `None` |
| 13235 | The Complete Stories and Poems | language_code | `''` | `None` | `None` |
| 13235689 | How Music Works | language_code | `''` | `None` | `None` |
| 13241659 | Ever After (The Hollows, #11) | original_title | `''` | `None` | `None` |
| 13256064 | Phantom (Harry Hole, #9) | language_code | `''` | `None` | `None` |
| 13272498 | Last to Die (Rizzoli & Isles, #10) | language_code | `''` | `None` | `None` |
| 13281637 | Intuition (The Premonition, #2) | original_title | `''` | `None` | `None` |
| 13312527 | The Opportunist (Love Me with Lies, #1) | isbn | `''` | `None` | `None` |
| 13312527 | The Opportunist (Love Me with Lies, #1) | isbn13 | `''` | `None` | `None` |
| 13323842 | Predestined (Existence Trilogy, #2) | isbn | `''` | `None` | `None` |
| 13323842 | Predestined (Existence Trilogy, #2) | isbn13 | `''` | `None` | `None` |
| 13330603 | The Sandcastle Girls | language_code | `''` | `None` | `None` |
| 13330761 | The Dog Stars | language_code | `''` | `None` | `None` |
| 13331184 | Heads in Beds: A Reckless Memoir of Hotels, Hustles, and So-Called Hospitality | language_code | `''` | `None` | `None` |
| 13331199 | The Smitten Kitchen Cookbook | original_title | `''` | `None` | `None` |
| 13331199 | The Smitten Kitchen Cookbook | language_code | `''` | `None` | `None` |
| 133445 | The Edible Woman | language_code | `''` | `None` | `None` |
| 13345975 | Avoiding Commitment (Avoiding, #1) | isbn | `''` | `None` | `None` |
| 13345975 | Avoiding Commitment (Avoiding, #1) | isbn13 | `''` | `None` | `None` |
| 13350 | Eragon & Eldest (Inheritance, #1-2) | language_code | `''` | `None` | `None` |
| 13362536 | Opal (Lux, #3) | language_code | `''` | `None` | `None` |
| 13363270 | Just One Drop (The Grey Wolves, #3) | isbn | `''` | `None` | `None` |
| 13363270 | Just One Drop (The Grey Wolves, #3) | isbn13 | `''` | `None` | `None` |
| 13369678 | The Vincent Brothers (The Vincent Boys, #2) | isbn | `''` | `None` | `None` |
| 13369678 | The Vincent Brothers (The Vincent Boys, #2) | isbn13 | `''` | `None` | `None` |
| 13372690 | Slammed (Slammed, #1) | isbn | `''` | `None` | `None` |
| 13372690 | Slammed (Slammed, #1) | isbn13 | `''` | `None` | `None` |
| 13376 | The House of the Scorpion (Matteo Alacran, #1) | original_title | `''` | `None` | `None` |
| 133906 | The Collected Poems | language_code | `''` | `None` | `None` |
| 133954 | Washington Square | language_code | `''` | `None` | `None` |
| 13402447 | UnEnchanted (An Unfortunate Fairy Tale, #1) | isbn | `''` | `None` | `None` |
| 13402447 | UnEnchanted (An Unfortunate Fairy Tale, #1) | isbn13 | `''` | `None` | `None` |
| 13412515 | Law Man (Dream Man, #3) | isbn | `''` | `None` | `None` |
| 13412515 | Law Man (Dream Man, #3) | isbn13 | `''` | `None` | `None` |
| 13415554 | The Assassin and the Pirate Lord (Throne of Glass, #0.1) | isbn | `''` | `None` | `None` |
| 13415554 | The Assassin and the Pirate Lord (Throne of Glass, #0.1) | isbn13 | `''` | `None` | `None` |
| 13417946 | Eden (Providence, #3) | original_title | `''` | `None` | `None` |
| 13417946 | Eden (Providence, #3) | language_code | `''` | `None` | `None` |
| 13419891 | The Assassin and the Desert (Throne of Glass, #0.3) | isbn | `''` | `None` | `None` |
| 13419891 | The Assassin and the Desert (Throne of Glass, #0.3) | isbn13 | `''` | `None` | `None` |
| 13425393 | I Suck at Girls | original_title | `''` | `None` | `None` |
| 13425393 | I Suck at Girls | language_code | `''` | `None` | `None` |
| 13425570 | How Will You Measure Your Life? | language_code | `''` | `None` | `None` |
| 13431827 | The Remaining (The Remaining, #1) | isbn | `''` | `None` | `None` |
| 13431827 | The Remaining (The Remaining, #1) | isbn13 | `''` | `None` | `None` |
| 13431827 | The Remaining (The Remaining, #1) | original_title | `''` | `None` | `None` |
| 134360 | Diane Arbus: Monograph | language_code | `''` | `None` | `None` |
| 13448656 | Motorcycle Man (Dream Man, #4) | isbn | `''` | `None` | `None` |
| 13448656 | Motorcycle Man (Dream Man, #4) | isbn13 | `''` | `None` | `None` |
| 13451 | Storm of the Century: An Original Screenplay | language_code | `''` | `None` | `None` |
| 13453029 | Wool Omnibus (Silo, #1) | isbn | `''` | `None` | `None` |
| 13453029 | Wool Omnibus (Silo, #1) | isbn13 | `''` | `None` | `None` |
| 1347837 | Rule of Two (Star Wars: Darth Bane, #2) | original_title | `''` | `None` | `None` |
| 13489517 | 28 حرف | isbn | `''` | `None` | `None` |
| 13489517 | 28 حرف | isbn13 | `''` | `None` | `None` |
| 13489518 | Out of the Dark (The Grey Wolves, #4) | isbn | `''` | `None` | `None` |
| 13489518 | Out of the Dark (The Grey Wolves, #4) | isbn13 | `''` | `None` | `None` |
| 134958 | Elizabeth: The Struggle for the Throne | language_code | `''` | `None` | `None` |
| 13496084 | Point of Retreat (Slammed, #2) | isbn | `''` | `None` | `None` |
| 13496084 | Point of Retreat (Slammed, #2) | isbn13 | `''` | `None` | `None` |
| 13496738 | While It Lasts (Sea Breeze, #3) | isbn | `''` | `None` | `None` |
| 13496738 | While It Lasts (Sea Breeze, #3) | isbn13 | `''` | `None` | `None` |
| 1350249 | The Lion King (Disney's Wonderful World of Reading) | original_title | `''` | `None` | `None` |
| 13502963 | Indebted (The Premonition, #3) | isbn | `''` | `None` | `None` |
| 13502963 | Indebted (The Premonition, #3) | isbn13 | `''` | `None` | `None` |
| 13502963 | Indebted (The Premonition, #3) | original_title | `''` | `None` | `None` |
| 13502970 | Incendiary (The Premonition, #4) | isbn | `''` | `None` | `None` |
| 13502970 | Incendiary (The Premonition, #4) | isbn13 | `''` | `None` | `None` |
| 13507011 | Low Pressure | isbn | `''` | `None` | `None` |
| 13507011 | Low Pressure | isbn13 | `''` | `None` | `None` |
| 13508607 | The Secret Keeper | language_code | `''` | `None` | `None` |
| 13519844 | Independence (Significance, #4) | original_title | `''` | `None` | `None` |
| 13521299 | Alex Cross, Run (Alex Cross, #20) | language_code | `''` | `None` | `None` |
| 13522957 | Feral Sins (The Phoenix Pack, #1) | isbn | `''` | `None` | `None` |
| 13522957 | Feral Sins (The Phoenix Pack, #1) | isbn13 | `''` | `None` | `None` |
| 13523061 | The Defining Decade: Why Your Twenties Matter--And How to Make the Most of Them Now | language_code | `''` | `None` | `None` |
| 13530981 | Dear Life: Stories | language_code | `''` | `None` | `None` |
| 13531832 | Vampires in the Lemon Grove | original_title | `''` | `None` | `None` |
| 13540215 | The Orchardist | language_code | `''` | `None` | `None` |
| 13545075 | UnWholly (Unwind, #2) | language_code | `''` | `None` | `None` |
| 13545345 | Tales from a Not-So-Graceful Ice Princess (Dork Diaries, #4) | language_code | `''` | `None` | `None` |
| 13546173 | The Assassin and the Underworld (Throne of Glass, #0.4) | isbn | `''` | `None` | `None` |
| 13546173 | The Assassin and the Underworld (Throne of Glass, #0.4) | isbn13 | `''` | `None` | `None` |
| 13547234 | The Testament of Mary | language_code | `''` | `None` | `None` |
| 13547241 | Unorthodox: The Scandalous Rejection of My Hasidic Roots | original_title | `''` | `None` | `None` |
| 13560262 | Avoiding Responsibility (Avoiding, #2) | original_title | `''` | `None` | `None` |
| 13565676 | The Assassin and the Empire (Throne of Glass, #0.5) | isbn | `''` | `None` | `None` |
| 13565676 | The Assassin and the Empire (Throne of Glass, #0.5) | isbn13 | `''` | `None` | `None` |
| 13565914 | Knight (Unfinished Hero, #1) | isbn | `''` | `None` | `None` |
| 13565914 | Knight (Unfinished Hero, #1) | isbn13 | `''` | `None` | `None` |
| 13568322 | The Zombie Room | original_title | `''` | `None` | `None` |
| 13568619 | The Shadowhunter's Codex | isbn | `''` | `None` | `None` |
| 13568619 | The Shadowhunter's Codex | isbn13 | `''` | `None` | `None` |
| 13569581 | Blood Song (Raven's Shadow, #1) | isbn | `''` | `None` | `None` |
| 13569581 | Blood Song (Raven's Shadow, #1) | isbn13 | `''` | `None` | `None` |
| 13573236 | The Racketeer | language_code | `''` | `None` | `None` |
| 13573795 | Ceaseless (Existence Trilogy, #3) | isbn | `''` | `None` | `None` |
| 13573795 | Ceaseless (Existence Trilogy, #3) | isbn13 | `''` | `None` | `None` |
| 13580846 | My Life with the Walter Boys (My Life with the Walter Boys #1) | isbn | `''` | `None` | `None` |
| 13580846 | My Life with the Walter Boys (My Life with the Walter Boys #1) | isbn13 | `''` | `None` | `None` |
| 13584236 | Fifty Shades Trilogy (Fifty Shades, #1-3) | original_title | `''` | `None` | `None` |
| 13584236 | Fifty Shades Trilogy (Fifty Shades, #1-3) | language_code | `''` | `None` | `None` |
| 13586743 | One Last Thing Before I Go | language_code | `''` | `None` | `None` |
| 13588356 | Daring Greatly: How the Courage to Be Vulnerable Transforms the Way We Live, Love, Parent, and Lead | language_code | `''` | `None` | `None` |
| 13589182 | Mastery | language_code | `''` | `None` | `None` |
| 13593526 | City of Women | original_title | `''` | `None` | `None` |
| 13593526 | City of Women | language_code | `''` | `None` | `None` |
| 13593553 | To Sell Is Human: The Surprising Truth About Moving Others | original_title | `''` | `None` | `None` |
| 13593553 | To Sell Is Human: The Surprising Truth About Moving Others | language_code | `''` | `None` | `None` |
| 13593555 | Mad River (Virgil Flowers, #6) | original_title | `''` | `None` | `None` |
| 13600318 | Reckless (Thoughtless, #3) | isbn | `''` | `None` | `None` |
| 13600318 | Reckless (Thoughtless, #3) | isbn13 | `''` | `None` | `None` |
| 13601550 | Accidentally on Purpose (Accidentally on Purpose, #1) | isbn | `''` | `None` | `None` |
| 13601550 | Accidentally on Purpose (Accidentally on Purpose, #1) | isbn13 | `''` | `None` | `None` |
| 13601550 | Accidentally on Purpose (Accidentally on Purpose, #1) | original_title | `''` | `None` | `None` |
| 13603717 | First Shift: Legacy (Shift, #1) | isbn | `''` | `None` | `None` |
| 13603717 | First Shift: Legacy (Shift, #1) | isbn13 | `''` | `None` | `None` |
| 13605723 | Sentinel (Covenant, #5) | original_title | `''` | `None` | `None` |
| 13605727 | Elixir (Covenant, #3.5) | language_code | `''` | `None` | `None` |
| 13612739 | Seduced in the Dark (The Dark Duet, #2) | isbn | `''` | `None` | `None` |
| 13612739 | Seduced in the Dark (The Dark Duet, #2) | isbn13 | `''` | `None` | `None` |
| 13612739 | Seduced in the Dark (The Dark Duet, #2) | original_title | `''` | `None` | `None` |
| 13621 | Death Note, Vol. 7: Zero (Death Note, #7) | language_code | `''` | `None` | `None` |
| 13623012 | The Prisoner of Heaven (The Cemetery of Forgotten Books, #3) | language_code | `''` | `None` | `None` |
| 13624367 | Checkmate (Neighbor from Hell, #3) | isbn | `''` | `None` | `None` |
| 13624367 | Checkmate (Neighbor from Hell, #3) | isbn13 | `''` | `None` | `None` |
| 13628812 | The Rent Collector | original_title | `''` | `None` | `None` |
| 13634927 | A Leaf on the Wind of All Hallows (Outlander, #8.5) | isbn | `''` | `None` | `None` |
| 13634927 | A Leaf on the Wind of All Hallows (Outlander, #8.5) | isbn13 | `''` | `None` | `None` |
| 13638570 | Out of Breath (Breathing, #3) | isbn | `''` | `None` | `None` |
| 13638570 | Out of Breath (Breathing, #3) | isbn13 | `''` | `None` | `None` |
| 13640229 | Creed (Unfinished Hero, #2) | isbn | `''` | `None` | `None` |
| 13640229 | Creed (Unfinished Hero, #2) | isbn13 | `''` | `None` | `None` |
| 13642929 | My Beloved World | original_title | `''` | `None` | `None` |
| 13643567 | The Evolution of Mara Dyer (Mara Dyer, #2) | isbn | `''` | `None` | `None` |
| 13643567 | The Evolution of Mara Dyer (Mara Dyer, #2) | isbn13 | `''` | `None` | `None` |
| 13649056 | Try Me (One Night with Sole Regret, #1) | isbn | `''` | `None` | `None` |
| 13649056 | Try Me (One Night with Sole Regret, #1) | isbn13 | `''` | `None` | `None` |
| 136640 | The Codex | language_code | `''` | `None` | `None` |
| 13667 | The Farthest Shore (Earthsea Cycle, #3) | language_code | `''` | `None` | `None` |
| 136977 | The Places That Scare You: A Guide to Fearlessness in Difficult Times | language_code | `''` | `None` | `None` |
| 1372055 | Courageous (The Lost Fleet, #3) | language_code | `''` | `None` | `None` |
| 1375896 | Queste (Septimus Heap, #4) | language_code | `''` | `None` | `None` |
| 13765729 | Abducted (Lizzy Gardner #1) | isbn | `''` | `None` | `None` |
| 13765729 | Abducted (Lizzy Gardner #1) | isbn13 | `''` | `None` | `None` |
| 137792 | Ya Yas in Bloom | language_code | `''` | `None` | `None` |
| 13809 | Exile's Return (Conclave of Shadows, #3) | language_code | `''` | `None` | `None` |
| 13817 | Shards of a Broken Crown (The Serpentwar Saga, #4) | language_code | `''` | `None` | `None` |
| 13891 | Winter's Heart (Wheel of Time, #9) | original_title | `''` | `None` | `None` |
| 139004 | Essays and Poems | language_code | `''` | `None` | `None` |
| 139220 | Heat: An Amateur's Adventures as Kitchen Slave, Line Cook, Pasta-Maker, and Apprentice to a Dante-Quoting Butcher in Tuscany | language_code | `''` | `None` | `None` |
| 140091 | Real Murders (Aurora Teagarden, #1) | original_title | `''` | `None` | `None` |
| 140131 | The Three Little Pigs (Disney Classic) | language_code | `''` | `None` | `None` |
| 140302 | Poirot Investiga (Hércules Poirot, #3) | isbn | `''` | `None` | `None` |
| 140302 | Poirot Investiga (Hércules Poirot, #3) | isbn13 | `''` | `None` | `None` |
| 14060046 | Obsession | isbn | `''` | `None` | `None` |
| 14060046 | Obsession | isbn13 | `''` | `None` | `None` |
| 14060046 | Obsession | original_title | `''` | `None` | `None` |
| 141019 | Snow White and the Seven Dwarfs (Little Golden Book) | language_code | `''` | `None` | `None` |
| 141077 | The Kreutzer Sonata | language_code | `''` | `None` | `None` |
| 14118 | Beauty and the Beast (Disney) | language_code | `''` | `None` | `None` |
| 141526 | Pulp | language_code | `''` | `None` | `None` |
| 141565 | This Is Your Brain on Music: The Science of a Human Obsession | language_code | `''` | `None` | `None` |
| 14165516 | The Marriage Trap (Marriage to a Billionaire, #2) | isbn | `''` | `None` | `None` |
| 14165516 | The Marriage Trap (Marriage to a Billionaire, #2) | isbn13 | `''` | `None` | `None` |
| 142108 | Rich Dad's Guide to Investing: What the Rich Invest in That the Poor and Middle Class Do Not! | language_code | `''` | `None` | `None` |
| 1422926 | Frosty the Snow Man | language_code | `''` | `None` | `None` |
| 142900 | The Master Butchers Singing Club | language_code | `''` | `None` | `None` |
| 14316 | Black Swan Green | language_code | `''` | `None` | `None` |
| 14367051 | City of Bones / City of Ashes / City of Glass / City of Fallen Angels / City of Lost Souls (The Mortal Instruments, #1-5) | original_title | `''` | `None` | `None` |
| 14367051 | City of Bones / City of Ashes / City of Glass / City of Fallen Angels / City of Lost Souls (The Mortal Instruments, #1-5) | language_code | `''` | `None` | `None` |
| 14469 | Selected Stories | language_code | `''` | `None` | `None` |
| 144773 | Contest | language_code | `''` | `None` | `None` |
| 14480 | Calling Doctor Amelia Bedelia | language_code | `''` | `None` | `None` |
| 14481 | Come Back, Amelia Bedelia | language_code | `''` | `None` | `None` |
| 1464757 | Edensor (Tetralogi Laskar Pelangi, #3) | isbn | `''` | `None` | `None` |
| 1464757 | Edensor (Tetralogi Laskar Pelangi, #3) | isbn13 | `''` | `None` | `None` |
| 147074 | Janet Evanovich Three and Four Two-Book Set (Stephanie Plum, #3-4) | language_code | `''` | `None` | `None` |
| 14740588 | Notorious Nineteen (Stephanie Plum, #19) | isbn | `''` | `None` | `None` |
| 14740588 | Notorious Nineteen (Stephanie Plum, #19) | isbn13 | `''` | `None` | `None` |
| 14744381 | The Walking Dead, Compendium 2 | original_title | `''` | `None` | `None` |
| 14745338 | Fairest (An Unfortunate Fairy Tale, #2) | isbn | `''` | `None` | `None` |
| 14745338 | Fairest (An Unfortunate Fairy Tale, #2) | isbn13 | `''` | `None` | `None` |
| 14745338 | Fairest (An Unfortunate Fairy Tale, #2) | original_title | `''` | `None` | `None` |
| 14758 | In Her Shoes | language_code | `''` | `None` | `None` |
| 14781501 | NYPD Red (NYPD Red, #1) | language_code | `''` | `None` | `None` |
| 147941 | Figure Drawing for All It's Worth (How to draw and paint) | language_code | `''` | `None` | `None` |
| 148337 | Where Eagles Dare  | language_code | `''` | `None` | `None` |
| 14889780 | Two Graves (Pendergast, #12) | language_code | `''` | `None` | `None` |
| 14905 | The Complete Novels | original_title | `''` | `None` | `None` |
| 1491906 | Gang Leader for a Day: A Rogue Sociologist Takes to the Streets | language_code | `''` | `None` | `None` |
| 149196 | Eva Luna | language_code | `''` | `None` | `None` |
| 14963 | A Wedding in December | language_code | `''` | `None` | `None` |
| 14965 | Light on Snow | language_code | `''` | `None` | `None` |
| 1499952 | Daddy-Long-Legs (Daddy-Long-Legs, #1) | isbn | `''` | `None` | `None` |
| 1499952 | Daddy-Long-Legs (Daddy-Long-Legs, #1) | isbn13 | `''` | `None` | `None` |
| 1503274 | Rhett Butler's People | language_code | `''` | `None` | `None` |
| 15034320 | Pines (Wayward Pines, #1) | language_code | `''` | `None` | `None` |
| 15055 | Oranges Are Not the Only Fruit | isbn | `''` | `None` | `None` |
| 15055 | Oranges Are Not the Only Fruit | isbn13 | `''` | `None` | `None` |
| 15059301 | Captured (The Captive, #1) | isbn | `''` | `None` | `None` |
| 15059301 | Captured (The Captive, #1) | isbn13 | `''` | `None` | `None` |
| 15059301 | Captured (The Captive, #1) | original_title | `''` | `None` | `None` |
| 15062217 | 14 | isbn | `''` | `None` | `None` |
| 15062217 | 14 | isbn13 | `''` | `None` | `None` |
| 15171 | A Girl Named Zippy | language_code | `''` | `None` | `None` |
| 15283043 | The Distance Between Us | original_title | `''` | `None` | `None` |
| 153136 | The Cake Bible | language_code | `''` | `None` | `None` |
| 153175 | King of Foxes (Conclave of Shadows, #2) | language_code | `''` | `None` | `None` |
| 153492 | The 39 Steps (Richard Hannay, #1) | language_code | `''` | `None` | `None` |
| 153542 | Mike Mulligan and His Steam Shovel | language_code | `''` | `None` | `None` |
| 153781 | Magic Steps (The Circle Opens, #1) | language_code | `''` | `None` | `None` |
| 153785 | Page (Protector of the Small, #2) | isbn | `''` | `None` | `None` |
| 153785 | Page (Protector of the Small, #2) | isbn13 | `''` | `None` | `None` |
| 153795 | Squire (Protector of the Small, #3) | isbn | `''` | `None` | `None` |
| 153795 | Squire (Protector of the Small, #3) | isbn13 | `''` | `None` | `None` |
| 153800 | Lady Knight (Protector of the Small, #4) | isbn | `''` | `None` | `None` |
| 153800 | Lady Knight (Protector of the Small, #4) | isbn13 | `''` | `None` | `None` |
| 153800 | Lady Knight (Protector of the Small, #4) | language_code | `''` | `None` | `None` |
| 15398 | The Last Days of Dogtown | language_code | `''` | `None` | `None` |
| 1540 | The Oedipus Cycle: Oedipus Rex/Oedipus at Colonus/Antigone (The Theban Plays, #1–3) | original_title | `''` | `None` | `None` |
| 15433 | Night Mare (Xanth, #6) | language_code | `''` | `None` | `None` |
| 15447 | The Source of Magic (Xanth, #2) | language_code | `''` | `None` | `None` |
| 15513156 | Of Triton (The Syrena Legacy, #2) | original_title | `''` | `None` | `None` |
| 155370 | Double Identity | language_code | `''` | `None` | `None` |
| 15549 | Armageddon's Children (Genesis of Shannara, #1) | language_code | `''` | `None` | `None` |
| 15561 | Wizard at Large (Magic Kingdom of Landover, #3) | language_code | `''` | `None` | `None` |
| 155981 | Psycho-Cybernetics, A New Way to Get More Living Out of Life | language_code | `''` | `None` | `None` |
| 15645 | Inferno (The Divine Comedy #1) | language_code | `''` | `None` | `None` |
| 15676 | Strangers | language_code | `''` | `None` | `None` |
| 15704001 | Seduction and Snacks (Chocolate Lovers, #1) | isbn | `''` | `None` | `None` |
| 15704001 | Seduction and Snacks (Chocolate Lovers, #1) | isbn13 | `''` | `None` | `None` |
| 157076 | The Most Dangerous Game | language_code | `''` | `None` | `None` |
| 15717721 | If I Were You (Inside Out, #1) | isbn | `''` | `None` | `None` |
| 15717721 | If I Were You (Inside Out, #1) | isbn13 | `''` | `None` | `None` |
| 15722284 | Saint Odd (Odd Thomas, #7) | isbn | `''` | `None` | `None` |
| 15722284 | Saint Odd (Odd Thomas, #7) | isbn13 | `''` | `None` | `None` |
| 15723286 | Curtsies & Conspiracies (Finishing School, #2) | isbn | `''` | `None` | `None` |
| 15723286 | Curtsies & Conspiracies (Finishing School, #2) | isbn13 | `''` | `None` | `None` |
| 15724654 | The Mighty Storm (The Storm, #1) | isbn | `''` | `None` | `None` |
| 15724654 | The Mighty Storm (The Storm, #1) | isbn13 | `''` | `None` | `None` |
| 15728921 | Don't Let Me Go | isbn | `''` | `None` | `None` |
| 15728921 | Don't Let Me Go | isbn13 | `''` | `None` | `None` |
| 15729261 | The Marriage Mistake (Marriage to a Billionaire, #3) | isbn | `''` | `None` | `None` |
| 15729261 | The Marriage Mistake (Marriage to a Billionaire, #3) | isbn13 | `''` | `None` | `None` |
| 15730101 | The Call of Cthulhu | isbn | `''` | `None` | `None` |
| 15730101 | The Call of Cthulhu | isbn13 | `''` | `None` | `None` |
| 15733346 | Is It Just Me? | original_title | `''` | `None` | `None` |
| 15733851 | You Had Me At Hello | language_code | `''` | `None` | `None` |
| 15734464 | 12th of Never (Women's Murder Club, #12) | isbn | `''` | `None` | `None` |
| 15734464 | 12th of Never (Women's Murder Club, #12) | isbn13 | `''` | `None` | `None` |
| 15737147 | Help Thanks Wow: The Three Essential Prayers | original_title | `''` | `None` | `None` |
| 15738951 | Deep Down (Jack Reacher, #16.5) | isbn | `''` | `None` | `None` |
| 15738951 | Deep Down (Jack Reacher, #16.5) | isbn13 | `''` | `None` | `None` |
| 15739018 | Taking Chances (Taking Chances, #1) | isbn | `''` | `None` | `None` |
| 15739018 | Taking Chances (Taking Chances, #1) | isbn13 | `''` | `None` | `None` |
| 15739018 | Taking Chances (Taking Chances, #1) | original_title | `''` | `None` | `None` |
| 15742039 | Breathe (Colorado Mountain, #4) | isbn | `''` | `None` | `None` |
| 15742039 | Breathe (Colorado Mountain, #4) | isbn13 | `''` | `None` | `None` |
| 15743078 | The Divergent Series 2-Book Collection (Divergent, #1-2) | original_title | `''` | `None` | `None` |
| 15745371 | Chosen at Nightfall (Shadow Falls, #5) | original_title | `''` | `None` | `None` |
| 15748335 | Leave Me Breathless (Ross Siblings, #3) | isbn | `''` | `None` | `None` |
| 15748335 | Leave Me Breathless (Ross Siblings, #3) | isbn13 | `''` | `None` | `None` |
| 15748335 | Leave Me Breathless (Ross Siblings, #3) | original_title | `''` | `None` | `None` |
| 15749186 | To All the Boys I've Loved Before (To All the Boys I've Loved Before, #1) | isbn | `''` | `None` | `None` |
| 15749186 | To All the Boys I've Loved Before (To All the Boys I've Loved Before, #1) | isbn13 | `''` | `None` | `None` |
| 15752 | By the Light of the Moon | language_code | `''` | `None` | `None` |
| 15752757 | Rock Chick Revolution (Rock Chick, #8) | isbn | `''` | `None` | `None` |
| 15752757 | Rock Chick Revolution (Rock Chick, #8) | isbn13 | `''` | `None` | `None` |
| 15752757 | Rock Chick Revolution (Rock Chick, #8) | original_title | `''` | `None` | `None` |
| 15757434 | Crash (Crash, #1) | isbn | `''` | `None` | `None` |
| 15757434 | Crash (Crash, #1) | isbn13 | `''` | `None` | `None` |
| 15760 | Dark Rivers of the Heart | language_code | `''` | `None` | `None` |
| 15760001 | On Dublin Street (On Dublin Street, #1) | isbn | `''` | `None` | `None` |
| 15760001 | On Dublin Street (On Dublin Street, #1) | isbn13 | `''` | `None` | `None` |
| 15761241 | The Wild Ones (The Wild Ones, #1) | isbn | `''` | `None` | `None` |
| 15761241 | The Wild Ones (The Wild Ones, #1) | isbn13 | `''` | `None` | `None` |
| 15762657 | Seducing Cinderella (Fighting for Love, #1) | isbn | `''` | `None` | `None` |
| 15762657 | Seducing Cinderella (Fighting for Love, #1) | isbn13 | `''` | `None` | `None` |
| 15762975 | Wrong Bed, Right Guy (Come Undone, #1) | isbn | `''` | `None` | `None` |
| 15762975 | Wrong Bed, Right Guy (Come Undone, #1) | isbn13 | `''` | `None` | `None` |
| 15764 | The Amateur Marriage | language_code | `''` | `None` | `None` |
| 15766776 | Rump: The True Story of Rumpelstiltskin | original_title | `''` | `None` | `None` |
| 15768191 | Sweet Peril (Sweet, #2) | original_title | `''` | `None` | `None` |
| 15768536 | Fall From Grace (Mad World, #1) | isbn | `''` | `None` | `None` |
| 15768536 | Fall From Grace (Mad World, #1) | isbn13 | `''` | `None` | `None` |
| 15768536 | Fall From Grace (Mad World, #1) | original_title | `''` | `None` | `None` |
| 15771862 | Wave | isbn | `''` | `None` | `None` |
| 15771862 | Wave | isbn13 | `''` | `None` | `None` |
| 15776904 | The Beggar King (The Hangman's Daughter, #3) | isbn | `''` | `None` | `None` |
| 15776904 | The Beggar King (The Hangman's Daughter, #3) | isbn13 | `''` | `None` | `None` |
| 15778138 | Just for Now (Sea Breeze, #4) | isbn | `''` | `None` | `None` |
| 15778138 | Just for Now (Sea Breeze, #4) | isbn13 | `''` | `None` | `None` |
| 15779 | Sideways Stories from Wayside School (Wayside School #1) | original_title | `''` | `None` | `None` |
| 15783307 | The Perfect Game (The Perfect Game, #1) | isbn | `''` | `None` | `None` |
| 15783307 | The Perfect Game (The Perfect Game, #1) | isbn13 | `''` | `None` | `None` |
| 15784909 | This Girl (Slammed, #3) | isbn | `''` | `None` | `None` |
| 15784909 | This Girl (Slammed, #3) | isbn13 | `''` | `None` | `None` |
| 15786110 | Relish: My Life in the Kitchen | original_title | `''` | `None` | `None` |
| 15791403 | Mistress | language_code | `''` | `None` | `None` |
| 15793165 | Don't Go | original_title | `''` | `None` | `None` |
| 15797722 | Deeply Odd (Odd Thomas, #6) | original_title | `''` | `None` | `None` |
| 15801668 | The Girls of Atomic City: The Untold Story of the Women Who Helped Win World War II | original_title | `''` | `None` | `None` |
| 15811495 | Touch & Go (Tessa Leoni, #2) | original_title | `''` | `None` | `None` |
| 15811520 | Detroit: An American Autopsy | original_title | `''` | `None` | `None` |
| 15820492 | Annabel (Delirium, #0.5) | language_code | `''` | `None` | `None` |
| 15820748 | The Prince (The Selection, #0.5) | language_code | `''` | `None` | `None` |
| 15828714 | Sometimes It Lasts (Sea Breeze, #5) | isbn | `''` | `None` | `None` |
| 15828714 | Sometimes It Lasts (Sea Breeze, #5) | isbn13 | `''` | `None` | `None` |
| 15832316 | Dirty Red (Love Me with Lies, #2) | isbn | `''` | `None` | `None` |
| 15832316 | Dirty Red (Love Me with Lies, #2) | isbn13 | `''` | `None` | `None` |
| 15835685 | Clash (Crash, #2) | isbn | `''` | `None` | `None` |
| 15835685 | Clash (Crash, #2) | isbn13 | `''` | `None` | `None` |
| 15843166 | You Are a Badass: How to Stop Doubting Your Greatness and Start Living an Awesome Life | original_title | `''` | `None` | `None` |
| 15843166 | You Are a Badass: How to Stop Doubting Your Greatness and Start Living an Awesome Life | language_code | `''` | `None` | `None` |
| 15849910 | The King's Curse (The Plantagenet and Tudor Novels, #7) | original_title | `''` | `None` | `None` |
| 158516 | The Twelve Chairs | language_code | `''` | `None` | `None` |
| 15852756 | Naked (The Blackstone Affair, #1) | isbn | `''` | `None` | `None` |
| 15852756 | Naked (The Blackstone Affair, #1) | isbn13 | `''` | `None` | `None` |
| 158944 | The Fannie Farmer Cookbook: Anniversary | language_code | `''` | `None` | `None` |
| 15902792 | Still Foolin' 'Em: Where I've Been, Where I'm Going, and Where the Hell Are My Keys | original_title | `''` | `None` | `None` |
| 159418 | Discourse on Method | original_title | `''` | `None` | `None` |
| 159760 | Reviving Ophelia: Saving the Selves of Adolescent Girls | language_code | `''` | `None` | `None` |
| 15981894 | Devoured (Devoured, #1) | isbn | `''` | `None` | `None` |
| 15981894 | Devoured (Devoured, #1) | isbn13 | `''` | `None` | `None` |
| 15993374 | Charade (Games, #1) | isbn | `''` | `None` | `None` |
| 15993374 | Charade (Games, #1) | isbn13 | `''` | `None` | `None` |
| 16001443 | All In (The Blackstone Affair, #2) | isbn | `''` | `None` | `None` |
| 16001443 | All In (The Blackstone Affair, #2) | isbn13 | `''` | `None` | `None` |
| 16001893 | Down to You (The Bad Boys, #1) | isbn | `''` | `None` | `None` |
| 16001893 | Down to You (The Bad Boys, #1) | isbn13 | `''` | `None` | `None` |
| 16007855 | Sweet Reckoning (Sweet, #3) | original_title | `''` | `None` | `None` |
| 160194 | Noises Off | language_code | `''` | `None` | `None` |
| 16031620 | الفيل الأزرق | isbn | `''` | `None` | `None` |
| 16031620 | الفيل الأزرق | isbn13 | `''` | `None` | `None` |
| 16031679 | Tempting the Player (Gamble Brothers, #2) | language_code | `''` | `None` | `None` |
| 1603923 | Beauty and the Beast | language_code | `''` | `None` | `None` |
| 16041169 | Disastrous (Disastrous, #1) | original_title | `''` | `None` | `None` |
| 16042305 | Love Left Behind | isbn | `''` | `None` | `None` |
| 16042305 | Love Left Behind | isbn13 | `''` | `None` | `None` |
| 16042305 | Love Left Behind | original_title | `''` | `None` | `None` |
| 16045144 | The Beautiful Mystery (Chief Inspector Armand Gamache, #8) | language_code | `''` | `None` | `None` |
| 16045855 | Crush (Crush, #1) | isbn | `''` | `None` | `None` |
| 16045855 | Crush (Crush, #1) | isbn13 | `''` | `None` | `None` |
| 16045855 | Crush (Crush, #1) | original_title | `''` | `None` | `None` |
| 16047244 | Rock the Heart (Black Falcon, #1) | isbn | `''` | `None` | `None` |
| 16047244 | Rock the Heart (Black Falcon, #1) | isbn13 | `''` | `None` | `None` |
| 16053316 | Wethering the Storm (The Storm, #2) | isbn | `''` | `None` | `None` |
| 16053316 | Wethering the Storm (The Storm, #2) | isbn13 | `''` | `None` | `None` |
| 16055 | The Magician's Assistant | original_title | `''` | `None` | `None` |
| 16056862 | The Unwanted Wife (Unwanted, #1) | isbn | `''` | `None` | `None` |
| 16056862 | The Unwanted Wife (Unwanted, #1) | isbn13 | `''` | `None` | `None` |
| 16058610 | Whistling Past the Graveyard | original_title | `''` | `None` | `None` |
| 16066586 | The Cellar (The Cellar, #1) | isbn | `''` | `None` | `None` |
| 16066586 | The Cellar (The Cellar, #1) | isbn13 | `''` | `None` | `None` |
| 16066586 | The Cellar (The Cellar, #1) | original_title | `''` | `None` | `None` |
| 16068905 | Fangirl | isbn | `''` | `None` | `None` |
| 16068905 | Fangirl | isbn13 | `''` | `None` | `None` |
| 16068905 | Fangirl | original_title | `''` | `None` | `None` |
| 16070018 | Truth (Consequences, #2) | original_title | `''` | `None` | `None` |
| 16070521 | Come Away with Me (With Me in Seattle, #1) | isbn | `''` | `None` | `None` |
| 16070521 | Come Away with Me (With Me in Seattle, #1) | isbn13 | `''` | `None` | `None` |
| 16070903 | Fallen Too Far (Rosemary Beach, #1; Too Far, #1) | isbn | `''` | `None` | `None` |
| 16070903 | Fallen Too Far (Rosemary Beach, #1; Too Far, #1) | isbn13 | `''` | `None` | `None` |
| 16076787 | السنجة | isbn | `''` | `None` | `None` |
| 16076787 | السنجة | isbn13 | `''` | `None` | `None` |
| 16079228 | Beautifully Damaged (Beautifully Damaged, #1) | isbn | `''` | `None` | `None` |
| 16079228 | Beautifully Damaged (Beautifully Damaged, #1) | isbn13 | `''` | `None` | `None` |
| 16081202 | Open Road Summer | isbn | `''` | `None` | `None` |
| 16081202 | Open Road Summer | isbn13 | `''` | `None` | `None` |
| 16081754 | Find You in the Dark (Find You in the Dark, #1) | isbn | `''` | `None` | `None` |
| 16081754 | Find You in the Dark (Find You in the Dark, #1) | isbn13 | `''` | `None` | `None` |
| 16081961 | الأسود يليق بك | isbn | `''` | `None` | `None` |
| 16081961 | الأسود يليق بك | isbn13 | `''` | `None` | `None` |
| 16084702 | Fifty Shades Duo: Fifty Shades Darker / Fifty Shades Freed (Fifty Shades, #2-3) | isbn | `''` | `None` | `None` |
| 16084702 | Fifty Shades Duo: Fifty Shades Darker / Fifty Shades Freed (Fifty Shades, #2-3) | isbn13 | `''` | `None` | `None` |
| 16084702 | Fifty Shades Duo: Fifty Shades Darker / Fifty Shades Freed (Fifty Shades, #2-3) | original_title | `''` | `None` | `None` |
| 160848 | Wanted | language_code | `''` | `None` | `None` |
| 16090636 | Fight with Me (With Me in Seattle, #2) | isbn | `''` | `None` | `None` |
| 16090636 | Fight with Me (With Me in Seattle, #2) | isbn13 | `''` | `None` | `None` |
| 16090636 | Fight with Me (With Me in Seattle, #2) | original_title | `''` | `None` | `None` |
| 16090981 | Thief (Love Me with Lies, #3) | isbn | `''` | `None` | `None` |
| 16090981 | Thief (Love Me with Lies, #3) | isbn13 | `''` | `None` | `None` |
| 16093188 | Up to Me (The Bad Boys, #2) | isbn | `''` | `None` | `None` |
| 16093188 | Up to Me (The Bad Boys, #2) | isbn13 | `''` | `None` | `None` |
| 16096873 | Revealed (House of Night, #11) | isbn | `''` | `None` | `None` |
| 16096873 | Revealed (House of Night, #11) | isbn13 | `''` | `None` | `None` |
| 16102880 | Bad Rep (Bad Rep, #1) | isbn | `''` | `None` | `None` |
| 16102880 | Bad Rep (Bad Rep, #1) | isbn13 | `''` | `None` | `None` |
| 16102880 | Bad Rep (Bad Rep, #1) | original_title | `''` | `None` | `None` |
| 16109563 | Undeniable (Undeniable, #1) | isbn | `''` | `None` | `None` |
| 16109563 | Undeniable (Undeniable, #1) | isbn13 | `''` | `None` | `None` |
| 16113791 | The Coincidence of Callie & Kayden (The Coincidence, #1) | isbn | `''` | `None` | `None` |
| 16113791 | The Coincidence of Callie & Kayden (The Coincidence, #1) | isbn13 | `''` | `None` | `None` |
| 16114861 | Unbeautifully (Undeniable, #2) | isbn | `''` | `None` | `None` |
| 16114861 | Unbeautifully (Undeniable, #2) | isbn13 | `''` | `None` | `None` |
| 16114861 | Unbeautifully (Undeniable, #2) | original_title | `''` | `None` | `None` |
| 16114862 | Unattainable (Undeniable, #3) | isbn | `''` | `None` | `None` |
| 16114862 | Unattainable (Undeniable, #3) | isbn13 | `''` | `None` | `None` |
| 16114862 | Unattainable (Undeniable, #3) | original_title | `''` | `None` | `None` |
| 16117182 | Broken Silence (Silence, #2) | isbn | `''` | `None` | `None` |
| 16117182 | Broken Silence (Silence, #2) | isbn13 | `''` | `None` | `None` |
| 16117804 | The Proposal (The Proposition, #2) | isbn | `''` | `None` | `None` |
| 16117804 | The Proposal (The Proposition, #2) | isbn13 | `''` | `None` | `None` |
| 16119079 | Forever My Girl (The Beaumont Series, #1) | original_title | `''` | `None` | `None` |
| 16122163 | From Ashes (From Ashes, #1) | original_title | `''` | `None` | `None` |
| 16122643 | Eyes Wide Open (The Blackstone Affair, #3) | isbn | `''` | `None` | `None` |
| 16122643 | Eyes Wide Open (The Blackstone Affair, #3) | isbn13 | `''` | `None` | `None` |
| 16124019 | Waking Up Married (Waking Up, #1) | isbn | `''` | `None` | `None` |
| 16124019 | Waking Up Married (Waking Up, #1) | isbn13 | `''` | `None` | `None` |
| 16130986 | An Innocent Client | isbn | `''` | `None` | `None` |
| 16130986 | An Innocent Client | isbn13 | `''` | `None` | `None` |
| 16131484 | The Infinite Sea (The 5th Wave, #2) | isbn | `''` | `None` | `None` |
| 16131484 | The Infinite Sea (The 5th Wave, #2) | isbn13 | `''` | `None` | `None` |
| 16134551 | Fallen Crest High (Fallen Crest High, #1) | isbn | `''` | `None` | `None` |
| 16134551 | Fallen Crest High (Fallen Crest High, #1) | isbn13 | `''` | `None` | `None` |
| 16134782 | In Flight (Up in the Air, #1) | isbn | `''` | `None` | `None` |
| 16134782 | In Flight (Up in the Air, #1) | isbn13 | `''` | `None` | `None` |
| 16136959 | Mile High (Up in the Air, #2) | isbn | `''` | `None` | `None` |
| 16136959 | Mile High (Up in the Air, #2) | isbn13 | `''` | `None` | `None` |
| 16139641 | Grounded (Up in the Air, #3) | isbn | `''` | `None` | `None` |
| 16139641 | Grounded (Up in the Air, #3) | isbn13 | `''` | `None` | `None` |
| 16140036 | This Man (This Man, #1) | isbn | `''` | `None` | `None` |
| 16140036 | This Man (This Man, #1) | isbn13 | `''` | `None` | `None` |
| 161415 | See You at the Top | language_code | `''` | `None` | `None` |
| 16141924 | Dad Is Fat | language_code | `''` | `None` | `None` |
| 16143347 | We Were Liars | isbn | `''` | `None` | `None` |
| 16143347 | We Were Liars | isbn13 | `''` | `None` | `None` |
| 16148398 | Saga #1 | isbn | `''` | `None` | `None` |
| 16148398 | Saga #1 | isbn13 | `''` | `None` | `None` |
| 16148938 | Second Shift: Order (Shift, #2) | isbn | `''` | `None` | `None` |
| 16148938 | Second Shift: Order (Shift, #2) | isbn13 | `''` | `None` | `None` |
| 16148938 | Second Shift: Order (Shift, #2) | original_title | `''` | `None` | `None` |
| 16150119 | Wired (Wired, #1) | isbn | `''` | `None` | `None` |
| 16150119 | Wired (Wired, #1) | isbn13 | `''` | `None` | `None` |
| 16150119 | Wired (Wired, #1) | original_title | `''` | `None` | `None` |
| 16150996 | Convicted (Consequences, #3) | isbn | `''` | `None` | `None` |
| 16150996 | Convicted (Consequences, #3) | isbn13 | `''` | `None` | `None` |
| 16150996 | Convicted (Consequences, #3) | original_title | `''` | `None` | `None` |
| 16151178 | The Sea of Tranquility | isbn | `''` | `None` | `None` |
| 16151178 | The Sea of Tranquility | isbn13 | `''` | `None` | `None` |
| 16152943 | Wanted (Wanted, #1) | original_title | `''` | `None` | `None` |
| 16163690 | Own the Wind (Chaos, #1) | isbn | `''` | `None` | `None` |
| 16163690 | Own the Wind (Chaos, #1) | isbn13 | `''` | `None` | `None` |
| 16170522 | صانع الظلام | isbn | `''` | `None` | `None` |
| 16170522 | صانع الظلام | isbn13 | `''` | `None` | `None` |
| 16170625 | المانيفستو | isbn | `''` | `None` | `None` |
| 16170625 | المانيفستو | isbn13 | `''` | `None` | `None` |
| 16174197 | Knight & Play (Knight, #1) | isbn | `''` | `None` | `None` |
| 16174197 | Knight & Play (Knight, #1) | isbn13 | `''` | `None` | `None` |
| 16175040 | Endless Knight (The Arcana Chronicles, #2) | isbn | `''` | `None` | `None` |
| 16175040 | Endless Knight (The Arcana Chronicles, #2) | isbn13 | `''` | `None` | `None` |
| 1617875 | My Best Friend's Girl | language_code | `''` | `None` | `None` |
| 16182601 | Bread and   Wine: A Love Letter to Life Around the Table with Recipes | original_title | `''` | `None` | `None` |
| 16204 | Daisy Miller | language_code | `''` | `None` | `None` |
| 16218778 | Coming Clean | original_title | `''` | `None` | `None` |
| 16233105 | Someone to Love (Someone to Love, #1) | isbn | `''` | `None` | `None` |
| 16233105 | Someone to Love (Someone to Love, #1) | isbn13 | `''` | `None` | `None` |
| 16248139 | The Last Original Wife | original_title | `''` | `None` | `None` |
| 16248196 | The Art of Thinking Clearly | language_code | `''` | `None` | `None` |
| 16277248 | Avatar: The Last Airbender (The Search, #1) | original_title | `''` | `None` | `None` |
| 16279715 | Connected (Connections, #1) | isbn | `''` | `None` | `None` |
| 16279715 | Connected (Connections, #1) | isbn13 | `''` | `None` | `None` |
| 1629007 | Where Are You Now? | original_title | `''` | `None` | `None` |
| 16299256 | The Game Changer (The Perfect Game, #2) | isbn | `''` | `None` | `None` |
| 16299256 | The Game Changer (The Perfect Game, #2) | isbn13 | `''` | `None` | `None` |
| 16299256 | The Game Changer (The Perfect Game, #2) | original_title | `''` | `None` | `None` |
| 16299991 | A Quest of Heroes (The Sorcerer's Ring, #1) | isbn | `''` | `None` | `None` |
| 16299991 | A Quest of Heroes (The Sorcerer's Ring, #1) | isbn13 | `''` | `None` | `None` |
| 16299991 | A Quest of Heroes (The Sorcerer's Ring, #1) | original_title | `''` | `None` | `None` |
| 16301111 | Always You (Best Friend, #1) | isbn | `''` | `None` | `None` |
| 16301111 | Always You (Best Friend, #1) | isbn13 | `''` | `None` | `None` |
| 1635 | Execution: The Discipline of Getting Things Done | original_title | `''` | `None` | `None` |
| 16429619 | The Kiss of Deception (The Remnant Chronicles, #1) | isbn | `''` | `None` | `None` |
| 16429619 | The Kiss of Deception (The Remnant Chronicles, #1) | isbn13 | `''` | `None` | `None` |
| 16431 | Sole Survivor | original_title | `''` | `None` | `None` |
| 164323 | The Google Story: Inside the Hottest Business, Media, and Technology Success of Our Time | language_code | `''` | `None` | `None` |
| 16479439 | Ex-Heroes (Ex-Heroes, #1) | language_code | `''` | `None` | `None` |
| 164836 | Succulent Wild Woman | language_code | `''` | `None` | `None` |
| 165030 | Anybody Out There? (Walsh Family, #4) | language_code | `''` | `None` | `None` |
| 165053 | Graffiti World: Street Art from Five Continents | language_code | `''` | `None` | `None` |
| 1662160 | Your Inner Fish: A Journey into the 3.5-Billion-Year History of the Human Body | language_code | `''` | `None` | `None` |
| 16704759 | Knight & Stay (Knight, #2) | isbn | `''` | `None` | `None` |
| 16704759 | Knight & Stay (Knight, #2) | isbn13 | `''` | `None` | `None` |
| 16704759 | Knight & Stay (Knight, #2) | original_title | `''` | `None` | `None` |
| 167216 | Amy and Isabelle  | language_code | `''` | `None` | `None` |
| 1672727 | Two-Way Street | language_code | `''` | `None` | `None` |
| 168571 | Shadow Prey (Lucas Davenport, #2) | isbn | `''` | `None` | `None` |
| 168571 | Shadow Prey (Lucas Davenport, #2) | isbn13 | `''` | `None` | `None` |
| 168571 | Shadow Prey (Lucas Davenport, #2) | original_title | `''` | `None` | `None` |
| 169718 | Babbitt | language_code | `''` | `None` | `None` |
| 169848 | A Christmas Carol, The Chimes and The Cricket on the Hearth | original_title | `''` | `None` | `None` |
| 169848 | A Christmas Carol, The Chimes and The Cricket on the Hearth | language_code | `''` | `None` | `None` |
| 169871 | Talking to Dragons (Enchanted Forest Chronicles, #4) | original_title | `''` | `None` | `None` |
| 169875 | Searching for Dragons (Enchanted Forest Chronicles, #2) | original_title | `''` | `None` | `None` |
| 169879 | Calling on Dragons (Enchanted Forest Chronicles, #3) | original_title | `''` | `None` | `None` |
| 170171 | Catalyst | original_title | `''` | `None` | `None` |
| 17032328 | If You Stay (Beautifully Broken, #1) | isbn | `''` | `None` | `None` |
| 17032328 | If You Stay (Beautifully Broken, #1) | isbn13 | `''` | `None` | `None` |
| 170618 | Daddy's Little Girl | language_code | `''` | `None` | `None` |
| 170619 | All Around the Town | language_code | `''` | `None` | `None` |
| 171102 | The Birth House | language_code | `''` | `None` | `None` |
| 17136 | The Time Machine/The Invisible Man | language_code | `''` | `None` | `None` |
| 17158513 | Captive Prince: Volume Two (Captive Prince, #2) | isbn | `''` | `None` | `None` |
| 17158513 | Captive Prince: Volume Two (Captive Prince, #2) | isbn13 | `''` | `None` | `None` |
| 17158596 | Collide (Collide, #1) | isbn | `''` | `None` | `None` |
| 17158596 | Collide (Collide, #1) | isbn13 | `''` | `None` | `None` |
| 17166702 | True Love Story | isbn | `''` | `None` | `None` |
| 17166702 | True Love Story | isbn13 | `''` | `None` | `None` |
| 17167042 | Fighting for Flight (Fighting, #1) | isbn | `''` | `None` | `None` |
| 17167042 | Fighting for Flight (Fighting, #1) | isbn13 | `''` | `None` | `None` |
| 17167042 | Fighting for Flight (Fighting, #1) | original_title | `''` | `None` | `None` |
| 17181905 | The Arrangement: The Ferro Family (The Arrangement, #1) | isbn | `''` | `None` | `None` |
| 17181905 | The Arrangement: The Ferro Family (The Arrangement, #1) | isbn13 | `''` | `None` | `None` |
| 17181905 | The Arrangement: The Ferro Family (The Arrangement, #1) | original_title | `''` | `None` | `None` |
| 17190226 | Surrender Your Love (Surrender Your Love, #1) | isbn | `''` | `None` | `None` |
| 17190226 | Surrender Your Love (Surrender Your Love, #1) | isbn13 | `''` | `None` | `None` |
| 17191012 | Fallen Crest Family (Fallen Crest High, #2) | isbn | `''` | `None` | `None` |
| 17191012 | Fallen Crest Family (Fallen Crest High, #2) | isbn13 | `''` | `None` | `None` |
| 17191012 | Fallen Crest Family (Fallen Crest High, #2) | original_title | `''` | `None` | `None` |
| 17200687 | Rule (Marked Men, #1) | isbn | `''` | `None` | `None` |
| 17200687 | Rule (Marked Men, #1) | isbn13 | `''` | `None` | `None` |
| 17201095 | Play with Me (With Me in Seattle, #3) | isbn | `''` | `None` | `None` |
| 17201095 | Play with Me (With Me in Seattle, #3) | isbn13 | `''` | `None` | `None` |
| 17201104 | Rock with Me (With Me in Seattle, #4) | isbn | `''` | `None` | `None` |
| 17201104 | Rock with Me (With Me in Seattle, #4) | isbn13 | `''` | `None` | `None` |
| 17201110 | Safe with Me (With Me in Seattle, #5) | isbn | `''` | `None` | `None` |
| 17201110 | Safe with Me (With Me in Seattle, #5) | isbn13 | `''` | `None` | `None` |
| 17201110 | Safe with Me (With Me in Seattle, #5) | original_title | `''` | `None` | `None` |
| 17204568 | Crazy Little Thing (Bell Harbor, #1) | isbn | `''` | `None` | `None` |
| 17204568 | Crazy Little Thing (Bell Harbor, #1) | isbn13 | `''` | `None` | `None` |
| 17204860 | Jet (Marked Men, #2) | isbn | `''` | `None` | `None` |
| 17204860 | Jet (Marked Men, #2) | isbn13 | `''` | `None` | `None` |
| 17225311 | Tampa | language_code | `''` | `None` | `None` |
| 1722717 | The Declaration (The Declaration, #1) | language_code | `''` | `None` | `None` |
| 17228280 | Better off Friends | isbn | `''` | `None` | `None` |
| 17228280 | Better off Friends | isbn13 | `''` | `None` | `None` |
| 17235347 | Life Before Legend: Stories of the Criminal and the Prodigy (Legend, #0.5) | isbn | `''` | `None` | `None` |
| 17235347 | Life Before Legend: Stories of the Criminal and the Prodigy (Legend, #0.5) | isbn13 | `''` | `None` | `None` |
| 17255186 | The Phoenix Project: A Novel About IT, DevOps, and Helping Your Business Win | original_title | `''` | `None` | `None` |
| 17255265 | This Man Confessed (This Man, #3) | isbn | `''` | `None` | `None` |
| 17255265 | This Man Confessed (This Man, #3) | isbn13 | `''` | `None` | `None` |
| 17255435 | A Shade of Vampire (A Shade of Vampire, #1) | original_title | `''` | `None` | `None` |
| 17257484 | Trouble | isbn | `''` | `None` | `None` |
| 17257484 | Trouble | isbn13 | `''` | `None` | `None` |
| 17257990 | Fire Inside (Chaos, #2) | isbn | `''` | `None` | `None` |
| 17257990 | Fire Inside (Chaos, #2) | isbn13 | `''` | `None` | `None` |
| 17257990 | Fire Inside (Chaos, #2) | original_title | `''` | `None` | `None` |
| 17257993 | Raid (Unfinished Hero, #3) | isbn | `''` | `None` | `None` |
| 17257993 | Raid (Unfinished Hero, #3) | isbn13 | `''` | `None` | `None` |
| 17267122 | Pulse (Collide, #2) | isbn | `''` | `None` | `None` |
| 17267122 | Pulse (Collide, #2) | isbn13 | `''` | `None` | `None` |
| 17286162 | Forever Black (Forever, #1) | isbn | `''` | `None` | `None` |
| 17286162 | Forever Black (Forever, #1) | isbn13 | `''` | `None` | `None` |
| 17287009 | Humans of New York | original_title | `''` | `None` | `None` |
| 17287028 | My Story | original_title | `''` | `None` | `None` |
| 17306293 | Shift (Silo, #2) | isbn | `''` | `None` | `None` |
| 17306293 | Shift (Silo, #2) | isbn13 | `''` | `None` | `None` |
| 17314410 | Beauty from Surrender (Beauty, #2) | isbn | `''` | `None` | `None` |
| 17314410 | Beauty from Surrender (Beauty, #2) | isbn13 | `''` | `None` | `None` |
| 17314430 | Wait for You (Wait for You, #1) | isbn | `''` | `None` | `None` |
| 17314430 | Wait for You (Wait for You, #1) | isbn13 | `''` | `None` | `None` |
| 17316075 | Second Chance Boyfriend (One Week Girlfriend, #2) | isbn | `''` | `None` | `None` |
| 17316075 | Second Chance Boyfriend (One Week Girlfriend, #2) | isbn13 | `''` | `None` | `None` |
| 17317675 | Epilogue (The Dark Duet, #3) | isbn | `''` | `None` | `None` |
| 17317675 | Epilogue (The Dark Duet, #3) | isbn13 | `''` | `None` | `None` |
| 17317675 | Epilogue (The Dark Duet, #3) | original_title | `''` | `None` | `None` |
| 17324 | The Visitation | language_code | `''` | `None` | `None` |
| 17331349 | Think Like a Freak | original_title | `''` | `None` | `None` |
| 17333237 | Stella Bain | original_title | `''` | `None` | `None` |
| 17333237 | Stella Bain | language_code | `''` | `None` | `None` |
| 17333880 | Twisted Perfection (Rosemary Beach, #5; Perfection, #1) | isbn | `''` | `None` | `None` |
| 17333880 | Twisted Perfection (Rosemary Beach, #5; Perfection, #1) | isbn13 | `''` | `None` | `None` |
| 17334079 | What Really Happened in Peru (The Bane Chronicles, #1) | original_title | `''` | `None` | `None` |
| 17336849 | Lost & Found (Lost & Found, #1) | original_title | `''` | `None` | `None` |
| 17337562 | Forever Too Far (Rosemary Beach, #3; Too Far, #3) | isbn | `''` | `None` | `None` |
| 17337562 | Forever Too Far (Rosemary Beach, #3; Too Far, #3) | isbn13 | `''` | `None` | `None` |
| 17339590 | "حكايات فرغلي المستكاوي "حكايتى مع كفر السحلاوية | isbn | `''` | `None` | `None` |
| 17339590 | "حكايات فرغلي المستكاوي "حكايتى مع كفر السحلاوية | isbn13 | `''` | `None` | `None` |
| 17340050 | Losing Hope (Hopeless, #2) | isbn | `''` | `None` | `None` |
| 17340050 | Losing Hope (Hopeless, #2) | isbn13 | `''` | `None` | `None` |
| 17348985 | Help for the Haunted | original_title | `''` | `None` | `None` |
| 173673 | A Course in Miracles | language_code | `''` | `None` | `None` |
| 17375956 | Reaper's Property (Reapers MC, #1) | isbn | `''` | `None` | `None` |
| 17375956 | Reaper's Property (Reapers MC, #1) | isbn13 | `''` | `None` | `None` |
| 17377032 | Bad Things (Tristan & Danika, #1) | isbn | `''` | `None` | `None` |
| 17377032 | Bad Things (Tristan & Danika, #1) | isbn13 | `''` | `None` | `None` |
| 17377032 | Bad Things (Tristan & Danika, #1) | original_title | `''` | `None` | `None` |
| 17383994 | Divergent Series Complete Box Set (Divergent, #1-3) | original_title | `''` | `None` | `None` |
| 17401198 | Only the Innocent (DCI Tom Douglas #1) | isbn | `''` | `None` | `None` |
| 17401198 | Only the Innocent (DCI Tom Douglas #1) | isbn13 | `''` | `None` | `None` |
| 17404452 | Forever You (Forever, #2) | isbn | `''` | `None` | `None` |
| 17404452 | Forever You (Forever, #2) | isbn13 | `''` | `None` | `None` |
| 17404452 | Forever You (Forever, #2) | original_title | `''` | `None` | `None` |
| 17406847 | Defy (Defy, #1) | isbn | `''` | `None` | `None` |
| 17406847 | Defy (Defy, #1) | isbn13 | `''` | `None` | `None` |
| 17407233 | The Submissive (Submissive, #1) | isbn | `''` | `None` | `None` |
| 17407233 | The Submissive (Submissive, #1) | isbn13 | `''` | `None` | `None` |
| 17448960 | Falling into You (Falling, #1) | isbn | `''` | `None` | `None` |
| 17448960 | Falling into You (Falling, #1) | isbn13 | `''` | `None` | `None` |
| 17449417 | Simple Perfection (Rosemary Beach, #6; Perfection, #2) | isbn | `''` | `None` | `None` |
| 17449417 | Simple Perfection (Rosemary Beach, #6; Perfection, #2) | isbn13 | `''` | `None` | `None` |
| 17455541 | Happy, Happy, Happy | isbn | `''` | `None` | `None` |
| 17455541 | Happy, Happy, Happy | isbn13 | `''` | `None` | `None` |
| 17455585 | White Hot Kiss (The Dark Elements, #1) | isbn | `''` | `None` | `None` |
| 17455585 | White Hot Kiss (The Dark Elements, #1) | isbn13 | `''` | `None` | `None` |
| 17455815 | Stone Cold Touch (The Dark Elements, #2) | isbn | `''` | `None` | `None` |
| 17455815 | Stone Cold Touch (The Dark Elements, #2) | isbn13 | `''` | `None` | `None` |
| 17465470 | The Royal Ranger (Ranger's Apprentice, #12) | language_code | `''` | `None` | `None` |
| 174703 | What to Expect When You're Expecting | language_code | `''` | `None` | `None` |
| 174845 | Life Together: The Classic Exploration of Christian Community | language_code | `''` | `None` | `None` |
| 174879 | On Becoming a Person: A Therapist's View of Psychotherapy | language_code | `''` | `None` | `None` |
| 175004 | Eagle Strike (Alex Rider, #4) | language_code | `''` | `None` | `None` |
| 17504320 | Taking Shots (Assassins, #1) | isbn | `''` | `None` | `None` |
| 17504320 | Taking Shots (Assassins, #1) | isbn13 | `''` | `None` | `None` |
| 17504320 | Taking Shots (Assassins, #1) | original_title | `''` | `None` | `None` |
| 17524166 | نادي السيارات | isbn | `''` | `None` | `None` |
| 17524166 | نادي السيارات | isbn13 | `''` | `None` | `None` |
| 17524166 | نادي السيارات | original_title | `''` | `None` | `None` |
| 17529 | Rebecca of Sunnybrook Farm | language_code | `''` | `None` | `None` |
| 17557143 | The Billionaire's Obsession ~ Simon (The Billionaire's Obsession, #1) | isbn | `''` | `None` | `None` |
| 17557143 | The Billionaire's Obsession ~ Simon (The Billionaire's Obsession, #1) | isbn13 | `''` | `None` | `None` |
| 17558817 | Be with Me (Wait for You, #2) | isbn | `''` | `None` | `None` |
| 17558817 | Be with Me (Wait for You, #2) | isbn13 | `''` | `None` | `None` |
| 17560674 | The Bet (The Bet, #1) | isbn | `''` | `None` | `None` |
| 17560674 | The Bet (The Bet, #1) | isbn13 | `''` | `None` | `None` |
| 17563080 | Murder of Crows (The Others, #2) | isbn | `''` | `None` | `None` |
| 17563080 | Murder of Crows (The Others, #2) | isbn13 | `''` | `None` | `None` |
| 17563539 | The Egg | isbn | `''` | `None` | `None` |
| 17563539 | The Egg | isbn13 | `''` | `None` | `None` |
| 1756703 | Blue-Eyed Devil (Travises, #2) | original_title | `''` | `None` | `None` |
| 17569860 | Conquer Your Love (Surrender Your Love, #2) | original_title | `''` | `None` | `None` |
| 17570538 | The Blood Mirror (Lightbringer, #4) | isbn | `''` | `None` | `None` |
| 17570538 | The Blood Mirror (Lightbringer, #4) | isbn13 | `''` | `None` | `None` |
| 17571564 | Hyperbole and a Half: Unfortunate Situations, Flawed Coping Mechanisms, Mayhem, and Other Things That Happened | original_title | `''` | `None` | `None` |
| 17660 | The Tommyknockers | isbn | `''` | `None` | `None` |
| 17660 | The Tommyknockers | isbn13 | `''` | `None` | `None` |
| 17660462 | The Everything Store: Jeff Bezos and the Age of Amazon | original_title | `''` | `None` | `None` |
| 17667452 | When I Found You | isbn | `''` | `None` | `None` |
| 17667452 | When I Found You | isbn13 | `''` | `None` | `None` |
| 17667561 | The Shadow Throne (The Ascendance Trilogy, #3) | isbn | `''` | `None` | `None` |
| 17667561 | The Shadow Throne (The Ascendance Trilogy, #3) | isbn13 | `''` | `None` | `None` |
| 17673271 | Si-cology 1: Tales and Wisdom from Duck Dynasty’s Favorite Uncle | original_title | `''` | `None` | `None` |
| 17673307 | Neanderthal Seeks Human (Knitting in the City, #1) | isbn | `''` | `None` | `None` |
| 17673307 | Neanderthal Seeks Human (Knitting in the City, #1) | isbn13 | `''` | `None` | `None` |
| 17674991 | Paddle Your Own Canoe: One Man's Fundamentals for Delicious Living | original_title | `''` | `None` | `None` |
| 17675031 | This Star Won't Go Out: The Life and Words of Esther Grace Earl | original_title | `''` | `None` | `None` |
| 1767779 | Five Little Monkeys Jumping on the Bed | language_code | `''` | `None` | `None` |
| 176839 | One True Thing | language_code | `''` | `None` | `None` |
| 17688 | The Metamorphosis, In the Penal Colony, and Other Stories: The Great Short Works of Franz Kafka | original_title | `''` | `None` | `None` |
| 17704902 | Five Days at Memorial: Life and Death in a Storm-Ravaged Hospital | original_title | `''` | `None` | `None` |
| 17707603 | George Washington's Secret Six: The Spy Ring That Saved the American Revolution | original_title | `''` | `None` | `None` |
| 17716 | Waiting for Godot | isbn | `''` | `None` | `None` |
| 17716 | Waiting for Godot | isbn13 | `''` | `None` | `None` |
| 17726978 | The Magpies | original_title | `''` | `None` | `None` |
| 1772910 | White Nights | isbn | `''` | `None` | `None` |
| 1772910 | White Nights | isbn13 | `''` | `None` | `None` |
| 17729712 | Beautiful Broken Rules (Broken, #1) | isbn | `''` | `None` | `None` |
| 17729712 | Beautiful Broken Rules (Broken, #1) | isbn13 | `''` | `None` | `None` |
| 17729712 | Beautiful Broken Rules (Broken, #1) | original_title | `''` | `None` | `None` |
| 17733861 | A Shade of Blood (A Shade of Vampire, #2) | isbn | `''` | `None` | `None` |
| 17733861 | A Shade of Blood (A Shade of Vampire, #2) | isbn13 | `''` | `None` | `None` |
| 17733861 | A Shade of Blood (A Shade of Vampire, #2) | original_publication_year | `''` | `None` | `None` |
| 17733861 | A Shade of Blood (A Shade of Vampire, #2) | original_title | `''` | `None` | `None` |
| 1776251 | Jamie at Home: Cook Your Way to the Good Life | language_code | `''` | `None` | `None` |
| 17788401 | Ugly Love | isbn | `''` | `None` | `None` |
| 17788401 | Ugly Love | isbn13 | `''` | `None` | `None` |
| 17792606 | Mine (Real, #2) | isbn | `''` | `None` | `None` |
| 17792606 | Mine (Real, #2) | isbn13 | `''` | `None` | `None` |
| 17794657 | The Lake (The Lake Trilogy #1) | isbn | `''` | `None` | `None` |
| 17794657 | The Lake (The Lake Trilogy #1) | isbn13 | `''` | `None` | `None` |
| 17794657 | The Lake (The Lake Trilogy #1) | original_title | `''` | `None` | `None` |
| 17798233 | Rome (Marked Men, #3) | isbn | `''` | `None` | `None` |
| 17798233 | Rome (Marked Men, #3) | isbn13 | `''` | `None` | `None` |
| 17798287 | Driven (Driven, #1) | isbn | `''` | `None` | `None` |
| 17798287 | Driven (Driven, #1) | isbn13 | `''` | `None` | `None` |
| 1779929 | The Middle Place | language_code | `''` | `None` | `None` |
| 17800786 | Damaged 2 (Damaged, #2) | isbn | `''` | `None` | `None` |
| 17800786 | Damaged 2 (Damaged, #2) | isbn13 | `''` | `None` | `None` |
| 17800786 | Damaged 2 (Damaged, #2) | original_title | `''` | `None` | `None` |
| 17810 | In the Miso Soup | isbn | `''` | `None` | `None` |
| 17810 | In the Miso Soup | isbn13 | `''` | `None` | `None` |
| 17825503 | Leo | isbn | `''` | `None` | `None` |
| 17825503 | Leo | isbn13 | `''` | `None` | `None` |
| 17830559 | Remy (Real, #3) | isbn | `''` | `None` | `None` |
| 17830559 | Remy (Real, #3) | isbn13 | `''` | `None` | `None` |
| 17830559 | Remy (Real, #3) | original_title | `''` | `None` | `None` |
| 17831614 | Beautiful Player (Beautiful Bastard, #3) | isbn | `''` | `None` | `None` |
| 17831614 | Beautiful Player (Beautiful Bastard, #3) | isbn13 | `''` | `None` | `None` |
| 17831616 | Beautiful Bitch (Beautiful Bastard, #1.5) | isbn | `''` | `None` | `None` |
| 17831616 | Beautiful Bitch (Beautiful Bastard, #1.5) | isbn13 | `''` | `None` | `None` |
| 17831617 | Beautiful Bombshell (Beautiful Bastard, #2.5) | isbn | `''` | `None` | `None` |
| 17831617 | Beautiful Bombshell (Beautiful Bastard, #2.5) | isbn13 | `''` | `None` | `None` |
| 17831619 | Beautiful Beginning (Beautiful Bastard, #3.5) | isbn | `''` | `None` | `None` |
| 17831619 | Beautiful Beginning (Beautiful Bastard, #3.5) | isbn13 | `''` | `None` | `None` |
| 17831619 | Beautiful Beginning (Beautiful Bastard, #3.5) | original_title | `''` | `None` | `None` |
| 17833099 | Price of a Kiss (Forbidden Men, #1) | isbn | `''` | `None` | `None` |
| 17833099 | Price of a Kiss (Forbidden Men, #1) | isbn13 | `''` | `None` | `None` |
| 17833099 | Price of a Kiss (Forbidden Men, #1) | original_title | `''` | `None` | `None` |
| 17835351 | Nikola Tesla: Imagination and the Man That Invented the 20th Century | isbn | `''` | `None` | `None` |
| 17835351 | Nikola Tesla: Imagination and the Man That Invented the 20th Century | isbn13 | `''` | `None` | `None` |
| 17835766 | One More Chance (Rosemary Beach, #8; Chance, #2) | isbn | `''` | `None` | `None` |
| 17835766 | One More Chance (Rosemary Beach, #8; Chance, #2) | isbn13 | `''` | `None` | `None` |
| 17835773 | Misbehaving (Sea Breeze, #6) | isbn | `''` | `None` | `None` |
| 17835773 | Misbehaving (Sea Breeze, #6) | isbn13 | `''` | `None` | `None` |
| 178599 | Arsenic and Old Lace | language_code | `''` | `None` | `None` |
| 17860199 | The World of Divergent: The Path to Allegiant (Divergent, #2.5) | original_title | `''` | `None` | `None` |
| 17860217 | Trust in Me (Wait for You, #1.5) | isbn | `''` | `None` | `None` |
| 17860217 | Trust in Me (Wait for You, #1.5) | isbn13 | `''` | `None` | `None` |
| 17880708 | Fueled (Driven, #2) | isbn | `''` | `None` | `None` |
| 17880708 | Fueled (Driven, #2) | isbn13 | `''` | `None` | `None` |
| 17880714 | Crashed (Driven, #3) | isbn | `''` | `None` | `None` |
| 17880714 | Crashed (Driven, #3) | isbn13 | `''` | `None` | `None` |
| 17899392 | First Love | language_code | `''` | `None` | `None` |
| 17903381 | Diary ng Panget | isbn | `''` | `None` | `None` |
| 17903381 | Diary ng Panget | isbn13 | `''` | `None` | `None` |
| 17903381 | Diary ng Panget | original_title | `''` | `None` | `None` |
| 17925397 | A Castle of Sand (A Shade of Vampire, #3) | isbn | `''` | `None` | `None` |
| 17925397 | A Castle of Sand (A Shade of Vampire, #3) | isbn13 | `''` | `None` | `None` |
| 17925397 | A Castle of Sand (A Shade of Vampire, #3) | original_title | `''` | `None` | `None` |
| 179264 | The Madonnas of Leningrad | language_code | `''` | `None` | `None` |
| 17927395 | A Court of Mist and Fury (A Court of Thorns and Roses, #2) | isbn | `''` | `None` | `None` |
| 17927395 | A Court of Mist and Fury (A Court of Thorns and Roses, #2) | isbn13 | `''` | `None` | `None` |
| 17930773 | Found in You (Fixed, #2) | isbn | `''` | `None` | `None` |
| 17930773 | Found in You (Fixed, #2) | isbn13 | `''` | `None` | `None` |
| 17934385 | Tempting Fate | original_title | `''` | `None` | `None` |
| 17948485 | Friend-Zoned (Friend-Zoned, #1) | isbn | `''` | `None` | `None` |
| 17948485 | Friend-Zoned (Friend-Zoned, #1) | isbn13 | `''` | `None` | `None` |
| 17948485 | Friend-Zoned (Friend-Zoned, #1) | original_title | `''` | `None` | `None` |
| 17950614 | UnDivided (Unwind, #4) | isbn | `''` | `None` | `None` |
| 17950614 | UnDivided (Unwind, #4) | isbn13 | `''` | `None` | `None` |
| 17970255 | Into the Deep (Into the Deep, #1) | isbn | `''` | `None` | `None` |
| 17970255 | Into the Deep (Into the Deep, #1) | isbn13 | `''` | `None` | `None` |
| 17973653 | Shine Not Burn (Shine Not Burn, #1) | isbn | `''` | `None` | `None` |
| 17973653 | Shine Not Burn (Shine Not Burn, #1) | isbn13 | `''` | `None` | `None` |
| 17977710 | Twisted (Tangled, #2) | isbn | `''` | `None` | `None` |
| 17977710 | Twisted (Tangled, #2) | isbn13 | `''` | `None` | `None` |
| 17985262 | CyberStorm | isbn | `''` | `None` | `None` |
| 17985262 | CyberStorm | isbn13 | `''` | `None` | `None` |
| 17989312 | The Sisterhood | isbn | `''` | `None` | `None` |
| 17989312 | The Sisterhood | isbn13 | `''` | `None` | `None` |
| 17989312 | The Sisterhood | original_title | `''` | `None` | `None` |
| 17999892 | The Atlantis Gene (The Origin Mystery, #1) | isbn | `''` | `None` | `None` |
| 17999892 | The Atlantis Gene (The Origin Mystery, #1) | isbn13 | `''` | `None` | `None` |
| 18045473 | Last Train to Istanbul | isbn | `''` | `None` | `None` |
| 18045473 | Last Train to Istanbul | isbn13 | `''` | `None` | `None` |
| 180463 | Leadership and Self-Deception: Getting Out of the Box | language_code | `''` | `None` | `None` |
| 18053782 | Take a Chance (Rosemary Beach, #7; Chance, #1) | isbn | `''` | `None` | `None` |
| 18053782 | Take a Chance (Rosemary Beach, #7; Chance, #1) | isbn13 | `''` | `None` | `None` |
| 18071296 | Willing Captive | isbn | `''` | `None` | `None` |
| 18071296 | Willing Captive | isbn13 | `''` | `None` | `None` |
| 18076876 | Reaper's Legacy (Reapers MC, #2) | isbn | `''` | `None` | `None` |
| 18076876 | Reaper's Legacy (Reapers MC, #2) | isbn13 | `''` | `None` | `None` |
| 18080889 | Worth the Fight (MMA Fighter, #1) | isbn | `''` | `None` | `None` |
| 18080889 | Worth the Fight (MMA Fighter, #1) | isbn13 | `''` | `None` | `None` |
| 18080923 | The Traitor (Divergent, #0.4) | original_title | `''` | `None` | `None` |
| 18089551 | Tall, Tatted and Tempting (The Reed Brothers, #1) | isbn | `''` | `None` | `None` |
| 18089551 | Tall, Tatted and Tempting (The Reed Brothers, #1) | isbn13 | `''` | `None` | `None` |
| 18089551 | Tall, Tatted and Tempting (The Reed Brothers, #1) | original_title | `''` | `None` | `None` |
| 18090061 | Big Girl Panties | original_title | `''` | `None` | `None` |
| 18104607 | Beautiful Oblivion (The Maddox Brothers, #1) | isbn | `''` | `None` | `None` |
| 18104607 | Beautiful Oblivion (The Maddox Brothers, #1) | isbn13 | `''` | `None` | `None` |
| 18105011 | Sweet Home (Sweet Home, #1) | isbn | `''` | `None` | `None` |
| 18105011 | Sweet Home (Sweet Home, #1) | isbn13 | `''` | `None` | `None` |
| 18105011 | Sweet Home (Sweet Home, #1) | original_title | `''` | `None` | `None` |
| 181077 | Sadako and the Thousand Paper Cranes | isbn | `''` | `None` | `None` |
| 181077 | Sadako and the Thousand Paper Cranes | isbn13 | `''` | `None` | `None` |
| 181077 | Sadako and the Thousand Paper Cranes | language_code | `''` | `None` | `None` |
| 18108281 | The King (Black Dagger Brotherhood, #12) | isbn | `''` | `None` | `None` |
| 18108281 | The King (Black Dagger Brotherhood, #12) | isbn13 | `''` | `None` | `None` |
| 18108795 | High Heat (Jack Reacher #17.5) | isbn | `''` | `None` | `None` |
| 18108795 | High Heat (Jack Reacher #17.5) | isbn13 | `''` | `None` | `None` |
| 18108877 | Timebound (The Chronos Files, #1) | isbn | `''` | `None` | `None` |
| 18108877 | Timebound (The Chronos Files, #1) | isbn13 | `''` | `None` | `None` |
| 18110808 | Fallen Crest Public (Fallen Crest High, #3) | isbn | `''` | `None` | `None` |
| 18110808 | Fallen Crest Public (Fallen Crest High, #3) | isbn13 | `''` | `None` | `None` |
| 18110808 | Fallen Crest Public (Fallen Crest High, #3) | original_title | `''` | `None` | `None` |
| 18111281 | A Long Way Home | isbn | `''` | `None` | `None` |
| 18111281 | A Long Way Home | isbn13 | `''` | `None` | `None` |
| 181116 | Monday Mourning (Temperance Brennan, #7) | original_title | `''` | `None` | `None` |
| 18114142 | A Fall of Marigolds | original_title | `''` | `None` | `None` |
| 18114142 | A Fall of Marigolds | language_code | `''` | `None` | `None` |
| 18115061 | Before Jamaica Lane (On Dublin Street, #3) | isbn | `''` | `None` | `None` |
| 18115061 | Before Jamaica Lane (On Dublin Street, #3) | isbn13 | `''` | `None` | `None` |
| 18115061 | Before Jamaica Lane (On Dublin Street, #3) | original_title | `''` | `None` | `None` |
| 181206 | The 80/20 Principle: The Secret to Achieving More with Less | language_code | `''` | `None` | `None` |
| 18129852 | Rival (Fall Away, #2) | isbn | `''` | `None` | `None` |
| 18129852 | Rival (Fall Away, #2) | isbn13 | `''` | `None` | `None` |
| 18130 | A Wind in the Door (A Wrinkle in Time Quintet, #2) | isbn | `''` | `None` | `None` |
| 18130 | A Wind in the Door (A Wrinkle in Time Quintet, #2) | isbn13 | `''` | `None` | `None` |
| 18134249 | Ruin (Ruin, #1) | isbn | `''` | `None` | `None` |
| 18134249 | Ruin (Ruin, #1) | isbn13 | `''` | `None` | `None` |
| 18134894 | Tears of Tess (Monsters in the Dark, #1) | original_title | `''` | `None` | `None` |
| 18138755 | Forever with You (Fixed, #3) | isbn | `''` | `None` | `None` |
| 18138755 | Forever with You (Fixed, #3) | isbn13 | `''` | `None` | `None` |
| 18138755 | Forever with You (Fixed, #3) | original_title | `''` | `None` | `None` |
| 18138755 | Forever with You (Fixed, #3) | language_code | `''` | `None` | `None` |
| 18143977 | All the Light We Cannot See | original_title | `''` | `None` | `None` |
| 18144115 | All Fall Down | original_title | `''` | `None` | `None` |
| 18149927 | Beneath This Man (This Man, #2) | isbn | `''` | `None` | `None` |
| 18149927 | Beneath This Man (This Man, #2) | isbn13 | `''` | `None` | `None` |
| 181601 | If You Give a Pig a Party | language_code | `''` | `None` | `None` |
| 18163646 | Falling into Place | isbn | `''` | `None` | `None` |
| 18163646 | Falling into Place | isbn13 | `''` | `None` | `None` |
| 18163646 | Falling into Place | language_code | `''` | `None` | `None` |
| 18191814 | A Blaze of Sun (A Shade of Vampire, #5) | isbn | `''` | `None` | `None` |
| 18191814 | A Blaze of Sun (A Shade of Vampire, #5) | isbn13 | `''` | `None` | `None` |
| 18191814 | A Blaze of Sun (A Shade of Vampire, #5) | original_title | `''` | `None` | `None` |
| 18211536 | Rush Too Far (Rosemary Beach, #4; Too Far, #4) | isbn | `''` | `None` | `None` |
| 18211536 | Rush Too Far (Rosemary Beach, #4; Too Far, #4) | isbn13 | `''` | `None` | `None` |
| 18221931 | Carter Reed (Carter Reed, #1) | isbn | `''` | `None` | `None` |
| 18221931 | Carter Reed (Carter Reed, #1) | isbn13 | `''` | `None` | `None` |
| 18243828 | Jake Undone (Jake, #1) | isbn | `''` | `None` | `None` |
| 18243828 | Jake Undone (Jake, #1) | isbn13 | `''` | `None` | `None` |
| 18243828 | Jake Undone (Jake, #1) | original_title | `''` | `None` | `None` |
| 18244799 | Hardwired (Hacker, #1) | isbn | `''` | `None` | `None` |
| 18244799 | Hardwired (Hacker, #1) | isbn13 | `''` | `None` | `None` |
| 18246727 | Mud Vein | isbn | `''` | `None` | `None` |
| 18246727 | Mud Vein | isbn13 | `''` | `None` | `None` |
| 18282800 | The Ladies' Room | isbn | `''` | `None` | `None` |
| 18282800 | The Ladies' Room | isbn13 | `''` | `None` | `None` |
| 18282800 | The Ladies' Room | original_title | `''` | `None` | `None` |
| 18285151 | More Than This (More Than, #1) | isbn | `''` | `None` | `None` |
| 18285151 | More Than This (More Than, #1) | isbn13 | `''` | `None` | `None` |
| 18285151 | More Than This (More Than, #1) | original_title | `''` | `None` | `None` |
| 18297707 | Tangled (Tangled, #1) | isbn | `''` | `None` | `None` |
| 18297707 | Tangled (Tangled, #1) | isbn13 | `''` | `None` | `None` |
| 18301124 | Making Faces | isbn | `''` | `None` | `None` |
| 18301124 | Making Faces | isbn13 | `''` | `None` | `None` |
| 1830755 | Mine to Possess (Psy-Changeling #4) | original_title | `''` | `None` | `None` |
| 183092 | Night Light (Restoration #2) | language_code | `''` | `None` | `None` |
| 18316089 | Lucky Us | language_code | `''` | `None` | `None` |
| 18323154 | المرحوم | isbn | `''` | `None` | `None` |
| 18323154 | المرحوم | isbn13 | `''` | `None` | `None` |
| 18331807 | Vain (The Seven Deadly, #1) | isbn | `''` | `None` | `None` |
| 18331807 | Vain (The Seven Deadly, #1) | isbn13 | `''` | `None` | `None` |
| 18331807 | Vain (The Seven Deadly, #1) | original_title | `''` | `None` | `None` |
| 18336965 | My Heart and Other Black Holes | isbn | `''` | `None` | `None` |
| 18336965 | My Heart and Other Black Holes | isbn13 | `''` | `None` | `None` |
| 18337259 | A Game of Thrones: Comic Book, Issue 1 | isbn | `''` | `None` | `None` |
| 18337259 | A Game of Thrones: Comic Book, Issue 1 | isbn13 | `''` | `None` | `None` |
| 1833852 | A Fraction of the Whole | language_code | `''` | `None` | `None` |
| 18340482 | Until Trevor (Until, #2) | isbn | `''` | `None` | `None` |
| 18340482 | Until Trevor (Until, #2) | isbn13 | `''` | `None` | `None` |
| 18340482 | Until Trevor (Until, #2) | original_title | `''` | `None` | `None` |
| 18341046 | Until November (Until, #1) | isbn | `''` | `None` | `None` |
| 18341046 | Until November (Until, #1) | isbn13 | `''` | `None` | `None` |
| 183554 | Developing the Leader Within You | language_code | `''` | `None` | `None` |
| 18363068 | حبيبتي بكماء | isbn | `''` | `None` | `None` |
| 18363068 | حبيبتي بكماء | isbn13 | `''` | `None` | `None` |
| 18363068 | حبيبتي بكماء | original_title | `''` | `None` | `None` |
| 1838166 | The Penderwicks on Gardam Street (The Penderwicks, #2) | language_code | `''` | `None` | `None` |
| 18387597 | 2 ضباط | isbn | `''` | `None` | `None` |
| 18387597 | 2 ضباط | isbn13 | `''` | `None` | `None` |
| 18405221 | Queen of Fire (Raven's Shadow, #3) | isbn | `''` | `None` | `None` |
| 18405221 | Queen of Fire (Raven's Shadow, #3) | isbn13 | `''` | `None` | `None` |
| 18420 | Hands Of Light | language_code | `''` | `None` | `None` |
| 18452 | The Painted Bird | original_title | `''` | `None` | `None` |
| 18452 | The Painted Bird | language_code | `''` | `None` | `None` |
| 1846 | Wild at Heart: Discovering the Secret of a Man's Soul | original_title | `''` | `None` | `None` |
| 18461986 | Deep (Stage Dive, #4) | isbn | `''` | `None` | `None` |
| 18461986 | Deep (Stage Dive, #4) | isbn13 | `''` | `None` | `None` |
| 18465657 | The One & Only | original_title | `''` | `None` | `None` |
| 18468559 | Raw (RAW Family, #1) | isbn | `''` | `None` | `None` |
| 18468559 | Raw (RAW Family, #1) | isbn13 | `''` | `None` | `None` |
| 18478222 | Twelve Years a Slave | isbn | `''` | `None` | `None` |
| 18478222 | Twelve Years a Slave | isbn13 | `''` | `None` | `None` |
| 1848444 | A Scandal in Bohemia (The Adventures of Sherlock Holmes, #1) | language_code | `''` | `None` | `None` |
| 184850 | Virgin River (Virgin River, #1) | language_code | `''` | `None` | `None` |
| 18500665 | End of Days (Penryn & the End of Days, #3) | isbn | `''` | `None` | `None` |
| 18500665 | End of Days (Penryn & the End of Days, #3) | isbn13 | `''` | `None` | `None` |
| 185012 | Doubt | language_code | `''` | `None` | `None` |
| 18505836 | The Girl Who Came Home | original_title | `''` | `None` | `None` |
| 18580 | Summer of My German Soldier (Summer of My German Soldier, #1) | language_code | `''` | `None` | `None` |
| 18607805 | Kindle Paperwhite User's Guide | isbn | `''` | `None` | `None` |
| 18607805 | Kindle Paperwhite User's Guide | isbn13 | `''` | `None` | `None` |
| 18641982 | The Vacationers | language_code | `''` | `None` | `None` |
| 18655937 | Nash (Marked Men, #4) | original_title | `''` | `None` | `None` |
| 18655937 | Nash (Marked Men, #4) | language_code | `''` | `None` | `None` |
| 18656036 | The Fever | language_code | `''` | `None` | `None` |
| 18659623 | Through the Woods | original_title | `''` | `None` | `None` |
| 186669 | Brilliance of the Moon (Tales of the Otori, #3) | language_code | `''` | `None` | `None` |
| 18667817 | Field of Prey (Lucas Davenport, #24) | original_title | `''` | `None` | `None` |
| 18667945 | #GIRLBOSS | original_title | `''` | `None` | `None` |
| 18668485 | The Initiate (Divergent, #0.2) | isbn | `''` | `None` | `None` |
| 18668485 | The Initiate (Divergent, #0.2) | isbn13 | `''` | `None` | `None` |
| 18680106 | Hard as It Gets (Hard Ink, #1) | isbn | `''` | `None` | `None` |
| 18680106 | Hard as It Gets (Hard Ink, #1) | isbn13 | `''` | `None` | `None` |
| 18711993 | فلتغفري | isbn | `''` | `None` | `None` |
| 18711993 | فلتغفري | isbn13 | `''` | `None` | `None` |
| 18718848 | Mosquitoland | isbn | `''` | `None` | `None` |
| 18718848 | Mosquitoland | isbn13 | `''` | `None` | `None` |
| 18739426 | The Bands of Mourning (Mistborn, #6) | isbn | `''` | `None` | `None` |
| 18739426 | The Bands of Mourning (Mistborn, #6) | isbn13 | `''` | `None` | `None` |
| 18739485 | King (King, #1) | original_title | `''` | `None` | `None` |
| 18752959 | The Staff of Serapis (Percy Jackson & Kane Chronicles Crossover #2) | original_title | `''` | `None` | `None` |
| 1876770 | Chrzest ognia (Saga o Wiedźminie, #5) | isbn | `''` | `None` | `None` |
| 1876770 | Chrzest ognia (Saga o Wiedźminie, #5) | isbn13 | `''` | `None` | `None` |
| 18775203 | Rusty Nailed (Cocktail, #2) | original_title | `''` | `None` | `None` |
| 187812 | Avalon High | language_code | `''` | `None` | `None` |
| 18781540 | Until Lilly (Until, #3) | isbn | `''` | `None` | `None` |
| 18781540 | Until Lilly (Until, #3) | isbn13 | `''` | `None` | `None` |
| 18781540 | Until Lilly (Until, #3) | original_title | `''` | `None` | `None` |
| 18781543 | Until Nico (Until, #4) | isbn | `''` | `None` | `None` |
| 18781543 | Until Nico (Until, #4) | isbn13 | `''` | `None` | `None` |
| 18781543 | Until Nico (Until, #4) | original_title | `''` | `None` | `None` |
| 18781543 | Until Nico (Until, #4) | language_code | `''` | `None` | `None` |
| 18799585 | Hidden (Bone Secrets. #1) | isbn | `''` | `None` | `None` |
| 18799585 | Hidden (Bone Secrets. #1) | isbn13 | `''` | `None` | `None` |
| 18800655 | Terms of Enlistment (Frontlines #1) | isbn | `''` | `None` | `None` |
| 18800655 | Terms of Enlistment (Frontlines #1) | isbn13 | `''` | `None` | `None` |
| 18806240 | Bone Gap | isbn | `''` | `None` | `None` |
| 18806240 | Bone Gap | isbn13 | `''` | `None` | `None` |
| 18813530 | A Shadow of Light (A Shade of Vampire, #4) | isbn | `''` | `None` | `None` |
| 18813530 | A Shadow of Light (A Shade of Vampire, #4) | isbn13 | `''` | `None` | `None` |
| 18813530 | A Shadow of Light (A Shade of Vampire, #4) | original_title | `''` | `None` | `None` |
| 18815695 | The Pecan Man | isbn | `''` | `None` | `None` |
| 18815695 | The Pecan Man | isbn13 | `''` | `None` | `None` |
| 18815695 | The Pecan Man | original_title | `''` | `None` | `None` |
| 18815695 | The Pecan Man | language_code | `''` | `None` | `None` |
| 1881621 | Shugo Chara!, Vol. 1: Who Do You Want to Be? (Shugo Chara!, #1) | language_code | `''` | `None` | `None` |
| 18819296 | Hidden | isbn | `''` | `None` | `None` |
| 18819296 | Hidden | isbn13 | `''` | `None` | `None` |
| 18867685 | The Atlantis Plague (The Origin Mystery, #2) | isbn | `''` | `None` | `None` |
| 18867685 | The Atlantis Plague (The Origin Mystery, #2) | isbn13 | `''` | `None` | `None` |
| 18884 | Polgara the Sorceress (Malloreon) | language_code | `''` | `None` | `None` |
| 18892134 | The Son (Divergent, #0.3) | isbn | `''` | `None` | `None` |
| 18892134 | The Son (Divergent, #0.3) | isbn13 | `''` | `None` | `None` |
| 18906484 | The Husband's Secret Free Preview | isbn | `''` | `None` | `None` |
| 18906484 | The Husband's Secret Free Preview | isbn13 | `''` | `None` | `None` |
| 18906484 | The Husband's Secret Free Preview | original_title | `''` | `None` | `None` |
| 18943009 | Rock Bottom (Tristan & Danika, #2) | isbn | `''` | `None` | `None` |
| 18943009 | Rock Bottom (Tristan & Danika, #2) | isbn13 | `''` | `None` | `None` |
| 18943009 | Rock Bottom (Tristan & Danika, #2) | original_title | `''` | `None` | `None` |
| 1897 | Eiger Dreams: Ventures Among Men and Mountains | language_code | `''` | `None` | `None` |
| 18982011 | The Line (Witching Savannah, #1) | isbn | `''` | `None` | `None` |
| 18982011 | The Line (Witching Savannah, #1) | isbn13 | `''` | `None` | `None` |
| 18989 | Tinker, Tailor, Soldier, Spy | language_code | `''` | `None` | `None` |
| 18999 | Smiley's People | language_code | `''` | `None` | `None` |
| 19000 | The Constant Gardener | isbn | `''` | `None` | `None` |
| 19000 | The Constant Gardener | isbn13 | `''` | `None` | `None` |
| 19000 | The Constant Gardener | language_code | `''` | `None` | `None` |
| 19001 | A Perfect Spy | language_code | `''` | `None` | `None` |
| 19030845 | Batman: The Dark Knight Returns #1 | isbn | `''` | `None` | `None` |
| 19030845 | Batman: The Dark Knight Returns #1 | isbn13 | `''` | `None` | `None` |
| 190361 | Obsidian Butterfly (Anita Blake, Vampire Hunter, #9) | isbn | `''` | `None` | `None` |
| 190361 | Obsidian Butterfly (Anita Blake, Vampire Hunter, #9) | isbn13 | `''` | `None` | `None` |
| 19049 | What the Bleep Do We Know!?: Discovering the Endless Possibilities for Altering Your Everyday Reality | language_code | `''` | `None` | `None` |
| 1908456 | Presentation Zen: Simple Ideas on Presentation Design and Delivery | language_code | `''` | `None` | `None` |
| 19095025 | Play (Stage Dive, #2) | isbn | `''` | `None` | `None` |
| 19095025 | Play (Stage Dive, #2) | isbn13 | `''` | `None` | `None` |
| 19103097 | The Magician's Land (The Magicians, #3) | isbn | `''` | `None` | `None` |
| 19103097 | The Magician's Land (The Magicians, #3) | isbn13 | `''` | `None` | `None` |
| 192341 | The Starter Wife | language_code | `''` | `None` | `None` |
| 1923820 | Holy Bible: King James Version | isbn | `''` | `None` | `None` |
| 1923820 | Holy Bible: King James Version | isbn13 | `''` | `None` | `None` |
| 1923820 | Holy Bible: King James Version | original_title | `''` | `None` | `None` |
| 19286674 | Seventh Grave and No Body (Charley Davidson, #7) | original_title | `''` | `None` | `None` |
| 193093 | Stone Soup | language_code | `''` | `None` | `None` |
| 19330 | The Complete Tales | language_code | `''` | `None` | `None` |
| 19351043 | Nimona | isbn | `''` | `None` | `None` |
| 19351043 | Nimona | isbn13 | `''` | `None` | `None` |
| 19351490 | Grimm's Fairy Tales | isbn | `''` | `None` | `None` |
| 19351490 | Grimm's Fairy Tales | isbn13 | `''` | `None` | `None` |
| 19494 | The Spy Who Came In from the Cold | isbn | `''` | `None` | `None` |
| 19494 | The Spy Who Came In from the Cold | isbn13 | `''` | `None` | `None` |
| 19549841 | Seraphina (Seraphina, #1) | isbn | `''` | `None` | `None` |
| 19549841 | Seraphina (Seraphina, #1) | isbn13 | `''` | `None` | `None` |
| 19552 | Essentials of Classic Italian Cooking | language_code | `''` | `None` | `None` |
| 1963638 | The Untethered Soul: The Journey Beyond Yourself | language_code | `''` | `None` | `None` |
| 19691 | The Hunt for Red October (Jack Ryan Universe, #4) | language_code | `''` | `None` | `None` |
| 196970 | The Night Before Christmas | original_title | `''` | `None` | `None` |
| 197436 | Ralph S. Mouse by Beverly Cleary: Teacher Guide (Novel Units) | original_publication_year | `''` | `None` | `None` |
| 197436 | Ralph S. Mouse by Beverly Cleary: Teacher Guide (Novel Units) | original_title | `''` | `None` | `None` |
| 197436 | Ralph S. Mouse by Beverly Cleary: Teacher Guide (Novel Units) | language_code | `''` | `None` | `None` |
| 19747756 | House | isbn | `''` | `None` | `None` |
| 19747756 | House | isbn13 | `''` | `None` | `None` |
| 19793 | The Power of Intention: Learning to Co-create Your World Your Way | language_code | `''` | `None` | `None` |
| 198863 | Screw It, Let's Do It: Lessons In Life | language_code | `''` | `None` | `None` |
| 2002 | Harry Potter Schoolbooks Box Set: Two Classic Books from the Library of Hogwarts School of Witchcraft and Wizardry | original_title | `''` | `None` | `None` |
| 20082 | The Renegades of Pern (Pern, #10) | language_code | `''` | `None` | `None` |
| 201145 | A Kiss for Little Bear (An I Can Read Book) by Minarik, Else Holmelund [1984] | language_code | `''` | `None` | `None` |
| 201175 | Rapture in Death (In Death, #4) | language_code | `''` | `None` | `None` |
| 2017056 | Skeletons at the Feast | language_code | `''` | `None` | `None` |
| 202146 | Flyboys: A True Story of Courage | language_code | `''` | `None` | `None` |
| 202948 | Ladder of Years | language_code | `''` | `None` | `None` |
| 20299683 | Rat Queens, Vol. 1: Sass & Sorcery | original_title | `''` | `None` | `None` |
| 20316309 | في قلبي أنثى عبرية | isbn | `''` | `None` | `None` |
| 20316309 | في قلبي أنثى عبرية | isbn13 | `''` | `None` | `None` |
| 20317106 | هيبتا | isbn | `''` | `None` | `None` |
| 20317106 | هيبتا | isbn13 | `''` | `None` | `None` |
| 20329634 | Lines of Departure (Frontlines, #2) | isbn | `''` | `None` | `None` |
| 20329634 | Lines of Departure (Frontlines, #2) | isbn13 | `''` | `None` | `None` |
| 20348781 | Loving Mr. Daniels | isbn | `''` | `None` | `None` |
| 20348781 | Loving Mr. Daniels | isbn13 | `''` | `None` | `None` |
| 203805 | Vincent Van Gogh: The Complete Paintings | original_title | `''` | `None` | `None` |
| 204045 | Naruto, Vol. 05: Exam Hell (Naruto, #5) | original_title | `''` | `None` | `None` |
| 20423680 | The Last Town (Wayward Pines, #3) | isbn | `''` | `None` | `None` |
| 20423680 | The Last Town (Wayward Pines, #3) | isbn13 | `''` | `None` | `None` |
| 20438825 | Vanished (Callahan & McLane #1) | isbn | `''` | `None` | `None` |
| 20438825 | Vanished (Callahan & McLane #1) | isbn13 | `''` | `None` | `None` |
| 20438825 | Vanished (Callahan & McLane #1) | original_title | `''` | `None` | `None` |
| 20439328 | How to Be Both | isbn | `''` | `None` | `None` |
| 20439328 | How to Be Both | isbn13 | `''` | `None` | `None` |
| 204479 | Spying in High Heels (High Heels, #1) | isbn | `''` | `None` | `None` |
| 204479 | Spying in High Heels (High Heels, #1) | isbn13 | `''` | `None` | `None` |
| 20509356 | Sand Omnibus (Sand, #1-5) | isbn | `''` | `None` | `None` |
| 20509356 | Sand Omnibus (Sand, #1-5) | isbn13 | `''` | `None` | `None` |
| 205218 | Ethics | language_code | `''` | `None` | `None` |
| 20525628 | How to Build a Girl | isbn | `''` | `None` | `None` |
| 20525628 | How to Build a Girl | isbn13 | `''` | `None` | `None` |
| 205330 | There Was an Old Lady Who Swallowed a Fly | language_code | `''` | `None` | `None` |
| 20559676 | Killing Sarai (In the Company of Killers, #1) | isbn | `''` | `None` | `None` |
| 20559676 | Killing Sarai (In the Company of Killers, #1) | isbn13 | `''` | `None` | `None` |
| 20563 | Adam Bede | language_code | `''` | `None` | `None` |
| 20575434 | Rain Reign | original_title | `''` | `None` | `None` |
| 20603820 | The Will (Magdalene, #1) | isbn | `''` | `None` | `None` |
| 20603820 | The Will (Magdalene, #1) | isbn13 | `''` | `None` | `None` |
| 20613920 | Under Locke | isbn | `''` | `None` | `None` |
| 20613920 | Under Locke | isbn13 | `''` | `None` | `None` |
| 20620995 | Take Me with You | isbn | `''` | `None` | `None` |
| 20620995 | Take Me with You | isbn13 | `''` | `None` | `None` |
| 20620995 | Take Me with You | original_title | `''` | `None` | `None` |
| 20639274 | Archer's Voice | isbn | `''` | `None` | `None` |
| 20639274 | Archer's Voice | isbn13 | `''` | `None` | `None` |
| 20646604 | Night Owl (Night Owl, #1) | isbn | `''` | `None` | `None` |
| 20646604 | Night Owl (Night Owl, #1) | isbn13 | `''` | `None` | `None` |
| 20646604 | Night Owl (Night Owl, #1) | original_title | `''` | `None` | `None` |
| 206731 | The Tibetan Book of Living and Dying | language_code | `''` | `None` | `None` |
| 20685373 | Without You, There Is No Us: My Time with the Sons of North Korea's Elite | language_code | `''` | `None` | `None` |
| 20758175 | The Life We Bury | language_code | `''` | `None` | `None` |
| 20761374 | Reasonable Doubt: Volume 1 (Reasonable Doubt, #1) | isbn | `''` | `None` | `None` |
| 20761374 | Reasonable Doubt: Volume 1 (Reasonable Doubt, #1) | isbn13 | `''` | `None` | `None` |
| 207694 | The Nanny | language_code | `''` | `None` | `None` |
| 20797535 | A Better World (Brilliance Saga, #2) | isbn | `''` | `None` | `None` |
| 20797535 | A Better World (Brilliance Saga, #2) | isbn13 | `''` | `None` | `None` |
| 208036 | Metaphysics | language_code | `''` | `None` | `None` |
| 20803953 | Bully (Fall Away, #1) | isbn | `''` | `None` | `None` |
| 20803953 | Bully (Fall Away, #1) | isbn13 | `''` | `None` | `None` |
| 20803953 | Bully (Fall Away, #1) | language_code | `''` | `None` | `None` |
| 20803962 | Until You (Fall Away, #1.5) | isbn | `''` | `None` | `None` |
| 20803962 | Until You (Fall Away, #1.5) | isbn13 | `''` | `None` | `None` |
| 20803962 | Until You (Fall Away, #1.5) | language_code | `''` | `None` | `None` |
| 20820995 | Deadline (Virgil Flowers, #8) | original_title | `''` | `None` | `None` |
| 20820995 | Deadline (Virgil Flowers, #8) | language_code | `''` | `None` | `None` |
| 20821376 | Belzhar | original_title | `''` | `None` | `None` |
| 20821376 | Belzhar | language_code | `''` | `None` | `None` |
| 20829994 | Percy Jackson's Greek Gods (A Percy Jackson and the Olympians Guide) | isbn | `''` | `None` | `None` |
| 20829994 | Percy Jackson's Greek Gods (A Percy Jackson and the Olympians Guide) | isbn13 | `''` | `None` | `None` |
| 20871704 | Before I Go | original_title | `''` | `None` | `None` |
| 20871704 | Before I Go | language_code | `''` | `None` | `None` |
| 20874139 | I Am Livia | isbn | `''` | `None` | `None` |
| 20874139 | I Am Livia | isbn13 | `''` | `None` | `None` |
| 20874139 | I Am Livia | original_title | `''` | `None` | `None` |
| 20886354 | Skin Deep (Legion, #2) | isbn | `''` | `None` | `None` |
| 20886354 | Skin Deep (Legion, #2) | isbn13 | `''` | `None` | `None` |
| 20894857 | Sleep Tight | isbn | `''` | `None` | `None` |
| 20894857 | Sleep Tight | isbn13 | `''` | `None` | `None` |
| 20912424 | The War that Saved My Life (The War That Saved My Life #1) | original_title | `''` | `None` | `None` |
| 20980373 | Reasonable Doubt: Volume 2 (Reasonable Doubt, #2) | isbn | `''` | `None` | `None` |
| 20980373 | Reasonable Doubt: Volume 2 (Reasonable Doubt, #2) | isbn13 | `''` | `None` | `None` |
| 21025 | The Gift of Therapy: An Open Letter to a New Generation of Therapists and Their Patients | language_code | `''` | `None` | `None` |
| 21027 | Love's Executioner and Other Tales of Psychotherapy | language_code | `''` | `None` | `None` |
| 210404 | A Sand County Almanac and Sketches Here and There | language_code | `''` | `None` | `None` |
| 21060 | Crown Duel (Crown & Court #1-2) | language_code | `''` | `None` | `None` |
| 21104828 | The Lake House | isbn | `''` | `None` | `None` |
| 21104828 | The Lake House | isbn13 | `''` | `None` | `None` |
| 21219083 | The One That Got Away | isbn | `''` | `None` | `None` |
| 21219083 | The One That Got Away | isbn13 | `''` | `None` | `None` |
| 2122216 | Special A, Vol. 1 (Special A, #1) | isbn | `''` | `None` | `None` |
| 2122216 | Special A, Vol. 1 (Special A, #1) | isbn13 | `''` | `None` | `None` |
| 213367 | Desiring God: Meditations of a Christian Hedonist | language_code | `''` | `None` | `None` |
| 21340 | City of Night (Dean Koontz's Frankenstein, #2) | language_code | `''` | `None` | `None` |
| 21394850 | أقوم قيلا | isbn | `''` | `None` | `None` |
| 21394850 | أقوم قيلا | isbn13 | `''` | `None` | `None` |
| 21394850 | أقوم قيلا | original_title | `''` | `None` | `None` |
| 21411058 | Bad Romeo (Starcrossed, #1) | isbn | `''` | `None` | `None` |
| 21411058 | Bad Romeo (Starcrossed, #1) | isbn13 | `''` | `None` | `None` |
| 21411887 | You Were Mine (Rosemary Beach, #9) | original_title | `''` | `None` | `None` |
| 21414439 | Truthwitch (The Witchlands, #1) | isbn | `''` | `None` | `None` |
| 21414439 | Truthwitch (The Witchlands, #1) | isbn13 | `''` | `None` | `None` |
| 21418017 | The Space Between (Outlander, #7.5) | isbn | `''` | `None` | `None` |
| 21418017 | The Space Between (Outlander, #7.5) | isbn13 | `''` | `None` | `None` |
| 21418017 | The Space Between (Outlander, #7.5) | original_title | `''` | `None` | `None` |
| 2141830 | Secrets of a Shoe Addict (Shoe Addict, #2) | language_code | `''` | `None` | `None` |
| 2142 | Blink | language_code | `''` | `None` | `None` |
| 21420473 | The Fixed Trilogy (Fixed, #1-3) | isbn | `''` | `None` | `None` |
| 21420473 | The Fixed Trilogy (Fixed, #1-3) | isbn13 | `''` | `None` | `None` |
| 21420473 | The Fixed Trilogy (Fixed, #1-3) | original_title | `''` | `None` | `None` |
| 214332 | The Case for Faith: A Journalist Investigates the Toughest Objections to Christianity | original_title | `''` | `None` | `None` |
| 214333 | The Case for a Creator: A Journalist Investigates Scientific Evidence That Points Toward God | language_code | `''` | `None` | `None` |
| 21445 | The 5th Horseman (Women's Murder Club, #5) | language_code | `''` | `None` | `None` |
| 21456940 | 1919 | isbn | `''` | `None` | `None` |
| 21456940 | 1919 | isbn13 | `''` | `None` | `None` |
| 21473305 | Dominic (Slater Brothers, #1) | isbn | `''` | `None` | `None` |
| 21473305 | Dominic (Slater Brothers, #1) | isbn13 | `''` | `None` | `None` |
| 21473305 | Dominic (Slater Brothers, #1) | original_title | `''` | `None` | `None` |
| 21483760 | Spell or High Water (Magic 2.0, #2) | original_title | `''` | `None` | `None` |
| 214856 | Leven Thumps and the Gateway to Foo (Leven Thumps, #1) | language_code | `''` | `None` | `None` |
| 21518647 | Axel (Corps Security, #1) | isbn | `''` | `None` | `None` |
| 21518647 | Axel (Corps Security, #1) | isbn13 | `''` | `None` | `None` |
| 21518647 | Axel (Corps Security, #1) | language_code | `''` | `None` | `None` |
| 21518679 | Cage (Corps Security, #2) | isbn | `''` | `None` | `None` |
| 21518679 | Cage (Corps Security, #2) | isbn13 | `''` | `None` | `None` |
| 21518679 | Cage (Corps Security, #2) | original_title | `''` | `None` | `None` |
| 21530229 | The Job (Fox and O'Hare, #3) | original_title | `''` | `None` | `None` |
| 21531503 | What I Know for Sure | original_title | `''` | `None` | `None` |
| 215539 | The Pilgrims of Rayne (Pendragon, #8) | language_code | `''` | `None` | `None` |
| 21683 | Prayers for Rain (Kenzie & Gennaro, #5) | language_code | `''` | `None` | `None` |
| 21727 | A Simple Plan | language_code | `''` | `None` | `None` |
| 2176735 | Breath | language_code | `''` | `None` | `None` |
| 21795430 | Promised (One Night, #1) | original_title | `''` | `None` | `None` |
| 21843117 | Scoring Wilder | isbn | `''` | `None` | `None` |
| 21843117 | Scoring Wilder | isbn13 | `''` | `None` | `None` |
| 21849362 | The Shadows (Black Dagger Brotherhood, #13) | isbn | `''` | `None` | `None` |
| 21849362 | The Shadows (Black Dagger Brotherhood, #13) | isbn13 | `''` | `None` | `None` |
| 21853628 | Every Fifteen Minutes | original_title | `''` | `None` | `None` |
| 21857294 | Reasonable Doubt: Volume 3 (Reasonable Doubt, #3) | isbn | `''` | `None` | `None` |
| 21857294 | Reasonable Doubt: Volume 3 (Reasonable Doubt, #3) | isbn13 | `''` | `None` | `None` |
| 21873331 | If I Stay Collection (If I Stay, #1-2) | original_title | `''` | `None` | `None` |
| 21943246 | Black Ice | original_title | `''` | `None` | `None` |
| 21943246 | Black Ice | language_code | `''` | `None` | `None` |
| 219535 | The Other | original_title | `''` | `None` | `None` |
| 21956060 | Monster in His Eyes (Monster in His Eyes, #1) | isbn | `''` | `None` | `None` |
| 21956060 | Monster in His Eyes (Monster in His Eyes, #1) | isbn13 | `''` | `None` | `None` |
| 21956060 | Monster in His Eyes (Monster in His Eyes, #1) | original_title | `''` | `None` | `None` |
| 21981841 | Corrupt (Devil's Night, #1) | original_title | `''` | `None` | `None` |
| 22009741 | The Woman Who Stole My Life | isbn | `''` | `None` | `None` |
| 22009741 | The Woman Who Stole My Life | isbn13 | `''` | `None` | `None` |
| 22020052 | It Ain't Me, Babe (Hades Hangmen, #1) | isbn | `''` | `None` | `None` |
| 22020052 | It Ain't Me, Babe (Hades Hangmen, #1) | isbn13 | `''` | `None` | `None` |
| 22020052 | It Ain't Me, Babe (Hades Hangmen, #1) | original_title | `''` | `None` | `None` |
| 22027055 | One Lavender Ribbon | isbn | `''` | `None` | `None` |
| 22027055 | One Lavender Ribbon | isbn13 | `''` | `None` | `None` |
| 22027459 | The Atlantis World (The Origin Mystery, #3) | isbn | `''` | `None` | `None` |
| 22027459 | The Atlantis World (The Origin Mystery, #3) | isbn13 | `''` | `None` | `None` |
| 22131009 | Where There's Smoke | isbn | `''` | `None` | `None` |
| 22131009 | Where There's Smoke | isbn13 | `''` | `None` | `None` |
| 22151696 | Lullabies | original_title | `''` | `None` | `None` |
| 22175 | Strange Pilgrims | language_code | `''` | `None` | `None` |
| 22206 | Lullaby | language_code | `''` | `None` | `None` |
| 2223324 | Harry Potter and the Chamber of Secrets: Sheet Music for Flute with C.D | language_code | `''` | `None` | `None` |
| 222458 | Rules | language_code | `''` | `None` | `None` |
| 22296542 | Addicted to You (Addicted, #1) | isbn | `''` | `None` | `None` |
| 22296542 | Addicted to You (Addicted, #1) | isbn13 | `''` | `None` | `None` |
| 22299763 | Crooked Kingdom (Six of Crows, #2) | isbn | `''` | `None` | `None` |
| 22299763 | Crooked Kingdom (Six of Crows, #2) | isbn13 | `''` | `None` | `None` |
| 22319275 | Yellow Crocus | isbn | `''` | `None` | `None` |
| 22319275 | Yellow Crocus | isbn13 | `''` | `None` | `None` |
| 22319275 | Yellow Crocus | original_title | `''` | `None` | `None` |
| 22341276 | The Glass Magician (The Paper Magician Trilogy, #2) | language_code | `''` | `None` | `None` |
| 22381326 | Half a War (Shattered Sea, #3) | isbn | `''` | `None` | `None` |
| 22381326 | Half a War (Shattered Sea, #3) | isbn13 | `''` | `None` | `None` |
| 22381892 | Killing Patton: The Strange Death of World War II's Most Audacious General | isbn | `''` | `None` | `None` |
| 22381892 | Killing Patton: The Strange Death of World War II's Most Audacious General | isbn13 | `''` | `None` | `None` |
| 223838 | In His Steps | language_code | `''` | `None` | `None` |
| 22428828 | Welcome to Shadowhunter Academy (Tales from the Shadowhunter Academy, #1) | isbn | `''` | `None` | `None` |
| 22428828 | Welcome to Shadowhunter Academy (Tales from the Shadowhunter Academy, #1) | isbn13 | `''` | `None` | `None` |
| 22428828 | Welcome to Shadowhunter Academy (Tales from the Shadowhunter Academy, #1) | original_title | `''` | `None` | `None` |
| 224410 | Dracula (Marvel Illustrated) | language_code | `''` | `None` | `None` |
| 22443261 | The Rithmatist (The Rithmatist, #1) | isbn | `''` | `None` | `None` |
| 22443261 | The Rithmatist (The Rithmatist, #1) | isbn13 | `''` | `None` | `None` |
| 22457201 | Hardpressed (Hacker, #2) | isbn | `''` | `None` | `None` |
| 22457201 | Hardpressed (Hacker, #2) | isbn13 | `''` | `None` | `None` |
| 22457201 | Hardpressed (Hacker, #2) | original_title | `''` | `None` | `None` |
| 22471294 | Black Lies | isbn | `''` | `None` | `None` |
| 22471294 | Black Lies | isbn13 | `''` | `None` | `None` |
| 22474626 | Hard Limit (Hacker, #4) | isbn | `''` | `None` | `None` |
| 22474626 | Hard Limit (Hacker, #4) | isbn13 | `''` | `None` | `None` |
| 22474626 | Hard Limit (Hacker, #4) | language_code | `''` | `None` | `None` |
| 2251306 | Brain Rules: 12 Principles for Surviving and Thriving at Work, Home, and School | language_code | `''` | `None` | `None` |
| 22551743 | The Truth According to Us | original_title | `''` | `None` | `None` |
| 22554204 | Lumberjanes, Vol. 1: Beware the Kitten Holy | original_title | `''` | `None` | `None` |
| 225545 | A Color of His Own | language_code | `''` | `None` | `None` |
| 22571612 | Crash & Burn (Tessa Leoni, #3) | original_title | `''` | `None` | `None` |
| 22600903 | Where I Belong (Alabama Summer, #1) | isbn | `''` | `None` | `None` |
| 22600903 | Where I Belong (Alabama Summer, #1) | isbn13 | `''` | `None` | `None` |
| 22609310 | Confess | original_title | `''` | `None` | `None` |
| 22611920 | The Hook Up (Game On, #1) | isbn | `''` | `None` | `None` |
| 22611920 | The Hook Up (Game On, #1) | isbn13 | `''` | `None` | `None` |
| 226315 | The Next Big Thing | language_code | `''` | `None` | `None` |
| 22632 | The Trial and Death of Socrates | original_title | `''` | `None` | `None` |
| 22669832 | Bright Side (Bright Side, #1) | isbn | `''` | `None` | `None` |
| 22669832 | Bright Side (Bright Side, #1) | isbn13 | `''` | `None` | `None` |
| 22669832 | Bright Side (Bright Side, #1) | original_title | `''` | `None` | `None` |
| 22674493 | NYPD Red 3 (NYPD Red, #3) | language_code | `''` | `None` | `None` |
| 22693182 | Where They Found Her | original_title | `''` | `None` | `None` |
| 22693222 | The Residence: Inside the Private World of the White House | language_code | `''` | `None` | `None` |
| 22695 | Summer Sisters | language_code | `''` | `None` | `None` |
| 227280 | I Do -- But I Don't | language_code | `''` | `None` | `None` |
| 22738563 | We Should All Be Feminists | isbn | `''` | `None` | `None` |
| 22738563 | We Should All Be Feminists | isbn13 | `''` | `None` | `None` |
| 227443 | Bridget Jones's Diary (Bridget Jones, #1) | original_title | `''` | `None` | `None` |
| 22744701 | My Sister's Grave (Tracy Crosswhite #1) | isbn | `''` | `None` | `None` |
| 22744701 | My Sister's Grave (Tracy Crosswhite #1) | isbn13 | `''` | `None` | `None` |
| 227729 | The Coffin Dancer (Lincoln Rhyme, #2) | original_title | `''` | `None` | `None` |
| 227778 | Charlie Bone and the Time Twister (The Children of the Red King, #2) | language_code | `''` | `None` | `None` |
| 22816087 | Seveneves | isbn | `''` | `None` | `None` |
| 22816087 | Seveneves | isbn13 | `''` | `None` | `None` |
| 22836957 | The Revenant | language_code | `''` | `None` | `None` |
| 22840421 | My Lady Jane (The Lady Janies, #1) | isbn | `''` | `None` | `None` |
| 22840421 | My Lady Jane (The Lady Janies, #1) | isbn13 | `''` | `None` | `None` |
| 22857396 | Sweet Addiction (Sweet Addiction, #1) | isbn | `''` | `None` | `None` |
| 22857396 | Sweet Addiction (Sweet Addiction, #1) | isbn13 | `''` | `None` | `None` |
| 2285777 | A Summer Affair | language_code | `''` | `None` | `None` |
| 228765 | Zen of Seeing: Seeing/Drawing as Meditation | language_code | `''` | `None` | `None` |
| 22886612 | Nemesis Games (The Expanse, #5) | isbn | `''` | `None` | `None` |
| 22886612 | Nemesis Games (The Expanse, #5) | isbn13 | `''` | `None` | `None` |
| 22895264 | Wicked (A Wicked Saga, #1) | isbn | `''` | `None` | `None` |
| 22895264 | Wicked (A Wicked Saga, #1) | isbn13 | `''` | `None` | `None` |
| 228990 | The Illearth War (The Chronicles of Thomas Covenant the Unbeliever, #2) | language_code | `''` | `None` | `None` |
| 229123 | Christy | language_code | `''` | `None` | `None` |
| 22914448 | The Dead Key | isbn | `''` | `None` | `None` |
| 22914448 | The Dead Key | isbn13 | `''` | `None` | `None` |
| 22914448 | The Dead Key | original_title | `''` | `None` | `None` |
| 22915460 | The Glassblower | isbn | `''` | `None` | `None` |
| 22915460 | The Glassblower | isbn13 | `''` | `None` | `None` |
| 22918050 | The Heir (The Selection, #4) | isbn | `''` | `None` | `None` |
| 22918050 | The Heir (The Selection, #4) | isbn13 | `''` | `None` | `None` |
| 22923997 | Overruled (The Legal Briefs, #1) | isbn | `''` | `None` | `None` |
| 22923997 | Overruled (The Legal Briefs, #1) | isbn13 | `''` | `None` | `None` |
| 22931009 | Kindle User's Guide | isbn | `''` | `None` | `None` |
| 22931009 | Kindle User's Guide | isbn13 | `''` | `None` | `None` |
| 22931009 | Kindle User's Guide | original_title | `''` | `None` | `None` |
| 2296567 | Say You're One of Them | language_code | `''` | `None` | `None` |
| 22995 | La casa de Bernarda Alba | language_code | `''` | `None` | `None` |
| 23012475 | The Knockoff | original_title | `''` | `None` | `None` |
| 23012475 | The Knockoff | language_code | `''` | `None` | `None` |
| 23014603 | Those Girls | original_title | `''` | `None` | `None` |
| 23014603 | Those Girls | language_code | `''` | `None` | `None` |
| 231 | I am Charlotte Simmons | original_title | `''` | `None` | `None` |
| 23122175 | The Friend Zone (Game On, #2) | isbn | `''` | `None` | `None` |
| 23122175 | The Friend Zone (Game On, #2) | isbn13 | `''` | `None` | `None` |
| 23158207 | How Google Works | isbn | `''` | `None` | `None` |
| 23158207 | How Google Works | isbn13 | `''` | `None` | `None` |
| 23196 | The River Why | language_code | `''` | `None` | `None` |
| 23207027 | Three Dark Crowns (Three Dark Crowns, #1) | isbn | `''` | `None` | `None` |
| 23207027 | Three Dark Crowns (Three Dark Crowns, #1) | isbn13 | `''` | `None` | `None` |
| 23212667 | All the Missing Girls | isbn | `''` | `None` | `None` |
| 23212667 | All the Missing Girls | isbn13 | `''` | `None` | `None` |
| 23245587 | Summer Secrets | original_title | `''` | `None` | `None` |
| 23245587 | Summer Secrets | language_code | `''` | `None` | `None` |
| 23245594 | Beach Town | original_title | `''` | `None` | `None` |
| 23245594 | Beach Town | language_code | `''` | `None` | `None` |
| 23252517 | The Law of Moses (The Law of Moses, #1) | isbn | `''` | `None` | `None` |
| 23252517 | The Law of Moses (The Law of Moses, #1) | isbn13 | `''` | `None` | `None` |
| 23281640 | Gathering Prey (Lucas Davenport, #25) | language_code | `''` | `None` | `None` |
| 23287179 | Orphan Number Eight | original_title | `''` | `None` | `None` |
| 232958 | I Love You Through and Through | language_code | `''` | `None` | `None` |
| 23355069 | Hero (Hero, #1) | isbn | `''` | `None` | `None` |
| 23355069 | Hero (Hero, #1) | isbn13 | `''` | `None` | `None` |
| 23357188 | Bound by Honor (Born in Blood Mafia Chronicles, #1) | isbn | `''` | `None` | `None` |
| 23357188 | Bound by Honor (Born in Blood Mafia Chronicles, #1) | isbn13 | `''` | `None` | `None` |
| 233691 | The Far Side Gallery 3 | language_code | `''` | `None` | `None` |
| 23398961 | The Sound of Glass | original_title | `''` | `None` | `None` |
| 23422 | The Art of Travel | language_code | `''` | `None` | `None` |
| 23454 | Dragons of Winter Night (Dragonlance: Chronicles, #2) | original_title | `''` | `None` | `None` |
| 234724 | Shadow Puppets (Ender's Shadow, #3) | language_code | `''` | `None` | `None` |
| 23481669 | Maude | isbn | `''` | `None` | `None` |
| 23481669 | Maude | isbn13 | `''` | `None` | `None` |
| 23481669 | Maude | original_title | `''` | `None` | `None` |
| 23481669 | Maude | language_code | `''` | `None` | `None` |
| 23485372 | The Master Magician (The Paper Magician Trilogy, #3) | isbn | `''` | `None` | `None` |
| 23485372 | The Master Magician (The Paper Magician Trilogy, #3) | isbn13 | `''` | `None` | `None` |
| 23492288 | Hidden Bodies (You, #2) | isbn | `''` | `None` | `None` |
| 23492288 | Hidden Bodies (You, #2) | isbn13 | `''` | `None` | `None` |
| 23492613 | Eight Hundred Grapes | language_code | `''` | `None` | `None` |
| 23492661 | Maybe in Another Life | language_code | `''` | `None` | `None` |
| 23492673 | Primates of Park Avenue | original_title | `''` | `None` | `None` |
| 2350129 | Preach My Gospel: A Guide To Missionary Service | language_code | `''` | `None` | `None` |
| 23545800 | Kaleidoscope Hearts (Hearts, #1) | isbn | `''` | `None` | `None` |
| 23545800 | Kaleidoscope Hearts (Hearts, #1) | isbn13 | `''` | `None` | `None` |
| 23566909 | The Marvels | original_title | `''` | `None` | `None` |
| 23587984 | Maybe Not (Maybe, #1.5) | isbn | `''` | `None` | `None` |
| 23587984 | Maybe Not (Maybe, #1.5) | isbn13 | `''` | `None` | `None` |
| 23602562 | Our Souls at Night | language_code | `''` | `None` | `None` |
| 23647129 | For the Love: Fighting for Grace in a World of Impossible Standards | language_code | `''` | `None` | `None` |
| 23675858 | Departure | isbn | `''` | `None` | `None` |
| 23675858 | Departure | isbn13 | `''` | `None` | `None` |
| 23692271 | Sapiens: A Brief History of Humankind | isbn | `''` | `None` | `None` |
| 23692271 | Sapiens: A Brief History of Humankind | isbn13 | `''` | `None` | `None` |
| 23714532 | Beautiful Sacrifice (The Maddox Brothers, #3) | isbn | `''` | `None` | `None` |
| 23714532 | Beautiful Sacrifice (The Maddox Brothers, #3) | isbn13 | `''` | `None` | `None` |
| 23714544 | Beautiful Burn (The Maddox Brothers, #4) | isbn | `''` | `None` | `None` |
| 23714544 | Beautiful Burn (The Maddox Brothers, #4) | isbn13 | `''` | `None` | `None` |
| 23743603 | Miramont's Ghost | isbn | `''` | `None` | `None` |
| 23743603 | Miramont's Ghost | isbn13 | `''` | `None` | `None` |
| 23743603 | Miramont's Ghost | original_title | `''` | `None` | `None` |
| 23745132 | Wreckage | isbn | `''` | `None` | `None` |
| 23745132 | Wreckage | isbn13 | `''` | `None` | `None` |
| 23745132 | Wreckage | original_title | `''` | `None` | `None` |
| 23745189 | The Mermaid's Sister | isbn | `''` | `None` | `None` |
| 23745189 | The Mermaid's Sister | isbn13 | `''` | `None` | `None` |
| 23844390 | The Pact | isbn | `''` | `None` | `None` |
| 23844390 | The Pact | isbn13 | `''` | `None` | `None` |
| 23844390 | The Pact | original_title | `''` | `None` | `None` |
| 23885 | No One Writes to the Colonel and Other Stories | language_code | `''` | `None` | `None` |
| 23965 | Porno | language_code | `''` | `None` | `None` |
| 24019 | The New Best Recipe | isbn | `''` | `None` | `None` |
| 24019 | The New Best Recipe | isbn13 | `''` | `None` | `None` |
| 24019 | The New Best Recipe | language_code | `''` | `None` | `None` |
| 24044596 | Kulti | isbn | `''` | `None` | `None` |
| 24044596 | Kulti | isbn13 | `''` | `None` | `None` |
| 24044596 | Kulti | original_title | `''` | `None` | `None` |
| 24044596 | Kulti | language_code | `''` | `None` | `None` |
| 24096 | Leonardo's Notebooks | original_title | `''` | `None` | `None` |
| 24096 | Leonardo's Notebooks | language_code | `''` | `None` | `None` |
| 24215 | Alice's Adventures in Wonderland: A Pop-Up Adaptation | original_title | `''` | `None` | `None` |
| 242157 | How to Talk to a Widower | language_code | `''` | `None` | `None` |
| 24228353 | Trail of Broken Wings | isbn | `''` | `None` | `None` |
| 24228353 | Trail of Broken Wings | isbn13 | `''` | `None` | `None` |
| 24244 | The Black Ice (Harry Bosch, #2; Harry Bosch Universe, #2) | original_title | `''` | `None` | `None` |
| 243298 | The Shining Ones (The Tamuli, #2) | language_code | `''` | `None` | `None` |
| 243308 | Steel Magnolias (DPS Acting Edition) | original_title | `''` | `None` | `None` |
| 24378015 | Never Never (Never Never, #1) | isbn | `''` | `None` | `None` |
| 24378015 | Never Never (Never Never, #1) | isbn13 | `''` | `None` | `None` |
| 24384 | The Cricket in Times Square | original_title | `''` | `None` | `None` |
| 24422492 | Never Never: Part Two (Never Never, #2) | original_title | `''` | `None` | `None` |
| 24429934 | The Einstein Prophecy | isbn | `''` | `None` | `None` |
| 24429934 | The Einstein Prophecy | isbn13 | `''` | `None` | `None` |
| 24429934 | The Einstein Prophecy | original_title | `''` | `None` | `None` |
| 24431 | Trickster's Choice (Daughter of the Lioness, #1) | original_title | `''` | `None` | `None` |
| 24445517 | Maybe Someday (Maybe, #1) | isbn | `''` | `None` | `None` |
| 24445517 | Maybe Someday (Maybe, #1) | isbn13 | `''` | `None` | `None` |
| 24473465 | The English Spy (Gabriel Allon, #15) | isbn | `''` | `None` | `None` |
| 24473465 | The English Spy (Gabriel Allon, #15) | isbn13 | `''` | `None` | `None` |
| 24473763 | Radiance (Wraith Kings, #1) | isbn | `''` | `None` | `None` |
| 24473763 | Radiance (Wraith Kings, #1) | isbn13 | `''` | `None` | `None` |
| 24480276 | The Versions of Us | isbn | `''` | `None` | `None` |
| 24480276 | The Versions of Us | isbn13 | `''` | `None` | `None` |
| 24488476 | The Fate of Ten (Lorien Legacies, #6) | isbn | `''` | `None` | `None` |
| 24488476 | The Fate of Ten (Lorien Legacies, #6) | isbn13 | `''` | `None` | `None` |
| 24488476 | The Fate of Ten (Lorien Legacies, #6) | original_title | `''` | `None` | `None` |
| 24504274 | Pucked (Pucked, #1) | original_title | `''` | `None` | `None` |
| 245700 | The Art of Amy Brown | language_code | `''` | `None` | `None` |
| 24631990 | Silent Scream (D.I. Kim Stone, #1) | isbn | `''` | `None` | `None` |
| 24631990 | Silent Scream (D.I. Kim Stone, #1) | isbn13 | `''` | `None` | `None` |
| 246468 | The Jordan Rules | language_code | `''` | `None` | `None` |
| 246546 | An Old-Fashioned Girl | language_code | `''` | `None` | `None` |
| 24709327 | Scion of Ikshvaku (RamChandra, #1) | original_title | `''` | `None` | `None` |
| 24766 | The Secret Hour (Midnighters, #1) | isbn | `''` | `None` | `None` |
| 24766 | The Secret Hour (Midnighters, #1) | isbn13 | `''` | `None` | `None` |
| 24819476 | Winter Stroll (Winter #2) | language_code | `''` | `None` | `None` |
| 248470 | River Secrets (The Books of Bayern, #3) | language_code | `''` | `None` | `None` |
| 24859245 | Stranger Child (DCI Tom Douglas, #4) | isbn | `''` | `None` | `None` |
| 24859245 | Stranger Child (DCI Tom Douglas, #4) | isbn13 | `''` | `None` | `None` |
| 24859245 | Stranger Child (DCI Tom Douglas, #4) | original_title | `''` | `None` | `None` |
| 24902492 | Ruby | language_code | `''` | `None` | `None` |
| 24903031 | Blood Kiss (Black Dagger Legacy, #1) | original_title | `''` | `None` | `None` |
| 24903919 | Depraved Heart (Kay Scarpetta, #23) | language_code | `''` | `None` | `None` |
| 249042 | Darkness Visible: A Memoir of Madness | language_code | `''` | `None` | `None` |
| 24920901 | The Deal (Off-Campus, #1) | isbn | `''` | `None` | `None` |
| 24920901 | The Deal (Off-Campus, #1) | isbn13 | `''` | `None` | `None` |
| 24937499 | Her Final Breath (Tracy Crosswhite, #2) | isbn | `''` | `None` | `None` |
| 24937499 | Her Final Breath (Tracy Crosswhite, #2) | isbn13 | `''` | `None` | `None` |
| 24937499 | Her Final Breath (Tracy Crosswhite, #2) | original_title | `''` | `None` | `None` |
| 24938 | Wicked - Piano/Vocal Arrangement | language_code | `''` | `None` | `None` |
| 24950845 | Tricky Twenty-Two (Stephanie Plum, #22) | original_title | `''` | `None` | `None` |
| 24961498 | The Midwife's Revolt (The Midwife Series, #1) | isbn | `''` | `None` | `None` |
| 24961498 | The Midwife's Revolt (The Midwife Series, #1) | isbn13 | `''` | `None` | `None` |
| 24961498 | The Midwife's Revolt (The Midwife Series, #1) | original_title | `''` | `None` | `None` |
| 24961531 | The Color of Secrets | isbn | `''` | `None` | `None` |
| 24961531 | The Color of Secrets | isbn13 | `''` | `None` | `None` |
| 24961531 | The Color of Secrets | original_title | `''` | `None` | `None` |
| 24961531 | The Color of Secrets | language_code | `''` | `None` | `None` |
| 25005214 | Queen Song (Red Queen, #0.1) | language_code | `''` | `None` | `None` |
| 2501453 | عابر سرير | isbn | `''` | `None` | `None` |
| 2501453 | عابر سرير | isbn13 | `''` | `None` | `None` |
| 2501455 | فوضى الحواس | isbn | `''` | `None` | `None` |
| 2501455 | فوضى الحواس | isbn13 | `''` | `None` | `None` |
| 2501458 | ذاكرة الجسد | isbn | `''` | `None` | `None` |
| 2501458 | ذاكرة الجسد | isbn13 | `''` | `None` | `None` |
| 25041504 | After You (Me Before You, #2) | isbn | `''` | `None` | `None` |
| 25041504 | After You (Me Before You, #2) | isbn13 | `''` | `None` | `None` |
| 25056528 | Sincerely, Carter (Sincerely Carter, #1) | isbn | `''` | `None` | `None` |
| 25056528 | Sincerely, Carter (Sincerely Carter, #1) | isbn13 | `''` | `None` | `None` |
| 25056528 | Sincerely, Carter (Sincerely Carter, #1) | original_title | `''` | `None` | `None` |
| 25056528 | Sincerely, Carter (Sincerely Carter, #1) | language_code | `''` | `None` | `None` |
| 2505836 | Money, and the Law of Attraction: Learning to Attract Wealth, Health, and Happiness | language_code | `''` | `None` | `None` |
| 25065522 | Wildflower | original_title | `''` | `None` | `None` |
| 25066591 | Cross Justice (Alex Cross, #23) | language_code | `''` | `None` | `None` |
| 2508854 | تاكسي: حواديت المشاوير | isbn | `''` | `None` | `None` |
| 2508854 | تاكسي: حواديت المشاوير | isbn13 | `''` | `None` | `None` |
| 25104491 | The Prettiest One | isbn | `''` | `None` | `None` |
| 25104491 | The Prettiest One | isbn13 | `''` | `None` | `None` |
| 25104491 | The Prettiest One | original_title | `''` | `None` | `None` |
| 25153134 | Follow You Home | isbn | `''` | `None` | `None` |
| 25153134 | Follow You Home | isbn13 | `''` | `None` | `None` |
| 25228579 | The Perfect Son | isbn | `''` | `None` | `None` |
| 25228579 | The Perfect Son | isbn13 | `''` | `None` | `None` |
| 253058 | Temple of the Winds (Sword of Truth, #4) | language_code | `''` | `None` | `None` |
| 25316313 | A Dark Lure | isbn | `''` | `None` | `None` |
| 25316313 | A Dark Lure | isbn13 | `''` | `None` | `None` |
| 25316313 | A Dark Lure | original_title | `''` | `None` | `None` |
| 25346 | Out of the Dust | language_code | `''` | `None` | `None` |
| 25387351 | Rogue Lawyer | original_title | `''` | `None` | `None` |
| 25387351 | Rogue Lawyer | language_code | `''` | `None` | `None` |
| 25422234 | Notorious RBG: The Life and Times of Ruth Bader Ginsburg | original_title | `''` | `None` | `None` |
| 25430584 | The Guest Room | original_title | `''` | `None` | `None` |
| 25451852 | Dawn of Wonder (The Wakening, #1) | isbn | `''` | `None` | `None` |
| 25451852 | Dawn of Wonder (The Wakening, #1) | isbn13 | `''` | `None` | `None` |
| 25454883 | Never Never: Part Three (Never Never, #3) | isbn | `''` | `None` | `None` |
| 25454883 | Never Never: Part Three (Never Never, #3) | isbn13 | `''` | `None` | `None` |
| 25454883 | Never Never: Part Three (Never Never, #3) | original_title | `''` | `None` | `None` |
| 2548866 | James Potter and the Hall of Elders' Crossing (James Potter, #1) | isbn | `''` | `None` | `None` |
| 2548866 | James Potter and the Hall of Elders' Crossing (James Potter, #1) | isbn13 | `''` | `None` | `None` |
| 25507925 | Binge | isbn | `''` | `None` | `None` |
| 25507925 | Binge | isbn13 | `''` | `None` | `None` |
| 25507925 | Binge | language_code | `''` | `None` | `None` |
| 255127 | The Fifth Discipline: The Art & Practice of The Learning Organization | original_title | `''` | `None` | `None` |
| 255127 | The Fifth Discipline: The Art & Practice of The Learning Organization | language_code | `''` | `None` | `None` |
| 255458 | Systematic Theology: An Introduction to Biblical Doctrine | language_code | `''` | `None` | `None` |
| 25558608 | A Torch Against the Night (An Ember in the Ashes, #2) | isbn | `''` | `None` | `None` |
| 25558608 | A Torch Against the Night (An Ember in the Ashes, #2) | isbn13 | `''` | `None` | `None` |
| 25564446 | The Air He Breathes (Elements, #1) | isbn | `''` | `None` | `None` |
| 25564446 | The Air He Breathes (Elements, #1) | isbn13 | `''` | `None` | `None` |
| 25564446 | The Air He Breathes (Elements, #1) | language_code | `''` | `None` | `None` |
| 25614984 | Spark Joy: An Illustrated Master Class on the Art of Organizing and Tidying Up | original_title | `''` | `None` | `None` |
| 25624089 | Killing Reagan: The Violent Assault That Changed a Presidency | isbn | `''` | `None` | `None` |
| 25624089 | Killing Reagan: The Violent Assault That Changed a Presidency | isbn13 | `''` | `None` | `None` |
| 25657 | Sellevision | language_code | `''` | `None` | `None` |
| 256598 | Curse of the Bane (The Last Apprentice / Wardstone Chronicles, #2) | language_code | `''` | `None` | `None` |
| 25690958 | Year of Yes: How to Dance It Out, Stand In the Sun and Be Your Own Person | isbn | `''` | `None` | `None` |
| 25690958 | Year of Yes: How to Dance It Out, Stand In the Sun and Be Your Own Person | isbn13 | `''` | `None` | `None` |
| 25690958 | Year of Yes: How to Dance It Out, Stand In the Sun and Be Your Own Person | original_title | `''` | `None` | `None` |
| 25693079 | Crooked Little Lies | isbn | `''` | `None` | `None` |
| 25693079 | Crooked Little Lies | isbn13 | `''` | `None` | `None` |
| 25693079 | Crooked Little Lies | original_title | `''` | `None` | `None` |
| 25693079 | Crooked Little Lies | language_code | `''` | `None` | `None` |
| 25711641 | Tyrant (King, #2) | isbn | `''` | `None` | `None` |
| 25711641 | Tyrant (King, #2) | isbn13 | `''` | `None` | `None` |
| 25711641 | Tyrant (King, #2) | original_title | `''` | `None` | `None` |
| 257257 | The 20th Century Art Book | language_code | `''` | `None` | `None` |
| 25773504 | Most Wanted | original_title | `''` | `None` | `None` |
| 25801299 | After Anna | isbn | `''` | `None` | `None` |
| 25801299 | After Anna | isbn13 | `''` | `None` | `None` |
| 25802884 | Hollywood Dirt (Hollywood Dirt, #1) | isbn | `''` | `None` | `None` |
| 25802884 | Hollywood Dirt (Hollywood Dirt, #1) | isbn13 | `''` | `None` | `None` |
| 25817531 | What She Knew | language_code | `''` | `None` | `None` |
| 25828204 | F*ck Love | isbn | `''` | `None` | `None` |
| 25828204 | F*ck Love | isbn13 | `''` | `None` | `None` |
| 25828204 | F*ck Love | original_title | `''` | `None` | `None` |
| 25828204 | F*ck Love | language_code | `''` | `None` | `None` |
| 25837338 | The Girl from Krakow | isbn | `''` | `None` | `None` |
| 25837338 | The Girl from Krakow | isbn13 | `''` | `None` | `None` |
| 25837341 | The Good Neighbor | isbn | `''` | `None` | `None` |
| 25837341 | The Good Neighbor | isbn13 | `''` | `None` | `None` |
| 25837341 | The Good Neighbor | original_title | `''` | `None` | `None` |
| 25866725 | Broken Grace | isbn | `''` | `None` | `None` |
| 25866725 | Broken Grace | isbn13 | `''` | `None` | `None` |
| 25866725 | Broken Grace | original_title | `''` | `None` | `None` |
| 25883848 | The Hating Game | isbn | `''` | `None` | `None` |
| 25883848 | The Hating Game | isbn13 | `''` | `None` | `None` |
| 25899336 | When Breath Becomes Air | isbn | `''` | `None` | `None` |
| 25899336 | When Breath Becomes Air | isbn13 | `''` | `None` | `None` |
| 25912358 | A Thousand Boy Kisses | isbn | `''` | `None` | `None` |
| 25912358 | A Thousand Boy Kisses | isbn13 | `''` | `None` | `None` |
| 26061591 | Extreme Prey (Lucas Davenport, #26) | isbn | `''` | `None` | `None` |
| 26061591 | Extreme Prey (Lucas Davenport, #26) | isbn13 | `''` | `None` | `None` |
| 26061591 | Extreme Prey (Lucas Davenport, #26) | original_title | `''` | `None` | `None` |
| 261083 | Heretic (The Grail Quest, #3) | language_code | `''` | `None` | `None` |
| 26114516 | The Weekenders | original_title | `''` | `None` | `None` |
| 26114516 | The Weekenders | language_code | `''` | `None` | `None` |
| 261161 | Dial L for Loser (The Clique, #6) | language_code | `''` | `None` | `None` |
| 2615 | The Innovator's Dilemma: The Revolutionary Book that Will Change the Way You Do Business (Collins Business Essentials) | language_code | `''` | `None` | `None` |
| 26158341 | The Girl With No Past | isbn | `''` | `None` | `None` |
| 26158341 | The Girl With No Past | isbn13 | `''` | `None` | `None` |
| 26192467 | First Comes Love | original_title | `''` | `None` | `None` |
| 26214866 | In the Clearing (Tracy Crosswhite, #3) | isbn | `''` | `None` | `None` |
| 26214866 | In the Clearing (Tracy Crosswhite, #3) | isbn13 | `''` | `None` | `None` |
| 26214866 | In the Clearing (Tracy Crosswhite, #3) | original_title | `''` | `None` | `None` |
| 26224667 | Wrong (Wrong, #1) | isbn | `''` | `None` | `None` |
| 26224667 | Wrong (Wrong, #1) | isbn13 | `''` | `None` | `None` |
| 262545 | The Whistling Season | language_code | `''` | `None` | `None` |
| 262731 | The Definitive Book of Body Language | isbn | `''` | `None` | `None` |
| 262731 | The Definitive Book of Body Language | isbn13 | `''` | `None` | `None` |
| 26324 | Social Intelligence: The New Science of Human Relationships | language_code | `''` | `None` | `None` |
| 264158 | The Raven | language_code | `''` | `None` | `None` |
| 265205 | Life Application Study Bible: NIV | original_title | `''` | `None` | `None` |
| 265264 | One | language_code | `''` | `None` | `None` |
| 265650 | Shakespeare's Romeo and Juliet | language_code | `''` | `None` | `None` |
| 26583370 | Life and Other Near-Death Experiences | isbn | `''` | `None` | `None` |
| 26583370 | Life and Other Near-Death Experiences | isbn13 | `''` | `None` | `None` |
| 26583370 | Life and Other Near-Death Experiences | original_title | `''` | `None` | `None` |
| 2659997 | Stolen Innocence: My Story of Growing Up in a Polygamous Sect, Becoming a Teenage Bride, and Breaking Free of Warren Jeffs | language_code | `''` | `None` | `None` |
| 26661 | Praying God's Word: Breaking Free From Spiritual Strongholds | language_code | `''` | `None` | `None` |
| 266904 | The Penderwicks: A Summer Tale of Four Sisters, Two Rabbits, and a Very Interesting Boy (The Penderwicks #1) | isbn | `''` | `None` | `None` |
| 266904 | The Penderwicks: A Summer Tale of Four Sisters, Two Rabbits, and a Very Interesting Boy (The Penderwicks #1) | isbn13 | `''` | `None` | `None` |
| 2678349 | استمتع بحياتك | isbn | `''` | `None` | `None` |
| 2678349 | استمتع بحياتك | isbn13 | `''` | `None` | `None` |
| 267972 | Wait Till Helen Comes | original_title | `''` | `None` | `None` |
| 268955 | Mummies in the Morning (Magic Tree House, #3) | original_title | `''` | `None` | `None` |
| 270032 | Seven Years in Tibet | language_code | `''` | `None` | `None` |
| 27037 | Confessions | language_code | `''` | `None` | `None` |
| 270521 | The Russia House | language_code | `''` | `None` | `None` |
| 27152124 | Dirty English (English, #1) | isbn | `''` | `None` | `None` |
| 27152124 | Dirty English (English, #1) | isbn13 | `''` | `None` | `None` |
| 27161845 | Here's to Us | original_title | `''` | `None` | `None` |
| 27207654 | Blood Defense (Samantha Brinkman, #1) | isbn | `''` | `None` | `None` |
| 27207654 | Blood Defense (Samantha Brinkman, #1) | isbn13 | `''` | `None` | `None` |
| 27207654 | Blood Defense (Samantha Brinkman, #1) | original_title | `''` | `None` | `None` |
| 27209486 | Modern Lovers | language_code | `''` | `None` | `None` |
| 272315 | Keeping You a Secret | language_code | `''` | `None` | `None` |
| 27239265 | The Short Drop (Gibson Vaughn, #1) | isbn | `''` | `None` | `None` |
| 27239265 | The Short Drop (Gibson Vaughn, #1) | isbn13 | `''` | `None` | `None` |
| 27239265 | The Short Drop (Gibson Vaughn, #1) | original_title | `''` | `None` | `None` |
| 27252717 | The Score (Off-Campus, #3) | isbn | `''` | `None` | `None` |
| 27252717 | The Score (Off-Campus, #3) | isbn13 | `''` | `None` | `None` |
| 27362503 | It Ends with Us | isbn | `''` | `None` | `None` |
| 27362503 | It Ends with Us | isbn13 | `''` | `None` | `None` |
| 27401883 | When I'm Gone | isbn | `''` | `None` | `None` |
| 27401883 | When I'm Gone | isbn13 | `''` | `None` | `None` |
| 27406436 | The Baller: A Down and Dirty Football Novel | isbn | `''` | `None` | `None` |
| 27406436 | The Baller: A Down and Dirty Football Novel | isbn13 | `''` | `None` | `None` |
| 27419654 | The Last Girl (The Dominion Trilogy, #1) | isbn | `''` | `None` | `None` |
| 27419654 | The Last Girl (The Dominion Trilogy, #1) | isbn13 | `''` | `None` | `None` |
| 27419654 | The Last Girl (The Dominion Trilogy, #1) | original_title | `''` | `None` | `None` |
| 27423283 | The Moonlit Garden | isbn | `''` | `None` | `None` |
| 27423283 | The Moonlit Garden | isbn13 | `''` | `None` | `None` |
| 2743 | The Lost Boy (Dave Pelzer #2) | original_title | `''` | `None` | `None` |
| 2747288 | Dragonheart (Pern, #21) | language_code | `''` | `None` | `None` |
| 2750180 | لا تحزن | isbn | `''` | `None` | `None` |
| 2750180 | لا تحزن | isbn13 | `''` | `None` | `None` |
| 275247 | Little Lord Fauntleroy | language_code | `''` | `None` | `None` |
| 276342 | Angel Falls | language_code | `''` | `None` | `None` |
| 278102 | Kaleidoscope | original_title | `''` | `None` | `None` |
| 27810589 | A Death in Sweden | isbn | `''` | `None` | `None` |
| 27810589 | A Death in Sweden | isbn13 | `''` | `None` | `None` |
| 27810589 | A Death in Sweden | original_title | `''` | `None` | `None` |
| 27810589 | A Death in Sweden | language_code | `''` | `None` | `None` |
| 27821486 | Don't You Cry | language_code | `''` | `None` | `None` |
| 27824826 | The Dry (Aaron Falk, #1) | isbn | `''` | `None` | `None` |
| 27824826 | The Dry (Aaron Falk, #1) | isbn13 | `''` | `None` | `None` |
| 27864391 | The Danish Girl | isbn | `''` | `None` | `None` |
| 27864391 | The Danish Girl | isbn13 | `''` | `None` | `None` |
| 27868677 | The House by the Lake | isbn | `''` | `None` | `None` |
| 27868677 | The House by the Lake | isbn13 | `''` | `None` | `None` |
| 27868677 | The House by the Lake | original_title | `''` | `None` | `None` |
| 2804776 | One Fifth Avenue | isbn | `''` | `None` | `None` |
| 2804776 | One Fifth Avenue | isbn13 | `''` | `None` | `None` |
| 2804776 | One Fifth Avenue | language_code | `''` | `None` | `None` |
| 280958 | Sin City: Una Dura Despedida, #1 de 3 | original_title | `''` | `None` | `None` |
| 280958 | Sin City: Una Dura Despedida, #1 de 3 | language_code | `''` | `None` | `None` |
| 281433 | Tick Tock | language_code | `''` | `None` | `None` |
| 281512 | He Chose the Nails | original_title | `''` | `None` | `None` |
| 28212 | And the Band Played On: Politics, People, and the AIDS Epidemic | language_code | `''` | `None` | `None` |
| 28233082 | The Girl In The Ice (Detective Erika Foster, #1) | isbn | `''` | `None` | `None` |
| 28233082 | The Girl In The Ice (Detective Erika Foster, #1) | isbn13 | `''` | `None` | `None` |
| 28240855 | The Girl You Lost | isbn | `''` | `None` | `None` |
| 28240855 | The Girl You Lost | isbn13 | `''` | `None` | `None` |
| 28240855 | The Girl You Lost | original_title | `''` | `None` | `None` |
| 28262024 | The Goal (Off-Campus, #4) | original_title | `''` | `None` | `None` |
| 283494 | Ironside (Modern Faerie Tales, #3) | language_code | `''` | `None` | `None` |
| 284195 | Nantucket Nights | language_code | `''` | `None` | `None` |
| 28449270 | Today Will Be Different | original_title | `''` | `None` | `None` |
| 28449270 | Today Will Be Different | language_code | `''` | `None` | `None` |
| 28477789 | Stuck-Up Suit | isbn | `''` | `None` | `None` |
| 28477789 | Stuck-Up Suit | isbn13 | `''` | `None` | `None` |
| 2854962 | Charlie Bone and the Shadow (The Children of the Red King, #7) | language_code | `''` | `None` | `None` |
| 285500 | The Declaration of Independence and The Constitution of the United States | language_code | `''` | `None` | `None` |
| 28587957 | Small Great Things | original_title | `''` | `None` | `None` |
| 2865944 | If You Give a Cat a Cupcake | language_code | `''` | `None` | `None` |
| 28678119 | Paper Princess (The Royals, #1) | isbn | `''` | `None` | `None` |
| 28678119 | Paper Princess (The Royals, #1) | isbn13 | `''` | `None` | `None` |
| 28698036 | Secret History (Mistborn, #3.5) | isbn | `''` | `None` | `None` |
| 28698036 | Secret History (Mistborn, #3.5) | isbn13 | `''` | `None` | `None` |
| 28802599 | The Light of the Fireflies | isbn | `''` | `None` | `None` |
| 28802599 | The Light of the Fireflies | isbn13 | `''` | `None` | `None` |
| 28802599 | The Light of the Fireflies | original_title | `''` | `None` | `None` |
| 28940 | Behind the Scenes at the Museum | language_code | `''` | `None` | `None` |
| 28959148 | We're All Damaged | isbn | `''` | `None` | `None` |
| 28959148 | We're All Damaged | isbn13 | `''` | `None` | `None` |
| 28959148 | We're All Damaged | original_title | `''` | `None` | `None` |
| 29034 | Twelve Angry Men | language_code | `''` | `None` | `None` |
| 29103028 | The Queen's Poisoner (Kingfountain, #1) | isbn | `''` | `None` | `None` |
| 29103028 | The Queen's Poisoner (Kingfountain, #1) | isbn13 | `''` | `None` | `None` |
| 29104680 | Punk 57 | isbn | `''` | `None` | `None` |
| 29104680 | Punk 57 | isbn13 | `''` | `None` | `None` |
| 29104680 | Punk 57 | language_code | `''` | `None` | `None` |
| 291364 | Curious George Rides a Bike | language_code | `''` | `None` | `None` |
| 2915 | The River (Brian's Saga, #2) | language_code | `''` | `None` | `None` |
| 29291 | Make Way for Ducklings | language_code | `''` | `None` | `None` |
| 29354916 | The Whistler | isbn | `''` | `None` | `None` |
| 29354916 | The Whistler | isbn13 | `''` | `None` | `None` |
| 293625 | Child of God | language_code | `''` | `None` | `None` |
| 29367958 | The Wall of Winnipeg and Me | isbn | `''` | `None` | `None` |
| 29367958 | The Wall of Winnipeg and Me | isbn13 | `''` | `None` | `None` |
| 29393 | Our Band Could Be Your Life: Scenes from the American Indie Underground 1981-1991 | language_code | `''` | `None` | `None` |
| 29430013 | The Trespasser (Dublin Murder Squad #6) | original_title | `''` | `None` | `None` |
| 29430788 | Faithful | original_title | `''` | `None` | `None` |
| 294613 | Little Bear's Friend | language_code | `''` | `None` | `None` |
| 295132 | Care of the Soul: A Guide for Cultivating Depth and Sacredness in Everyday Life | language_code | `''` | `None` | `None` |
| 29580 | Second Foundation (Foundation #3) | original_title | `''` | `None` | `None` |
| 295961 | The Eagle Has Landed (Liam Devlin, #1) | language_code | `''` | `None` | `None` |
| 29610595 | Too Late | isbn | `''` | `None` | `None` |
| 29610595 | Too Late | isbn13 | `''` | `None` | `None` |
| 29610595 | Too Late | original_title | `''` | `None` | `None` |
| 296298 | The Guns of Navarone | language_code | `''` | `None` | `None` |
| 29632984 | The Things We Wish Were True | isbn | `''` | `None` | `None` |
| 29632984 | The Things We Wish Were True | isbn13 | `''` | `None` | `None` |
| 29632984 | The Things We Wish Were True | original_title | `''` | `None` | `None` |
| 29639736 | Everything We Keep (Everything We Keep, #1) | isbn | `''` | `None` | `None` |
| 29639736 | Everything We Keep (Everything We Keep, #1) | isbn13 | `''` | `None` | `None` |
| 297135 | Summer Island | language_code | `''` | `None` | `None` |
| 29744 | Goodbye, Columbus and Five Short Stories | language_code | `''` | `None` | `None` |
| 2978 | Lost Horizon | language_code | `''` | `None` | `None` |
| 29780253 | Born a Crime: Stories From a South African Childhood | original_title | `''` | `None` | `None` |
| 29797 | The Pilgrim's Progress | original_title | `''` | `None` | `None` |
| 29797 | The Pilgrim's Progress | language_code | `''` | `None` | `None` |
| 29801 | Scott Pilgrim, Volume 2: Scott Pilgrim vs. The World | language_code | `''` | `None` | `None` |
| 29802 | Scott Pilgrim, Volume 3: Scott Pilgrim & The Infinite Sadness | language_code | `''` | `None` | `None` |
| 298137 | Mao's Last Dancer | original_title | `''` | `None` | `None` |
| 298137 | Mao's Last Dancer | language_code | `''` | `None` | `None` |
| 298230 | Agnes Grey | language_code | `''` | `None` | `None` |
| 2983489 | Why We Suck: A Feel Good Guide to Staying Fat, Loud, Lazy and Stupid | language_code | `''` | `None` | `None` |
| 298568 | Night of the Soul Stealer (The Last Apprentice / Wardstone Chronicles, #3) | language_code | `''` | `None` | `None` |
| 298663 | The Killer Inside Me | language_code | `''` | `None` | `None` |
| 298816 | Peace Child: An Unforgettable Story of Primitive Jungle Treachery in the 20th Century | language_code | `''` | `None` | `None` |
| 29925715 | The Sister | isbn | `''` | `None` | `None` |
| 29925715 | The Sister | isbn13 | `''` | `None` | `None` |
| 299384 | Sleeping Beauty: a Little Golden Book (Disney Princess) | original_title | `''` | `None` | `None` |
| 29948 | The Bridge Across Forever: A True Love Story | language_code | `''` | `None` | `None` |
| 29981261 | The Butterfly Garden (The Collector #1) | isbn | `''` | `None` | `None` |
| 29981261 | The Butterfly Garden (The Collector #1) | isbn13 | `''` | `None` | `None` |
| 29991719 | Royally Screwed (Royally, #1) | isbn | `''` | `None` | `None` |
| 29991719 | Royally Screwed (Royally, #1) | isbn13 | `''` | `None` | `None` |
| 30002998 | Two By Two | isbn | `''` | `None` | `None` |
| 30002998 | Two By Two | isbn13 | `''` | `None` | `None` |
| 300044 | Knife Edge (Noughts & Crosses, #2) | language_code | `''` | `None` | `None` |
| 30013 | Prelude to Foundation | isbn | `''` | `None` | `None` |
| 30013 | Prelude to Foundation | isbn13 | `''` | `None` | `None` |
| 300225 | Bloodline | language_code | `''` | `None` | `None` |
| 300650 | On Becoming Baby Wise: Giving Your Infant the Gift of Nighttime Sleep | language_code | `''` | `None` | `None` |
| 30065028 | Fantastic Beasts and Where to Find Them: The Original Screenplay | isbn | `''` | `None` | `None` |
| 30065028 | Fantastic Beasts and Where to Find Them: The Original Screenplay | isbn13 | `''` | `None` | `None` |
| 30071 | The Walking Dead, Book One (The Walking Dead #1-12) | original_title | `''` | `None` | `None` |
| 30122 | The Missing Piece | language_code | `''` | `None` | `None` |
| 30253700 | Anti-Stepbrother | isbn | `''` | `None` | `None` |
| 30253700 | Anti-Stepbrother | isbn13 | `''` | `None` | `None` |
| 30253700 | Anti-Stepbrother | original_title | `''` | `None` | `None` |
| 3028 | Economics in One Lesson: The Shortest & Surest Way to Understand Basic Economics | language_code | `''` | `None` | `None` |
| 303098 | Riptide | language_code | `''` | `None` | `None` |
| 30314465 | No Man's Land (John Puller, #4) | isbn | `''` | `None` | `None` |
| 30314465 | No Man's Land (John Puller, #4) | isbn13 | `''` | `None` | `None` |
| 30364931 | Neighbor Dearest | isbn | `''` | `None` | `None` |
| 30364931 | Neighbor Dearest | isbn13 | `''` | `None` | `None` |
| 30364931 | Neighbor Dearest | original_title | `''` | `None` | `None` |
| 30364931 | Neighbor Dearest | language_code | `''` | `None` | `None` |
| 304079 | The Essential Rumi | language_code | `''` | `None` | `None` |
| 3049 | Sir Gawain and the Green Knight  | language_code | `''` | `None` | `None` |
| 30512 | Paddy Clarke Ha Ha Ha | language_code | `''` | `None` | `None` |
| 306654 | Cold Sassy Tree | language_code | `''` | `None` | `None` |
| 30831912 | Norse Mythology | isbn | `''` | `None` | `None` |
| 30831912 | Norse Mythology | isbn13 | `''` | `None` | `None` |
| 30839185 | Vicious (Sinners of Saint, #1) | isbn | `''` | `None` | `None` |
| 30839185 | Vicious (Sinners of Saint, #1) | isbn13 | `''` | `None` | `None` |
| 3090465 | The Twilight Saga (Twilight, #1-4) | language_code | `''` | `None` | `None` |
| 3099780 | The Initiation / The Captive Part I (The Secret Circle, #1-2) | original_title | `''` | `None` | `None` |
| 31140847 | Bossman | isbn | `''` | `None` | `None` |
| 31140847 | Bossman | isbn13 | `''` | `None` | `None` |
| 31140847 | Bossman | original_title | `''` | `None` | `None` |
| 31168 | Shirley | language_code | `''` | `None` | `None` |
| 31176886 | The Chemist | isbn | `''` | `None` | `None` |
| 31176886 | The Chemist | isbn13 | `''` | `None` | `None` |
| 31194270 | Evelyn, After | isbn | `''` | `None` | `None` |
| 31194270 | Evelyn, After | isbn13 | `''` | `None` | `None` |
| 31231 | The Matarese Circle (Matarese #1) | language_code | `''` | `None` | `None` |
| 31266 | The Scarlatti Inheritance | language_code | `''` | `None` | `None` |
| 313256 | Dark Challenge (Dark, #5) | isbn | `''` | `None` | `None` |
| 313256 | Dark Challenge (Dark, #5) | isbn13 | `''` | `None` | `None` |
| 313256 | Dark Challenge (Dark, #5) | language_code | `''` | `None` | `None` |
| 313620 | If You Want to Walk on Water, You've Got to Get Out of the Boat | language_code | `''` | `None` | `None` |
| 31426 | The Collected Poems | language_code | `''` | `None` | `None` |
| 31493 | Standing in the Rainbow (Elmwood Springs, #2) | original_title | `''` | `None` | `None` |
| 31538647 | Hogwarts: An Incomplete and Unreliable Guide (Pottermore Presents, #3) | isbn | `''` | `None` | `None` |
| 31538647 | Hogwarts: An Incomplete and Unreliable Guide (Pottermore Presents, #3) | isbn13 | `''` | `None` | `None` |
| 315519 | Rich Man, Poor Man | language_code | `''` | `None` | `None` |
| 3157876 | Do-It-Yourself Book (Diary of a Wimpy Kid) | original_title | `''` | `None` | `None` |
| 315882 | Henry's Freedom Box: A True Story from the Underground Railroad | original_title | `''` | `None` | `None` |
| 31741 | Innocent Erendira and Other Stories | language_code | `''` | `None` | `None` |
| 31818 | The Philosophy of Andy Warhol (From A to B and Back Again) | language_code | `''` | `None` | `None` |
| 31819 | Harry Potter and Philosophy: If Aristotle Ran Hogwarts | language_code | `''` | `None` | `None` |
| 3181953 | The Heretic's Daughter | language_code | `''` | `None` | `None` |
| 318525 | Red Storm Rising | language_code | `''` | `None` | `None` |
| 318742 | The Souls of Black Folk | language_code | `''` | `None` | `None` |
| 32127 | Ina May's Guide to Childbirth | language_code | `''` | `None` | `None` |
| 321645 | Kissed by an Angel/The Power of Love/Soulmates (Kissed by an Angel, #1-3) | original_title | `''` | `None` | `None` |
| 3240691 | واحة الغروب | isbn | `''` | `None` | `None` |
| 3240691 | واحة الغروب | isbn13 | `''` | `None` | `None` |
| 32423 | Watchers | isbn | `''` | `None` | `None` |
| 32423 | Watchers | isbn13 | `''` | `None` | `None` |
| 32423 | Watchers | language_code | `''` | `None` | `None` |
| 32429 | Dragon Tears | language_code | `''` | `None` | `None` |
| 3243517 | رأيت رام الله | isbn | `''` | `None` | `None` |
| 3243517 | رأيت رام الله | isbn13 | `''` | `None` | `None` |
| 32442 | Cold Fire | language_code | `''` | `None` | `None` |
| 32445 | Strange Highways | language_code | `''` | `None` | `None` |
| 324737 | Fresh Wind, Fresh Fire: What Happens When God's Spirit Invades the Heart of His People | language_code | `''` | `None` | `None` |
| 324748 | The Dip: A Little Book That Teaches You When to Quit (and When to Stick) | language_code | `''` | `None` | `None` |
| 325128 | Kidnapped (David Balfour, #1) | language_code | `''` | `None` | `None` |
| 32527 | Alone (Detective D.D. Warren, #1) | original_title | `''` | `None` | `None` |
| 3253215 | An Illustrated Life: Drawing Inspiration From The Private Sketchbooks Of Artists, Illustrators And Designers | language_code | `''` | `None` | `None` |
| 325416 | The Voyages of Doctor Dolittle (Doctor Dolittle, #2) | language_code | `''` | `None` | `None` |
| 325421 | The Story of Doctor Dolittle (Doctor Dolittle, #1) | language_code | `''` | `None` | `None` |
| 32552 | Essential Tales and Poems | original_title | `''` | `None` | `None` |
| 32559 | The Fall of the House of Usher and Other Tales  | language_code | `''` | `None` | `None` |
| 327246 | Anatomy for the Artist | language_code | `''` | `None` | `None` |
| 327847 | The Joy of Cooking | language_code | `''` | `None` | `None` |
| 32848471 | Egomaniac | original_title | `''` | `None` | `None` |
| 32848471 | Egomaniac | language_code | `''` | `None` | `None` |
| 32929 | Goodnight Moon | original_title | `''` | `None` | `None` |
| 32987 | The Greatest Generation | language_code | `''` | `None` | `None` |
| 3301759 | The Murders in the Rue Morgue | isbn | `''` | `None` | `None` |
| 3301759 | The Murders in the Rue Morgue | isbn13 | `''` | `None` | `None` |
| 331695 | Almost French: Love and a New Life in Paris | language_code | `''` | `None` | `None` |
| 331701 | Stone Soup | language_code | `''` | `None` | `None` |
| 3320520 | The 3 Mistakes of My Life | isbn | `''` | `None` | `None` |
| 3320520 | The 3 Mistakes of My Life | isbn13 | `''` | `None` | `None` |
| 332348 | The Year of Fog | language_code | `''` | `None` | `None` |
| 33288638 | Wait for It | isbn | `''` | `None` | `None` |
| 33288638 | Wait for It | isbn13 | `''` | `None` | `None` |
| 33293 | Naked Economics: Undressing the Dismal Science | language_code | `''` | `None` | `None` |
| 3331756 | عائد إلى حيفا | isbn | `''` | `None` | `None` |
| 3331756 | عائد إلى حيفا | isbn13 | `''` | `None` | `None` |
| 33335 | The Hidden Messages in Water | language_code | `''` | `None` | `None` |
| 3338544 | رحلتي من الشك إلى الإيمان | isbn | `''` | `None` | `None` |
| 3338544 | رحلتي من الشك إلى الإيمان | isbn13 | `''` | `None` | `None` |
| 336161 | The Grouchy Ladybug | language_code | `''` | `None` | `None` |
| 337058 | Jacob Have I Loved | isbn | `''` | `None` | `None` |
| 337058 | Jacob Have I Loved | isbn13 | `''` | `None` | `None` |
| 33726 | Crazy For You | language_code | `''` | `None` | `None` |
| 337615 | Nine Parts of Desire: The Hidden World of Islamic Women | language_code | `''` | `None` | `None` |
| 33770 | Getting Over It | language_code | `''` | `None` | `None` |
| 3379 | All Families are Psychotic | language_code | `''` | `None` | `None` |
| 33808 | The Lion's Game (John Corey, #2) | language_code | `''` | `None` | `None` |
| 33813 | The Gold Coast | language_code | `''` | `None` | `None` |
| 33820 | Up Country | language_code | `''` | `None` | `None` |
| 339026 | The Akhenaten Adventure (Children of the Lamp, #1) | language_code | `''` | `None` | `None` |
| 33926 | The Girls' Guide to Hunting and Fishing | language_code | `''` | `None` | `None` |
| 34053 | Just So Stories | language_code | `''` | `None` | `None` |
| 34072 | Jimmy Corrigan, the Smartest Kid on Earth | language_code | `''` | `None` | `None` |
| 342637 | Dali: The Paintings | language_code | `''` | `None` | `None` |
| 342667 | A Total Waste of Makeup (Charlize Edwards, #1) | language_code | `''` | `None` | `None` |
| 3431 | The Five People You Meet in Heaven | language_code | `''` | `None` | `None` |
| 343614 | The Law of Attraction: The Basics of the Teachings of Abraham | language_code | `''` | `None` | `None` |
| 34451 | Eat to Live: The Revolutionary Formula for Fast and Sustained Weight Loss | language_code | `''` | `None` | `None` |
| 34511 | Monstrous Regiment (Discworld, #31; Industrial Revolution, #3) | isbn | `''` | `None` | `None` |
| 34511 | Monstrous Regiment (Discworld, #31; Industrial Revolution, #3) | isbn13 | `''` | `None` | `None` |
| 34527 | Feet of Clay (Discworld, #19; City Watch, #3) | language_code | `''` | `None` | `None` |
| 34548 | If Chins Could Kill: Confessions of a B-Movie Actor | language_code | `''` | `None` | `None` |
| 345627 | Vampire Academy (Vampire Academy, #1) | original_title | `''` | `None` | `None` |
| 347143 | The Abstinence Teacher | language_code | `''` | `None` | `None` |
| 3474186 | Forever Princess (The Princess Diaries, #10) | language_code | `''` | `None` | `None` |
| 347577 | Away Laughing on a Fast Camel (Confessions of Georgia Nicolson, #5) | language_code | `''` | `None` | `None` |
| 347656 | Don't Waste Your Life | language_code | `''` | `None` | `None` |
| 348573 | The Borrowers (The Borrowers, #1) | language_code | `''` | `None` | `None` |
| 3491072 | حول العالم في 200 يوم | isbn | `''` | `None` | `None` |
| 3491072 | حول العالم في 200 يوم | isbn13 | `''` | `None` | `None` |
| 349254 | The Lord of the Rings: The Return of the King: Visual Companion | original_publication_year | `''` | `None` | `None` |
| 349254 | The Lord of the Rings: The Return of the King: Visual Companion | original_title | `''` | `None` | `None` |
| 34988 | The Scions of Shannara (Heritage of Shannara, #1) | original_title | `''` | `None` | `None` |
| 34993 | The Sum of All Fears (Jack Ryan Universe, #7) | language_code | `''` | `None` | `None` |
| 351023 | The Worst Witch (Worst Witch, #1) | original_publication_year | `''` | `None` | `None` |
| 351023 | The Worst Witch (Worst Witch, #1) | language_code | `''` | `None` | `None` |
| 35231 | Lord of Chaos (Wheel of Time, #6) | original_title | `''` | `None` | `None` |
| 35233 | The Wheel of Time: Boxed Set #1 (Wheel of Time, #1-3) | language_code | `''` | `None` | `None` |
| 352383 | Antigone | language_code | `''` | `None` | `None` |
| 353 | Time Enough for Love | isbn | `''` | `None` | `None` |
| 353 | Time Enough for Love | isbn13 | `''` | `None` | `None` |
| 35354 | Remember Me | language_code | `''` | `None` | `None` |
| 35430 | Path of Destruction (Star Wars: Darth Bane, #1) | original_title | `''` | `None` | `None` |
| 3554772 | عزازيل | isbn | `''` | `None` | `None` |
| 3554772 | عزازيل | isbn13 | `''` | `None` | `None` |
| 356373 | Experiencing God: Knowing and Doing the Will of God, Workbook | isbn | `''` | `None` | `None` |
| 356373 | Experiencing God: Knowing and Doing the Will of God, Workbook | isbn13 | `''` | `None` | `None` |
| 356373 | Experiencing God: Knowing and Doing the Will of God, Workbook | language_code | `''` | `None` | `None` |
| 3579 | The Complete Anne of Green Gables Boxed Set (Anne of Green Gables, #1-8) | language_code | `''` | `None` | `None` |
| 3586 | The Complete Sherlock Holmes, Vol 2 | language_code | `''` | `None` | `None` |
| 36 | The Lord of the Rings: Weapons and Warfare | original_publication_year | `''` | `None` | `None` |
| 3609760 | Twilight: The Complete Illustrated Movie Companion | original_publication_year | `''` | `None` | `None` |
| 3648 | The Emperor's Children | language_code | `''` | `None` | `None` |
| 364826 | سینوهه | isbn | `''` | `None` | `None` |
| 364826 | سینوهه | isbn13 | `''` | `None` | `None` |
| 36638 | The Wolves of Willoughby Chase (The Wolves Chronicles, #1) | language_code | `''` | `None` | `None` |
| 3692091 | 1/4 جرام | isbn | `''` | `None` | `None` |
| 3692091 | 1/4 جرام | isbn13 | `''` | `None` | `None` |
| 3698601 | Food Matters: A Guide to Conscious Eating with More Than 75 Recipes | language_code | `''` | `None` | `None` |
| 370057 | The Truth Seeker (O'Malley #3) | language_code | `''` | `None` | `None` |
| 374233 | If on a Winter's Night a Traveler | isbn | `''` | `None` | `None` |
| 374233 | If on a Winter's Night a Traveler | isbn13 | `''` | `None` | `None` |
| 37426 | Little Children | language_code | `''` | `None` | `None` |
| 3754026 | Beyond the Shadows (Night Angel, #3) | original_title | `''` | `None` | `None` |
| 380975 | K is for Killer (Kinsey Millhone, #11) | language_code | `''` | `None` | `None` |
| 380976 | P is for Peril (Kinsey Millhone, #16) | language_code | `''` | `None` | `None` |
| 381421 | Jesus Calling: Enjoying Peace in His Presence | original_title | `''` | `None` | `None` |
| 381421 | Jesus Calling: Enjoying Peace in His Presence | language_code | `''` | `None` | `None` |
| 381787 | Truth Will Prevail (The Work and the Glory, #3) | language_code | `''` | `None` | `None` |
| 3819326 | Angels' Blood (Guild Hunter, #1) | original_title | `''` | `None` | `None` |
| 3831279 | ڤيرتيجو | isbn | `''` | `None` | `None` |
| 3831279 | ڤيرتيجو | isbn13 | `''` | `None` | `None` |
| 38501 | Ham on Rye | language_code | `''` | `None` | `None` |
| 38505 | Hollywood | language_code | `''` | `None` | `None` |
| 386142 | Legally Blonde | language_code | `''` | `None` | `None` |
| 3882 | Rachael Ray 365: No Repeats: A Year of Deliciously Different Dinners | language_code | `''` | `None` | `None` |
| 3885 | The Taste of Home Cookbook | language_code | `''` | `None` | `None` |
| 3888 | The America's Test Kitchen Family Cookbook | language_code | `''` | `None` | `None` |
| 38990 | Fun Home: A Family Tragicomic | original_title | `''` | `None` | `None` |
| 39032 | Mount Dragon | language_code | `''` | `None` | `None` |
| 392431 | Damaged: The Heartbreaking True Story of a Forgotten Child | language_code | `''` | `None` | `None` |
| 393145 | The Riddle (The Books of Pellinor, #2) | original_title | `''` | `None` | `None` |
| 394772 | The Mixed-Up Chameleon | language_code | `''` | `None` | `None` |
| 394841 | Travel Team | language_code | `''` | `None` | `None` |
| 39542 | How to Be a Domestic Goddess: Baking and the Art of Comfort Cooking | language_code | `''` | `None` | `None` |
| 396266 | The Winter Rose (The Tea Rose, #2) | language_code | `''` | `None` | `None` |
| 3975186 | True Colors | language_code | `''` | `None` | `None` |
| 397860 | The Fog | language_code | `''` | `None` | `None` |
| 39916 | Epileptic | original_title | `''` | `None` | `None` |
| 3992598 | The Demigod Files (Percy Jackson and the Olympians) | original_title | `''` | `None` | `None` |
| 39933 | How to Read Literature Like a Professor: A Lively and Entertaining Guide to Reading Between the Lines | original_title | `''` | `None` | `None` |
| 4005310 | Why Evolution Is True | language_code | `''` | `None` | `None` |
| 40136 | The Nasty Bits: Collected Varietal Cuts, Usable Trim, Scraps, and Bones | language_code | `''` | `None` | `None` |
| 40158 | The Queen of Attolia (The Queen's Thief, #2) | language_code | `''` | `None` | `None` |
| 401679 | Llama Llama Red Pajama | language_code | `''` | `None` | `None` |
| 40168 | The Creative License: Giving Yourself Permission to Be The Artist You Truly Are | language_code | `''` | `None` | `None` |
| 40173 | Are You There, Vodka? It's Me, Chelsea | language_code | `''` | `None` | `None` |
| 402014 | On the Bright Side, I'm Now the Girlfriend of a Sex God (Confessions of Georgia Nicolson, #2) | language_code | `''` | `None` | `None` |
| 402017 | The Cake Mix Doctor | language_code | `''` | `None` | `None` |
| 4031 | Lunar Park | language_code | `''` | `None` | `None` |
| 404223 | The Wounded Land (The Second Chronicles of Thomas Covenant, #1) | language_code | `''` | `None` | `None` |
| 404562 | Henry & Ramona | language_code | `''` | `None` | `None` |
| 40465 | Thank You for Smoking | language_code | `''` | `None` | `None` |
| 40470 | Cities of the Plain (The Border Trilogy, #3) | language_code | `''` | `None` | `None` |
| 40471 | Outer Dark | language_code | `''` | `None` | `None` |
| 40722 | The Sportswriter | language_code | `''` | `None` | `None` |
| 4076 | In Search of Excellence: Lessons from America's Best-Run Companies | language_code | `''` | `None` | `None` |
| 407813 | The Blue Sword (Damar, #1) | original_title | `''` | `None` | `None` |
| 407813 | The Blue Sword (Damar, #1) | language_code | `''` | `None` | `None` |
| 407999 | Competitive Strategy: Techniques for Analyzing Industries and Competitors | language_code | `''` | `None` | `None` |
| 4110198 | The 8th Confession (Women's Murder Club, #8) | language_code | `''` | `None` | `None` |
| 411053 | Better Homes and Gardens New Cook Book   | language_code | `''` | `None` | `None` |
| 417780 | Why Mosquitoes Buzz in People's Ears | language_code | `''` | `None` | `None` |
| 419083 | Killing Pablo: The Hunt for the World's Greatest Outlaw | language_code | `''` | `None` | `None` |
| 41950 | Quentins | language_code | `''` | `None` | `None` |
| 420278 | The Complete Poems 1927-1979 | original_title | `''` | `None` | `None` |
| 42058 | Richard III | language_code | `''` | `None` | `None` |
| 4212386 | Maryamah Karpov: Mimpi-mimpi Lintang (Tetralogi Laskar Pelangi, #4) | isbn | `''` | `None` | `None` |
| 4212386 | Maryamah Karpov: Mimpi-mimpi Lintang (Tetralogi Laskar Pelangi, #4) | isbn13 | `''` | `None` | `None` |
| 4214 | Life of Pi | language_code | `''` | `None` | `None` |
| 424 | Slouching Towards Bethlehem | language_code | `''` | `None` | `None` |
| 42435 | In Harm's Way: The Sinking of the U.S.S. Indianapolis and the Extraordinary Story of Its Survivors | language_code | `''` | `None` | `None` |
| 425029 | Presumed Innocent | language_code | `''` | `None` | `None` |
| 425124 | Sacred (Kenzie & Gennaro, #3) | language_code | `''` | `None` | `None` |
| 426625 | Fancy Nancy | language_code | `''` | `None` | `None` |
| 4268 | How to Be Good | language_code | `''` | `None` | `None` |
| 42696 | Trinity | language_code | `''` | `None` | `None` |
| 428862 | Wreck This Journal | language_code | `''` | `None` | `None` |
| 429024 | The Old Curiosity Shop | language_code | `''` | `None` | `None` |
| 42909 | All Things Wise and Wonderful | language_code | `''` | `None` | `None` |
| 43325 | Nothing Lasts Forever | isbn | `''` | `None` | `None` |
| 43325 | Nothing Lasts Forever | isbn13 | `''` | `None` | `None` |
| 43339 | Where Are the Children? | language_code | `''` | `None` | `None` |
| 434229 | Cape Fear | isbn | `''` | `None` | `None` |
| 434229 | Cape Fear | isbn13 | `''` | `None` | `None` |
| 434229 | Cape Fear | language_code | `''` | `None` | `None` |
| 437885 | Frosty the Snowman (Frosty the Snowman) | language_code | `''` | `None` | `None` |
| 43797 | Pandora / Vittorio the Vampire (New Tales of the Vampires) | language_code | `''` | `None` | `None` |
| 438024 | Let's Pretend This Never Happened (Dear Dumb Diary #1) | language_code | `''` | `None` | `None` |
| 43805 | Servant of the Bones | language_code | `''` | `None` | `None` |
| 43884 | Phantom (Sword of Truth, #10) | language_code | `''` | `None` | `None` |
| 43917 | Rise of a Merchant Prince (The Serpentwar Saga, #2) | language_code | `''` | `None` | `None` |
| 43944 | Suite Française | language_code | `''` | `None` | `None` |
| 43945 | Portnoy's Complaint | language_code | `''` | `None` | `None` |
| 441618 | Breaking Free: Discover the Victory of Total Surrender | language_code | `''` | `None` | `None` |
| 44361 | Velvet Elvis: Repainting the Christian Faith | language_code | `''` | `None` | `None` |
| 44688 | Magician's Gambit (The Belgariad, #3) | language_code | `''` | `None` | `None` |
| 44796 | The Moon and Sixpence | language_code | `''` | `None` | `None` |
| 4499669 | The Love Dare | original_title | `''` | `None` | `None` |
| 4502877 | Midnight Sun (Twilight, #1.5) | isbn | `''` | `None` | `None` |
| 4502877 | Midnight Sun (Twilight, #1.5) | isbn13 | `''` | `None` | `None` |
| 4507 | Sickened: The Memoir of a Munchausen by Proxy Childhood | language_code | `''` | `None` | `None` |
| 450836 | Like a Fire Burning (The Work and the Glory, #2) | language_code | `''` | `None` | `None` |
| 45108 | Fool's Fate (Tawny Man, #3) | language_code | `''` | `None` | `None` |
| 45110 | Shaman's Crossing (Soldier Son, #1) | language_code | `''` | `None` | `None` |
| 452157 | The Road to the Dark Tower: Exploring Stephen King's Magnum Opus | language_code | `''` | `None` | `None` |
| 45260 | The Naked God (Night's Dawn, #3) | language_code | `''` | `None` | `None` |
| 4527502 | The Scarecrow (Jack McEvoy, #2) | isbn | `''` | `None` | `None` |
| 4527502 | The Scarecrow (Jack McEvoy, #2) | isbn13 | `''` | `None` | `None` |
| 4538 | The View from Saturday | language_code | `''` | `None` | `None` |
| 454236 | Miracle in the Andes | language_code | `''` | `None` | `None` |
| 455764 | Audrey Rose | language_code | `''` | `None` | `None` |
| 4566934 | Winter in Tokyo | isbn | `''` | `None` | `None` |
| 4566934 | Winter in Tokyo | isbn13 | `''` | `None` | `None` |
| 457457 | Fine Things | language_code | `''` | `None` | `None` |
| 45760 | Girl With Curious Hair | language_code | `''` | `None` | `None` |
| 458034 | Caressed by Ice (Psy-Changeling #3) | original_title | `''` | `None` | `None` |
| 460717 | The Dogs of War | language_code | `''` | `None` | `None` |
| 4618728 | Honolulu | language_code | `''` | `None` | `None` |
| 46191 | Why Men Love Bitches: From Doormat to Dreamgirl—A Woman's Guide to Holding Her Own in a Relationship | language_code | `''` | `None` | `None` |
| 46201 | The Selected Poetry of Rainer Maria Rilke | original_title | `''` | `None` | `None` |
| 4633 | Islands in the Stream | language_code | `''` | `None` | `None` |
| 4634266 | NARUTO -ナルト- 巻ノ四十三 | isbn | `''` | `None` | `None` |
| 4634266 | NARUTO -ナルト- 巻ノ四十三 | isbn13 | `''` | `None` | `None` |
| 46460 | Call for the Dead | language_code | `''` | `None` | `None` |
| 4652 | In Our Time | language_code | `''` | `None` | `None` |
| 4653511 | رجال في الشمس | isbn | `''` | `None` | `None` |
| 4653511 | رجال في الشمس | isbn13 | `''` | `None` | `None` |
| 4657 | The Water-Method Man | language_code | `''` | `None` | `None` |
| 4659 | A Widow for One Year | language_code | `''` | `None` | `None` |
| 465904 | Dragonsdawn (Pern, #9) | language_code | `''` | `None` | `None` |
| 46676 | When Bad Things Happen to Good People | language_code | `''` | `None` | `None` |
| 46913 | FRUiTS | original_title | `''` | `None` | `None` |
| 4708 | The Beautiful and Damned | language_code | `''` | `None` | `None` |
| 47520 | Castle in the Air (Howl's Moving Castle, #2) | language_code | `''` | `None` | `None` |
| 47620 | Grim Tuesday (The Keys to the Kingdom, #2) | language_code | `''` | `None` | `None` |
| 47881 | Charlie Bone and the Hidden King (The Children of the Red King, #5) | language_code | `''` | `None` | `None` |
| 478894 | The Sword of Shannara Trilogy (Shannara, #1-3) | language_code | `''` | `None` | `None` |
| 47922 | Because I'm Worth It (Gossip Girl, #4) | language_code | `''` | `None` | `None` |
| 47959 | Queen of the Darkness (The Black Jewels, #3) | language_code | `''` | `None` | `None` |
| 48019 | The Effective Executive: The Definitive Guide to Getting the Right Things Done (Harperbusiness Essentials) | language_code | `''` | `None` | `None` |
| 481749 | Jesus the Christ | language_code | `''` | `None` | `None` |
| 4837112 | Percy Jackson and the Sword of Hades (Percy Jackson and the Olympians, #4.5) | language_code | `''` | `None` | `None` |
| 48464 | A Good Man is Hard to Find and Other Stories | language_code | `''` | `None` | `None` |
| 4865 | How to Win Friends and Influence People | isbn | `''` | `None` | `None` |
| 4865 | How to Win Friends and Influence People | isbn13 | `''` | `None` | `None` |
| 487445 | The Onion Field | language_code | `''` | `None` | `None` |
| 48811 | Nancy Drew: #1-64 | original_publication_year | `''` | `None` | `None` |
| 4898 | Blue Ocean Strategy: How To Create Uncontested Market Space And Make The Competition Irrelevant | language_code | `''` | `None` | `None` |
| 49006 | The Darkest Hour (Warriors, #6) | original_title | `''` | `None` | `None` |
| 4902793 | Sookie Stackhouse 7-copy Boxed Set (Sookie Stackhouse, #1-7) | language_code | `''` | `None` | `None` |
| 491735 | The Dirty Girls Social Club (Dirty Girls, #1) | language_code | `''` | `None` | `None` |
| 49245 | His Needs, Her Needs: Building an Affair-Proof Marriage | isbn | `''` | `None` | `None` |
| 49245 | His Needs, Her Needs: Building an Affair-Proof Marriage | isbn13 | `''` | `None` | `None` |
| 49251 | Citizen Soldiers: The U. S. Army from the Normandy Beaches to the Bulge to the Surrender of Germany | language_code | `''` | `None` | `None` |
| 493455 | The Uglies Trilogy (Uglies, #1-3) | language_code | `''` | `None` | `None` |
| 49455 | Notes from Underground | original_title | `''` | `None` | `None` |
| 49552 | The Stranger | isbn | `''` | `None` | `None` |
| 49552 | The Stranger | isbn13 | `''` | `None` | `None` |
| 497164 | Camera Lucida: Reflections on Photography | language_code | `''` | `None` | `None` |
| 497199 | Factotum | language_code | `''` | `None` | `None` |
| 498641 | The Practice of the Presence of God | language_code | `''` | `None` | `None` |
| 50001 | The Complete Guide to Middle-Earth | language_code | `''` | `None` | `None` |
| 502406 | Curious George Takes a Job | language_code | `''` | `None` | `None` |
| 5031805 | ESV Study Bible | original_title | `''` | `None` | `None` |
| 5048174 | 2BR02B | isbn | `''` | `None` | `None` |
| 5048174 | 2BR02B | isbn13 | `''` | `None` | `None` |
| 5052 | Code to Zero | language_code | `''` | `None` | `None` |
| 5061675 | A Game of Thrones / A Clash of Kings (A Song of Ice and Fire, #1-2) | isbn | `''` | `None` | `None` |
| 5061675 | A Game of Thrones / A Clash of Kings (A Song of Ice and Fire, #1-2) | isbn13 | `''` | `None` | `None` |
| 5061675 | A Game of Thrones / A Clash of Kings (A Song of Ice and Fire, #1-2) | language_code | `''` | `None` | `None` |
| 5068 | Last Orders | language_code | `''` | `None` | `None` |
| 50750 | You Slay Me (Aisling Grey #1) | original_title | `''` | `None` | `None` |
| 508413 | The Shunning (The Heritage of Lancaster County, #1) | language_code | `''` | `None` | `None` |
| 5103512 | Martha Stewart's Cupcakes: 175 Inspired Ideas for Everyone's Favorite Treat | language_code | `''` | `None` | `None` |
| 512475 | The Cradle Will Fall | language_code | `''` | `None` | `None` |
| 51370 | Leading Change | original_title | `''` | `None` | `None` |
| 51370 | Leading Change | language_code | `''` | `None` | `None` |
| 514313 | Bringing Down the House: The Inside Story of Six M.I.T. Students Who Took Vegas for Millions | language_code | `''` | `None` | `None` |
| 5153799 | Father Mine (Black Dagger Brotherhood, #6.5) | isbn | `''` | `None` | `None` |
| 5153799 | Father Mine (Black Dagger Brotherhood, #6.5) | isbn13 | `''` | `None` | `None` |
| 5153799 | Father Mine (Black Dagger Brotherhood, #6.5) | original_title | `''` | `None` | `None` |
| 5171894 | The Doomsday Key (Sigma Force, #6) | original_publication_year | `''` | `None` | `None` |
| 5171894 | The Doomsday Key (Sigma Force, #6) | original_title | `''` | `None` | `None` |
| 5181 | Jewel | language_code | `''` | `None` | `None` |
| 5198 | Paradise | original_title | `''` | `None` | `None` |
| 519933 | The Lives of Christopher Chant (Chrestomanci, #2) | language_code | `''` | `None` | `None` |
| 5206937 | A Modest Proposal | language_code | `''` | `None` | `None` |
| 520738 | On Ugliness | language_code | `''` | `None` | `None` |
| 52309 | The Autobiography of Benjamin Franklin | original_title | `''` | `None` | `None` |
| 527862 | The Acid House | language_code | `''` | `None` | `None` |
| 5292173 | Relentless (The Lost Fleet, #5) | language_code | `''` | `None` | `None` |
| 5295735 | الحرافيش | isbn | `''` | `None` | `None` |
| 5295735 | الحرافيش | isbn13 | `''` | `None` | `None` |
| 529626 | Sometimes a Great Notion | language_code | `''` | `None` | `None` |
| 530793 | The Wives of Henry VIII | language_code | `''` | `None` | `None` |
| 531421 | Bella Tuscany | language_code | `''` | `None` | `None` |
| 53168 | Demon Thief (The Demonata, #2) | language_code | `''` | `None` | `None` |
| 531989 | Drown | language_code | `''` | `None` | `None` |
| 5326 | A Christmas Carol | language_code | `''` | `None` | `None` |
| 533675 | Pinocchio | language_code | `''` | `None` | `None` |
| 5348 | The Testament | language_code | `''` | `None` | `None` |
| 5350 | The Partner | language_code | `''` | `None` | `None` |
| 5354 | The Brethren | language_code | `''` | `None` | `None` |
| 535494 | How Should We Then Live? The Rise and Decline of Western Thought and Culture | language_code | `''` | `None` | `None` |
| 536790 | Trumps of Doom (The Chronicles of Amber, #6) | isbn | `''` | `None` | `None` |
| 536790 | Trumps of Doom (The Chronicles of Amber, #6) | isbn13 | `''` | `None` | `None` |
| 5369 | The Amber Room | language_code | `''` | `None` | `None` |
| 537070 | Gregor and the Code of Claw (Underland Chronicles, #5) | language_code | `''` | `None` | `None` |
| 537094 | The Overcoat | language_code | `''` | `None` | `None` |
| 541341 | Deep and Dark and Dangerous (A Ghost Story) | language_code | `''` | `None` | `None` |
| 542639 | The Shock of the New | language_code | `''` | `None` | `None` |
| 543086 | Tom's Midnight Garden | language_code | `''` | `None` | `None` |
| 543505 | The Tale of Mrs. Tiggy-Winkle | language_code | `''` | `None` | `None` |
| 54539 | Silas Marner | language_code | `''` | `None` | `None` |
| 5508 | Anne Frank: Beyond the Diary - A Photographic Remembrance | language_code | `''` | `None` | `None` |
| 5517 | A Raisin in the Sun | language_code | `''` | `None` | `None` |
| 55229 | April 1865: The Month That Saved America | language_code | `''` | `None` | `None` |
| 554674 | The Story of the Trapp Family Singers | language_code | `''` | `None` | `None` |
| 5552 | QED: The Strange Theory of Light and Matter | language_code | `''` | `None` | `None` |
| 5557442 | ظل الأفعى | isbn | `''` | `None` | `None` |
| 5557442 | ظل الأفعى | isbn13 | `''` | `None` | `None` |
| 556629 | The Holiness of God | language_code | `''` | `None` | `None` |
| 5607622 | قمر على سمرقند | isbn | `''` | `None` | `None` |
| 5607622 | قمر على سمرقند | isbn13 | `''` | `None` | `None` |
| 56157 | The Proper Care and Feeding of Husbands | language_code | `''` | `None` | `None` |
| 5628753 | Branded by Fire (Psy-Changeling #6) | original_title | `''` | `None` | `None` |
| 563887 | The Littles | language_code | `''` | `None` | `None` |
| 56405 | Love and Respect: The Love She Most Desires; The Respect He Desperately Needs | original_title | `''` | `None` | `None` |
| 56405 | Love and Respect: The Love She Most Desires; The Respect He Desperately Needs | language_code | `''` | `None` | `None` |
| 56452 | Now, Discover Your Strengths | language_code | `''` | `None` | `None` |
| 56465 | The Gift of Fear: Survival Signals That Protect Us from Violence | language_code | `''` | `None` | `None` |
| 56480 | Passion and Purity: Learning to Bring Your Love Life Under Christ's Control | language_code | `''` | `None` | `None` |
| 5664022 | حوار مع صديقي الملحد | isbn | `''` | `None` | `None` |
| 5664022 | حوار مع صديقي الملحد | isbn13 | `''` | `None` | `None` |
| 5664022 | حوار مع صديقي الملحد | original_title | `''` | `None` | `None` |
| 56674 | Empire of the Sun (Empire of the Sun, #1) | isbn | `''` | `None` | `None` |
| 56674 | Empire of the Sun (Empire of the Sun, #1) | isbn13 | `''` | `None` | `None` |
| 56674 | Empire of the Sun (Empire of the Sun, #1) | language_code | `''` | `None` | `None` |
| 567616 | The Art Book | original_title | `''` | `None` | `None` |
| 5697 | The Complete Short Novels | original_title | `''` | `None` | `None` |
| 57605 | Pat the Bunny | language_code | `''` | `None` | `None` |
| 576570 | The Princess and the Pea | language_code | `''` | `None` | `None` |
| 5771014 | The Talent Code: Unlocking the Secret of Skill in Sports, Art, Music, Math, and Just About Everything Else | language_code | `''` | `None` | `None` |
| 577542 | Rikki-Tikki-Tavi | language_code | `''` | `None` | `None` |
| 579143 | Scuffy the Tugboat (Big Little Golden Book) | language_code | `''` | `None` | `None` |
| 58077 | Grave Sight (Harper Connelly, #1) | original_title | `''` | `None` | `None` |
| 581125 | The Minority Report | language_code | `''` | `None` | `None` |
| 581552 | In the Penal Colony | isbn | `''` | `None` | `None` |
| 581552 | In the Penal Colony | isbn13 | `''` | `None` | `None` |
| 58547 | Journals | language_code | `''` | `None` | `None` |
| 58728 | Anne Frank's Tales from the Secret Annex | language_code | `''` | `None` | `None` |
| 5883777 | The Holy Bible: English Standard Version | isbn | `''` | `None` | `None` |
| 5883777 | The Holy Bible: English Standard Version | isbn13 | `''` | `None` | `None` |
| 590552 | Chicken Soup with Rice: A Book of Months (The Nutshell Library) | language_code | `''` | `None` | `None` |
| 594361 | The Lion King: A little Golden Book | language_code | `''` | `None` | `None` |
| 5946 | In the Skin of a Lion | language_code | `''` | `None` | `None` |
| 595822 | The Protector (O'Malley #4) | original_title | `''` | `None` | `None` |
| 596259 | Standing for Something: 10 Neglected Virtues That Will Heal Our Hearts and Homes | language_code | `''` | `None` | `None` |
| 59882 | Accident | original_title | `''` | `None` | `None` |
| 59882 | Accident | language_code | `''` | `None` | `None` |
| 59889 | Safe Harbour | language_code | `''` | `None` | `None` |
| 59978 | Sin City, Vol. 4: That Yellow Bastard (Sin City, #4) | isbn | `''` | `None` | `None` |
| 59978 | Sin City, Vol. 4: That Yellow Bastard (Sin City, #4) | isbn13 | `''` | `None` | `None` |
| 6023056 | Act Like a Lady, Think Like a Man: What Men Really Think About Love, Relationships, Intimacy, and Commitment | language_code | `''` | `None` | `None` |
| 60431 | Andy Goldsworthy: A Collaboration with Nature | language_code | `''` | `None` | `None` |
| 6054190 | Dune Road | original_publication_year | `''` | `None` | `None` |
| 6054190 | Dune Road | original_title | `''` | `None` | `None` |
| 60551 | The Book on the Taboo Against Knowing Who You Are | language_code | `''` | `None` | `None` |
| 606818 | Holy Blood, Holy Grail | isbn | `''` | `None` | `None` |
| 606818 | Holy Blood, Holy Grail | isbn13 | `''` | `None` | `None` |
| 6080822 | The Castaways | language_code | `''` | `None` | `None` |
| 60935 | Possessing the Secret of Joy | language_code | `''` | `None` | `None` |
| 6131786 | The Virgin Cure | language_code | `''` | `None` | `None` |
| 6145711 | The Walking Dead, Vol. 10: What We Become | isbn | `''` | `None` | `None` |
| 6145711 | The Walking Dead, Vol. 10: What We Become | isbn13 | `''` | `None` | `None` |
| 616318 | Justice, Volume 1 | original_title | `''` | `None` | `None` |
| 6164358 | The Mysterious Benedict Society and the Prisoner's Dilemma (The Mysterious Benedict Society, #3) | language_code | `''` | `None` | `None` |
| 61665 | Billions & Billions: Thoughts on Life and Death at the Brink of the Millennium | language_code | `''` | `None` | `None` |
| 616678 | The Diamond Throne (The Elenium, #1) | language_code | `''` | `None` | `None` |
| 6167746 | Marked / Betrayed / Chosen / Untamed (House of Night, #1-4) | original_title | `''` | `None` | `None` |
| 61905 | Barrayar (Vorkosigan Saga, #7) | original_title | `''` | `None` | `None` |
| 61915 | Falling Free (Vorkosigan Saga, #4) | isbn | `''` | `None` | `None` |
| 61915 | Falling Free (Vorkosigan Saga, #4) | isbn13 | `''` | `None` | `None` |
| 6193 | Life and Times of Michael K | language_code | `''` | `None` | `None` |
| 61938 | The Rowan (The Tower and the Hive, #1) | original_title | `''` | `None` | `None` |
| 61942 | The Dragonriders of Pern (Dragonriders of Pern, #1-3) | language_code | `''` | `None` | `None` |
| 621 | The Automatic Millionaire: A Powerful One-Step Plan to Live and Finish Rich | language_code | `''` | `None` | `None` |
| 621739 | Millions of Cats | language_code | `''` | `None` | `None` |
| 62479 | Servant of the Shard (Forgotten Realms: Paths of Darkness, #3; The Sellswords, #1) | original_title | `''` | `None` | `None` |
| 6251012 | UR | isbn | `''` | `None` | `None` |
| 6251012 | UR | isbn13 | `''` | `None` | `None` |
| 625554 | Pillar of Light (The Work and the Glory, #1) | language_code | `''` | `None` | `None` |
| 6324090 | Alice's Adventures in Wonderland | isbn | `''` | `None` | `None` |
| 6324090 | Alice's Adventures in Wonderland | isbn13 | `''` | `None` | `None` |
| 6324090 | Alice's Adventures in Wonderland | original_title | `''` | `None` | `None` |
| 6328 | Revolting Rhymes | language_code | `''` | `None` | `None` |
| 6332526 | Inside of a Dog: What Dogs See, Smell, and Know | original_title | `''` | `None` | `None` |
| 633270 | The Ear, the Eye, and the Arm | language_code | `''` | `None` | `None` |
| 6339989 | Vampire Academy Collection (Vampire Academy, #1-3) | language_code | `''` | `None` | `None` |
| 63432 | 3001: The Final Odyssey (Space Odyssey, #4) | language_code | `''` | `None` | `None` |
| 6344097 | The Stand: Captain Trips | original_title | `''` | `None` | `None` |
| 6344534 | The Second Ship (The Rho Agenda, #1) | language_code | `''` | `None` | `None` |
| 6351910 | Dynasty of Evil (Star Wars: Darth Bane, #3) | original_title | `''` | `None` | `None` |
| 6357022 | Club Shadowlands (Masters of the Shadowlands, #1) | isbn | `''` | `None` | `None` |
| 6357022 | Club Shadowlands (Masters of the Shadowlands, #1) | isbn13 | `''` | `None` | `None` |
| 6361871 | The Pioneer Woman Cooks: Recipes from an Accidental Country Girl | language_code | `''` | `None` | `None` |
| 63832 | Blue Highways | language_code | `''` | `None` | `None` |
| 6387565 | Witch & Wizard (Witch & Wizard, #1) | isbn | `''` | `None` | `None` |
| 6387565 | Witch & Wizard (Witch & Wizard, #1) | isbn13 | `''` | `None` | `None` |
| 6388558 | The Warlord Wants Forever (Immortals After Dark #1) | isbn | `''` | `None` | `None` |
| 6388558 | The Warlord Wants Forever (Immortals After Dark #1) | isbn13 | `''` | `None` | `None` |
| 6393047 | The Viper's Nest (39 Clues, #7) | original_title | `''` | `None` | `None` |
| 6393082 | Ender's Game, Volume 1: Battle School (Ender's Saga) | original_title | `''` | `None` | `None` |
| 6395833 | Guts | isbn | `''` | `None` | `None` |
| 6395833 | Guts | isbn13 | `''` | `None` | `None` |
| 64081 | The Irresistible Revolution: Living as an Ordinary Radical | language_code | `''` | `None` | `None` |
| 6421588 | Hourglass (Evernight, #3) | original_title | `''` | `None` | `None` |
| 643301 | Angels and Demons / The Da Vinci Code (Robert Langdon, #1-2) | original_title | `''` | `None` | `None` |
| 643301 | Angels and Demons / The Da Vinci Code (Robert Langdon, #1-2) | language_code | `''` | `None` | `None` |
| 643962 | L is for Lawless (Kinsey Millhone, #12) | language_code | `''` | `None` | `None` |
| 6443349 | Percy Jackson and the Olympians Boxed Set (Percy Jackson and the Olympians, #1-5) | language_code | `''` | `None` | `None` |
| 6452796 | Drive: The Surprising Truth About What Motivates Us | language_code | `''` | `None` | `None` |
| 646056 | The Little Mermaid | language_code | `''` | `None` | `None` |
| 646462 | The Qur'an / القرآن الكريم | isbn | `''` | `None` | `None` |
| 646462 | The Qur'an / القرآن الكريم | isbn13 | `''` | `None` | `None` |
| 64860 | E is for Evidence (Kinsey Millhone, #5) | language_code | `''` | `None` | `None` |
| 6486483 | Emotional Intelligence 2.0 | language_code | `''` | `None` | `None` |
| 6488483 | The Walking Dead, Vol. 11: Fear the Hunters | language_code | `''` | `None` | `None` |
| 64955 | Midnight | language_code | `''` | `None` | `None` |
| 6506085 | Food Inc.: A Participant Guide: How Industrial Food is Making Us Sicker, Fatter, and Poorer-And What You Can Do About It | isbn | `''` | `None` | `None` |
| 6506085 | Food Inc.: A Participant Guide: How Industrial Food is Making Us Sicker, Fatter, and Poorer-And What You Can Do About It | isbn13 | `''` | `None` | `None` |
| 6512154 | Zeitoun | language_code | `''` | `None` | `None` |
| 651260 | Domes of Fire (The Tamuli, #1) | language_code | `''` | `None` | `None` |
| 6515834 | Forgotten God: Reversing Our Tragic Neglect of the Holy Spirit | language_code | `''` | `None` | `None` |
| 6520 | My Friend Leonard | language_code | `''` | `None` | `None` |
| 6532496 | Not My Daughter | language_code | `''` | `None` | `None` |
| 65336 | Selected Poems | language_code | `''` | `None` | `None` |
| 653559 | Sherlock Holmes and the Case of the Hound of the Baskervilles (Illustrated Classic Editions) | original_title | `''` | `None` | `None` |
| 6554 | Darkness | language_code | `''` | `None` | `None` |
| 6582637 | Archangel's Kiss (Guild Hunter, #2) | original_title | `''` | `None` | `None` |
| 65840 | Anne of Windy Poplars (Anne of Green Gables, #4) | language_code | `''` | `None` | `None` |
| 6596 | The Four Agreements: A Practical Guide to Personal Freedom | language_code | `''` | `None` | `None` |
| 6600807 | Jealousy (Strange Angels, #3) | language_code | `''` | `None` | `None` |
| 6604887 | أنت لي | isbn | `''` | `None` | `None` |
| 6604887 | أنت لي | isbn13 | `''` | `None` | `None` |
| 6609490 | Night World: The Ultimate Fan Guide | language_code | `''` | `None` | `None` |
| 6609549 | By the Time You Read This, I'll Be Dead | language_code | `''` | `None` | `None` |
| 6613 | Four Blondes | language_code | `''` | `None` | `None` |
| 6614886 | زغازيغ | isbn | `''` | `None` | `None` |
| 6614886 | زغازيغ | isbn13 | `''` | `None` | `None` |
| 6614886 | زغازيغ | original_publication_year | `''` | `None` | `None` |
| 6614886 | زغازيغ | original_title | `''` | `None` | `None` |
| 6621143 | Something Like Fate | language_code | `''` | `None` | `None` |
| 6621287 | com نسيان | isbn | `''` | `None` | `None` |
| 6621287 | com نسيان | isbn13 | `''` | `None` | `None` |
| 6630751 | First to Kill (Nathan McBride, #1) | isbn | `''` | `None` | `None` |
| 6630751 | First to Kill (Nathan McBride, #1) | isbn13 | `''` | `None` | `None` |
| 66655 | Necroscope (Necroscope, #1) | language_code | `''` | `None` | `None` |
| 6667514 | The Checklist Manifesto: How to Get Things Right | language_code | `''` | `None` | `None` |
| 6670 | The Magic Finger (Young Puffin Developing Reader) | original_title | `''` | `None` | `None` |
| 6681333 | Eleventh Grade Burns (The Chronicles of Vladimir Tod, #4) | language_code | `''` | `None` | `None` |
| 6681454 | Caught | language_code | `''` | `None` | `None` |
| 6686671 | Electric Daisy, Vol. 1 (Dengeki Daisy, #1) | isbn | `''` | `None` | `None` |
| 6686671 | Electric Daisy, Vol. 1 (Dengeki Daisy, #1) | isbn13 | `''` | `None` | `None` |
| 6687 | Charlie and the Great Glass Elevator (Charlie Bucket, #2) | language_code | `''` | `None` | `None` |
| 668710 | Magic and Other Misdemeanors (The Sisters Grimm, #5) | language_code | `''` | `None` | `None` |
| 6688121 | Negeri 5 Menara (Negeri 5 Menara, #1) | isbn | `''` | `None` | `None` |
| 6688121 | Negeri 5 Menara (Negeri 5 Menara, #1) | isbn13 | `''` | `None` | `None` |
| 6690 | Danny the Champion of the World | language_code | `''` | `None` | `None` |
| 6692041 | Mornings in Jenin | language_code | `''` | `None` | `None` |
| 6694937 | Game Change: Obama and the Clintons, McCain and Palin, and the Race of a Lifetime | language_code | `''` | `None` | `None` |
| 6696465 | Finally (Willow Falls, #2) | language_code | `''` | `None` | `None` |
| 6697 | Little Altars Everywhere | language_code | `''` | `None` | `None` |
| 6709 | Practicing the Power of Now: Essential Teachings, Meditations, and Exercises from the Power of Now | language_code | `''` | `None` | `None` |
| 6713071 | Last Words | original_title | `''` | `None` | `None` |
| 672493 | The Pursuit of God | language_code | `''` | `None` | `None` |
| 672948 | Arch of Triumph: A Novel of a Man Without a Country | language_code | `''` | `None` | `None` |
| 673252 | Anne McCaffrey's Dragonflight #1 | original_title | `''` | `None` | `None` |
| 6750 | The Broom of the System | language_code | `''` | `None` | `None` |
| 6758423 | Women, Food and God: An Unexpected Path to Almost Everything | original_title | `''` | `None` | `None` |
| 67657 | The Lady & Sons Savannah Country Cookbook | language_code | `''` | `None` | `None` |
| 6765740 | Perahu Kertas | isbn | `''` | `None` | `None` |
| 6765740 | Perahu Kertas | isbn13 | `''` | `None` | `None` |
| 6801614 | One Piece, Volume 38: Rocketman!! (One Piece, #38) | language_code | `''` | `None` | `None` |
| 6820 | number9dream | language_code | `''` | `None` | `None` |
| 682745 | The Basketball Diaries | isbn | `''` | `None` | `None` |
| 682745 | The Basketball Diaries | isbn13 | `''` | `None` | `None` |
| 6828896 | Delivering Happiness: A Path to Profits, Passion, and Purpose | language_code | `''` | `None` | `None` |
| 68380 | Dragonlance Chronicles (Dragonlance #1-3) | language_code | `''` | `None` | `None` |
| 68429 | The Well of Ascension (Mistborn, #2) | original_title | `''` | `None` | `None` |
| 68521 | Excalibur (The Warlord Chronicles, #3) | language_code | `''` | `None` | `None` |
| 685401 | Permission Marketing: Turning Strangers Into Friends And Friends Into Customers | original_title | `''` | `None` | `None` |
| 685401 | Permission Marketing: Turning Strangers Into Friends And Friends Into Customers | language_code | `''` | `None` | `None` |
| 6855294 | Tell-All | language_code | `''` | `None` | `None` |
| 6862 | Amsterdam | language_code | `''` | `None` | `None` |
| 6871646 | Pete the Cat: I Love My White Shoes | original_title | `''` | `None` | `None` |
| 6871737 | Turtle in Paradise | original_title | `''` | `None` | `None` |
| 687278 | When Things Fall Apart: Heart Advice for Difficult Times | language_code | `''` | `None` | `None` |
| 6878614 | Storm Prey (Lucas Davenport, #20) | language_code | `''` | `None` | `None` |
| 6882 | Papillon | language_code | `''` | `None` | `None` |
| 688663 | The Art of Simple Food: Notes, Lessons, and Recipes from a Delicious Revolution | language_code | `''` | `None` | `None` |
| 6891433 | Panserhjerte (Harry Hole, #8) | isbn | `''` | `None` | `None` |
| 6891433 | Panserhjerte (Harry Hole, #8) | isbn13 | `''` | `None` | `None` |
| 6907672 | The Talisman (Volume 1): The Road of Trials | original_title | `''` | `None` | `None` |
| 691520 | No One Here Gets Out Alive | language_code | `''` | `None` | `None` |
| 6931246 | Kraken | language_code | `''` | `None` | `None` |
| 693172 | Twilight Eyes | language_code | `''` | `None` | `None` |
| 6988014 | Seven Days in the Art World | language_code | `''` | `None` | `None` |
| 7010683 | Beachcombers | original_title | `''` | `None` | `None` |
| 7025086 | Ender's Game, Volume 2: Command School | original_title | `''` | `None` | `None` |
| 70287 | The Many Lives & Secret Sorrows of Josephine B. (Josephine Bonaparte, #1) | language_code | `''` | `None` | `None` |
| 70420 | The Undercover Economist | language_code | `''` | `None` | `None` |
| 7073 | A Son of the Circus | language_code | `''` | `None` | `None` |
| 7090290 | My Fair Lazy: One Reality Television Addict's Attempt to Discover If Not Being A Dumb Ass Is the New Black, or, a Culture-Up Manifesto | original_title | `''` | `None` | `None` |
| 7108725 | Start with Why: How Great Leaders Inspire Everyone to Take Action | language_code | `''` | `None` | `None` |
| 7119070 | أحببتك أكثر مما ينبغي | isbn | `''` | `None` | `None` |
| 7119070 | أحببتك أكثر مما ينبغي | isbn13 | `''` | `None` | `None` |
| 712807 | Ruby Holler | language_code | `''` | `None` | `None` |
| 7135858 | My Name Is Memory | original_title | `''` | `None` | `None` |
| 714380 | The Discoverers: A History of Man's Search to Know His World and Himself | language_code | `''` | `None` | `None` |
| 71458 | Stupeur et tremblements | isbn | `''` | `None` | `None` |
| 71458 | Stupeur et tremblements | isbn13 | `''` | `None` | `None` |
| 714711 | You Can Win: A Step by Step Tool for Top Achievers | language_code | `''` | `None` | `None` |
| 7147831 | Min kamp 1 (Min kamp #1) | isbn | `''` | `None` | `None` |
| 7147831 | Min kamp 1 (Min kamp #1) | isbn13 | `''` | `None` | `None` |
| 716696 | رباعيات خيام | isbn | `''` | `None` | `None` |
| 716696 | رباعيات خيام | isbn13 | `''` | `None` | `None` |
| 71784 | A New Song (Mitford Years, #5) | language_code | `''` | `None` | `None` |
| 71787 | In This Mountain (Mitford Years, #7) | language_code | `''` | `None` | `None` |
| 7182899 | Into the Gauntlet (The 39 Clues, #10) | original_title | `''` | `None` | `None` |
| 7184 | Twenty Years After (The D'Artagnan Romances, #2) | language_code | `''` | `None` | `None` |
| 71863 | A Killing Frost (Tomorrow, #3) | language_code | `''` | `None` | `None` |
| 71867 | The Other Side of Dawn (Tomorrow, #7) | language_code | `''` | `None` | `None` |
| 7190 | The Three Musketeers | isbn | `''` | `None` | `None` |
| 7190 | The Three Musketeers | isbn13 | `''` | `None` | `None` |
| 7190 | The Three Musketeers | language_code | `''` | `None` | `None` |
| 7194 | The Club Dumas | isbn | `''` | `None` | `None` |
| 7194 | The Club Dumas | isbn13 | `''` | `None` | `None` |
| 7201 | As the Crow Flies | language_code | `''` | `None` | `None` |
| 7202825 | Unleashed (Ross Siblings, #1) | original_title | `''` | `None` | `None` |
| 720298 | Codependent No More: How to Stop Controlling Others and Start Caring for Yourself | language_code | `''` | `None` | `None` |
| 7262166 | Tough Customer (Mitchell & Associates #2) | original_title | `''` | `None` | `None` |
| 7263429 | Wolfsbane (Nightshade #2; Nightshade World #5) | original_title | `''` | `None` | `None` |
| 7278837 | Diary of a Wimpy Kid: #1-4 | original_title | `''` | `None` | `None` |
| 7290826 | Promises to Keep | original_title | `''` | `None` | `None` |
| 72978 | Titus Andronicus | original_title | `''` | `None` | `None` |
| 7307503 | Archangel's Consort (Guild Hunter, #3) | original_title | `''` | `None` | `None` |
| 73186 | The Case for Christ | language_code | `''` | `None` | `None` |
| 7329 | Unfinished Tales of Númenor and Middle-Earth | language_code | `''` | `None` | `None` |
| 734542 | Freight Train | language_code | `''` | `None` | `None` |
| 7352220 | Black Butler, Vol. 3 (Black Butler, #3) | isbn | `''` | `None` | `None` |
| 7352220 | Black Butler, Vol. 3 (Black Butler, #3) | isbn13 | `''` | `None` | `None` |
| 7389 | Runaways, Vol. 1: Pride and Joy (Runaways, #1) | original_title | `''` | `None` | `None` |
| 73965 | Drinking: A Love Story | language_code | `''` | `None` | `None` |
| 73968 | Love Story (Love Story, #1) | language_code | `''` | `None` | `None` |
| 74169 | Facing Your Giants: A David and Goliath Story for Everyday People | language_code | `''` | `None` | `None` |
| 7433 | Messenger of Truth (Maisie Dobbs, #4) | language_code | `''` | `None` | `None` |
| 744615 | Scott Pilgrim, Volume 4: Scott Pilgrim Gets It Together | language_code | `''` | `None` | `None` |
| 7455 | Sex and the City | language_code | `''` | `None` | `None` |
| 7468160 | Every Last One | original_title | `''` | `None` | `None` |
| 7469133 | Dexter Is Delicious (Dexter, #5) | language_code | `''` | `None` | `None` |
| 747061 | Book of Mormon, Doctrine and Covenants, Pearl of Great Price | language_code | `''` | `None` | `None` |
| 7494887 | The Pacific | original_title | `''` | `None` | `None` |
| 7497897 | Radical: Taking Back Your Faith from the American Dream | original_title | `''` | `None` | `None` |
| 7505716 | Alice's Adventures in Wonderland & Other Stories | original_title | `''` | `None` | `None` |
| 7521400 | This Time Together: Laughter and Reflection | original_title | `''` | `None` | `None` |
| 7557548 | Men at Arms: The Play | original_title | `''` | `None` | `None` |
| 758153 | Born Free: A Lioness of Two Worlds (Story of Elsa, #1) | language_code | `''` | `None` | `None` |
| 7592279 | The Emperor of Nihon-Ja (Ranger's Apprentice, #10) | original_title | `''` | `None` | `None` |
| 759960 | Rumble Fish | language_code | `''` | `None` | `None` |
| 760025 | Positioning: The Battle for Your Mind: How to Be Seen and Heard in the Overcrowded Marketplace | language_code | `''` | `None` | `None` |
| 760168 | Just Me in the Tub (Mercer Mayer's Little Critter) | language_code | `''` | `None` | `None` |
| 760205 | There's a Nightmare in My Closet | language_code | `''` | `None` | `None` |
| 7603 | Reading Lolita in Tehran | isbn | `''` | `None` | `None` |
| 7603 | Reading Lolita in Tehran | isbn13 | `''` | `None` | `None` |
| 7604 | Lolita | isbn | `''` | `None` | `None` |
| 7604 | Lolita | isbn13 | `''` | `None` | `None` |
| 7614747 | Venom (Elemental Assassin, #3) | original_title | `''` | `None` | `None` |
| 7619057 | Warm Bodies (Warm Bodies, #1) | language_code | `''` | `None` | `None` |
| 762288 | Nothing's Fair in Fifth Grade | language_code | `''` | `None` | `None` |
| 76237 | The Further Adventures of Sherlock Holmes: After Sir Arthur Conan Doyle (Classic Crime) | language_code | `''` | `None` | `None` |
| 76248 | Sherlock Holmes of Baker Street: A Life of the World's First Consulting Detective | language_code | `''` | `None` | `None` |
| 7628 | The Good Soldier | language_code | `''` | `None` | `None` |
| 763047 | Straight Talking | language_code | `''` | `None` | `None` |
| 76401 | Bury My Heart at Wounded Knee: An Indian History of the American West | language_code | `''` | `None` | `None` |
| 7646805 | The Gift (Witch & Wizard, #2) | language_code | `''` | `None` | `None` |
| 7648269 | Empire of the Summer Moon: Quanah Parker and the Rise and Fall of the Comanches, the Most Powerful Indian Tribe in American History | language_code | `''` | `None` | `None` |
| 765148 | Giraffes Can't Dance | original_publication_year | `''` | `None` | `None` |
| 765148 | Giraffes Can't Dance | original_title | `''` | `None` | `None` |
| 766020 | The Rainbow Fish | original_title | `''` | `None` | `None` |
| 7664334 | Amy & Roger's Epic Detour | original_title | `''` | `None` | `None` |
| 76664 | A Spell for Chameleon (Xanth #1) | language_code | `''` | `None` | `None` |
| 76668 | For Love of Evil (Incarnations of Immortality, #6) | language_code | `''` | `None` | `None` |
| 7670 | The Andromeda Strain | language_code | `''` | `None` | `None` |
| 7673 | Eaters of the Dead | language_code | `''` | `None` | `None` |
| 7675 | Disclosure | language_code | `''` | `None` | `None` |
| 7682 | The Great Train Robbery | language_code | `''` | `None` | `None` |
| 7683254 | Monster Hunter Vendetta (Monster Hunter International, #2) | original_title | `''` | `None` | `None` |
| 769212 | The Last Seven Months of Anne Frank | language_code | `''` | `None` | `None` |
| 7696135 | Making Ideas Happen: Overcoming the Obstacles Between Vision and Reality | original_title | `''` | `None` | `None` |
| 7696135 | Making Ideas Happen: Overcoming the Obstacles Between Vision and Reality | language_code | `''` | `None` | `None` |
| 769658 | Battlefield Earth: A Saga of the Year 3000 | isbn | `''` | `None` | `None` |
| 769658 | Battlefield Earth: A Saga of the Year 3000 | isbn13 | `''` | `None` | `None` |
| 770038 | Is Your Mama a Llama? | language_code | `''` | `None` | `None` |
| 7701043 | الجزار | isbn | `''` | `None` | `None` |
| 7701043 | الجزار | isbn13 | `''` | `None` | `None` |
| 7701275 | The Immortals Boxed Set (The Immortals, #1-3) | original_title | `''` | `None` | `None` |
| 7701275 | The Immortals Boxed Set (The Immortals, #1-3) | language_code | `''` | `None` | `None` |
| 7704143 | تراب الماس | isbn | `''` | `None` | `None` |
| 7704143 | تراب الماس | isbn13 | `''` | `None` | `None` |
| 7707 | Pygmalion & My Fair Lady | language_code | `''` | `None` | `None` |
| 77161 | Grass for His Pillow (Tales of the Otori, #2) | language_code | `''` | `None` | `None` |
| 7726143 | Origins (The Vampire Diaries: Stefan's Diaries, #1) | original_title | `''` | `None` | `None` |
| 7726892 | The Island | original_title | `''` | `None` | `None` |
| 7726892 | The Island | language_code | `''` | `None` | `None` |
| 772852 | The Cross and the Switchblade | language_code | `''` | `None` | `None` |
| 77295 | Gift from the Sea | language_code | `''` | `None` | `None` |
| 772976 | Frida Kahlo: 1907-1954 Pain and Passion | language_code | `''` | `None` | `None` |
| 773276 | Good Night, Gorilla | language_code | `''` | `None` | `None` |
| 77366 | The Hero and the Crown (Damar, #2) | original_title | `''` | `None` | `None` |
| 773951 | The Story of Ferdinand | language_code | `''` | `None` | `None` |
| 774060 | Prisoner of My Desire | language_code | `''` | `None` | `None` |
| 7742 | Ahab's Wife, or The Star-Gazer | original_title | `''` | `None` | `None` |
| 7743783 | The Unidentified Redhead (Redhead, #1) | isbn | `''` | `None` | `None` |
| 7743783 | The Unidentified Redhead (Redhead, #1) | isbn13 | `''` | `None` | `None` |
| 7746259 | The Stand: Soul Survivors | original_title | `''` | `None` | `None` |
| 77477 | Blessings | language_code | `''` | `None` | `None` |
| 7769 | Dr. Seuss's ABC: An Amazing Alphabet Book! (Bright and Early Board Books) | original_title | `''` | `None` | `None` |
| 7770 | One Fish, Two Fish, Red Fish, Blue Fish | language_code | `''` | `None` | `None` |
| 77735 | The Honor of the Queen (Honor Harrington, #2) | language_code | `''` | `None` | `None` |
| 77736 | The Short Victorious War (Honor Harrington, #3) | language_code | `''` | `None` | `None` |
| 77739 | Honor Among Enemies (Honor Harrington, #6) | language_code | `''` | `None` | `None` |
| 7775841 | Sleepwalk With Me and Other Painfully True Stories | original_title | `''` | `None` | `None` |
| 7775841 | Sleepwalk With Me and Other Painfully True Stories | language_code | `''` | `None` | `None` |
| 7778609 | Kill the Dead (Sandman Slim, #2) | original_title | `''` | `None` | `None` |
| 7780 | The Secret Art of Dr. Seuss | language_code | `''` | `None` | `None` |
| 7783920 | Because of Mr. Terupt | original_title | `''` | `None` | `None` |
| 7785207 | The Mating  (Law of the Lycans, #2) | isbn | `''` | `None` | `None` |
| 7785207 | The Mating  (Law of the Lycans, #2) | isbn13 | `''` | `None` | `None` |
| 7788 | The Cat in the Hat and Other Dr. Seuss Favorites | language_code | `''` | `None` | `None` |
| 78039 | Ramona the Pest (Ramona, #2) | language_code | `''` | `None` | `None` |
| 781498 | The Day Jimmy's Boa Ate the Wash | language_code | `''` | `None` | `None` |
| 7821447 | Sh*t My Dad Says | language_code | `''` | `None` | `None` |
| 7824768 | ليتها تقرأ | isbn | `''` | `None` | `None` |
| 7824768 | ليتها تقرأ | isbn13 | `''` | `None` | `None` |
| 7831145 | Play of Passion (Psy-Changeling #9) | original_title | `''` | `None` | `None` |
| 78408 | Lemony Snicket: The Unauthorized Autobiography (A Series of Unfortunate Events companion) | language_code | `''` | `None` | `None` |
| 78427 | The Total Money Makeover: A Proven Plan for Financial Fitness | language_code | `''` | `None` | `None` |
| 784911 | Rise of the Evening Star (Fablehaven, #2) | language_code | `''` | `None` | `None` |
| 785092 | Secrets of the Millionaire Mind: Mastering the Inner Game of Wealth | language_code | `''` | `None` | `None` |
| 7862725 | Branded (Fall of Angels, #1) | original_title | `''` | `None` | `None` |
| 7882 | On the Banks of Plum Creek  (Little House, #4) | original_title | `''` | `None` | `None` |
| 7882 | On the Banks of Plum Creek  (Little House, #4) | language_code | `''` | `None` | `None` |
| 7894870 | Bone: Tall Tales | original_title | `''` | `None` | `None` |
| 78960 | Good Wives (Little Women, #1.5) | language_code | `''` | `None` | `None` |
| 78970 | A Matter of Honor | language_code | `''` | `None` | `None` |
| 7897478 | The Bedwetter: Stories of Courage, Redemption, and Pee | isbn | `''` | `None` | `None` |
| 7897478 | The Bedwetter: Stories of Courage, Redemption, and Pee | isbn13 | `''` | `None` | `None` |
| 78982 | Not a Penny More, Not a Penny Less | language_code | `''` | `None` | `None` |
| 79006 | Honor Among Thieves | language_code | `''` | `None` | `None` |
| 7905977 | The Adventures of Ook and Gluk, Kung-Fu Cavemen from the Future | original_title | `''` | `None` | `None` |
| 7907803 | An Object of Beauty | original_title | `''` | `None` | `None` |
| 7908638 | Star Island (Skink, #6) | language_code | `''` | `None` | `None` |
| 7913305 | The Immortals of Meluha (Shiva Trilogy, #1) | isbn | `''` | `None` | `None` |
| 7913305 | The Immortals of Meluha (Shiva Trilogy, #1) | isbn13 | `''` | `None` | `None` |
| 7933292 | Heaven is for Real: A Little Boy's Astounding Story of His Trip to Heaven and Back | original_title | `''` | `None` | `None` |
| 7942786 | Fair Game (Alpha & Omega, #3) | original_title | `''` | `None` | `None` |
| 7973 | Enchantment | language_code | `''` | `None` | `None` |
| 7979 | The Bellmaker (Redwall, #7) | language_code | `''` | `None` | `None` |
| 7980 | Pearls of Lutra (Redwall, #9) | language_code | `''` | `None` | `None` |
| 7981 | The Long Patrol (Redwall, #10) | language_code | `''` | `None` | `None` |
| 7981206 | Dead Reckoning (Sookie Stackhouse, #11) | isbn | `''` | `None` | `None` |
| 7981206 | Dead Reckoning (Sookie Stackhouse, #11) | isbn13 | `''` | `None` | `None` |
| 7987 | The Legend of Luke (Redwall, #12) | language_code | `''` | `None` | `None` |
| 79879 | From Head to Toe | language_code | `''` | `None` | `None` |
| 7993 | Mariel of Redwall (Redwall, #4) | language_code | `''` | `None` | `None` |
| 7999 | Marlfox (Redwall, #11) | language_code | `''` | `None` | `None` |
| 8 | Harry Potter Boxed Set, Books 1-5 (Harry Potter, #1-5) | original_title | `''` | `None` | `None` |
| 8008928 | Savages | original_title | `''` | `None` | `None` |
| 8034188 | Where Good Ideas Come From: The Natural History of Innovation | original_title | `''` | `None` | `None` |
| 80449 | On the Genealogy of Morals | language_code | `''` | `None` | `None` |
| 805023 | My Sweet Audrina (Audrina, #1) | language_code | `''` | `None` | `None` |
| 80534 | Me & Emma | language_code | `''` | `None` | `None` |
| 80536 | Little Earthquakes | language_code | `''` | `None` | `None` |
| 80568 | Sam's Letters to Jennifer | language_code | `''` | `None` | `None` |
| 80670 | Otherwise Known as Sheila the Great (Fudge #2) | language_code | `''` | `None` | `None` |
| 8074967 | Archangel's Blade (Guild Hunter, #4) | language_code | `''` | `None` | `None` |
| 80750 | The Covenant (Abram's Daughters, #1) | language_code | `''` | `None` | `None` |
| 808853 | The Complete Adventures of Curious George | language_code | `''` | `None` | `None` |
| 809849 | Dear Zoo: A Lift-the-Flap Book | original_publication_year | `''` | `None` | `None` |
| 809849 | Dear Zoo: A Lift-the-Flap Book | original_title | `''` | `None` | `None` |
| 809849 | Dear Zoo: A Lift-the-Flap Book | language_code | `''` | `None` | `None` |
| 8112318 | The Candymakers (The Candymakers, #1) | original_title | `''` | `None` | `None` |
| 8113940 | Witches of East End (The Beauchamp Family, #1) | isbn | `''` | `None` | `None` |
| 8113940 | Witches of East End (The Beauchamp Family, #1) | isbn13 | `''` | `None` | `None` |
| 8135807 | Rock Me (Ross Siblings, #2) | isbn | `''` | `None` | `None` |
| 8135807 | Rock Me (Ross Siblings, #2) | isbn13 | `''` | `None` | `None` |
| 8135807 | Rock Me (Ross Siblings, #2) | original_title | `''` | `None` | `None` |
| 815234 | The Napping House | language_code | `''` | `None` | `None` |
| 8152697 | Wishin' and Hopin' | isbn | `''` | `None` | `None` |
| 8152697 | Wishin' and Hopin' | isbn13 | `''` | `None` | `None` |
| 8177526 | Fate (My Blood Approves, #2) | isbn | `''` | `None` | `None` |
| 8177526 | Fate (My Blood Approves, #2) | isbn13 | `''` | `None` | `None` |
| 81939 | The Mastery of Love: A Practical Guide to the Art of Relationship --Toltec Wisdom Book | language_code | `''` | `None` | `None` |
| 81948 | The E-Myth Revisited: Why Most Small Businesses Don't Work and What to Do About It | language_code | `''` | `None` | `None` |
| 81959 | As a Man Thinketh | original_title | `''` | `None` | `None` |
| 821056 | Hinds' Feet on High Places | language_code | `''` | `None` | `None` |
| 8229399 | Big Nate Strikes Again (Big Nate Novels, #2) | original_title | `''` | `None` | `None` |
| 82356 | The Comedy of Errors | original_title | `''` | `None` | `None` |
| 82356 | The Comedy of Errors | language_code | `''` | `None` | `None` |
| 8239301 | الطنطورية | isbn | `''` | `None` | `None` |
| 8239301 | الطنطورية | isbn13 | `''` | `None` | `None` |
| 82397 | Richard II | language_code | `''` | `None` | `None` |
| 824763 | Reborn! Vol. 01: Reborn Arrives! (Reborn!, #1) | language_code | `''` | `None` | `None` |
| 8248 | By the Shores of Silver Lake  (Little House, #5) | language_code | `''` | `None` | `None` |
| 825081 | Lilly's Purple Plastic Purse | language_code | `''` | `None` | `None` |
| 8252 | Farmer Boy (Little House, #3) | language_code | `''` | `None` | `None` |
| 825473 | The Devil's Alternative | language_code | `''` | `None` | `None` |
| 826583 | If You Take a Mouse to the Movies | language_code | `''` | `None` | `None` |
| 826584 | If You Give a Moose a Muffin | original_title | `''` | `None` | `None` |
| 8274537 | Tales from a Not-So-Popular Party Girl (Dork Diaries, #2) | language_code | `''` | `None` | `None` |
| 82748 | Sushi for Beginners | language_code | `''` | `None` | `None` |
| 827497 | One Flew Over the Cuckoo's Nest | language_code | `''` | `None` | `None` |
| 8281069 | The Unofficial Harry Potter Cookbook: From Cauldron Cakes to Knickerbocker Glory--More Than 150 Magical Recipes for Wizards and Non-Wizards Alike (Unofficial Cookbook) | original_title | `''` | `None` | `None` |
| 8281069 | The Unofficial Harry Potter Cookbook: From Cauldron Cakes to Knickerbocker Glory--More Than 150 Magical Recipes for Wizards and Non-Wizards Alike (Unofficial Cookbook) | language_code | `''` | `None` | `None` |
| 82817 | Zoya | isbn | `''` | `None` | `None` |
| 82817 | Zoya | isbn13 | `''` | `None` | `None` |
| 82817 | Zoya | language_code | `''` | `None` | `None` |
| 8282 | The Long Winter (Little House, #6) | language_code | `''` | `None` | `None` |
| 8288246 | Red Glove (Curse Workers, #2) | original_title | `''` | `None` | `None` |
| 8296140 | Clara and Mr. Tiffany | language_code | `''` | `None` | `None` |
| 831470 | Bambi | original_title | `''` | `None` | `None` |
| 831829 | 30 Days of Night, Vol. 1 | language_code | `''` | `None` | `None` |
| 8320534 | Raymond E. Feist's Magician Master | original_title | `''` | `None` | `None` |
| 8320534 | Raymond E. Feist's Magician Master | language_code | `''` | `None` | `None` |
| 833253 | The Power of a Praying Wife | language_code | `''` | `None` | `None` |
| 8343444 | Daun Yang Jatuh Tak Pernah Membenci Angin | isbn | `''` | `None` | `None` |
| 8343444 | Daun Yang Jatuh Tak Pernah Membenci Angin | isbn13 | `''` | `None` | `None` |
| 8346300 | Harry Potter: A Pop-Up Book: Based on the Film Phenomenon | original_title | `''` | `None` | `None` |
| 8346300 | Harry Potter: A Pop-Up Book: Based on the Film Phenomenon | language_code | `''` | `None` | `None` |
| 835155 | See Jane Date | language_code | `''` | `None` | `None` |
| 83539 | Fantastic Voyage | language_code | `''` | `None` | `None` |
| 8354134 | The Running Dream | original_title | `''` | `None` | `None` |
| 836984 | Distant Shores | language_code | `''` | `None` | `None` |
| 83763 | Prey | language_code | `''` | `None` | `None` |
| 838917 | The Power of a Praying Woman | language_code | `''` | `None` | `None` |
| 839263 | David Goes To School | original_title | `''` | `None` | `None` |
| 8407173 | Jasper Jones | isbn | `''` | `None` | `None` |
| 8407173 | Jasper Jones | isbn13 | `''` | `None` | `None` |
| 8428984 | Half Way Home | isbn | `''` | `None` | `None` |
| 8428984 | Half Way Home | isbn13 | `''` | `None` | `None` |
| 8428984 | Half Way Home | original_title | `''` | `None` | `None` |
| 84351 | The Secret History of the Pink Carnation (Pink Carnation, #1) | original_title | `''` | `None` | `None` |
| 84525 | What Got You Here Won't Get You There: How Successful People Become Even More Successful | isbn | `''` | `None` | `None` |
| 84525 | What Got You Here Won't Get You There: How Successful People Become Even More Successful | isbn13 | `''` | `None` | `None` |
| 84525 | What Got You Here Won't Get You There: How Successful People Become Even More Successful | language_code | `''` | `None` | `None` |
| 845977 | A Return to Love: Reflections on the Principles of "A Course in Miracles" | language_code | `''` | `None` | `None` |
| 846066 | The Berenstain Bears Forget Their Manners | original_title | `''` | `None` | `None` |
| 846984 | Love, Stargirl (Stargirl, #2) | language_code | `''` | `None` | `None` |
| 84699 | Never Eat Alone: And Other Secrets to Success, One Relationship at a Time | language_code | `''` | `None` | `None` |
| 8471815 | You Don't Have to Say You Love Me | original_title | `''` | `None` | `None` |
| 849380 | The Seven Principles for Making Marriage Work: A Practical Guide from the Country's Foremost Relationship Expert | language_code | `''` | `None` | `None` |
| 851393 | The Imitation of Christ | language_code | `''` | `None` | `None` |
| 851678 | What Remains: A Memoir of Fate, Friendship, and Love | language_code | `''` | `None` | `None` |
| 852460 | Fix-It and Forget-It Cookbook: Feasting with Your Slow Cooker | language_code | `''` | `None` | `None` |
| 85321 | The Tenth Justice | language_code | `''` | `None` | `None` |
| 8542839 | Fire Burn and Cauldron Bubble (Jolie Wilkins, #1) | isbn | `''` | `None` | `None` |
| 8542839 | Fire Burn and Cauldron Bubble (Jolie Wilkins, #1) | isbn13 | `''` | `None` | `None` |
| 85431 | Friday Night Lights: A Town, a Team, and a Dream | language_code | `''` | `None` | `None` |
| 85443 | The Lords of Discipline | language_code | `''` | `None` | `None` |
| 856917 | Absolute Boyfriend, Vol. 1 | original_publication_year | `''` | `None` | `None` |
| 8570787 | Drop Dead Healthy: One Man's Humble Quest for Bodily Perfection | original_title | `''` | `None` | `None` |
| 857418 | The Carrot Seed | language_code | `''` | `None` | `None` |
| 857448 | Harry the Dirty Dog | original_title | `''` | `None` | `None` |
| 857501 | Hand, Hand, Fingers, Thumb | language_code | `''` | `None` | `None` |
| 8575295 | Wisdom (My Blood Approves, #4) | isbn | `''` | `None` | `None` |
| 8575295 | Wisdom (My Blood Approves, #4) | isbn13 | `''` | `None` | `None` |
| 858514 | Wemberly Worried | language_code | `''` | `None` | `None` |
| 858719 | Clifford the Big Red Dog | language_code | `''` | `None` | `None` |
| 8593026 | Hostile Witness (Witness Series, #1) | isbn | `''` | `None` | `None` |
| 8593026 | Hostile Witness (Witness Series, #1) | isbn13 | `''` | `None` | `None` |
| 85987 | Portrait in Sepia | language_code | `''` | `None` | `None` |
| 85989 | Princess on the Brink (The Princess Diaries, #8) | language_code | `''` | `None` | `None` |
| 85993 | Party Princess (The Princess Diaries, #7) | language_code | `''` | `None` | `None` |
| 86172 | A Man in Full | language_code | `''` | `None` | `None` |
| 8635145 | Embrace (The Violet Eden Chapters, #1) | isbn | `''` | `None` | `None` |
| 8635145 | Embrace (The Violet Eden Chapters, #1) | isbn13 | `''` | `None` | `None` |
| 86424 | Lifeguard | language_code | `''` | `None` | `None` |
| 8643220 | Vampire Academy: The Graphic Novel (Vampire Academy: The Graphic Novel, #1) | language_code | `''` | `None` | `None` |
| 866222 | Winning | language_code | `''` | `None` | `None` |
| 86658 | The Secret Agent | language_code | `''` | `None` | `None` |
| 867247 | A Book of Five Rings: The Classic Guide to Strategy | language_code | `''` | `None` | `None` |
| 8676 | Unlimited Power : The New Science Of Personal Achievement | language_code | `''` | `None` | `None` |
| 867650 | The Little Red Hen (Little Golden Book) | language_code | `''` | `None` | `None` |
| 8686068 | The Devotion of Suspect X | language_code | `''` | `None` | `None` |
| 8689913 | Madame Tussaud: A Novel of the French Revolution | original_title | `''` | `None` | `None` |
| 8696 | Last Chance to See | language_code | `''` | `None` | `None` |
| 8702806 | Eve (Eve Duncan, #12; Eve, Quinn and Bonnie #1) | original_title | `''` | `None` | `None` |
| 8712343 | Kiss of Snow (Psy-Changeling #10) | original_title | `''` | `None` | `None` |
| 8718952 | Vampire Academy Box Set (Vampire Academy, #1-4) | original_title | `''` | `None` | `None` |
| 8720415 | Miles to Go (The Walk, #2) | language_code | `''` | `None` | `None` |
| 8724779 | Marked / Betrayed / Chosen / Untamed / Hunted (House of Night #1-5) | original_publication_year | `''` | `None` | `None` |
| 8724779 | Marked / Betrayed / Chosen / Untamed / Hunted (House of Night #1-5) | original_title | `''` | `None` | `None` |
| 8726744 | The Twilight Saga Complete Collection  (Twilight, #1-4 + 3.5) | original_title | `''` | `None` | `None` |
| 8732 | The Red Pony | isbn | `''` | `None` | `None` |
| 8732 | The Red Pony | isbn13 | `''` | `None` | `None` |
| 8732 | The Red Pony | language_code | `''` | `None` | `None` |
| 87425 | Tintin in Tibet (Tintin, #20) | original_title | `''` | `None` | `None` |
| 87632 | Ultramarathon Man: Confessions of an All-Night Runner | language_code | `''` | `None` | `None` |
| 87640 | PostSecret: Extraordinary Confessions from Ordinary Lives (PostSecret) | language_code | `''` | `None` | `None` |
| 8765461 | Choosing to SEE | original_title | `''` | `None` | `None` |
| 8765461 | Choosing to SEE | language_code | `''` | `None` | `None` |
| 8793878 | The Keeping (Law of the Lycans, #3) | isbn | `''` | `None` | `None` |
| 8793878 | The Keeping (Law of the Lycans, #3) | isbn13 | `''` | `None` | `None` |
| 8835897 | Defiance (Strange Angels, #4) | language_code | `''` | `None` | `None` |
| 8857310 | Unfamiliar Fishes | language_code | `''` | `None` | `None` |
| 886512 | Jamberry | language_code | `''` | `None` | `None` |
| 887201 | Faeries | isbn | `''` | `None` | `None` |
| 887201 | Faeries | isbn13 | `''` | `None` | `None` |
| 887201 | Faeries | language_code | `''` | `None` | `None` |
| 8914 | The First World War | language_code | `''` | `None` | `None` |
| 89186 | Pushing Ice | language_code | `''` | `None` | `None` |
| 892295 | The Annotated Sherlock Holmes: The Four Novels and the Fifty-Six Short Stories Complete (2 Volume Set) | language_code | `''` | `None` | `None` |
| 89369 | The Te of Piglet | original_title | `''` | `None` | `None` |
| 89375 | 90 Minutes in Heaven: A True Story of Death and Life | language_code | `''` | `None` | `None` |
| 89399 | Fortune's Rocks | language_code | `''` | `None` | `None` |
| 894072 | The Little Red Caboose (Little Golden Book) | language_code | `''` | `None` | `None` |
| 8948 | Sons of Destiny (Cirque Du Freak, #12) | language_code | `''` | `None` | `None` |
| 8951 | The Lake of Souls (Cirque Du Freak, #10) | language_code | `''` | `None` | `None` |
| 8951449 | Hollowland (The Hollows, #1) | original_title | `''` | `None` | `None` |
| 8952 | Killers of the Dawn (Cirque Du Freak, #9) | isbn | `''` | `None` | `None` |
| 8952 | Killers of the Dawn (Cirque Du Freak, #9) | isbn13 | `''` | `None` | `None` |
| 8952 | Killers of the Dawn (Cirque Du Freak, #9) | language_code | `''` | `None` | `None` |
| 8957 | Tunnels of Blood (Cirque Du Freak, #3) | isbn | `''` | `None` | `None` |
| 8957 | Tunnels of Blood (Cirque Du Freak, #3) | isbn13 | `''` | `None` | `None` |
| 8957 | Tunnels of Blood (Cirque Du Freak, #3) | language_code | `''` | `None` | `None` |
| 895886 | Lassie Come-Home | language_code | `''` | `None` | `None` |
| 8962 | A Living Nightmare (Cirque Du Freak, #1) | language_code | `''` | `None` | `None` |
| 8963 | Hunters of the Dusk (Cirque Du Freak, #7) | language_code | `''` | `None` | `None` |
| 8965 | The Vampire's Assistant (Cirque Du Freak, #2) | isbn | `''` | `None` | `None` |
| 8965 | The Vampire's Assistant (Cirque Du Freak, #2) | isbn13 | `''` | `None` | `None` |
| 8965 | The Vampire's Assistant (Cirque Du Freak, #2) | language_code | `''` | `None` | `None` |
| 8966 | Allies of the Night (Cirque du Freak, #8) | language_code | `''` | `None` | `None` |
| 896622 | The Wolf and the Dove | language_code | `''` | `None` | `None` |
| 896623 | The Flame and the Flower | language_code | `''` | `None` | `None` |
| 8967 | Trials of Death (Cirque Du Freak, #5) | language_code | `''` | `None` | `None` |
| 8968 | The Vampire Prince (Cirque Du Freak, #6) | language_code | `''` | `None` | `None` |
| 89731 | Kira-Kira | original_title | `''` | `None` | `None` |
| 89959 | The Constitution of the United States of America | language_code | `''` | `None` | `None` |
| 900070 | The Berenstain Bears Go to School | original_title | `''` | `None` | `None` |
| 90010001 | The Lantern Keeper's Daughter | image_url | `''` | `None` | `None` |
| 90010001 | The Lantern Keeper's Daughter | small_image_url | `''` | `None` | `None` |
| 90010002 | Salt and Ember | image_url | `''` | `None` | `None` |
| 90010002 | Salt and Ember | small_image_url | `''` | `None` | `None` |
| 90010003 | A Field Guide to Quiet Places | image_url | `''` | `None` | `None` |
| 90010003 | A Field Guide to Quiet Places | small_image_url | `''` | `None` | `None` |
| 90010004 | Winter Orchard | image_url | `''` | `None` | `None` |
| 90010004 | Winter Orchard | small_image_url | `''` | `None` | `None` |
| 90010005 | The Cartographer's Error | image_url | `''` | `None` | `None` |
| 90010005 | The Cartographer's Error | small_image_url | `''` | `None` | `None` |
| 90010006 | Notes from the Night Ferry | isbn | `''` | `None` | `None` |
| 90010006 | Notes from the Night Ferry | image_url | `''` | `None` | `None` |
| 90010006 | Notes from the Night Ferry | small_image_url | `''` | `None` | `None` |
| 90010007 | Small Hours | isbn | `''` | `None` | `None` |
| 90010007 | Small Hours | isbn13 | `''` | `None` | `None` |
| 90010007 | Small Hours | image_url | `''` | `None` | `None` |
| 90010007 | Small Hours | small_image_url | `''` | `None` | `None` |
| 90010008 | The Glass Aviary | isbn | `''` | `None` | `None` |
| 90010008 | The Glass Aviary | isbn13 | `''` | `None` | `None` |
| 90010008 | The Glass Aviary | image_url | `''` | `None` | `None` |
| 90010008 | The Glass Aviary | small_image_url | `''` | `None` | `None` |
| 90010009 | Borrowed Light | isbn | `''` | `None` | `None` |
| 90010009 | Borrowed Light | isbn13 | `''` | `None` | `None` |
| 90010009 | Borrowed Light | image_url | `''` | `None` | `None` |
| 90010009 | Borrowed Light | small_image_url | `''` | `None` | `None` |
| 90010010 | Untitled Manuscript | isbn | `''` | `None` | `None` |
| 90010010 | Untitled Manuscript | isbn13 | `''` | `None` | `None` |
| 90010010 | Untitled Manuscript | image_url | `''` | `None` | `None` |
| 90010010 | Untitled Manuscript | small_image_url | `''` | `None` | `None` |
| 90010011 | Tides of Marrow Bay | image_url | `''` | `None` | `None` |
| 90010011 | Tides of Marrow Bay | small_image_url | `''` | `None` | `None` |
| 90010012 | The Long Walk Home | image_url | `''` | `None` | `None` |
| 90010012 | The Long Walk Home | small_image_url | `''` | `None` | `None` |
| 90010014 | An Atlas of Small Kindnesses | image_url | `''` | `None` | `None` |
| 90010014 | An Atlas of Small Kindnesses | small_image_url | `''` | `None` | `None` |
| 90072 | Dr. Seuss's Green Eggs and Ham: For Soprano, Boy Soprano, and Orchestra | original_publication_year | `''` | `None` | `None` |
| 90072 | Dr. Seuss's Green Eggs and Ham: For Soprano, Boy Soprano, and Orchestra | original_title | `''` | `None` | `None` |
| 90072 | Dr. Seuss's Green Eggs and Ham: For Soprano, Boy Soprano, and Orchestra | language_code | `''` | `None` | `None` |
| 90078 | An Essay Concerning Human Understanding | language_code | `''` | `None` | `None` |
| 900892 | A Random Walk Down Wall Street | original_title | `''` | `None` | `None` |
| 9010 | I Hope They Serve Beer in Hell (Tucker Max, #1) | language_code | `''` | `None` | `None` |
| 901680 | Edvard Munch: 1863-1944 (Basic Art) | language_code | `''` | `None` | `None` |
| 9018370 | The Walking Dead, Vol. 13: Too Far Gone | language_code | `''` | `None` | `None` |
| 905092 | The Millionaire Mind | original_title | `''` | `None` | `None` |
| 905092 | The Millionaire Mind | language_code | `''` | `None` | `None` |
| 905382 | Anne Frank : The Biography | language_code | `''` | `None` | `None` |
| 906560 | Tramp for the Lord | language_code | `''` | `None` | `None` |
| 9086994 | Aleph | isbn | `''` | `None` | `None` |
| 9086994 | Aleph | isbn13 | `''` | `None` | `None` |
| 91244 | Beezus and Ramona (Ramona, #1) | language_code | `''` | `None` | `None` |
| 91249 | Ramona Forever (Ramona, #7) | language_code | `''` | `None` | `None` |
| 9160695 | Battle Hymn of the Tiger Mother | original_title | `''` | `None` | `None` |
| 9166559 | These Things Hidden | language_code | `''` | `None` | `None` |
| 91767 | Frida: A Biography of Frida Kahlo | language_code | `''` | `None` | `None` |
| 918789 | West Side Story | language_code | `''` | `None` | `None` |
| 9219901 | Unbearable Lightness: A Story of Loss and Gain | original_title | `''` | `None` | `None` |
| 9219901 | Unbearable Lightness: A Story of Loss and Gain | language_code | `''` | `None` | `None` |
| 92254 | Angels in America, Part Two: Perestroika | original_title | `''` | `None` | `None` |
| 92308 | The Importance of Being Earnest and Other Plays | original_title | `''` | `None` | `None` |
| 92371 | Lie Down with Lions | language_code | `''` | `None` | `None` |
| 925367 | The Climb: Tragic Ambitions on Everest | language_code | `''` | `None` | `None` |
| 9279734 | Forever Mine (The Moreno Brothers, #1) | isbn | `''` | `None` | `None` |
| 9279734 | Forever Mine (The Moreno Brothers, #1) | isbn13 | `''` | `None` | `None` |
| 92871 | Brothers Majere (Dragonlance: Preludes, #3) | language_code | `''` | `None` | `None` |
| 9293020 | The Elephant Tree | original_title | `''` | `None` | `None` |
| 9296438 | Save Me | language_code | `''` | `None` | `None` |
| 9300 | Watermelon (Walsh Family, #1) | language_code | `''` | `None` | `None` |
| 93000 | Piano/Vocal/Guitar Sheet Music: The Chronicles of Narnia: The Lion, the Witch and The Wardrobe | language_code | `''` | `None` | `None` |
| 9302 | The Other Side of the Story | language_code | `''` | `None` | `None` |
| 9305362 | Captive Prince (Captive Prince, #1) | isbn | `''` | `None` | `None` |
| 9305362 | Captive Prince (Captive Prince, #1) | isbn13 | `''` | `None` | `None` |
| 93276 | King Arthur and His Knights: Selected Tales | language_code | `''` | `None` | `None` |
| 9370 | Skinny Legs and All | language_code | `''` | `None` | `None` |
| 93726 | Princess in Training (The Princess Diaries, #6) | language_code | `''` | `None` | `None` |
| 9375 | Fried Green Tomatoes at the Whistle Stop Cafe | language_code | `''` | `None` | `None` |
| 93981 | The Interpretation of Dreams | language_code | `''` | `None` | `None` |
| 9409469 | The Gray Wolf Throne (Seven Realms, #3) | isbn | `''` | `None` | `None` |
| 9409469 | The Gray Wolf Throne (Seven Realms, #3) | isbn13 | `''` | `None` | `None` |
| 9418327 | Bossypants | isbn | `''` | `None` | `None` |
| 9418327 | Bossypants | isbn13 | `''` | `None` | `None` |
| 9429531 | The Dry Grass of August | language_code | `''` | `None` | `None` |
| 9440324 | The Midnight Palace (Niebla, #2) | language_code | `''` | `None` | `None` |
| 94669 | The Mistress of Spices | language_code | `''` | `None` | `None` |
| 94799 | Ghost Soldiers: The Epic Account of World War II's Greatest Rescue Mission | language_code | `''` | `None` | `None` |
| 94807 | The Frog and Toad Treasury: Frog and Toad are Friends/Frog and Toad Together/Frog and Toad All Year  (Frog and Toad #1-3) | language_code | `''` | `None` | `None` |
| 9484114 | The Happiness Advantage: The Seven Principles of Positive Psychology That Fuel Success and Performance at Work | language_code | `''` | `None` | `None` |
| 9489502 | Cold Vengeance (Pendergast, #11) | language_code | `''` | `None` | `None` |
| 9496240 | The Hangman's Daughter (The Hangman's Daughter, #1) | isbn | `''` | `None` | `None` |
| 9496240 | The Hangman's Daughter (The Hangman's Daughter, #1) | isbn13 | `''` | `None` | `None` |
| 949709 | There Was An Old Lady Who Swallowed A Fly (Classic Books) | language_code | `''` | `None` | `None` |
| 9512985 | The Personal MBA: Master the Art of Business | original_title | `''` | `None` | `None` |
| 9512985 | The Personal MBA: Master the Art of Business | language_code | `''` | `None` | `None` |
| 952 | The Five Love Languages of Children | language_code | `''` | `None` | `None` |
| 9522 | Persepolis, Volume 1 | original_title | `''` | `None` | `None` |
| 9526 | Embroideries | original_title | `''` | `None` | `None` |
| 9528186 | Pretty Little Liars (TV Series) | original_publication_year | `''` | `None` | `None` |
| 9528186 | Pretty Little Liars (TV Series) | original_title | `''` | `None` | `None` |
| 9529502 | Big Nate on a Roll (Big Nate Novels, #3) | language_code | `''` | `None` | `None` |
| 953260 | Disney after Dark (Kingdom Keepers, #1) | language_code | `''` | `None` | `None` |
| 9545064 | The Story of Beautiful Girl | language_code | `''` | `None` | `None` |
| 95558 | Solaris | isbn | `''` | `None` | `None` |
| 95558 | Solaris | isbn13 | `''` | `None` | `None` |
| 95607 | Unveiled: Tamar (Lineage of Grace #1) | language_code | `''` | `None` | `None` |
| 95622 | The Last Sin Eater | language_code | `''` | `None` | `None` |
| 95658 | Best Friends for Never (The Clique, #2) | language_code | `''` | `None` | `None` |
| 95659 | Invasion of the Boy Snatchers (The Clique, #4) | language_code | `''` | `None` | `None` |
| 95660 | The Pretty Committee Strikes Back (The Clique, #5) | language_code | `''` | `None` | `None` |
| 95661 | Revenge of the Wannabes (The Clique, #3) | language_code | `''` | `None` | `None` |
| 9567 | Half Asleep in Frog Pajamas | language_code | `''` | `None` | `None` |
| 9569 | Villa Incognito | language_code | `''` | `None` | `None` |
| 95707 | Your Best Life Now: 7 Steps to Living at Your Full Potential | language_code | `''` | `None` | `None` |
| 95747 | The Miracle of Mindfulness: An Introduction to the Practice of Meditation | language_code | `''` | `None` | `None` |
| 9581507 | Don't Breathe a Word | original_title | `''` | `None` | `None` |
| 95819 | The Poetry of Robert Frost (Collected Poems, Complete & Unabridged) | original_title | `''` | `None` | `None` |
| 9589 | Hocus Pocus | language_code | `''` | `None` | `None` |
| 9593 | Galápagos | language_code | `''` | `None` | `None` |
| 9606002 | The Preacher (Patrik Hedström, #2) | language_code | `''` | `None` | `None` |
| 96082 | The Last Time They Met | language_code | `''` | `None` | `None` |
| 961833 | Mariana | language_code | `''` | `None` | `None` |
| 9635657 | Tales from a Not-So-Talented Pop Star (Dork Diaries, #3) | isbn | `''` | `None` | `None` |
| 9635657 | Tales from a Not-So-Talented Pop Star (Dork Diaries, #3) | isbn13 | `''` | `None` | `None` |
| 9639197 | Turn of Mind | language_code | `''` | `None` | `None` |
| 9650 | Burmese Days | language_code | `''` | `None` | `None` |
| 96594 | Fearless (The Lost Fleet, #2) | language_code | `''` | `None` | `None` |
| 96642 | Rocket Boys (Coalwood #1) | language_code | `''` | `None` | `None` |
| 9666241 | النبطي | isbn | `''` | `None` | `None` |
| 9666241 | النبطي | isbn13 | `''` | `None` | `None` |
| 9670094 | Through My Eyes | original_title | `''` | `None` | `None` |
| 968403 | The Descendants | language_code | `''` | `None` | `None` |
| 96980 | Centaur Aisle (Xanth, #4) | language_code | `''` | `None` | `None` |
| 97084 | Apathy and Other Small Victories | language_code | `''` | `None` | `None` |
| 9722217 | رغم الفراق | isbn | `''` | `None` | `None` |
| 9722217 | رغم الفراق | isbn13 | `''` | `None` | `None` |
| 9722217 | رغم الفراق | original_title | `''` | `None` | `None` |
| 9748274 | A Tale of Two Cities / Great Expectations | original_publication_year | `''` | `None` | `None` |
| 9748274 | A Tale of Two Cities / Great Expectations | original_title | `''` | `None` | `None` |
| 9751378 | Summer Rental | original_title | `''` | `None` | `None` |
| 9757266 | Sometimes It Happens | original_title | `''` | `None` | `None` |
| 9762 | Loving What Is: Four Questions That Can Change Your Life | language_code | `''` | `None` | `None` |
| 97860 | Tuesday | language_code | `''` | `None` | `None` |
| 9798177 | Middle School: The Worst Years of My Life (Midde School, #1) | original_title | `''` | `None` | `None` |
| 9799572 | Rock Chick Redemption (Rock Chick, #3) | original_title | `''` | `None` | `None` |
| 9802372 | The Name of the Star (Shades of London, #1) | language_code | `''` | `None` | `None` |
| 9814682 | A Song of Ice and Fire (A Song of Ice and Fire, #1-4) | original_title | `''` | `None` | `None` |
| 9822 | Mrs. Frisby and the Rats of NIMH (Rats of NIMH, #1) | language_code | `''` | `None` | `None` |
| 98250 | Once a Runner | language_code | `''` | `None` | `None` |
| 9832370 | BookRags Summary:  A Storm of Swords | isbn | `''` | `None` | `None` |
| 9832370 | BookRags Summary:  A Storm of Swords | isbn13 | `''` | `None` | `None` |
| 9832370 | BookRags Summary:  A Storm of Swords | original_publication_year | `''` | `None` | `None` |
| 9832370 | BookRags Summary:  A Storm of Swords | original_title | `''` | `None` | `None` |
| 98427 | The General's Daughter | language_code | `''` | `None` | `None` |
| 9854 | The End of Poverty | original_title | `''` | `None` | `None` |
| 9854 | The End of Poverty | language_code | `''` | `None` | `None` |
| 9858488 | Dead End in Norvelt | original_title | `''` | `None` | `None` |
| 9858714 | The Mind Readers (Mind Readers, #1) | isbn | `''` | `None` | `None` |
| 9858714 | The Mind Readers (Mind Readers, #1) | isbn13 | `''` | `None` | `None` |
| 98687 | Call Me by Your Name | language_code | `''` | `None` | `None` |
| 988170 | Tawny Scrawny Lion | language_code | `''` | `None` | `None` |
| 989313 | Heart of Darkness and Selected Short Fiction | original_title | `''` | `None` | `None` |
| 9902804 | Lies That Chelsea Handler Told Me | original_title | `''` | `None` | `None` |
| 99110 | The Complete Tales and Poems of Winnie-the-Pooh (Winnie-the-Pooh, #1-4) | original_title | `''` | `None` | `None` |
| 9915707 | Endure (Need, #4) | isbn | `''` | `None` | `None` |
| 9915707 | Endure (Need, #4) | isbn13 | `''` | `None` | `None` |
| 9917879 | The Unwanteds (Unwanteds, #1) | original_title | `''` | `None` | `None` |
| 9917945 | Perfect (Impulse, #2) | original_title | `''` | `None` | `None` |
| 9923372 | Maine | language_code | `''` | `None` | `None` |
| 9925913 | Shock Wave (Virgil Flowers, #5) | isbn | `''` | `None` | `None` |
| 9925913 | Shock Wave (Virgil Flowers, #5) | isbn13 | `''` | `None` | `None` |
| 99452 | Ogre, Ogre (Xanth #5) | language_code | `''` | `None` | `None` |
| 9969571 | Ready Player One | original_title | `''` | `None` | `None` |
| 99955 | Common Sense, The Rights of Man and Other Essential Writings | original_title | `''` | `None` | `None` |

## Appendix B: every warning-labeling difference, in full

| goodreads_book_id | Title | Kristina (field/reason) | Anthony (field/reason) | Abigail (field/reason) | Raw value |
|---|---|---|---|---|---|
| 10295484 | Heart on a Chain | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 10374 | Hard-Boiled Wonderland and the End of the World | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 10586539 | Wake (Watersong #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 10599302 | Head Over Heels (Lucky Harbor, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 10664113 | A Dance with Dragons (A Song of Ice and Fire, #5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 10776793 | War Brides | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 10790376 | A Modern Witch (A Modern Witch, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 10813469 | Rock Chick Renegade (Rock Chick, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 10813480 | For You (The 'Burg, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 10830444 | Guilty Wives | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 10975 | The Sound and the Fury | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11096647 | Flat-Out Love (Flat-Out Love, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11227040 | Sweet Dreams (Colorado Mountain, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11227041 | The Gamble (Colorado Mountain, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11227043 | Rock Chick Revenge (Rock Chick, #5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11237412 | Six's Legacy (Lorien Legacies: The Lost Files, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11262424 | Between the Lines (Between the Lines, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11324166 | Timeless (Parasol Protectorate, #5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11350430 | The Mystery Knight (The Tales of Dunk and Egg, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11408650 | The Unbecoming of Mara Dyer (Mara Dyer, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 114170 | Then Came You (The Gamblers, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11450591 | The Mill River Recluse | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11479285 | Breathe (Sea Breeze, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11505797 | Beautiful Disaster (Beautiful, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11561469 | Reason to Breathe (Breathing, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11665750 | At Peace (The 'Burg, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11757975 | The Look of Love (San Francisco Sullivans, #1; The Sullivans, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11784281 | Take This Regret (Take This Regret, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11821514 | Long Time Coming | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11851522 | The Complete Works of H.P. Lovecraft | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11913681 | The Boyfriend Thief (Stolen Kiss, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11947156 | Prince of Wolves (The Grey Wolves, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11970096 | Twenty-Eight and a Half Wishes (Rose Gardner Mystery, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11970747 | The Hedge Knight (The Tales of Dunk and Egg, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11981168 | The One You Love (Emma Holden Suspense Mystery, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 11985631 | The Sworn Sword (The Tales of Dunk and Egg, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12067972 | Where You Are (Between the Lines, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12191246 | Second Son (Jack Reacher, #15.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12254379 | 1Q84 #1-2 (1Q84, #1-2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12287209 | Wool (Wool, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12299419 | Mystery Man (Dream Man, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12326627 | The White Princess (The Plantagenet and Tudor Novels, #5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12341557 | The Wind Through the Keyhole (The Dark Tower, #4.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12390650 | Wildest Dreams (Fantasyland, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12458287 | The Golden Dynasty (Fantasyland, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12583975 | The Billionaire Wins the Game (Billionaire Bachelors, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12602078 | The Tycoon's Revenge (Baby for the Billionaire, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12647642 | Love Unrehearsed (Love, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12652457 | The Broken Eye (Lightbringer, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12667194 | Accordance (Significance, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12675109 | Great by Choice: Uncertainty, Chaos, and Luck--Why Some Thrive Despite Them All | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 1268479 | Warbreaker (Warbreaker, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12706435 | Defiance (Significance, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12716010 | Rapture (Fallen, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12760903 | The Vision (Fallen Star, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12799058 | Summerland | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12842134 | Just One Year (Just One Day, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12881141 | Wild Man (Dream Man, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12900174 | The Vincent Boys (The Vincent Boys, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12902549 | An Invisible Thread: The True Story of an 11-Year-Old Panhandler, a Busy Sales Executive, and an Unlikely Meeting with Destiny | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12922320 | Criminal (Will Trent, #6) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 12958487 | Lady Luck (Colorado Mountain, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13051316 | The Misremembered Man (Tailorstown #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13065142 | Rock Chick Reckoning (Rock Chick, #6) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13070346 | Blood Rites (The Grey Wolves, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13132816 | Emmy & Oliver | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13146214 | Because of Low (Sea Breeze, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13151283 | بضع ساعات في يوم ما | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13151637 | طه الغريب | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13178410 | Proper Gauge (Wool, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13184572 | The Next Best Thing | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13184992 | Rock Chick Regret (Rock Chick, #7) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13188676 | Ignite Me (Shatter Me, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13223520 | Existence (Existence Trilogy, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13312527 | The Opportunist (Love Me with Lies, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13323842 | Predestined (Existence Trilogy, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13363270 | Just One Drop (The Grey Wolves, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13369678 | The Vincent Brothers (The Vincent Boys, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13372690 | Slammed (Slammed, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13402447 | UnEnchanted (An Unfortunate Fairy Tale, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13412515 | Law Man (Dream Man, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13415554 | The Assassin and the Pirate Lord (Throne of Glass, #0.1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13419891 | The Assassin and the Desert (Throne of Glass, #0.3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13431827 | The Remaining (The Remaining, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13453029 | Wool Omnibus (Silo, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13489517 | 28 حرف | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13496084 | Point of Retreat (Slammed, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13496738 | While It Lasts (Sea Breeze, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13502963 | Indebted (The Premonition, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13507011 | Low Pressure | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13522957 | Feral Sins (The Phoenix Pack, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13546173 | The Assassin and the Underworld (Throne of Glass, #0.4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13565676 | The Assassin and the Empire (Throne of Glass, #0.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13565914 | Knight (Unfinished Hero, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13568619 | The Shadowhunter's Codex | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13569581 | Blood Song (Raven's Shadow, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13573795 | Ceaseless (Existence Trilogy, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13580846 | My Life with the Walter Boys (My Life with the Walter Boys #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13600318 | Reckless (Thoughtless, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13601550 | Accidentally on Purpose (Accidentally on Purpose, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13603717 | First Shift: Legacy (Shift, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13612739 | Seduced in the Dark (The Dark Duet, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13624367 | Checkmate (Neighbor from Hell, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13634927 | A Leaf on the Wind of All Hallows (Outlander, #8.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13638570 | Out of Breath (Breathing, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13643567 | The Evolution of Mara Dyer (Mara Dyer, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 13765729 | Abducted (Lizzy Gardner #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 140302 | Poirot Investiga (Hércules Poirot, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 14060046 | Obsession | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 14165516 | The Marriage Trap (Marriage to a Billionaire, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 14740588 | Notorious Nineteen (Stephanie Plum, #19) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 14745338 | Fairest (An Unfortunate Fairy Tale, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 1499952 | Daddy-Long-Legs (Daddy-Long-Legs, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15055 | Oranges Are Not the Only Fruit | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15059301 | Captured (The Captive, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15062217 | 14 | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 153785 | Page (Protector of the Small, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 153795 | Squire (Protector of the Small, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 153800 | Lady Knight (Protector of the Small, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15704001 | Seduction and Snacks (Chocolate Lovers, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15717721 | If I Were You (Inside Out, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15722284 | Saint Odd (Odd Thomas, #7) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15723286 | Curtsies & Conspiracies (Finishing School, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15724654 | The Mighty Storm (The Storm, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15728921 | Don't Let Me Go | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15729261 | The Marriage Mistake (Marriage to a Billionaire, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15730101 | The Call of Cthulhu | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15734464 | 12th of Never (Women's Murder Club, #12) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15738951 | Deep Down (Jack Reacher, #16.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15739018 | Taking Chances (Taking Chances, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15748335 | Leave Me Breathless (Ross Siblings, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15749186 | To All the Boys I've Loved Before (To All the Boys I've Loved Before, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15760001 | On Dublin Street (On Dublin Street, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15761241 | The Wild Ones (The Wild Ones, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15762975 | Wrong Bed, Right Guy (Come Undone, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15768536 | Fall From Grace (Mad World, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15771862 | Wave | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15776904 | The Beggar King (The Hangman's Daughter, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15778138 | Just for Now (Sea Breeze, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15783307 | The Perfect Game (The Perfect Game, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15784909 | This Girl (Slammed, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15828714 | Sometimes It Lasts (Sea Breeze, #5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15832316 | Dirty Red (Love Me with Lies, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 15852756 | Naked (The Blackstone Affair, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16001443 | All In (The Blackstone Affair, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16045855 | Crush (Crush, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16047244 | Rock the Heart (Black Falcon, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16053316 | Wethering the Storm (The Storm, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16056862 | The Unwanted Wife (Unwanted, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16066586 | The Cellar (The Cellar, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16068905 | Fangirl | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16070521 | Come Away with Me (With Me in Seattle, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16070903 | Fallen Too Far (Rosemary Beach, #1; Too Far, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16079228 | Beautifully Damaged (Beautifully Damaged, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16081202 | Open Road Summer | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16081754 | Find You in the Dark (Find You in the Dark, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16084702 | Fifty Shades Duo: Fifty Shades Darker / Fifty Shades Freed (Fifty Shades, #2-3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16090636 | Fight with Me (With Me in Seattle, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16090981 | Thief (Love Me with Lies, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16093188 | Up to Me (The Bad Boys, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16096873 | Revealed (House of Night, #11) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16102880 | Bad Rep (Bad Rep, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16113791 | The Coincidence of Callie & Kayden (The Coincidence, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16117182 | Broken Silence (Silence, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16117804 | The Proposal (The Proposition, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16122643 | Eyes Wide Open (The Blackstone Affair, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16124019 | Waking Up Married (Waking Up, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16130986 | An Innocent Client | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16131484 | The Infinite Sea (The 5th Wave, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16134551 | Fallen Crest High (Fallen Crest High, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16134782 | In Flight (Up in the Air, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16136959 | Mile High (Up in the Air, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16139641 | Grounded (Up in the Air, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16140036 | This Man (This Man, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16143347 | We Were Liars | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16148398 | Saga #1 | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16148938 | Second Shift: Order (Shift, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16150119 | Wired (Wired, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16150996 | Convicted (Consequences, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16151178 | The Sea of Tranquility | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16163690 | Own the Wind (Chaos, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16174197 | Knight & Play (Knight, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16175040 | Endless Knight (The Arcana Chronicles, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16233105 | Someone to Love (Someone to Love, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16299256 | The Game Changer (The Perfect Game, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16299991 | A Quest of Heroes (The Sorcerer's Ring, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16301111 | Always You (Best Friend, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16429619 | The Kiss of Deception (The Remnant Chronicles, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 16704759 | Knight & Stay (Knight, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17158513 | Captive Prince: Volume Two (Captive Prince, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17158596 | Collide (Collide, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17166702 | True Love Story | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17181905 | The Arrangement: The Ferro Family (The Arrangement, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17191012 | Fallen Crest Family (Fallen Crest High, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17200687 | Rule (Marked Men, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17201110 | Safe with Me (With Me in Seattle, #5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17204568 | Crazy Little Thing (Bell Harbor, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17204860 | Jet (Marked Men, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17228280 | Better off Friends | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17235347 | Life Before Legend: Stories of the Criminal and the Prodigy (Legend, #0.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17255265 | This Man Confessed (This Man, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17257484 | Trouble | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17257990 | Fire Inside (Chaos, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17257993 | Raid (Unfinished Hero, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17267122 | Pulse (Collide, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17286162 | Forever Black (Forever, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17306293 | Shift (Silo, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17314410 | Beauty from Surrender (Beauty, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17317675 | Epilogue (The Dark Duet, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17333880 | Twisted Perfection (Rosemary Beach, #5; Perfection, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17337562 | Forever Too Far (Rosemary Beach, #3; Too Far, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17340050 | Losing Hope (Hopeless, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17375956 | Reaper's Property (Reapers MC, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17377032 | Bad Things (Tristan & Danika, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17401198 | Only the Innocent (DCI Tom Douglas #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17404452 | Forever You (Forever, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17406847 | Defy (Defy, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17407233 | The Submissive (Submissive, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17449417 | Simple Perfection (Rosemary Beach, #6; Perfection, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17455541 | Happy, Happy, Happy | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17455585 | White Hot Kiss (The Dark Elements, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17455815 | Stone Cold Touch (The Dark Elements, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17504320 | Taking Shots (Assassins, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17524166 | نادي السيارات | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17557143 | The Billionaire's Obsession ~ Simon (The Billionaire's Obsession, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17558817 | Be with Me (Wait for You, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17560674 | The Bet (The Bet, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17563080 | Murder of Crows (The Others, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17563539 | The Egg | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17570538 | The Blood Mirror (Lightbringer, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17660 | The Tommyknockers | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17667452 | When I Found You | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17667561 | The Shadow Throne (The Ascendance Trilogy, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17673307 | Neanderthal Seeks Human (Knitting in the City, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17716 | Waiting for Godot | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 1772910 | White Nights | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17729712 | Beautiful Broken Rules (Broken, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17733861 | A Shade of Blood (A Shade of Vampire, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17788401 | Ugly Love | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17792606 | Mine (Real, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17794657 | The Lake (The Lake Trilogy #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17798233 | Rome (Marked Men, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17798287 | Driven (Driven, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17825503 | Leo | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17830559 | Remy (Real, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17831614 | Beautiful Player (Beautiful Bastard, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17831616 | Beautiful Bitch (Beautiful Bastard, #1.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17831617 | Beautiful Bombshell (Beautiful Bastard, #2.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17831619 | Beautiful Beginning (Beautiful Bastard, #3.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17833099 | Price of a Kiss (Forbidden Men, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17835351 | Nikola Tesla: Imagination and the Man That Invented the 20th Century | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17835766 | One More Chance (Rosemary Beach, #8; Chance, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17835773 | Misbehaving (Sea Breeze, #6) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17860217 | Trust in Me (Wait for You, #1.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17880708 | Fueled (Driven, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17880714 | Crashed (Driven, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17925397 | A Castle of Sand (A Shade of Vampire, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17927395 | A Court of Mist and Fury (A Court of Thorns and Roses, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17950614 | UnDivided (Unwind, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17970255 | Into the Deep (Into the Deep, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17973653 | Shine Not Burn (Shine Not Burn, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17977710 | Twisted (Tangled, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17985262 | CyberStorm | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17989312 | The Sisterhood | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 17999892 | The Atlantis Gene (The Origin Mystery, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18045473 | Last Train to Istanbul | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18053782 | Take a Chance (Rosemary Beach, #7; Chance, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18071296 | Willing Captive | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18076876 | Reaper's Legacy (Reapers MC, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18080889 | Worth the Fight (MMA Fighter, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18089551 | Tall, Tatted and Tempting (The Reed Brothers, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18104607 | Beautiful Oblivion (The Maddox Brothers, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18105011 | Sweet Home (Sweet Home, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18108281 | The King (Black Dagger Brotherhood, #12) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18108795 | High Heat (Jack Reacher #17.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18108877 | Timebound (The Chronos Files, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18110808 | Fallen Crest Public (Fallen Crest High, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18115061 | Before Jamaica Lane (On Dublin Street, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18129852 | Rival (Fall Away, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18134249 | Ruin (Ruin, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18138755 | Forever with You (Fixed, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18149927 | Beneath This Man (This Man, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18163646 | Falling into Place | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18191814 | A Blaze of Sun (A Shade of Vampire, #5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18211536 | Rush Too Far (Rosemary Beach, #4; Too Far, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18221931 | Carter Reed (Carter Reed, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18243828 | Jake Undone (Jake, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18244799 | Hardwired (Hacker, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18246727 | Mud Vein | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18282800 | The Ladies' Room | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18285151 | More Than This (More Than, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18297707 | Tangled (Tangled, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18323154 | المرحوم | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18331807 | Vain (The Seven Deadly, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18336965 | My Heart and Other Black Holes | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18340482 | Until Trevor (Until, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18341046 | Until November (Until, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18363068 | حبيبتي بكماء | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18387597 | 2 ضباط | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18405221 | Queen of Fire (Raven's Shadow, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18461986 | Deep (Stage Dive, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18500665 | End of Days (Penryn & the End of Days, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18607805 | Kindle Paperwhite User's Guide | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18668485 | The Initiate (Divergent, #0.2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18680106 | Hard as It Gets (Hard Ink, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18718848 | Mosquitoland | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18739426 | The Bands of Mourning (Mistborn, #6) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 1876770 | Chrzest ognia (Saga o Wiedźminie, #5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18781543 | Until Nico (Until, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18799585 | Hidden (Bone Secrets. #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18800655 | Terms of Enlistment (Frontlines #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18806240 | Bone Gap | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18813530 | A Shadow of Light (A Shade of Vampire, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18815695 | The Pecan Man | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18819296 | Hidden | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18867685 | The Atlantis Plague (The Origin Mystery, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18892134 | The Son (Divergent, #0.3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18906484 | The Husband's Secret Free Preview | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18943009 | Rock Bottom (Tristan & Danika, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 18982011 | The Line (Witching Savannah, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 19030845 | Batman: The Dark Knight Returns #1 | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 19095025 | Play (Stage Dive, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 19103097 | The Magician's Land (The Magicians, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 1923820 | Holy Bible: King James Version | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 19351043 | Nimona | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 19351490 | Grimm's Fairy Tales | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 19549841 | Seraphina (Seraphina, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 19747756 | House | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20317106 | هيبتا | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20329634 | Lines of Departure (Frontlines, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20423680 | The Last Town (Wayward Pines, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20438825 | Vanished (Callahan & McLane #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20439328 | How to Be Both | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20509356 | Sand Omnibus (Sand, #1-5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20525628 | How to Build a Girl | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20559676 | Killing Sarai (In the Company of Killers, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20603820 | The Will (Magdalene, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20613920 | Under Locke | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20620995 | Take Me with You | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20639274 | Archer's Voice | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20646604 | Night Owl (Night Owl, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20797535 | A Better World (Brilliance Saga, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20803953 | Bully (Fall Away, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20803962 | Until You (Fall Away, #1.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20829994 | Percy Jackson's Greek Gods (A Percy Jackson and the Olympians Guide) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20874139 | I Am Livia | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20886354 | Skin Deep (Legion, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20894857 | Sleep Tight | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 20980373 | Reasonable Doubt: Volume 2 (Reasonable Doubt, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 21104828 | The Lake House | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 21219083 | The One That Got Away | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 2122216 | Special A, Vol. 1 (Special A, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 21411058 | Bad Romeo (Starcrossed, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 21414439 | Truthwitch (The Witchlands, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 21418017 | The Space Between (Outlander, #7.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 21420473 | The Fixed Trilogy (Fixed, #1-3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 21473305 | Dominic (Slater Brothers, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 21518647 | Axel (Corps Security, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 21518679 | Cage (Corps Security, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 21849362 | The Shadows (Black Dagger Brotherhood, #13) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 21857294 | Reasonable Doubt: Volume 3 (Reasonable Doubt, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 21956060 | Monster in His Eyes (Monster in His Eyes, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22020052 | It Ain't Me, Babe (Hades Hangmen, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22027055 | One Lavender Ribbon | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22027459 | The Atlantis World (The Origin Mystery, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22131009 | Where There's Smoke | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22296542 | Addicted to You (Addicted, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22299763 | Crooked Kingdom (Six of Crows, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22319275 | Yellow Crocus | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22381326 | Half a War (Shattered Sea, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22381892 | Killing Patton: The Strange Death of World War II's Most Audacious General | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22428828 | Welcome to Shadowhunter Academy (Tales from the Shadowhunter Academy, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22443261 | The Rithmatist (The Rithmatist, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22457201 | Hardpressed (Hacker, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22471294 | Black Lies | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22474626 | Hard Limit (Hacker, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22600903 | Where I Belong (Alabama Summer, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22611920 | The Hook Up (Game On, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22738563 | We Should All Be Feminists | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22744701 | My Sister's Grave (Tracy Crosswhite #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22816087 | Seveneves | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22840421 | My Lady Jane (The Lady Janies, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22857396 | Sweet Addiction (Sweet Addiction, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22886612 | Nemesis Games (The Expanse, #5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22895264 | Wicked (A Wicked Saga, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22914448 | The Dead Key | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22915460 | The Glassblower | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22918050 | The Heir (The Selection, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22923997 | Overruled (The Legal Briefs, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 22931009 | Kindle User's Guide | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23122175 | The Friend Zone (Game On, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23158207 | How Google Works | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23207027 | Three Dark Crowns (Three Dark Crowns, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23212667 | All the Missing Girls | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23252517 | The Law of Moses (The Law of Moses, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23355069 | Hero (Hero, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23481669 | Maude | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23485372 | The Master Magician (The Paper Magician Trilogy, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23492288 | Hidden Bodies (You, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23545800 | Kaleidoscope Hearts (Hearts, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23587984 | Maybe Not (Maybe, #1.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23675858 | Departure | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23692271 | Sapiens: A Brief History of Humankind | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23714532 | Beautiful Sacrifice (The Maddox Brothers, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23714544 | Beautiful Burn (The Maddox Brothers, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23743603 | Miramont's Ghost | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23745132 | Wreckage | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 23745189 | The Mermaid's Sister | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24044596 | Kulti | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24228353 | Trail of Broken Wings | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24378015 | Never Never (Never Never, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24429934 | The Einstein Prophecy | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24445517 | Maybe Someday (Maybe, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24473465 | The English Spy (Gabriel Allon, #15) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24473763 | Radiance (Wraith Kings, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24488476 | The Fate of Ten (Lorien Legacies, #6) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24631990 | Silent Scream (D.I. Kim Stone, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24859245 | Stranger Child (DCI Tom Douglas, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24920901 | The Deal (Off-Campus, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24937499 | Her Final Breath (Tracy Crosswhite, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24961498 | The Midwife's Revolt (The Midwife Series, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 24961531 | The Color of Secrets | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25041504 | After You (Me Before You, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25056528 | Sincerely, Carter (Sincerely Carter, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25104491 | The Prettiest One | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25153134 | Follow You Home | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25228579 | The Perfect Son | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25316313 | A Dark Lure | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25451852 | Dawn of Wonder (The Wakening, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25454883 | Never Never: Part Three (Never Never, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 2548866 | James Potter and the Hall of Elders' Crossing (James Potter, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25507925 | Binge | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25564446 | The Air He Breathes (Elements, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25624089 | Killing Reagan: The Violent Assault That Changed a Presidency | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25690958 | Year of Yes: How to Dance It Out, Stand In the Sun and Be Your Own Person | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25693079 | Crooked Little Lies | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25711641 | Tyrant (King, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25801299 | After Anna | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25802884 | Hollywood Dirt (Hollywood Dirt, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25828204 | F*ck Love | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25837338 | The Girl from Krakow | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25837341 | The Good Neighbor | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25866725 | Broken Grace | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25883848 | The Hating Game | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25899336 | When Breath Becomes Air | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 25912358 | A Thousand Boy Kisses | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 26061591 | Extreme Prey (Lucas Davenport, #26) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 26158341 | The Girl With No Past | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 26214866 | In the Clearing (Tracy Crosswhite, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 26224667 | Wrong (Wrong, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 26583370 | Life and Other Near-Death Experiences | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 2678349 | استمتع بحياتك | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 27152124 | Dirty English (English, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 27207654 | Blood Defense (Samantha Brinkman, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 27239265 | The Short Drop (Gibson Vaughn, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 27252717 | The Score (Off-Campus, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 27362503 | It Ends with Us | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 27401883 | When I'm Gone | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 27406436 | The Baller: A Down and Dirty Football Novel | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 27419654 | The Last Girl (The Dominion Trilogy, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 27423283 | The Moonlit Garden | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 2750180 | لا تحزن | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 27810589 | A Death in Sweden | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 27824826 | The Dry (Aaron Falk, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 27868677 | The House by the Lake | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 28233082 | The Girl In The Ice (Detective Erika Foster, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 28240855 | The Girl You Lost | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 28477789 | Stuck-Up Suit | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 28678119 | Paper Princess (The Royals, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 28698036 | Secret History (Mistborn, #3.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 28802599 | The Light of the Fireflies | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 28959148 | We're All Damaged | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 29103028 | The Queen's Poisoner (Kingfountain, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 29104680 | Punk 57 | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 29354916 | The Whistler | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 29367958 | The Wall of Winnipeg and Me | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 29610595 | Too Late | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 29632984 | The Things We Wish Were True | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 29639736 | Everything We Keep (Everything We Keep, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 29925715 | The Sister | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 29981261 | The Butterfly Garden (The Collector #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 29991719 | Royally Screwed (Royally, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 30002998 | Two By Two | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 30013 | Prelude to Foundation | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 30065028 | Fantastic Beasts and Where to Find Them: The Original Screenplay | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 30253700 | Anti-Stepbrother | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 30314465 | No Man's Land (John Puller, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 30364931 | Neighbor Dearest | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 30831912 | Norse Mythology | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 30839185 | Vicious (Sinners of Saint, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 31140847 | Bossman | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 31176886 | The Chemist | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 31194270 | Evelyn, After | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 313256 | Dark Challenge (Dark, #5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 31538647 | Hogwarts: An Incomplete and Unreliable Guide (Pottermore Presents, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 3243517 | رأيت رام الله | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 33288638 | Wait for It | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 3331756 | عائد إلى حيفا | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 3338544 | رحلتي من الشك إلى الإيمان | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 34511 | Monstrous Regiment (Discworld, #31; Industrial Revolution, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 3491072 | حول العالم في 200 يوم | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 353 | Time Enough for Love | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 3554772 | عزازيل | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 356373 | Experiencing God: Knowing and Doing the Will of God, Workbook | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 364826 | سینوهه | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 3831279 | ڤيرتيجو | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 434229 | Cape Fear | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 4502877 | Midnight Sun (Twilight, #1.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 4527502 | The Scarecrow (Jack McEvoy, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 4653511 | رجال في الشمس | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 49552 | The Stranger | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 5048174 | 2BR02B | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 5061675 | A Game of Thrones / A Clash of Kings (A Song of Ice and Fire, #1-2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 5153799 | Father Mine (Black Dagger Brotherhood, #6.5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 5295735 | الحرافيش | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 536790 | Trumps of Doom (The Chronicles of Amber, #6) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 5607622 | قمر على سمرقند | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 5664022 | حوار مع صديقي الملحد | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 581552 | In the Penal Colony | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 5883777 | The Holy Bible: English Standard Version | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 59978 | Sin City, Vol. 4: That Yellow Bastard (Sin City, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 606818 | Holy Blood, Holy Grail | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 6251012 | UR | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 6324090 | Alice's Adventures in Wonderland | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 6357022 | Club Shadowlands (Masters of the Shadowlands, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 6387565 | Witch & Wizard (Witch & Wizard, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 6388558 | The Warlord Wants Forever (Immortals After Dark #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 6395833 | Guts | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 646462 | The Qur'an / القرآن الكريم | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 6506085 | Food Inc.: A Participant Guide: How Industrial Food is Making Us Sicker, Fatter, and Poorer-And What You Can Do About It | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 6604887 | أنت لي | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 6614886 | زغازيغ | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 6630751 | First to Kill (Nathan McBride, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 682745 | The Basketball Diaries | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 71458 | Stupeur et tremblements | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 716696 | رباعيات خيام | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 7190 | The Three Musketeers | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 7604 | Lolita | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 769658 | Battlefield Earth: A Saga of the Year 3000 | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 7704143 | تراب الماس | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 7743783 | The Unidentified Redhead (Redhead, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 7785207 | The Mating  (Law of the Lycans, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 7897478 | The Bedwetter: Stories of Courage, Redemption, and Pee | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 7913305 | The Immortals of Meluha (Shiva Trilogy, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 7981206 | Dead Reckoning (Sookie Stackhouse, #11) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 8113940 | Witches of East End (The Beauchamp Family, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 8135807 | Rock Me (Ross Siblings, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 8152697 | Wishin' and Hopin' | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 8177526 | Fate (My Blood Approves, #2) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 8428984 | Half Way Home | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 8575295 | Wisdom (My Blood Approves, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 8593026 | Hostile Witness (Witness Series, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 887201 | Faeries | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 90010010 | Untitled Manuscript | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 9279734 | Forever Mine (The Moreno Brothers, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 9305362 | Captive Prince (Captive Prince, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 9409469 | The Gray Wolf Throne (Seven Realms, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 9418327 | Bossypants | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 9496240 | The Hangman's Daughter (The Hangman's Daughter, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 95558 | Solaris | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 9635657 | Tales from a Not-So-Talented Pop Star (Dork Diaries, #3) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 9722217 | رغم الفراق | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 9832370 | BookRags Summary:  A Storm of Swords | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 9858714 | The Mind Readers (Mind Readers, #1) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 9915707 | Endure (Need, #4) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 9925913 | Shock Wave (Virgil Flowers, #5) | isbn/no-usable-isbn | isbn13/no-usable-isbn | isbn13/no-usable-isbn | `` |
| 10088913 | مخطوطة بن إسحاق: مدينة الموتى | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78977629706e+12` |
| 10169662 | Never Knowing | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78031259568e+12` |
| 10468258 | The Finding (Law of the Lycans, #5) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001119121e+12` |
| 105189 | The Story of a Shipwrecked Sailor | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78014015755e+12` |
| 10706934 | بيكاسو وستاربكس | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78995356624e+12` |
| 10801027 | Cross My Heart (Cross My Heart, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `1.2300000055e+12` |
| 11201007 | Hearts in Darkness (Hearts in Darkness, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001266893e+12` |
| 11239856 | Maid for the Billionaire (Legacy Collection, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001248214e+12` |
| 11382346 | That Boy (That Boy, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78061540899e+12` |
| 11436 | Rejoice (Redemption, #4) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78084238688e+12` |
| 114954 | The Opal Deception  (Artemis Fowl, #4) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.781423104e+12` |
| 11808919 | Maid for Love (Gansett Island Series, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78098347544e+12` |
| 11942408 | شاب كشك في رحلة البحث عن الجادون | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78977633759e+12` |
| 11995136 | محال | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78977093092e+12` |
| 12288282 | Gunmetal Magic (Kate Daniels, #5.5) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78110158519e+12` |
| 12351649 | Perfection (Neighbor from Hell, #2) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78098321255e+12` |
| 12415695 | كخه يا بابا | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78995356618e+12` |
| 12513614 | Captive in the Dark (The Dark Duet, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001144494e+12` |
| 12755792 | A Hidden Fire (Elemental Mysteries, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001328325e+12` |
| 128711 | The Yacoubian Building | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78006087814e+12` |
| 13345975 | Avoiding Commitment (Avoiding, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78147627142e+12` |
| 13448656 | Motorcycle Man (Dream Man, #4) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78147624895e+12` |
| 13489518 | Out of the Dark (The Grey Wolves, #4) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001474615e+12` |
| 13502970 | Incendiary (The Premonition, #4) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78147920712e+12` |
| 13640229 | Creed (Unfinished Hero, #2) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78130116082e+12` |
| 13649056 | Try Me (One Night with Sole Regret, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001463181e+12` |
| 1464757 | Edensor (Tetralogi Laskar Pelangi, #3) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78979122702e+12` |
| 15742039 | Breathe (Colorado Mountain, #4) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78147614539e+12` |
| 15752757 | Rock Chick Revolution (Rock Chick, #8) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78130189562e+12` |
| 15757434 | Crash (Crash, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001497963e+12` |
| 15762657 | Seducing Cinderella (Fighting for Love, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001497768e+12` |
| 15835685 | Clash (Crash, #2) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001513629e+12` |
| 15981894 | Devoured (Devoured, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7813001603e+12` |
| 15993374 | Charade (Games, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001549587e+12` |
| 16001893 | Down to You (The Bad Boys, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78130171672e+12` |
| 16031620 | الفيل الأزرق | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78977093155e+12` |
| 16042305 | Love Left Behind | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78098847441e+12` |
| 16076787 | السنجة | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78999219574e+12` |
| 16081961 | الأسود يليق بك | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7899532672e+12` |
| 16109563 | Undeniable (Undeniable, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94004498098e+12` |
| 16114861 | Unbeautifully (Undeniable, #2) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78130134567e+12` |
| 16114862 | Unattainable (Undeniable, #3) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7813019853e+12` |
| 16170522 | صانع الظلام | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78999219576e+12` |
| 16170625 | المانيفستو | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78999219584e+12` |
| 16279715 | Connected (Connections, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78098894191e+12` |
| 168571 | Shadow Prey (Lucas Davenport, #2) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78042520885e+12` |
| 17032328 | If You Stay (Beautifully Broken, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001624931e+12` |
| 17167042 | Fighting for Flight (Fighting, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78130112018e+12` |
| 17190226 | Surrender Your Love (Surrender Your Love, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7814823343e+12` |
| 17201095 | Play with Me (With Me in Seattle, #3) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001631951e+12` |
| 17201104 | Rock with Me (With Me in Seattle, #4) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001655433e+12` |
| 17314430 | Wait for You (Wait for You, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001623192e+12` |
| 17316075 | Second Chance Boyfriend (One Week Girlfriend, #2) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001648708e+12` |
| 17339590 | "حكايات فرغلي المستكاوي "حكايتى مع كفر السحلاوية | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7897748813e+12` |
| 17448960 | Falling into You (Falling, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001635694e+12` |
| 17800786 | Damaged 2 (Damaged, #2) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78098554735e+12` |
| 17810 | In the Miso Soup | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7801430357e+12` |
| 17903381 | Diary ng Panget | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78971057365e+12` |
| 17930773 | Found in You (Fixed, #2) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7816270402e+12` |
| 17948485 | Friend-Zoned (Friend-Zoned, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94004447015e+12` |
| 181077 | Sadako and the Thousand Paper Cranes | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78069811803e+12` |
| 18111281 | A Long Way Home | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78067007704e+12` |
| 18130 | A Wind in the Door (A Wrinkle in Time Quintet, #2) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78044048762e+12` |
| 18301124 | Making Faces | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78130167387e+12` |
| 18337259 | A Game of Thrones: Comic Book, Issue 1 | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78034553615e+12` |
| 18468559 | Raw (RAW Family, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94014886112e+12` |
| 18478222 | Twelve Years a Slave | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7809897948e+12` |
| 18711993 | فلتغفري | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78614432065e+12` |
| 18781540 | Until Lilly (Until, #3) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78131050159e+12` |
| 19000 | The Constant Gardener | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7807432872e+12` |
| 190361 | Obsidian Butterfly (Anita Blake, Vampire Hunter, #9) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78051513451e+12` |
| 19494 | The Spy Who Came In from the Cold | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78074344253e+12` |
| 20316309 | في قلبي أنثى عبرية | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78977637644e+12` |
| 20348781 | Loving Mr. Daniels | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78069222191e+12` |
| 204479 | Spying in High Heels (High Heels, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7809848574e+12` |
| 20761374 | Reasonable Doubt: Volume 1 (Reasonable Doubt, #1) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94014954334e+12` |
| 21394850 | أقوم قيلا | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7860301506e+12` |
| 21456940 | 1919 | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78977093293e+12` |
| 21843117 | Scoring Wilder | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7809904904e+12` |
| 22009741 | The Woman Who Stole My Life | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78071815535e+12` |
| 22669832 | Bright Side (Bright Side, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78099114022e+12` |
| 23357188 | Bound by Honor (Born in Blood Mafia Chronicles, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78131173642e+12` |
| 23844390 | The Pact | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78150572452e+12` |
| 24019 | The New Best Recipe | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78093618475e+12` |
| 24480276 | The Versions of Us | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78147460016e+12` |
| 24766 | The Secret Hour (Midnighters, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78006051954e+12` |
| 2501453 | عابر سرير | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78995389059e+12` |
| 2501455 | فوضى الحواس | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78995389058e+12` |
| 2501458 | ذاكرة الجسد | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78995389053e+12` |
| 2508854 | تاكسي: حواديت المشاوير | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `6.22110201718e+12` |
| 25558608 | A Torch Against the Night (An Ember in the Ashes, #2) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78000825045e+12` |
| 262731 | The Definitive Book of Body Language | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78055380472e+12` |
| 266904 | The Penderwicks: A Summer Tale of Four Sisters, Two Rabbits, and a Very Interesting Boy (The Penderwicks #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78044042048e+12` |
| 27864391 | The Danish Girl | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78147460157e+12` |
| 2804776 | One Fifth Avenue | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78140139027e+12` |
| 3240691 | واحة الغروب | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `6.22110201942e+12` |
| 32423 | Watchers | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7804251888e+12` |
| 3301759 | The Murders in the Rue Morgue | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7814961664e+12` |
| 3320520 | The 3 Mistakes of My Life | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78812911373e+12` |
| 337058 | Jacob Have I Loved | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78006440369e+12` |
| 3692091 | 1/4 جرام | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78977175496e+12` |
| 374233 | If on a Winter's Night a Traveler | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78008861945e+12` |
| 4212386 | Maryamah Karpov: Mimpi-mimpi Lintang (Tetralogi Laskar Pelangi, #4) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78979122745e+12` |
| 43325 | Nothing Lasts Forever | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78044635474e+12` |
| 4566934 | Winter in Tokyo | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78979223984e+12` |
| 4634266 | NARUTO -ナルト- 巻ノ四十三 | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78408874553e+12` |
| 4865 | How to Win Friends and Influence People | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78067172365e+12` |
| 49245 | His Needs, Her Needs: Building an Affair-Proof Marriage | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78080071789e+12` |
| 5557442 | ظل الأفعى | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78977092281e+12` |
| 56674 | Empire of the Sun (Empire of the Sun, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78074326523e+12` |
| 6145711 | The Walking Dead, Vol. 10: What We Become | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78160706076e+12` |
| 61915 | Falling Free (Vorkosigan Saga, #4) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78188677854e+12` |
| 6621287 | com نسيان | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78995389122e+12` |
| 6686671 | Electric Daisy, Vol. 1 (Dengeki Daisy, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78979233558e+12` |
| 6688121 | Negeri 5 Menara (Negeri 5 Menara, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78979224862e+12` |
| 6765740 | Perahu Kertas | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78979122778e+12` |
| 6891433 | Panserhjerte (Harry Hole, #8) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78820319552e+12` |
| 7119070 | أحببتك أكثر مما ينبغي | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78995371806e+12` |
| 7147831 | Min kamp 1 (Min kamp #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78825257459e+12` |
| 7194 | The Club Dumas | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78015603283e+12` |
| 7352220 | Black Butler, Vol. 3 (Black Butler, #3) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78979276087e+12` |
| 7603 | Reading Lolita in Tehran | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78081297106e+12` |
| 7701043 | الجزار | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78977778055e+12` |
| 7824768 | ليتها تقرأ | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.7899537151e+12` |
| 8239301 | الطنطورية | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78977092829e+12` |
| 82817 | Zoya | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78987566161e+12` |
| 8343444 | Daun Yang Jatuh Tak Pernah Membenci Angin | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78979225781e+12` |
| 8407173 | Jasper Jones | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78174237262e+12` |
| 84525 | What Got You Here Won't Get You There: How Successful People Become Even More Successful | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78178125156e+12` |
| 8542839 | Fire Burn and Cauldron Bubble (Jolie Wilkins, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78145236586e+12` |
| 8635145 | Embrace (The Violet Eden Chapters, #1) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78073441185e+12` |
| 8732 | The Red Pony | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78014196282e+12` |
| 8793878 | The Keeping (Law of the Lycans, #3) | isbn13/float-precision-lost | isbn13/lost-precision,bad-prefix | isbn13/lost-precision,bad-prefix | `2.94001108065e+12` |
| 8952 | Killers of the Dawn (Cirque Du Freak, #9) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78031601667e+12` |
| 8957 | Tunnels of Blood (Cirque Du Freak, #3) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78031690573e+12` |
| 8965 | The Vampire's Assistant (Cirque Du Freak, #2) | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78031690572e+12` |
| 90010008 | The Glass Aviary | isbn13/invalid-characters | isbn13/bad-characters | isbn13/bad-characters | `04390A3483` |
| 90010009 | Borrowed Light | isbn13/wrong-length | isbn13/bad-length | isbn13/bad-length | `15287463097` |
| 9086994 | Aleph | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78857542577e+12` |
| 9666241 | النبطي | isbn13/float-precision-lost | isbn13/lost-precision | isbn13/lost-precision | `9.78977092938e+12` |

## Why our data differs

Checked by reading all three `ingest.py` files and `rules.md` directly, not just diffing the databases. One piece of context first: Abigail had already run this same comparison against Anthony's database on her own (see her `comparison.md`) and changed her own code to match his on two points. That's why, in every category below, Anthony's and Abigail's databases agree with each other on every row, and mine is the one that differs from both.

Four distinct causes. All four are gaps in `rules.md` itself -- not bugs, and not something either test suite could have caught.

### 1. ISBN check-digit casing (`031200009x` vs. `031200009X`)

The raw source CSV already has it lowercase (`books-batch2.csv`, line 27). Anthony's `ingest.py` has a `clean()` step whose docstring literally says "strip separators... uppercase a final x" -- carried over from his own original week3 `rules.md`, which had that rule explicitly. It never made it into our agreed `rules.md`: section 1's "formatted with hyphens/spaces" row only says to strip separators, nothing about letter case. My code does exactly what `rules.md` says -- strip separators, leave the characters alone -- so the lowercase `x` passes through unchanged.

**Rule gap.** `rules.md` never says to normalize case, so "leave it alone" (mine) and "uppercase it" (Anthony's and Abigail's) are both faithful to what each of us actually had written down. Neither test suite catches it because neither one's examples include a lowercase trailing `x`.

### 2. `wrong-length` vs. `bad-checksum` after a failed zero-pad

`rules.md` section 1 says a short all-numeric ISBN-10 gets zero-padded "only if the padded result then passes the checksum" -- and stops there. It never says what to call it when padding is tried and the checksum still fails. Anthony's `check_isbn_column()` explicitly returns `BAD_CHECKSUM` in that case (treating the 10-digit padded candidate as the thing that failed the check); my code falls through to the same generic `wrong-length` branch used for a short value that was never retried at all.

**Rule gap.** Section 1's example table has no example of a short value that still fails after padding, so neither test suite was ever forced to settle on one answer.

### 3. Which field a "no usable ISBN" warning is filed under, and its wording

`rules.md` requires a warning when both `isbn` and `isbn13` are blank, but never says which column name the warning record itself should use, or what exact string the reason should be. My code files it under `isbn` as `no-usable-isbn`; Anthony's and Abigail's file it under `isbn13`. The same gap shows up in the wording for other warnings too: `lost-precision` (theirs) vs. `float-precision-lost` (mine), `bad-characters` vs. `invalid-characters`, `bad-length` vs. `wrong-length`.

**Rule gap** -- and the clearest example of a gap tests structurally cannot see: each test suite (mine included) only asserts that the code matches its own author's chosen string. Three self-consistent, all-green test suites can still describe three different vocabularies for the exact same event. It took comparing the databases directly, not running any test suite, to surface this.

### 4. `NULL` vs. `''` for a missing text field

`rules.md` section 5 (schema) never says whether a blank CSV cell should be stored as SQL `NULL` or an empty string. Anthony's `analyse_row()` has an explicit line -- `None if blank(raw.get(c)) else raw[c]` -- that converts every blank field to `None`, for every column, on purpose. My code has no equivalent step; a blank CSV cell is just whatever Python's `csv.reader` gives back (`''`), stored as-is, because nothing in my code ever decided it should be anything else.

**Rule gap**, again invisible to both test suites for the same reason as #3.

### What this means

All four differences trace back to the same root: `rules.md` is genuinely silent on each of these points -- not ambiguous, just silent. None are bugs. Every implementation does exactly what its own author intended, consistently, and passes its own tests. That is also *why* the tests didn't catch any of it: a test suite can only check code against the rules it was given, and when the rules don't address a question, a passing suite means "this code agrees with itself," not "this code agrees with anyone else's." The database comparison -- not the tests -- is what was actually capable of finding these four gaps.

If the group wants `rules.md` to fully pin down behavior, these are the four things worth adding: whether to normalize ISBN check-digit case, what to call a zero-pad that still fails its checksum, which field and exact wording a blank-ISBN warning uses, and whether missing text is stored as `NULL` or `''`.

### `consolidated-books.db`

Since all four differences are rule gaps rather than disagreements about what `rules.md` actually says, they're resolvable by majority vote rather than by a group decision -- `consolidated-books.db` does exactly that: for every book and every column (run timestamps excluded, since those never agree across three separate real ingestion runs by design), the value at least 2 of the 3 databases hold exactly is used. Every single disagreement in this comparison had a clean 2-of-3 majority -- **0 conflicts** (see `majority-conflicts.txt`).

Because Anthony's and Abigail's databases already agree with each other on every row (Abigail aligned her own code to match his before this comparison), the majority vote resolves to their shared value every time there's a disagreement. In other words, `consolidated-books.db` is identical to Anthony's and Abigail's databases on every field that ever differed from mine -- majority rule didn't invent a new answer here, it just formalizes "where two of us already agree, go with that" as a reproducible, documented script rather than a one-off hand edit.
