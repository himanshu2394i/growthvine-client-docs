---
name: growthvine-client-docs
description: Apply Growthvine's brand system — Vine Indigo/Foundation Grey/Mint/Peach/Mustard palette, Poppins type, the fingerprint motif, and the donut/waffle/hairline-table component vocabulary from the fund-detail prototypes — whenever generating a client-facing PDF or PowerPoint for Growthvine, e.g. a fund fact sheet, a portfolio review deck, a one-pager, a proposal, or any document meant to go to a client or prospect. Trigger this even when the user just pastes fund numbers and says "make this a PDF" or "turn this into a deck" without naming colors, fonts, or the brand explicitly — matching the identity consistently is the whole point. Read this before reaching for reportlab/python-pptx defaults; its references/ folder has the exact tokens and print/slide translations needed so the output doesn't look like a generic auto-generated report.
---

# Growthvine client documents

Growthvine's brand system — the Growthvine Brand Book plus the fund-detail web
prototypes in Growthvine's product repo (`frontend/home-app/src/prototypes/`,
especially the "Split board" / C design) — distilled into something usable for a PDF
or PPTX. It
exists so a document asked for today and one asked for three months from now look
like they came from the same design system, without re-deriving colors, type, or
layout from scratch each time.

## Before you start

- **Work only from numbers given in the conversation** — pasted text, a file, a
  screenshot. Never invent a return, a rank, an AUM figure, or a benchmark name. If a
  section's numbers aren't available, drop that section rather than guessing or
  writing "N/A" into a chart.
- **Confirm the deliverable** if it's not obvious: PDF or PPTX, one fund or several,
  and whether there's a fixed page/slide count or the data should decide it.
- **Carry the "as of" date.** These are point-in-time figures — print the date
  somewhere on every page/slide that shows returns, NAV, or rank, the same way the
  live fund pages do.

## Brand tokens (quick reference)

| Role | Color |
|---|---|
| Primary | Vine Indigo `#9B81F5` |
| Ink / dark ground | Foundation Grey `#1D1D1B` |
| Ground | Clarity White `#FFFFFF` |
| Secondary | Mint `#B1F0DB`, Peach `#FFBB90`, Mustard `#F1F68E` |

Type is Poppins throughout — **Semibold (600)** for headings, **Regular (400)** for
body. If the rendering pipeline can't load Poppins, say so explicitly and pick a
deliberate fallback (see the font notes in each generation guide) — never let it
silently fall back to Times/Calibri.

The white/inverse logo lockup is bundled at `assets/logo-inverse.webp`. Use it on
Vine Indigo or Foundation Grey grounds — **never place the colored or black logo on
either of those two backgrounds**, it's the one hard rule in the brand book's "Don'ts."

Full palette (RGB/CMYK), the type scale, logo minimum sizes and clear-space rule, and
the brand book's other don'ts are in **`references/design-tokens.md`** — read it
before laying out a cover or header treatment.

## The page/slide grammar

The web prototypes use a sticky side panel that stays pinned while you scroll — that's
a browser-only trick with no equivalent on a printed page or a slide. The honest
translation: **one "chapter" of the web design becomes one PDF page or one PPT
slide** — same colored panel with an oversized stat, same content well, just static
instead of scroll-linked.

A fund document's natural chapter order (skip any chapter the pasted data doesn't
support):

1. **Cover / at-a-glance** — fund name, category, one headline stat (rank, or the
   return that matters most), as-of date.
2. **Performance** — return vs. benchmark by period, rolling-return chart, calendar
   years.
3. **Composition** — asset/credit/market-cap/instrument splits.
4. **Risk** — Sharpe, drawdown, riskometer band.
5. **Fund info / close** — NAV, expense ratio, AUM, exit load, manager, contact.

A portfolio-review deck for several funds is the same grammar repeated per fund, with
one summary chapter up front.

## Components → print/slide

| Web component | Print/slide translation |
|---|---|
| Oversized-stat colored panel | A full-bleed colored band (PDF) or a full colored slide background (PPT) with the number set huge, label beneath, 1–2 lines of context. |
| Donut + legend | Donut chart, legend as a plain hairline-divided list beside it, values right-aligned in tabular figures. Center label names the largest/most relevant slice. |
| Waffle (100-square grid) | Use when a composition has several small slices, or you want a literal "each square = 1%" reading. Always pair with the same legend list as the donut. |
| Hairline table | 0.5–1pt rules, no cell shading, label left (small caps, letter-spaced), value right, tabular figures. |
| Paired bar (fund vs. index) | Solid brand-color bar = fund, dashed-outline bar = benchmark, one pair per period. |
| Quartile tower | One bar split into proportioned blocks by time-in-quartile %, the % labeled directly on each block — not a legend off to the side. |
| Fingerprint arcs | Low-opacity (10–20%) decorative motif in a panel's corner — never under body text. Reuse `assets/fp-arcs.svg` (bundled here) rather than redrawing it. |

Construction detail (exact donut/waffle math, worked examples) is in
**`references/components.md`**.

## Generating the file

Read the matching guide before writing code — each covers font handling, the
donut/waffle fidelity tradeoff, and a working code pattern:

- PDF → **`references/pdf-generation.md`**
- PPTX → **`references/pptx-generation.md`**

Both point to **`scripts/charts.py`**, a small, dependency-free module with the two
components that don't already exist as a standard chart type:

```python
from charts import donut_svg, waffle_cells, COLORS

donut_svg([("Equity", 58.4, COLORS["indigo"]), ("Debt", 36.2, COLORS["ink"]), ("Other", 5.4, COLORS["peach"])])
# -> an <svg> string, viewBox 0 0 42 42, ready to rasterize or embed

waffle_cells([("Equity", 58.4, COLORS["indigo"]), ("Debt", 36.2, COLORS["ink"]), ("Other", 5.4, COLORS["peach"])])
# -> a flat list of exactly 100 hex colors, one per cell, largest-remainder rounded
```

It's a direct port of the same math the web prototypes use (`mock-core.js`'s
`donutSvg`/`hundred`), so a donut drawn this way matches what's already been shown and
approved, not a fresh reinterpretation.

## If something here feels stale

The tokens above were read straight from Growthvine's internal Brand Book and the
fund-detail app's own prototype code, both of which live in Growthvine's private
`Funds-Details` repo, not this one. If a number here doesn't match what's actually
rendered on a Growthvine product or a document someone else produced, trust that over
this file and flag it internally so this skill gets updated — don't guess a
replacement value.
