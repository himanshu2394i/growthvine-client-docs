# C split (Mint Billboard)

Source of truth is the **live fund page**, not an old prototype experiment:

- `frontend/home-app/src/fund/SplitLayout.jsx`
- `frontend/home-app/src/fund/fund.css` (`.proto-split`, `.mint-board`, `.mint-brief`)
- `frontend/home-app/src/fund/mintMotion.js` (web-only lighting)
- Tabs: `Performance.jsx`, `Rolling.jsx`, `Portfolio.jsx`, `Info.jsx`, `Faqs.jsx`

Print and slides copy this grammar. They do not copy browser tricks (sticky
chapter rail, scroll spy, anime.js, hover scale on donuts).

## Two worlds

The root `.proto-split` is mint `#B1F0DB` with Foundation Grey ink. The brief
then switches to a white field with a 1px ink rule on top. That is the only
theme switch.

| | Mint outdoor board | White brief |
|---|---|---|
| Markup | `.mint-board` | `.mint-brief` |
| Ground | Mint (the whole proto root) | Clarity White |
| Ink | Foundation Grey | Foundation Grey |
| Graphic | `.mint-wash` (white radial) + `.mint-bands` fingerprint at **14%** opacity, one crop, bleeding off the top-right | None. No sticky mint orb, no second fingerprint. That treatment was tried and removed. |
| Type | `h1` Poppins 600, `clamp(2.2rem, 5vw, 4.2rem)`, line-height 0.94, **max-width 18ch** | Chapter `h3` about 1.55–2.05rem, tracking -0.035em |
| Data | Three stairs, exit-load pair, one CTA | Hairline metrics, mustard table headers, stacked donut+ledger mixes |

Do not add a purple hero after the mint board. Do not put a fingerprint tile under
brief body copy.

## Cover stack (top to bottom)

On the live page the mint field also carries a **breadcrumb** (Mutual Funds /
category / scheme) in `.mint-crumbs`, then the board.

The board itself, from `SplitLayout.jsx`, is only:

1. White radial wash (`.mint-wash`)
2. Fingerprint (`FingerprintBands.mint-bands`)
3. Scheme **short name** as `h1` (no category line, no as-of, no subtext)
4. Stairs: **3 year return**, **5 year return**, **Assets**
5. Exit load: big rate, then icon + "Exit load" + optional note
6. CTA: **Download the app**

Category and as-of live in the **brief** (rank card, fund info "Data as of"). Do
not invent a cover kicker to "complete" the poster.

### Grid

`grid-template-columns: minmax(0, 42rem) minmax(8rem, 1fr)`. Copy max-width 42rem,
aligned to the bottom. Fingerprint sits in the leftover column, `width: min(88vw, 920px)`, `right: -8%`, `top: -22%`, `color: #1D1D1B`, `opacity: 0.14`.

Full-bleed mint in print: `@page { margin: 0 }` or a slide fill. `min-height` on
the web is `calc(100dvh - 8.5rem)` so the board fills the first viewport under
the site header. A PDF cover should still feel like a poster, not a skinny banner.

### Stairs (not a bar chart)

Widths are a **fixed cascade**, not mapped from the numbers:

| Row | Label | `--mint-bar` / `data-scale` |
|---|---|---|
| `.is-a` | 3 year return | `1` |
| `.is-b` | 5 year return | `0.78` |
| `.is-c` | Assets | `0.54` |

Fill is Foundation Grey at **16%** opacity (`rgba(29, 29, 27, 0.16)`). Label left,
tabular figure right. Do not paint each stair mint / mustard / peach. Do not
scale the 3Y bar to 12.5% of the page because the return is 12.5%.

### CTA

Pill (`border-radius: 999px`), Foundation Grey fill `#1D1D1B`, **white** type
`#FFFFFF`, label "Download the app". Hover on the web is Mustard `#F1F68E` with
ink type. One CTA intent. In print, the rest state is enough.

### Motion (web only)

`mintMotion.js` draws the fingerprint, unmasks the title, scales the stairs from
0 to 1 / 0.78 / 0.54, and counts the tickers. No translate vibration, no magnetic
pointer, no fingerprint opacity loop. PDF/PPTX ship the **lit** rest state.
Honor `prefers-reduced-motion` if you animate an HTML preview.

## White brief

`.mint-brief` is `grid-template-columns: 220px minmax(0, 1fr)`, padding about 5rem
top, white, ink hairline on the top edge.

### Chapter rail (web)

Swiss outline: numbered `01`…`0n` plus the section label, idle opacity 0.42,
active opacity 1 + a 2px ink tick on the left rule. Those numbers are **jump
navigation**, not decorative "INDEX" eyebrows. Phone: sticky pill, snap chips,
black/white active chip.

Print/PPTX: one chapter per page or slide. Title is the section name (`Fund
information`). You may keep a small `01` as a caption. Do not print `08 / INDEX`.

### Cards

No drop shadow, no 22px radius. Vertical rhythm is padding + a 1px rule at
`rgba(29, 29, 27, 0.14)` (~14% ink). Sections fade/rise on the web (`InView`);
print is static.

### Rank / metrics

Hairline metric cells: small label (~0.68rem), value ~1.45rem / 600, 2-col on
wide pages (`brief-facts`). Rank block also shows stars and composite score, with
as-of in the card-sub. Do not nth-child rainbow fills.

### Tables

`table.data th` is **Mustard** `#F1F68E` with ink type. That is the live highlight,
used once per table, not a page wash. Relative-returns cells can mark a beat
without inventing traffic-light green.

### Composition (stacked mixes)

Live `Portfolio.jsx` stacks every mix in `.mix-board` (`grid-template-columns: 1fr`):
asset allocation, market cap, credit, instruments. Each `MixFigure` is **donut
(~280px) + mustard-header table**, not one lead figure and four tiny pies, and
not five equal pies in a row. Order: asset → cap → credit → instruments.
Concentration is a separate hairline metric pair (top 5 / top 10).

Slice colors stay inside the brand book (`MixFigure.jsx` `MIX`): indigo, ink,
peach, mint, mustard. No traffic-light green/red.

### Quartile

Live treatment is the same MixFigure: donut + table, Q1 mint, Q2 mustard, Q3
peach, Q4 ink. Not a 14px strip. A stacked "quartile tower" is only a print
fallback if a donut will not reproduce.

### Names and about

AMC and manager use `.brief-house-name` (large Poppins). About is a lede
(`.brief-statement .prose`, ~1.28–1.65rem). No mint highlighter behind the name.

### FAQ

Hairline rows. `summary::after` is a **1.75rem mint disc** with ink `+`, rotating
45° to × when open. Answer is type with a clip-path unmask on the web. Open row
is not a mustard block.

## Print / slide translation

| Web | PDF / PPTX |
|---|---|
| Sticky swiss rail | One chapter per page/slide. Title is the rail. |
| Full-viewport mint board | Full-bleed mint first page/slide, same 42rem copy column + fingerprint crop |
| anime.js board lighting | Static lit board |
| Hover scale on donuts | Still donut, no hover |
| InView brief rise | Static |
| Breadcrumb on mint | Optional small line above the name, or omit |

## What C split is not

- Not Ionic Wealth (no cobalt, Geist, or their logo)
- Not the pre-split fund-detail admin cards (shadows, 22px radii, equal pie rows)
- Not "use all five brand colors on every page"
- Not a sticky mint orb on the white brief (removed in live code)
- Not stairs whose length equals the return percentage
