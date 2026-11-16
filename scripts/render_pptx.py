"""PPT drawing for render.py (python-pptx). Same layout numbers as the PDF;
tables and charts are native so advisors can edit them in PowerPoint."""
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.oxml.ns import qn
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Pt

from render import (ASSETS, MARK, MARK_RATIO, shot_for, BAR, COLORS, CONTENT_BOTTOM, FOOT_Y, GREY, H, LINE, M,
                    MINT_TINT, NOTE_H, PEACH_TINT, SOFT, W, blend, is_numeric, palette,
                    to_number)

REG, SEMI = "Poppins", "Poppins SemiBold"
INK, INDIGO, WHITE = COLORS["ink"], COLORS["indigo"], COLORS["white"]
ALIGN = {"left": PP_ALIGN.LEFT, "right": PP_ALIGN.RIGHT, "center": PP_ALIGN.CENTER}


def rgb(hex_):
    return RGBColor.from_string(hex_.lstrip("#"))


class Slide:
    def __init__(self, prs, doc, n, total):
        self.s = prs.slides.add_slide(prs.slide_layouts[6])  # blank
        self.doc, self.n, self.total = doc, n, total

    def rect(self, x, y, w, h, fill, radius=False, shape=None):
        sh = self.s.shapes.add_shape(shape or (MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE),
                                     Pt(x), Pt(y), Pt(w), Pt(h))
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(fill)
        sh.line.fill.background()
        sh.shadow.inherit = False
        if radius:
            sh.adjustments[0] = 0.12
        return sh

    def text(self, x, y, w, h, s, size, font=REG, color=INK, align="left", anchor=MSO_ANCHOR.TOP, spacing=None):
        tb = self.s.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = anchor
        para = tf.paragraphs[0]
        para.alignment = ALIGN[align]
        if spacing:
            para.line_spacing = spacing
        run = para.add_run()
        run.text = s
        run.font.size = Pt(size)
        run.font.name = font
        run.font.color.rgb = rgb(color)
        return tb

    def image(self, name, x, y, h):
        return self.s.shapes.add_picture(str(ASSETS / "logos" / name), Pt(x), Pt(y), height=Pt(h))

    def mark(self):
        """Place only the on-slide part of the mark: PowerPoint shows anything
        hanging off the slide while editing, so crop instead of overhanging."""
        x, y, h = shot_for(self.doc, self.n)
        w = h * MARK_RATIO
        left, top = max(x, 0), max(y, 0)
        right, bottom = min(x + w, W), min(y + h, H)
        pic = self.s.shapes.add_picture(str(MARK), Pt(left), Pt(top), Pt(right - left), Pt(bottom - top))
        pic.crop_left, pic.crop_right = (left - x) / w, (x + w - right) / w
        pic.crop_top, pic.crop_bottom = (top - y) / h, (y + h - bottom) / h

    def dark(self):
        self.rect(0, 0, W, H, INK)
        self.mark()

    def counter(self, color):
        self.text(W - M - 80, FOOT_Y, 80, 12, f"{self.n:02d} / {self.total:02d}", 8, REG, color, "right")

    def content_frame(self, sc):
        self.rect(0, 0, W, H, WHITE)
        self.rect(0, 0, W, BAR, INK)
        self.rect(0, H - BAR, W, BAR, INK)
        top = 40
        if sc.get("kicker"):
            self.text(M, top, 500, 14, sc["kicker"].upper(), 9, SEMI, INDIGO)
            top += 20
        if sc.get("as_of"):
            self.text(W - M - 220, 42, 220, 12, sc["as_of"], 8.5, REG, GREY, "right")
        # ponytail: character-count estimate (~44 per line at 25pt, allowing for a
        # wider fallback font when Poppins isn't installed); measure if it misfires.
        lines = 1 if len(sc["title"]) <= 44 else 2
        self.text(M, top, W - 2 * M - 150, 31 * lines, sc["title"], 25, SEMI, INK, spacing=1.0)
        top += 31 * lines
        pic = self.image("logo-light.png", M, FOOT_Y - 3, 13)
        footer = self.doc.get("meta", {}).get("footer", "")
        if footer:
            self.text(M + pic.width.pt + 12, FOOT_Y, 500, 12, footer, 8, REG, GREY)
        self.counter(GREY)
        return top + 26

    def note(self, sc):
        n = sc.get("note")
        if not n:
            return CONTENT_BOTTOM
        y = CONTENT_BOTTOM - NOTE_H
        self.rect(M, y, W - 2 * M, NOTE_H, PEACH_TINT if n.get("tone") == "caution" else MINT_TINT, radius=True)
        self.text(M + 20, y + 10, 600, 12, n.get("label", "").upper(), 8.5, SEMI, INK)
        self.text(M + 20, y + 26, W - 2 * M - 40, 28, n["text"], 11, REG, INK)
        return y - 18


def cover(sl, sc):
    sl.dark()
    sl.image("logo-dark.png", M, 44, 30)
    sl.text(M, 150, 600, 16, sc["eyebrow"].upper(), 11, SEMI, INDIGO)
    sl.text(M, 168, 700, 72, sc["title"], 60, SEMI, WHITE)
    sl.text(M, 262, 560, 60, sc["logline"], 17, REG, SOFT)
    sl.rect(M, 340, 64, 3, INDIGO)
    col = (W - 2 * M) / len(sc["facts"])
    for i, f in enumerate(sc["facts"]):
        x = M + i * col
        sl.text(x, 420, col - 16, 14, f["label"].upper(), 8.5, SEMI, SOFT)
        sl.text(x, 438, col - 16, 44, f["value"], 17, SEMI, WHITE)
    meta = sl.doc.get("meta", {})
    credit = " · ".join(v for v in (meta.get("rm") and f"Prepared by {meta['rm']}", meta.get("date")) if v)
    if credit:
        sl.text(M, FOOT_Y, 500, 12, credit, 8.5, REG, SOFT)


def act(sl, sc):
    sl.dark()
    sl.text(M, 194, 40, 18, sc["number"], 13, SEMI, INDIGO)
    sl.rect(M + 30, 203, 48, 2, INDIGO)
    sl.text(M, 218, 700, 64, sc["title"], 52, SEMI, WHITE)
    sl.text(M, 296, 600, 56, sc["logline"], 18, REG, SOFT)
    sl.counter(SOFT)


def statement(sl, sc):
    top = sl.content_frame(sc)
    bottom = sl.note(sc)
    mid = top + (bottom - top) / 2 - 50
    sl.rect(M, mid, 4, 96, INDIGO)
    sl.text(M + 28, mid, 700, 84, sc["text"], 30, SEMI, INK, spacing=1.05)
    if sc.get("sub"):
        sl.text(M + 28, mid + 98, 640, 44, sc["sub"], 14, REG, GREY)


def stats(sl, sc):
    top = sl.content_frame(sc)
    bottom = sl.note(sc)
    items = sc["stats"]
    col = (W - 2 * M) / len(items)
    y = top + max(0, (bottom - top - 150) / 2)
    for i, st in enumerate(items):
        x = M + i * col
        sl.rect(x, y, 28, 3, INDIGO)
        sl.text(x, y + 18, col - 24, 60, st["value"], 46 if len(items) < 4 else 38, SEMI, INK)
        sl.text(x, y + 90, col - 36, 50, st["label"], 14, REG, GREY)


def donut(sl, sc):
    top = sl.content_frame(sc)
    bottom = sl.note(sc)
    slices = sc["slices"]
    colors = palette(sl.doc, [s["label"] for s in slices])
    r = min(130, (bottom - top) / 2 - 4)
    cx, cy = M + 150, top + (bottom - top) / 2
    data = CategoryChartData()
    data.categories = [s["label"] for s in slices]
    data.add_series("Share", [s["value"] for s in slices])
    gf = sl.s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Pt(cx - r), Pt(cy - r), Pt(2 * r), Pt(2 * r), data)
    chart = gf.chart
    chart.has_legend = False
    chart.has_title = False
    plot = chart.plots[0]
    hole = plot._element.find(qn("c:holeSize"))
    if hole is None:
        hole = plot._element.makeelement(qn("c:holeSize"), {})
        plot._element.append(hole)
    hole.set("val", "62")
    for i, s in enumerate(slices):
        pt = plot.series[0].points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = rgb(colors[s["label"]])
        pt.format.line.color.rgb = rgb(WHITE)
    if sc.get("center"):
        sl.text(cx - 70, cy - 12, 140, 24, sc["center"], 19, SEMI, INK, "center")
    x0, x1 = M + 360, W - M
    row = min(44, (bottom - top) / len(slices))
    y = cy - row * len(slices) / 2
    for s in slices:
        sl.rect(x0, y + row / 2 - 6, 12, 12, colors[s["label"]], radius=True)
        sl.text(x0 + 24, y + row / 2 - 9, 260, 18, s["label"], 13, REG, INK)
        sl.text(x1 - 230, y + row / 2 - 9, 140, 18, s["display"], 13, SEMI, INK, "right")
        sl.text(x1 - 80, y + row / 2 - 9, 80, 18, s["share"], 13, REG, GREY, "right")
        sl.rect(x0, y + row - 1, x1 - x0, 1, LINE)
        y += row


def table(sl, sc):
    top = sl.content_frame(sc)
    bottom = sl.note(sc)
    cols, rows, total = sc["columns"], sc["rows"], sc.get("total")
    body = rows + ([total] if total else [])
    n = len(cols)
    width = W - 2 * M
    first = width * (0.32 if n > 3 else 0.45)
    rest = (width - first) / max(1, n - 1)
    numeric = [j > 0 and all(is_numeric(r[j]) for r in body) for j in range(n)]
    row_h = min(32, (bottom - top) / (len(body) + 1))
    size = 11 if row_h >= 28 else 10
    heat_max = max([to_number(r[j]) or 0 for r in rows for j in range(1, n) if numeric[j]] or [1]) or 1
    gf = sl.s.shapes.add_table(len(body) + 1, n, Pt(M), Pt(top), Pt(width), Pt(row_h * (len(body) + 1)))
    tbl = gf.table
    tbl.first_row = tbl.horz_banding = False
    tbl.columns[0].width = Pt(first)
    for j in range(1, n):
        tbl.columns[j].width = Pt(rest)
    last_is_total = cols[-1].lower() == "total"

    def fill(i, j, text, font, color, bg):
        cell = tbl.cell(i, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(bg)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = cell.margin_right = Pt(10)
        tf = cell.text_frame
        tf.text = ""
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT if numeric[j] else PP_ALIGN.LEFT
        run = p.add_run()
        run.text = str(text)
        run.font.size, run.font.name = Pt(size), font
        run.font.color.rgb = rgb(color)

    for j, h in enumerate(cols):
        fill(0, j, h, SEMI, WHITE, INK)
    for i, r in enumerate(rows, 1):
        for j, v in enumerate(r):
            bg = WHITE
            if sc.get("heat") and numeric[j] and not (last_is_total and j == n - 1):
                val = to_number(v)
                if val:
                    bg = blend(WHITE, INDIGO, 0.1 + 0.5 * val / heat_max)
            fill(i, j, v, SEMI if j == 0 else REG, INK, bg)
    if total:
        for j, v in enumerate(total):
            fill(len(body), j, v, SEMI, INK, MINT_TINT)
    for i in range(len(body) + 1):
        tbl.rows[i].height = Pt(row_h)


def bars(sl, sc):
    top = sl.content_frame(sc)
    bottom = sl.note(sc)
    series, cats = sc["series"], sc["categories"]
    scolors = [INDIGO, INK, COLORS["peach"]][:len(series)]
    data = CategoryChartData()
    data.categories = [c["label"] for c in cats]
    for k, name in enumerate(series):
        data.add_series(name, [c["values"][k] for c in cats])
    gf = sl.s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Pt(M), Pt(top), Pt(W - 2 * M), Pt(bottom - top), data)
    ch = gf.chart
    ch.has_legend = True
    ch.legend.position = XL_LEGEND_POSITION.TOP
    ch.legend.include_in_layout = False
    ch.legend.font.size, ch.legend.font.name = Pt(10), REG
    ch.category_axis.reverse_order = True
    ch.category_axis.tick_labels.font.size = Pt(12)
    ch.category_axis.tick_labels.font.name = SEMI
    ch.category_axis.format.line.fill.background()
    ch.value_axis.visible = False
    ch.value_axis.has_major_gridlines = False
    for k, s in enumerate(ch.plots[0].series):
        s.format.fill.solid()
        s.format.fill.fore_color.rgb = rgb(scolors[k])
        for i, c in enumerate(cats):
            dl = s.points[i].data_label
            dl.has_text_frame = True
            dl.text_frame.text = c["display"][k]
            dl.font.size, dl.font.name = Pt(11), REG


def timeline(sl, sc):
    top = sl.content_frame(sc)
    bottom = sl.note(sc)
    stops = sc["stops"]
    gap = (W - 2 * M) / len(stops)
    line_y = top + max(50, (bottom - top - 190) / 2)
    sl.rect(M + gap / 2, line_y - 1, gap * (len(stops) - 1), 2, LINE)
    for i, st in enumerate(stops):
        cx = M + gap * i + gap / 2
        sl.text(cx - 30, line_y - 40, 60, 16, f"{i + 1:02d}", 12, SEMI, INDIGO, "center")
        sl.rect(cx - 7, line_y - 7, 14, 14, INDIGO if i == 0 else INK, shape=MSO_SHAPE.OVAL)
        sl.text(cx - gap / 2 + 12, line_y + 24, gap - 24, 50, st["label"], 18, SEMI, INK, "center")
        sl.text(cx - gap / 2 + 14, line_y + 76, gap - 28, 80, st["text"], 13.5, REG, GREY, "center")


def steps(sl, sc):
    top = sl.content_frame(sc)
    bottom = sl.note(sc)
    items = sc["steps"]
    col = (W - 2 * M) / len(items)
    y = top + max(0, (bottom - top - 200) / 2)
    for i, st in enumerate(items):
        x = M + i * col
        sl.rect(x, y, col - 28, 2, LINE)
        sl.text(x, y + 14, col - 32, 56, f"{i + 1:02d}", 46, SEMI, INDIGO)
        sl.text(x, y + 84, col - 32, 28, st["title"], 19, SEMI, INK)
        sl.text(x, y + 116, col - 36, 80, st["text"], 14, REG, GREY)


def text(sl, sc):
    top = sl.content_frame(sc)
    bottom = sl.note(sc)
    tb = sl.text(M, top + 6, 700, bottom - top - 6, sc["paragraphs"][0], 19, REG, INK, spacing=1.15)
    tf = tb.text_frame
    for para in sc["paragraphs"][1:]:
        p = tf.add_paragraph()
        p.space_before = Pt(18)
        p.line_spacing = 1.15
        run = p.add_run()
        run.text = para
        run.font.size, run.font.name = Pt(19), REG
        run.font.color.rgb = rgb(INK)


def close(sl, sc):
    sl.dark()
    sl.image("logo-dark-tagline.png", M, 52, 44)
    sl.text(M, 186, 700, 64, sc["title"], 52, SEMI, WHITE)
    y = 262
    if sc.get("rm"):
        sl.text(M, y, 600, 20, sc["rm"], 15, SEMI, WHITE)
        y += 26
    sl.text(M, y, 600, 20, sc["contact"], 14, REG, SOFT)
    sl.text(M, 398, 760, 90, sc["disclaimer"], 8.5, REG, SOFT)


DRAW = {"cover": cover, "act": act, "statement": statement, "stats": stats, "donut": donut,
        "table": table, "bars": bars, "timeline": timeline, "steps": steps, "text": text,
        "close": close}


def render(doc, out):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Pt(W), Pt(H)
    prs.core_properties.title = f"Growthvine · {doc.get('meta', {}).get('client', '')}".strip(" ·")
    prs.core_properties.author = "Growthvine"
    scenes = doc["scenes"]
    for n, sc in enumerate(scenes, 1):
        DRAW[sc["type"]](Slide(prs, doc, n, len(scenes)), sc)
    prs.save(str(out))
