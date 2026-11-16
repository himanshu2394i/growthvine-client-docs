# scenes.json

One file describes the whole document. `scripts/render.py` turns it into a PDF
or PPT. All visible text is written as strings exactly as it should appear;
numbers in `value` / `values` fields are only for drawing chart geometry.

```json
{
  "meta": {
    "client": "Client name",
    "rm": "Advisor name",
    "date": "16 November 2026",
    "footer": "Private and confidential, Prepared for discussion"
  },
  "palette": {"Core Growth": "indigo", "Stability": "mint",
              "Diversifier": "peach", "High Growth Alternatives": "mustard"},
  "scenes": [ ... ]
}
```

`palette` colours: `indigo`, `mint`, `peach`, `mustard`, `ink`. Labels without a
palette entry get colours in that order.

## Fields every content scene may have

| Field | Meaning |
|---|---|
| `title` | Headline that states the takeaway. Required. Max 90 characters. |
| `kicker` | Small label above the title (e.g. the act name). Optional. |
| `as_of` | "Data as of 13 Oct 2026". Required on any scene with returns, NAV, ranks or holdings. |
| `note` | `{"label": "Why this split", "text": "...", "tone": "info" \| "caution"}`. Optional. `caution` for risks to watch and not-a-guarantee notes. Text max 220 characters. |

## Scene types

| `type` | Required fields | Limits |
|---|---|---|
| `cover` | `eyebrow`, `title` (client name), `logline`, `facts: [{label, value}]` | facts 1-4 |
| `act` | `number` ("01"), `title`, `logline` | |
| `statement` | `title`, `text` (the big sentence), optional `sub` | text max 160 chars |
| `stats` | `title`, `stats: [{value, label}]` | 1-4 stats |
| `donut` | `title`, `slices: [{label, value, display, share}]`, optional `center` | 2-7 slices |
| `table` | `title`, `columns: [...]`, `rows: [[...]]`, optional `total: [...]`, optional `heat: true` | max 8 columns, 11 rows |
| `bars` | `title`, `series: [...]`, `categories: [{label, values: [...], display: [...]}]` | 1-3 series, max 8 categories |
| `timeline` | `title`, `stops: [{label, text}]` | 2-6 stops |
| `steps` | `title`, `steps: [{title, text}]` | 2-5 steps |
| `text` | `title`, `paragraphs: [...]` | max 700 chars in total |
| `close` | `title`, `contact`, `disclaimer`, optional `rm`, optional `sources` | disclaimer and sources max 900 chars each |
| `fund` | `title` (fund name), `stats: [{value, label}]`, `facts: [{label, value}]`, `what`, optional `watch`, optional `what_label` / `watch_label` | 1-3 stats, 1-7 facts; `what` max 260, `watch` max 220 chars. Put "its role" in `note` |
| `panels` | `title`, `layout` (`2`, `3`, `2x2`, `1+2`, `2+1`), `panels: [...]`, optional `strip: [{value, label}]` | panel count must match the layout (2, 3, 4, 3, 3); strip up to 6 |
| `line` | `title`, `x: [labels]`, `series: [{name, values, end, style}]` | 1-5 series, 2-400 points; one value per `x` label; `end` is the label shown at the line's end (e.g. "₹2.11 L"); `style: "index"` draws a dashed market line |

`heat: true` shades numeric cells by size (darker = bigger), for cross-tabs.
Numeric-looking columns are right-aligned automatically.

## Basic disclaimer (until compliance wording exists)

"Investments in mutual funds, SIFs, PMS, AIFs and structured products are subject
to market risks. Past performance does not indicate future results. Please read
all scheme-related documents carefully before investing. Figures marked as
expected are estimates, not guarantees."

## Panels (inside a `panels` scene)

Each panel has a `kind`, an optional small `title`, and:

| `kind` | Fields |
|---|---|
| `bars` | `series: [names]`, `categories: [{label, values, display}]` (negative values draw left of zero) |
| `donut` | `slices: [{label, value, display}]`, optional `center` |
| `stack` | `segments: [{label, value, display}]`: one 100% bar with a legend (company size, asset mix, liquidity) |
| `table` | `columns`, `rows` (compact; long tables raise an error, so split or trim) |
| `text` | `bullets: [...]`: two or three insight sentences |
| `stats` | `stats: [{value, label}]` |
| `line` | `x`, `series: [{name, values, end, style}]` |

No text anywhere may contain `·`; validation rejects it.
