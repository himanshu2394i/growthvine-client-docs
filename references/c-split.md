# C split (Mint Billboard)

Source of truth is the **live fund page** as of this file:

- `frontend/home-app/src/fund/SplitLayout.jsx` (`mint-board` + `brief brief-c`)
- `frontend/home-app/src/fund/fund.css` (`.proto-split`, `.mint-board`, `.brief-c`)
- `frontend/home-app/src/fund/mintMotion.js` (cover lighting only)
- Tabs in `frontend/home-app/src/fund/tabs/`

Print and slides copy this grammar. They do not copy sticky pins, scroll spy,
anime.js, or hover scale on donuts.

## Two parts

1. **Mint outdoor board** (`.mint-board`): first viewport. Unchanged poster.
2. **Pin brief** (`.brief.brief-c`): every chapter is a two-column **pin + flow**.
   There is no leftover swiss chapter rail and no `.mint-brief` shell. CSS still
   contains dead `.mint-brief` rules; live JSX does not use them. Do not copy that
   shell.

The root `.proto-split` is mint `#B1F0DB` with Foundation Grey ink so the cover
and breadcrumbs sit on mint. The brief then uses a white flow column. Pins
**alternate mint and ink**. That stripe is the C-split signature, not a random
mid-page theme flip. Do not add a third ground (beige, purple, peach wash).

| | Mint outdoor board | Pin (left) | Flow (right) |
|---|---|---|---|
| Ground | Mint | Even chapters mint, odd chapters ink `#1D1D1B` | White |
| Graphic | Wash + fingerprint at 14%, top-right crop | Fingerprint crop bottom-left, 14% on mint / 10% white on ink | None |
| Type | `h1` 18ch, `clamp(2.2rem, 5vw, 4.2rem)`, leading 0.94 | `01 / Title`, then `hero-n` `clamp(4rem, 8vw, 7rem)` | Chapter `h3`, body, tables |
| Data | Stairs, exit load, one CTA | One oversized stat + 2–3 `dl` rows | Charts, mixes, hairline facts |

## Cover (`.mint-board`)

Live markup in `SplitLayout.jsx`. Breadcrumb `.mint-crumbs` sits in `.mint-tools`
above the board (Mutual Funds / category / scheme).

Board only:

1. `.mint-wash` white radial
2. `FingerprintBands.mint-bands` (ink, opacity **0.14**, `right: -8%`, `top: -22%`, up to 920px)
3. `h1` short name, **max-width 18ch**, no category, no as-of, no subtext
4. Stairs: 3 year return, 5 year return, Assets
5. Exit load: rate, then icon + "Exit load" + optional note
6. CTA: Download the app

Grid: `minmax(0, 42rem) minmax(8rem, 1fr)`, copy max-width 42rem, `min-height: calc(100dvh - 8.5rem)`.

### Stairs

Fixed cascade, not a chart of the values:

| Row | Label | scale |
|---|---|---|
| `.is-a` | 3 year return | `1` |
| `.is-b` | 5 year return | `0.78` |
| `.is-c` | Assets | `0.54` |

Fill `rgba(29, 29, 27, 0.16)`. Do not paint stairs in three brand colors. Do not
set bar length to the return percentage.

### CTA

Pill, `#1D1D1B` fill, `#FFFFFF` type. Hover on web: Mustard `#F1F68E` + ink type.

### Motion (web only)

`mintMotion.js`: draw fingerprint, unmask title, scale stairs, count tickers.
No vibration, no magnetic pointer. PDF/PPTX = lit rest state.

## Pin brief (`.brief-c`)

Copied from mock-c-split. Each `sectionsFor(KIND)` item is:

```
section.chapter
  pin-col[.dark]
    aside.pin
      FingerprintBands.arcs
      span.n     → "01 / Fund performance"
      div.hero-n → oversized number + optional <small> unit
      p.lede
      dl         → 2–3 dt/dd rows
  div.flow     → SectionBody (the tab)
```

Chapter `0, 2, 4…` mint pin. Chapter `1, 3, 5…` `.pin-col.dark` (ink field, white
type, mint `01 / Title`, white fingerprint at 10%).

Grid: `minmax(18rem, 26rem) minmax(0, 1fr)`, ink `border-top`. Pin is `position: sticky; top: 5.5rem; min-height: calc(100vh - 5.5rem)` on desktop. Under 760px the pin stacks above the flow and is no longer sticky.

`01 / Fund performance` is the live pin caption (number + real section name).
That is allowed. Do not invent `08 / INDEX` or `00 / INDEX` as a label with no
section name.

FAQs sit **after** the chapters, full-width white (`.brief-faq-reveal`), not in a pin.

### Pin numbers (`pinProps` in SplitLayout.jsx)

Use these jobs when a dump/connector can support them. Skip a row if the figure
is missing.

| Chapter id | Oversized | Small | Typical rows |
|---|---|---|---|
| performance | `#rank` | ` of N` | Star rating, composite score, 3Y vs index |
| rolling | `%` in top two quartiles, else median | ` top half` or ` median` | Median window, worst window |
| portfolio / holdings | Lead mix (equity % or AAA+Sov % or top 5) | unit label | Top 5, top 10 |
| metrics / riskometer | Riskometer name or Sharpe | | Max drawdown, Sharpe |
| drawdown | Max drawdown % | | Peak date, trough date |
| portfolio-stats | YTM | ` YTM` | Modified duration, average maturity |
| info | NAV `₹` | | Expense ratio, AUM |

Lede is one short sentence (pin `max-width: 30ch`). Portfolio pin currently says
"Each square below is 1% of the fund" even though the flow still draws **donuts**.
In a document, either ship a waffle in the flow or change the lede. Do not promise
squares and draw a ring.

### Flow

White, padding ~3rem 3rem 5rem, gap 4rem. Cards have no shadow, no radius, no
fill. Mixes still stack as MixFigure donut + table in `.mix-board`. Holdings also
uses `Ring` for concentration / overlap.

`table.data th` under `.proto-split` is still Mustard. `.brief table.t` (if used)
is ink hairline headers, muted uppercase labels, no mustard fill. Prefer the
Mustard header when copying live fund tables.

FAQ: mint 1.75rem disc on `+`, rotates 45° when open. Not a mustard open block.

## Print / slide

| Web | PDF / PPTX |
|---|---|
| Sticky pin | Static left column, same mint/ink stripe, same fingerprint crop |
| Full-viewport mint board | Full-bleed first page |
| One chapter = pin + flow | One page/slide: left pin, right flow (or pin on top if the page is too narrow) |
| anime.js / InView | Static lit |
| Hover donut | Still donut |

Do not flatten C split into a white report with a mint cover. The **alternating
pin** is the brief.

## What C split is not

- Not Ionic Wealth
- Not a leftover swiss tick-rail on a flat white letter
- Not a sticky mint orb behind the whole brief (removed)
- Not stairs scaled to the return
- Not five equal pies in a row (stacked MixFigures in the flow are fine)
- Not `08 / INDEX` without a real section name
