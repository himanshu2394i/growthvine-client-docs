---
name: growthvine-client-docs
description: Use when making a Growthvine client-facing PDF, PowerPoint, fact sheet, one-pager, proposal, portfolio review, or any document from dumped fund numbers, a pasted file, or a named scheme. Trigger even if the user only pastes data and says "make this a PDF" or "turn this into a deck," without naming colors, Poppins, C split, Mint Billboard, or the brand. Also use when inventing a new document section that must still look like Growthvine, or when live fund figures should come from the Growthvine connector.
---

# Growthvine client documents

A complete production skill, not a color cheat sheet. It interviews for the job,
pulls or accepts data, then designs and writes a file that looks like Growthvine's
**C split** (Mint Billboard cover + white research brief) and the Brand Book.

Two documents made months apart should still look like the same house.

## Do this first: briefing

Do not generate the file until the briefing below is answered. If the user already
answered a slot in the same message, skip that slot. Ask the rest in **one** pass,
then wait.

Read **`references/briefing.md`** and ask:

1. **What are we making?** Fact sheet, portfolio review, one-pager, proposal, or
   something else they name.
2. **What file?** PDF, PPTX, both, or an HTML print preview.
3. **Where does the data come from?** A dump in this chat (paste, file, screenshot),
   live figures from the **Growthvine connector**, or dump as the story with the
   connector filling gaps. Ask this even when they already pasted numbers: confirm
   that dump is the source of truth.
4. **Who is it for, and what tone?** Advisor-to-client (default), sales proposal,
   internal research, or SEBI-cautious facts-only. See the tone menu in briefing.md.
5. **Which sections?** Show the known chapter menu. Ask what to keep, skip, and
   **what extra chapters they want that are not on the menu**. New chapters are
   allowed. New visual languages are not.
6. **Length?** Let the data decide, or a fixed page/slide count.

If they say "just make it," still confirm **source + file type + tone** in one short
question. Guessing those three is how generic decks get shipped.

## Then get the numbers

Never invent a return, rank, NAV, AUM, TER, benchmark name, holding, or as-of date.

- **Dump in chat:** that dump is canonical. Do not "improve" a pasted figure with a
  live pull unless they asked for a refresh.
- **Named fund, no dump:** use the Growthvine connector. Read
  **`references/data.md`** first (`get_analysis_guide` before any derived math).
- **Both:** dump wins on conflict; connector only fills holes they approved.

If a section has no numbers, drop the section or ask. Do not write "N/A" into a
chart. Print the **as-of date** on every page or slide that shows returns, NAV, or
rank.

## Then design

Read **`references/c-split.md`** before the first layout. Read
**`references/design-tokens.md`** before any cover, logo, or color field.

Quick lock (full rules live in those files):

| Role | Value |
|---|---|
| Type | Poppins 600 headings, Poppins 400 body. Never Inter, Geist, Calibri, Times. |
| Primary | Vine Indigo `#9B81F5` |
| Ink / dark ground | Foundation Grey `#1D1D1B` |
| Ground | Clarity White `#FFFFFF` |
| Secondaries | Mint `#B1F0DB`, Peach `#FFBB90`, Mustard `#F1F68E` |
| Logo on indigo or ink | Inverse lockup only (`assets/logo-inverse.webp`) |
| Fingerprint | One cropped graphic. Never a tile. Color fields 10–20% opacity. Texture 5–10%. |

**C split is two worlds, not two themes:**

1. **Mint outdoor board** (cover / at-a-glance): mint field, huge scheme name
   (about 18ch), fingerprint at the edge, stair bars for the few stats that earn
   the first page. Do not restyle this into a purple hero or a card grid.
2. **White brief** (everything after): research letter, hairline tables, one quiet
   fingerprint or mint orb in the background, not a new fill on every metric cell.

Sticky chapter rails are a browser trick. In PDF/PPTX, **one chapter = one page or
slide**. Same panel + well, just static.

Known chapters, layout families, and how to invent a chapter this skill has never
seen: **`references/new-sections.md`**. Components (donut, waffle, stairs, hairline
table, paired bars, quartile tower): **`references/components.md`**.

Copy for the client: no hype verbs, no fake-precise specs, no em-dash. One CTA
intent per document (usually "Download the app" or nothing).

## Then generate the file

- PDF → **`references/pdf-generation.md`**
- PPTX → **`references/pptx-generation.md`**

Use **`scripts/charts.py`** for donut and waffle so they match the approved web math:

```python
from charts import donut_svg, waffle_cells, COLORS

donut_svg([("Equity", 58.4, COLORS["indigo"]), ("Debt", 36.2, COLORS["ink"]), ("Other", 5.4, COLORS["peach"])])
waffle_cells([("Equity", 58.4, COLORS["indigo"]), ("Debt", 36.2, COLORS["ink"]), ("Other", 5.4, COLORS["peach"])])
```

## Red flags (stop and restart the briefing)

- Generating before source, file type, and tone are known
- Painting each NAV/AUM cell a different brand color
- Five equal donuts, traffic-light green/red, Inter/Geist
- Colored or black logo on Vine Indigo or Foundation Grey
- Fingerprint tiled like wallpaper
- Invented numbers, or a live pull silently overwriting a dump
- A new section that also invents a new palette or typeface

## If something here feels stale

Tokens and C-split rules were read from Growthvine's Brand Book and the Split board
prototype in the private product repo. If a live Growthvine page or a document
someone else produced disagrees, trust that, flag it, and do not guess a replacement.
