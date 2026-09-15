# Design tokens

Read straight from `Growthvine Brandbook.pdf` (repo root). Values here are the source
of truth for any client document — don't approximate them from a screenshot.

## Color

| Name | Hex | RGB | CMYK | Role |
|---|---|---|---|---|
| Vine Indigo | `#9B81F5` | 155, 129, 245 | 50, 50, 0, 0 | Primary. Trust, stability. Contrasts against both black and white. |
| Foundation Grey | `#1D1D1B` | 29, 29, 27 | 70, 65, 65, 75 | Ink / dark ground. Not pure black. |
| Clarity White | `#FFFFFF` | 255, 255, 255 | 0, 0, 0, 0 | Ground. |
| Mint | `#B1F0DB` | 177, 240, 219 | 30, 0, 20, 0 | Secondary. Growth, freshness. |
| Peach | `#FFBB90` | 255, 187, 144 | 0, 30, 45, 0 | Secondary. Warmth. |
| Mustard | `#F1F68E` | 241, 246, 142 | 10, 0, 55, 0 | Secondary. Optimism. |

Palette discipline: one primary (Vine Indigo), the neutrals (Foundation Grey /
Clarity White) carry most of a page, and the three secondaries are used to
differentiate categories in charts (composition slices, quartiles) — not as random
decoration. Don't invent a fourth secondary; if a chart needs a 6th color, reuse one
of the five at reduced opacity rather than picking something new.

## Typography

Font: **Poppins** (Google Fonts). Two weights cover everything:

- **Semibold (600)** — all headings, the oversized stat figures, chapter titles.
- **Regular (400)** — body copy, table cells, captions.

There is no defined numeric type scale in the brand book beyond "headings strong and
attention-grabbing, body clean and legible" — the web prototypes' scale is a
reasonable default to carry over:

| Role | Size (rough, scale to the page) |
|---|---|
| Oversized stat | 48–72pt |
| Chapter / page title | 28–36pt |
| Section heading | 18–22pt |
| Body | 10–11pt |
| Caption / eyebrow label | 7–8pt, letter-spaced, uppercase |

**Font availability matters more in a document than on a web page** — a PDF or PPT can
ship to a machine that doesn't have Poppins installed:

- **PDF**: embed the font (reportlab: register the Poppins `.ttf`; browser-print
  route: `@font-face` with the Google Fonts URL bakes it into the rendered PDF
  automatically since the browser rasterizes before printing).
- **PPTX**: PowerPoint renders with whatever's on the *viewer's* machine unless the
  font is embedded in the file (`File > Options > Save > Embed fonts` equivalent, or
  python-pptx doesn't support embedding directly — note this limitation to the user
  rather than silently shipping a file that'll fall back to Calibri on their client's
  laptop). If font embedding isn't practical, say so and either pick a very close
  system-available fallback (e.g. Montserrat, also on Google Fonts and visually
  close) or export the deck as PDF instead.

## Logo

Two lockups:

- **Primary horizontal** — icon + "Growthvine" wordmark side by side. Default choice.
- **Secondary vertical** — icon above wordmark. Only when the horizontal genuinely
  doesn't fit the space (a square badge, a narrow column).

Both have a tagline variant ("Own Your Financial Future" set beneath the wordmark) and
a plain variant. Use the tagline variant on a cover or closing page; plain elsewhere.

**Color rule**: the wordmark is Foundation Grey + Vine Indigo (light grounds) or white
+ Vine Indigo (dark grounds, `assets/logo-inverse.webp` in this skill). Monochrome
(all-white or all-grey) variants exist for constrained print contexts (single-color
printing, watermarks) — don't invent an in-between tint.

**Minimum sizes** (below these, drop to the icon alone):
- Horizontal, tagline: 4.8in / 350px wide
- Horizontal, no tagline: 2.75in / 200px wide
- Vertical, tagline: 3.5in / 250px wide
- Vertical, no tagline: 2in / 150px wide

**Clear space**: on all sides, leave at least the width of the icon's "G" stroke area
(call it ~15% of the lockup's total width if eyeballing) — don't crowd it with a rule
line, a page edge, or another logo.

## Brand don'ts (from the brand book's own "Logo Don'ts" page)

- Don't stretch or squeeze the logo to fit a space — resize proportionally.
- Don't place the colored or black wordmark on Vine Indigo or Foundation Grey
  backgrounds — use the white/inverse lockup instead.
- Don't recreate the wordmark in a different typeface.
- Don't add drop shadows, bevels, or other effects that weren't part of the approved
  mark.
- Don't recolor outside the palette above.
- Don't change the icon-to-wordmark ratio or move the tagline.

## Decorative elements

- **Fingerprint arcs** — the icon's concentric ring motif, scaled up hugely and placed
  bleeding off one corner of a colored panel, at 10–20% opacity. This is what gives
  the mint/indigo panels their texture in the prototypes. Bundled here as
  `assets/fp-arcs.svg`, stroke hardcoded white — reuse it, editing the `stroke="#ffffff"`
  value (a plain text find-replace) to match whatever panel color it sits on; don't
  redraw the arcs themselves, they need to trace the icon's actual curves exactly.
- **Dense fingerprint texture** — a different, denser fingerprint line-art used as a
  near-invisible (5–10% opacity) background texture in the brand book's own sample
  creative. Optional; the arcs motif above is the one actually used in the built
  prototypes and is the simpler, safer default for a document that needs to render
  reliably at various sizes and print resolutions.
