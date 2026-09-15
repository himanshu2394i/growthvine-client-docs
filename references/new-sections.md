# Inventing a section this skill has not seen

New *content* is expected. A new *brand* is not.

When the user asks for a chapter that is not on the briefing menu (SIP illustration,
tax note, peer set, why-this-category, manager timeline, suitability paragraph,
fee comparison, …), build it from the kit below. Do not reach for Inter, a sixth
hex, equal feature cards, or painted metric tiles.

## Recipe

1. **Name the job in one sentence.** If you cannot, ask them what the page must
   make the reader understand.
2. **Pick a ground.** Cover-like (mint field) only if this *is* a divider or a
   second poster. Otherwise white brief.
3. **Pick exactly one layout family** from the table. One family per page/slide.
4. **One graphic field if needed.** Fingerprint crop on the mint board, or a single
   mustard table header. Not a sticky orb on the white brief.
5. **Numbers only from the agreed source.** If the new chapter needs a figure
   you do not have, ask or drop it.
6. **As-of date** if the page shows returns, NAV, rank, or holdings.

## Layout families (use these, then stop)

| Family | When | How |
|---|---|---|
| **Outdoor stairs** | Three cover stats | Mint board; grey washes at fixed 100 / 78 / 54; label / figure. Not scaled to the return. |
| **Oversized stat panel** | One number is the point (rank, drawdown, TER) | Full-bleed mint *or* a left third of indigo/ink with inverse type. Huge figure, short label |
| **Stacked mix** | Asset / cap / credit / instruments | Each mix is donut (~280px) + mustard-header table, stacked 1fr, not a row of equal pies |
| **Hairline facts** | NAV, dates, TER, AUM, category | 2-col on desktop/page, 1-col on a narrow slide. No cell paint |
| **Donut + ledger** | A mix that sums toward 100% | One ring, square swatches, values right, tabular figures |
| **Waffle** | Many small slices, or "each square is 1%" | 100 cells, largest-remainder rounding via `scripts/charts.py` |
| **Paired bars** | Fund vs benchmark by period | Solid indigo = fund, dashed ink outline = index |
| **Quartile tower** | Time in Q1–Q4 | Mint / mustard / peach / ink blocks, % inside the block |
| **Lede** | About, suitability, tax note, "why this category" | Headline + body max ~65ch. No split-header of giant title vs floating blurb |
| **House name** | AMC, manager, trustee | Oversized name, then a short paragraph |
| **FAQ list** | Questions from data | Hairline rows, mint disc on the control, answer as type |
| **Peer strip** | 2–5 named funds | Hairline table or paired bars. Connector: `compare_funds`, not a loop of detail calls |

A page with eight chapters still needs several families across the document, but
**this page** only gets one.

If none of the families fit, combine **lede + hairline facts** on the same page.
Do not invent family #12 on the fly (bento of six tinted cards, photo hero,
progress-bar score tracks).

## Worked shape (imagined chapter: "Why this category")

- Ground: white brief
- Family: lede
- Title: the category name in plain language
- Body: ≤25 words on what the category does, then a hairline row for category
  average TER or return **from `get_category_stats`**, with as-of
- Graphic: none, or the brief fingerprint already on the document
- Not: three equal "benefit" cards in peach/mint/mustard

## Worked shape (imagined chapter: "SIP for this scheme")

- Only if they asked and the dump or connector can support an illustration
- Family: oversized stat (illustrated value) + hairline assumptions under it
- Label assumptions as assumptions, never as live NAV history
- Do not invent a 12% market return because it "looks typical"

## Checks before you ship a new chapter

- Same Poppins, same five colors
- Same corner logic as the rest of the file (sharp, not mixed radius systems)
- No second CTA with the same intent as the cover
- No em-dash in client-visible strings
- Readable type on mint and on white (ink on mint, ink on white; inverse type
  only on indigo/ink)
