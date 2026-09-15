# Component construction

Concrete recipes for the components that aren't a standard chart type. For anything
not covered here — a plain line chart, a bar chart — use the target format's native
chart object (matplotlib for PDF, python-pptx's `XL_CHART_TYPE` for PPT) with colors
pulled from `design-tokens.md`, rather than hand-drawing it.

## Donut + legend

The prototypes draw a donut by stacking `stroke-dasharray`'d circles on top of each
other on a `viewBox="0 0 42 42"` canvas with `r="15.915"` — that radius makes the
circle's circumference come out to almost exactly 100 units, so each segment's dash
length can just be its percentage value directly, no circumference math needed per
call. `scripts/charts.py`'s `donut_svg()` is this exact technique ported to Python —
use it rather than re-deriving the trick.

Pair it with a legend as a plain list, not a second chart:

```
● Equity              58.4%
● Debt                36.2%
● Other                5.4%
```

- Live C split uses a **10px filled circle** swatch in the mix table (`.mix-table .dot`).
  Match that. A square swatch is fine only if you are not copying the live mix ledger.
- Label left, value right, tabular-figure alignment (values line up on the decimal /
  percent sign across rows).
- The donut's center can carry a single number — usually the largest slice's value and
  a short label ("58% equity") — never "Total 100%", which tells the reader nothing
  they can't already see from the ring being full.

## Waffle (100-square grid)

A 10×10 or 20×5 grid where each cell is exactly 1% of the total. Reads well in print
because it needs no hover/legend interaction to understand, and it's honest about
partial totals (a composition that sums to 94% just leaves 6 cells uncolored, or
colored a neutral grey — don't stretch the colored cells to fake 100%).

`waffle_cells()` in `scripts/charts.py` does largest-remainder rounding so the 100
cells always account for the full total even when percentages don't divide evenly
(e.g. 58.4% + 36.2% + 5.4% = exactly 100, but 58.4 → floor 58, 36.2 → floor 36, 5.4 →
floor 5 only sums to 99 — the leftover cell goes to whichever slice had the largest
fractional remainder, here Equity's .4). Never round each slice independently and let
the grid over- or under-fill.

## Hairline table

- Rule weight: 0.5–1pt, Foundation Grey at reduced opacity (roughly 12–15%) rather
  than full black — this is what makes the tables in the prototypes feel quiet instead
  of like a spreadsheet.
- Header row: Mustard `#F1F68E` fill, ink type (live `.proto-split table.data th`).
  Body cells have no fill. Do not mustard-wash the whole table or paint zebra rows.
- Numbers right-aligned, tabular figures (`font-variant-numeric: tabular-nums` in CSS;
  in reportlab/python-pptx, this means picking a font/table style where digit widths
  are fixed — Poppins numerals are already reasonably tabular).

## Paired bar (fund vs. benchmark)

Two bars per period, same baseline, different treatment — never two different colors
for "which is which," since that reads as arbitrary:

- **Fund** — solid fill, Vine Indigo.
- **Benchmark** — outline only (1.5pt dashed stroke, no fill), Foundation Grey.

Label each pair with the period (1Y/3Y/5Y), the fund's value large, the benchmark's
value smaller beside it, and a one-line delta ("▲ 1.6 pts ahead" / "▼ 2.3 pts behind")
— color the delta chip Mint (ahead) or Peach (behind), never green/red, which aren't
in the palette and read as a different brand entirely.

## Outdoor stairs (mint board)

Three headline stats on the cover, from live `SplitLayout.jsx`: 3 year return,
5 year return, Assets. Each row is a Foundation Grey wash at 16% opacity
(`rgba(29, 29, 27, 0.16)`). Label left, tabular figure right. One graphic field.
Do not give each stair its own brand fill.

Widths are a **fixed staircase**, not a chart of the values:

- 3Y: 100% (`data-scale="1"`)
- 5Y: 78%
- Assets: 54%

Print: rectangles at those fractions of the copy column. Do not set the 3Y bar
to 12% of the column because the return is 12%.

## Pin column (brief chapter)

Live `.brief-c .pin`. Left column 18–26rem. Even chapters mint + ink fingerprint
at 14%. Odd chapters ink + white type + mint `01 / Title` + white fingerprint at
10%. Stack: caption `01 / {section label}`, `hero-n` number, lede (max ~30ch),
`dl` of 2–3 hairline rows. Sticky on the web; static left column in print.

## Mint disc control (FAQ / expandable)

A 1.75rem circle, fill Mint `#B1F0DB`, ink plus sign. Open state rotates 45° to ×.
The FAQ plus control is a mint disc. Do not reuse that disc as a page background.

## Quartile tower

One bar, four blocks stacked by height/width proportional to time-in-quartile %, each
block's own % printed inside it (not in a separate legend) since there are only four
values and the reader shouldn't have to look elsewhere to read them:

- Q1 (top quartile) — Mint
- Q2 — Mustard
- Q3 — Peach
- Q4 (bottom quartile) — Foundation Grey, white text

That color order (best → worst reading as mint → grey) matches the prototypes and
should stay consistent across every document — don't reassign colors to quartiles
per-document.
