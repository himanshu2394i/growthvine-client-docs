# Generating a PPTX

Use **python-pptx** (the `anthropic-skills:pptx` skill, already available in this
project, covers the general mechanics — slide layouts, text frames, tables). Two
brand-specific decisions to make deliberately rather than defaulting:

## Colors and type on native shapes

```python
from pptx.util import Pt
from pptx.dml.color import RGBColor

INDIGO = RGBColor(0x9B, 0x81, 0xF5)
INK    = RGBColor(0x1D, 0x1D, 0x1B)
MINT   = RGBColor(0xB1, 0xF0, 0xDB)
PEACH  = RGBColor(0xFF, 0xBB, 0x90)
MUSTARD = RGBColor(0xF1, 0xF6, 0x8E)

run.font.name = "Poppins"            # PowerPoint needs only the *name* here —
run.font.size = Pt(11)               # actual rendering depends on the font being
run.font.color.rgb = INK             # present on whoever opens the file, see below
```

**Font availability**: python-pptx can set the font *name* on every run, but it can't
embed the font file into the `.pptx` the way PowerPoint's own "Embed fonts" option
does. If Poppins isn't installed on the client's machine, PowerPoint silently
substitutes a default (usually Calibri) and the whole brand feel is gone. Decide
explicitly:

- If the deck will only ever be opened on machines you control (or presented from
  your own laptop), Poppins-as-name is fine.
- If it's going to a client who'll open it themselves, either accept a close
  Google-Fonts fallback that's more likely to be present (Montserrat is visually
  close and common), or export the finished deck to PDF as well and send both.

## The donut/waffle tradeoff

Two options, pick based on whether the client needs to *edit* the chart later:

**Native chart** (editable in PowerPoint, harder to match the exact web look):

```python
from pptx.chart.data import ChartData
from pptx.enum.chart import XL_CHART_TYPE

chart_data = ChartData()
chart_data.categories = ["Equity", "Debt", "Other"]
chart_data.add_series("Allocation", (58.4, 36.2, 5.4))
graphic_frame = slide.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, x, y, cx, cy, chart_data)
# Color each point to match the brand palette — python-pptx doesn't do this by
# series color alone for a doughnut (each point needs its own fill):
chart = graphic_frame.chart
plot = chart.plots[0]
for point, color in zip(plot.series[0].points, [INDIGO, INK, PEACH]):
    point.format.fill.solid()
    point.format.fill.fore_color.rgb = color
# python-pptx has no built-in "center label" for a doughnut — place a text box
# on top of the chart's known center coordinates if you need one.
```

**Image drop-in** (pixel-identical to the web design, not editable):

```python
import cairosvg
from charts import donut_svg, COLORS

svg = donut_svg([("Equity", 58.4, COLORS["indigo"]), ("Debt", 36.2, COLORS["ink"]), ("Other", 5.4, COLORS["peach"])])
cairosvg.svg2png(bytestring=svg.encode(), write_to="/tmp/donut.png", scale=4)
slide.shapes.add_picture("/tmp/donut.png", x, y, height=chart_height)
```

Default to the image route when visual fidelity to the approved design matters more
than the client being able to tweak the chart themselves — which, for a fund
composition chart, is almost always. Use the native chart route only if the client has
explicitly asked to be able to edit the numbers in PowerPoint directly.

## Layout

One "chapter" (see `SKILL.md`'s page/slide grammar) per slide. The colored panel
becomes either the whole slide background (`slide.background.fill.solid()`) for a
cover/divider slide, or a colored rectangle covering roughly the left third for a
content slide carrying an oversized stat — mirroring the "Split board" web layout's
proportions rather than centering everything, which is the generic-deck default this
skill exists to avoid.
