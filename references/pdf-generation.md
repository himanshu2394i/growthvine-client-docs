# Generating a PDF

Two real routes, pick based on how visual the page needs to be:

## Route A — HTML/CSS → PDF (default for anything with a colored panel, a donut, or a waffle)

Write the page as plain HTML/CSS using the tokens in `design-tokens.md`, then print it
to PDF with a headless browser. This is the only route that reliably gets Poppins,
exact hex colors, hairline rules, and the SVG donut/waffle pixel-correct — because
it's rendering the same technology the approved design was reviewed in, not a
reinterpretation of it.

Check what's actually available before picking a tool:

```bash
python -c "import playwright" 2>&1   # best fidelity, needs `playwright install chromium` once
python -c "import weasyprint" 2>&1   # pure Python, no browser binary needed, slightly weaker CSS support
```

**Playwright** (preferred if installed):

```python
from playwright.sync_api import sync_playwright

def html_to_pdf(html: str, out_path: str, page_size="A4"):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")  # lets @font-face / SVG finish loading
        page.pdf(path=out_path, format=page_size, print_background=True)  # print_background is required — without it every colored panel renders white
        browser.close()
```

**Weasyprint** fallback:

```python
from weasyprint import HTML
HTML(string=html).write_pdf(out_path)
```

CSS gotchas specific to print:

- Set `@page { size: A4; margin: 0; }` and build the bleed/margin into your layout
  instead, so a full-bleed colored panel actually reaches the page edge.
- `print_background=True` (Playwright) or WeasyPrint's default — without it, every
  background color and the donut/waffle SVG's fills can vanish in the PDF.
- No `position: sticky`. There is no scroll in a PDF. Each chapter is a full page;
  the pin is a static left column. C-split cover = full-bleed mint page (see
  `c-split.md` and `figures.md`).
- Load Poppins via `<link>` to Google Fonts, or inline it as a base64 `@font-face` if
  the render environment has no network access.

## Page breaks

One chapter = one A4 page. Cover is its own page. The mock's pin + flow stay together.

```css
@page { size: A4; margin: 0; }
.page { width: 210mm; height: 297mm; overflow: hidden; page-break-after: always; page-break-inside: avoid; }
.page:last-child { page-break-after: auto; }
.pairs, .gv-chart, .waffle, .cy-strip, .tower, .steps { page-break-inside: avoid; }
```

| Sheet | What goes on it |
|---|---|
| 1 | Ink logo bar (optional but preferred) + mint board. `page-break-after: always`. |
| 2…n-1 | One pin + its flow. Do not split them. `page-break-after: always`. |
| Last pin or FAQ | Same, but `page-break-after: auto` so you do not ship a blank sheet. |
| FAQ | After the last pin, own page, no pin column. Skip if there are no questions. |

Never:

- Start 01 / Fund performance on the cover sheet
- Break a pin from its flow
- Let a waffle, rolling line, paired-bar block, calendar strip, quartile tower, or
  riskometer split across a fold
- Copy the web fingerprint at `width: 920px` onto A4 (rings will sit on the stairs).
  Clip it to the right column; keep a **12mm** gap. CSS is in `figures.md`.

If a flow does not fit: drop the least important block (usually a second table).
Do not invent a pin-less continuation page.

Cover page order, matching the mock:

1. Inverse logo on a 12–14mm Foundation Grey strip (`assets/logo-inverse.png`)
2. Mint board: crumbs, 18ch name, fingerprint in the **right** column only,
   stairs in the left column, exit load, one CTA
3. As-of line at the foot of that mint page

## Figures

Use `scripts/charts.py` (`donut_svg`, `waffle_cells`, `chart_svg`) and the CSS in
`references/figures.md`. Those are the mock C-split diagrams. Do not swap them
for a default matplotlib pie.

## Route B — reportlab (for a plain, mostly-tabular one-pager where exact CSS fidelity doesn't matter)

The `anthropic-skills:pdf` skill (already available in this project) covers the
mechanics — `SimpleDocTemplate`/`Platypus` for multi-section flow, `Paragraph` styles
for text. Two things that skill's generic guidance won't tell you, specific to this
brand:

1. **Register Poppins explicitly** — reportlab's built-in fonts don't include it, and
   the output will silently be Helvetica otherwise:

   ```python
   from reportlab.pdfbase import pdfmetrics
   from reportlab.pdfbase.ttfonts import TTFont

   pdfmetrics.registerFont(TTFont("Poppins", "Poppins-Regular.ttf"))
   pdfmetrics.registerFont(TTFont("Poppins-SemiBold", "Poppins-SemiBold.ttf"))
   ```

   (Download the two weights from Google Fonts once, keep them alongside the
   generation script — don't re-fetch per run.)

2. **Donut/waffle as images, not native shapes** — reportlab has no donut primitive.
   Get the SVG from `scripts/charts.py`'s `donut_svg()`/`waffle_cells()`, rasterize it
   (`cairosvg.svg2png(bytestring=svg.encode(), write_to="chart.png", scale=3)` for
   crisp print resolution), then place it with `reportlab.platypus.Image`.

Reach for Route A whenever the page has more than one colored panel or any chart —
Route B is for the rare case that's genuinely just a data table.
