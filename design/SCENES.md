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
    "footer": "Private and confidential · Prepared for discussion"
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
| `note` | `{"label": "Why this split", "text": "...", "tone": "info" \| "caution"}`. Optional. `caution` for the catch and not-a-guarantee notes. Text max 220 characters. |

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
| `close` | `title`, `contact`, `disclaimer`, optional `rm` | disclaimer max 900 chars |

`heat: true` shades numeric cells by size (darker = bigger), for cross-tabs.
Numeric-looking columns are right-aligned automatically.

## Basic disclaimer (until compliance wording exists)

"Investments in mutual funds, SIFs, PMS, AIFs and structured products are subject
to market risks. Past performance does not indicate future results. Please read
all scheme-related documents carefully before investing. Figures marked as
expected are estimates, not guarantees."
