# Figures in mock C split

Source: `.superdesign/tmp/mock-c-split.html` plus `mock-core.js`.
That is the C-split document language. Port these figures. Do not
replace them with a generic dashboard chart.

Print has no hover and no Annualised/Absolute or 1Y/3Y/5Y segment
control. Draw the rest state the mock shows (3Y rolling, annualised
paired bars).

## What is executable in this skill

| Figure | Mock | In this skill |
|---|---|---|
| Donut ring | `mock-core.js` `donutSvg` | `scripts/charts.py` `donut_svg()` |
| Waffle 100 cells | `hundred()` + `.waffle` 20-col grid | `waffle_cells()` then CSS in this file |
| Rolling line | `chartSvg` | `scripts/charts.py` `chart_svg()` |
| Fingerprint crop | `fp-arcs` / `BANDS` | `assets/fp-arcs.svg` |
| Inverse logo | `cropped-Logo-Inverse.webp` in the dark header | `assets/logo-inverse.webp` and `.png` |
| G mark | `gv-mark.svg` | `assets/gv-mark.svg` |
| Paired bars | `.pair-bars` CSS | CSS below (no Python) |
| Calendar-year strip | `.cy-strip` | CSS below |
| Quartile tower | `.tower` | CSS below |
| Holdings weight bar | `.rows.hl i` | CSS below |
| Riskometer steps | `.steps` six columns | CSS below |
| Stairs | `.mint-bar-row` 100 / 78 / 54 | CSS in `c-split.md` |

Not in the kit (use a native line/bar only if the mock has no
equivalent): NAV sparkline, capture-ratio scatter, photo heroes.

## Cover: fingerprint vs stairs

On desktop the mint board is a **two-column grid**. Copy + stairs sit
in column 1 (`max-width: 42rem`). The fingerprint is `position:
absolute; right: -8%; top: -22%; width: min(88vw, 920px)` and lives in
the empty right column. Copy is `z-index: 1` so type wins if they
cross.

**Do not paste that 920px crop onto A4.** 920px is almost the full
page, so the rings sit on the stairs. Print:

```css
.cover {
  display: grid;
  grid-template-columns: minmax(0, 118mm) minmax(24mm, 1fr);
  background: #B1F0DB;
  color: #1D1D1B;
}
.cover .mint-copy { grid-column: 1; max-width: 118mm; position: relative; z-index: 1; }
.cover .arcs-slot {
  grid-column: 2;
  position: relative;
  overflow: hidden;
  min-height: 90mm;
}
.cover .arcs-slot svg {
  position: absolute;
  right: -18%;
  top: -22%;
  width: 140mm;   /* not 920px */
  opacity: 0.14;
  color: #1D1D1B;
}
.stairs { margin-top: 12mm; } /* air under the title, still inside column 1 */
```

Keep at least **12mm** between the left edge of the fingerprint slot
and the copy column, and **12mm** between the lowest visible arc and
the first stair if you use absolute placement instead of the grid.
Never let a ring cross a stair fill.

## Logo

The mock puts the **inverse lockup** in the dark site header *above*
the mint board, not on the mint field.

Print: a 12–14mm Foundation Grey bar at the top of page 1, inverse
logo left (`assets/logo-inverse.png`, height ~8mm). Clear space around
the G. Do not put that inverse file on mint.

If you skip the ink bar, use the light lockup on mint: `assets/gv-mark.svg`
(color `#1D1D1B`) plus Poppins 600 `Growth` in ink and `vine` in
`#9B81F5`. That matches `BrandLockup` surface=`light`. Never recreate
the wordmark in another typeface.

Ink pins and indigo fields: inverse lockup only.

## Paired bars (returns vs index)

Solid Vine Indigo = fund. Dashed Foundation Grey outline = index.
Not two fill colors.

```css
.pairs { display: grid; gap: 1.25rem; }
.pair { display: grid; grid-template-columns: 3rem minmax(0, 1fr) 9rem; gap: 1.25rem; align-items: center; }
.pair-bars { display: grid; gap: 5px; }
.pair-bars .f { height: 16px; background: #9B81F5; }
.pair-bars .i { height: 13px; border: 1.5px dashed #1D1D1B; }
```

Bar width is `value / max(fund, index)` of that row set, not a
category scale. Print the fund % large, index % muted, delta with
▲/▼ and the point gap.

## Rolling line

```python
from charts import chart_svg
chart_svg(fund_series, bench_series, ["Jan 2023", "Jun 2024", "Dec 2025"], aria="3Y rolling")
```

Indigo stroke 3.5, last-point circle, optional indigo area at 30% → 0.
Index dashed `5 5`. Hairline y-grid. No chart junk (no legend box, no
gradient besides that area).

## Calendar-year strip

Indigo columns, height = return / max return, rank printed on the bar
(`#3`). Labels under: year, return, `of N`.

```css
.cy-strip { display: flex; align-items: flex-end; gap: 0.75rem; height: 200px; border-bottom: 1px solid #1D1D1B; }
.cy-strip .col { background: #9B81F5; min-height: 2rem; }
```

Negative years still get a short column (min-height), do not invent a
red fill.

## Quartile tower

Four stacked blocks, `flex: share`. Mint / mustard / peach / ink.
Label `Q1`…`Q4` inside. Hairline list of % next to it.

## Waffle

Mock grid is **20 columns** (5 rows × 20), each cell 1%. Use
`waffle_cells()` then:

```css
.waffle { display: grid; grid-template-columns: repeat(20, minmax(0, 1fr)); gap: 2px; }
.waffle i { aspect-ratio: 1; display: block; }
```

Ledger: 10px swatch, label, tabular %.

## Holdings rows

Name left, weight right, a 4px indigo rule under the row whose width
is that holding relative to the largest in the list (`width: rel*100%`).

## Riskometer

Six columns, height `30% + i * 14%`. Filled indigo for bands below
current, Foundation Grey for the current band, `#EDEDEA` for the rest.
Labels under, current label ink + semibold.

## Pin fingerprint

On each pin, one crop, bottom-left, 540px wide, `left: -150px; bottom:
-280px`, opacity 0.14 ink on mint / 0.10 white on ink. Same
`assets/fp-arcs.svg` (stroke `currentColor` or find-replace).
