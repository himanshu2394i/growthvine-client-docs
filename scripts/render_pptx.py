"""PPT drawing for render.py (python-pptx). Same layout numbers as the PDF;
tables and charts are native so advisors can edit them in PowerPoint."""
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_MARKER_STYLE, XL_TICK_LABEL_POSITION
from pptx.enum.dml import MSO_LINE
from pptx.oxml.ns import qn
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Pt

from render import (ASSETS, MARK, MARK_RATIO, shot_for, BAR, COLORS, CONTENT_BOTTOM, FOOT_Y, GREY, H, LINE, M,
                    MINT_TINT, NOTE_H, PEACH_TINT, SOFT, W, blend, boxes, col_widths, is_numeric, palette,
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
    from render_pdf import cover_title, COVER_TITLE_W
    size, leading, lines = cover_title(sc["title"])
    sl.text(M, 168, COVER_TITLE_W + 20, leading * len(lines), sc["title"], size, SEMI, WHITE)
    top = max(262, 172 + leading * len(lines) + 16)
    sl.text(M, top, 560, 60, sc["logline"], 17, REG, SOFT)
    sl.rect(M, min(top + 78, 400), 64, 3, INDIGO)
    col = (W - 2 * M) / len(sc["facts"])
    for i, f in enumerate(sc["facts"]):
        x = M + i * col
        sl.text(x, 420, col - 16, 14, f["label"].upper(), 8.5, SEMI, SOFT)
        sl.text(x, 438, col - 16, 44, f["value"], 17, SEMI, WHITE)
    meta = sl.doc.get("meta", {})
    credit = ", ".join(v for v in (meta.get("rm") and f"Prepared by {meta['rm']}", meta.get("date")) if v)
    if credit:
        sl.text(M, FOOT_Y, 500, 12, credit, 8.5, REG, SOFT)


def act(sl, sc):
    sl.dark()
    sl.text(M, 194, 40, 18, sc["number"], 13, SEMI, INDIGO)
    sl.rect(M + 30, 203, 48, 2, INDIGO)
    from render_pdf import fit_title, COVER_TITLE_W
    size, leading, lines = fit_title(sc["title"], 52, 40)
    sl.text(M, 218, COVER_TITLE_W + 20, leading * len(lines), sc["title"], size, SEMI, WHITE)
    sl.text(M, max(296, 222 + leading * len(lines) + 16), 600, 56, sc["logline"], 18, REG, SOFT)
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
    widths = col_widths(cols, body, width)
    numeric = [j > 0 and all(is_numeric(r[j]) for r in body) for j in range(n)]
    row_h = min(32, (bottom - top) / (len(body) + 1))
    size = 11 if row_h >= 28 else 10
    heat_max = max([to_number(r[j]) or 0 for r in rows for j in range(1, n) if numeric[j]] or [1]) or 1
    gf = sl.s.shapes.add_table(len(body) + 1, n, Pt(M), Pt(top), Pt(width), Pt(row_h * (len(body) + 1)))
    tbl = gf.table
    tbl.first_row = tbl.horz_banding = False
    for j in range(n):
        tbl.columns[j].width = Pt(widths[j])  # rows grow to fit wrapped text
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
    y = 352
    if sc.get("sources"):
        sl.text(M, y, 300, 12, "SOURCES", 8, SEMI, SOFT)
        sl.text(M, y + 14, 760, 40, sc["sources"], 8.5, REG, SOFT)
        y += 62
    sl.text(M, max(y, 398 if not sc.get("sources") else y), 760, 90, sc["disclaimer"], 8.5, REG, SOFT)


def _box(sl, x, y, w, h, label, text, fill):
    sl.rect(x, y, w, h, fill, radius=True)
    sl.text(x + 16, y + 10, w - 32, 12, label.upper(), 8.5, SEMI, INK)
    sl.text(x + 16, y + 28, w - 32, h - 34, text, 11.5, REG, INK)


def fund(sl, sc):
    top = sl.content_frame(sc)
    bottom = sl.note(sc)
    stats_ = sc["stats"]
    gap = 16
    cw = (W - 2 * M - gap * (len(stats_) - 1)) / len(stats_)
    card = blend(WHITE, INDIGO, 0.07)
    for i, st in enumerate(stats_):
        x = M + i * (cw + gap)
        sl.rect(x, top, cw, 66, card, radius=True)
        sl.text(x + 18, top + 10, cw - 36, 30, st["value"], 24, SEMI, INK)
        sl.text(x + 18, top + 44, cw - 36, 14, st["label"], 10, REG, GREY)
    y0 = top + 84
    half = (W - 2 * M - 20) / 2
    facts = sc["facts"]
    gf = sl.s.shapes.add_table(len(facts), 2, Pt(M), Pt(y0), Pt(half), Pt(26 * len(facts)))
    tbl = gf.table
    tbl.first_row = tbl.horz_banding = False
    tbl.columns[0].width, tbl.columns[1].width = Pt(half * 0.38), Pt(half * 0.62)
    for i, f in enumerate(facts):
        for j, (text, font, color) in enumerate(((f["label"], REG, GREY), (f["value"], SEMI, INK))):
            cell = tbl.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(WHITE)
            cell.margin_left = Pt(10)
            cell.text_frame.text = ""
            run = cell.text_frame.paragraphs[0].add_run()
            run.text, run.font.size, run.font.name = text, Pt(10.5), font
            run.font.color.rgb = rgb(color)
    x2 = M + half + 20
    avail = bottom - y0
    what_h = min(avail * 0.5, 40 + 16 * (len(sc["what"]) // 60 + 1))
    _box(sl, x2, y0, half, what_h, sc.get("what_label", "What it does"), sc["what"], MINT_TINT)
    if sc.get("watch"):
        watch_h = min(avail - what_h - 12, 40 + 16 * (len(sc["watch"]) // 60 + 1))
        _box(sl, x2, y0 + what_h + 12, half, watch_h, sc.get("watch_label", "Worth knowing"), sc["watch"], PEACH_TINT)


def line(sl, sc):
    top = sl.content_frame(sc)
    bottom = sl.note(sc)
    data = CategoryChartData()
    data.categories = sc["x"]
    for sr in sc["series"]:
        data.add_series(sr["name"], sr["values"])
    gf = sl.s.shapes.add_chart(XL_CHART_TYPE.LINE, Pt(M), Pt(top - 10), Pt(W - 2 * M), Pt(bottom - top + 10), data)
    ch = gf.chart
    ch.has_legend = True
    ch.legend.position = XL_LEGEND_POSITION.TOP
    ch.legend.include_in_layout = False
    ch.legend.font.size, ch.legend.font.name = Pt(10), REG
    ch.value_axis.visible = False
    ch.value_axis.major_gridlines.format.line.color.rgb = rgb(LINE)
    ch.category_axis.tick_labels.font.size = Pt(9.5)
    ch.category_axis.format.line.color.rgb = rgb(LINE)
    if len(sc["x"]) > 8:                       # label about six points, not every month
        ax = ch.category_axis._element
        skip = ax.makeelement(qn("c:tickLblSkip"), {"val": str(max(1, len(sc["x"]) // 6))})
        anchor = ax.find(qn("c:noMultiLvlLbl"))      # schema order: tickLblSkip comes before it
        if anchor is not None:
            anchor.addprevious(skip)
        else:
            ax.append(skip)
    palette_ = [INDIGO, COLORS["peach"], blend(COLORS["mint"], INK, 0.35), blend(COLORS["mustard"], INK, 0.4)]
    k = 0
    for sr, plot_s in zip(sc["series"], ch.plots[0].series):
        index = sr.get("style") == "index"
        col = INK if index else palette_[k % len(palette_)]
        k += 0 if index else 1
        plot_s.smooth = False
        plot_s.marker.style = XL_MARKER_STYLE.NONE
        plot_s.format.line.color.rgb = rgb(col)
        plot_s.format.line.width = Pt(1.6 if index else 2.4)
        if index:
            plot_s.format.line.dash_style = MSO_LINE.DASH
        if sr.get("end"):
            dl = plot_s.points[len(sr["values"]) - 1].data_label
            dl.has_text_frame = True
            dl.text_frame.text = sr["end"]
            dl.position = XL_LABEL_POSITION.RIGHT
            dl.font.size, dl.font.name = Pt(12), SEMI


# ---------- panels: several charts, tables and notes on one slide ----------

SERIES_COLORS = [INDIGO, INK, COLORS["peach"], blend(COLORS["mint"], INK, 0.35)]


def _head(sl, box, title):
    x, y, w, h = box
    if not title:
        return y
    sl.text(x, y, w, 12, title.upper(), 8.5, SEMI, INDIGO)
    sl.rect(x, y + 16, w, 0.8, LINE)
    return y + 26


def _plain_chart(ch):
    ch.font.size, ch.font.name = Pt(9), REG
    return ch


def pn_bars(sl, box, pn):
    x, y, w, h = box
    top = _head(sl, box, pn.get("title"))
    data = CategoryChartData()
    data.categories = [c["label"] for c in pn["categories"]]
    for k, name in enumerate(pn["series"]):
        data.add_series(name, [c["values"][k] for c in pn["categories"]])
    from render import bar_block
    n_s, n_c = len(pn["series"]), len(pn["categories"])
    ch_h = min(y + h - top, bar_block(y + h - top, n_c, n_s) * n_c + (22 if n_s > 1 else 0) + 10)
    ch = _plain_chart(sl.s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Pt(x), Pt(top), Pt(w), Pt(ch_h), data).chart)
    ch.has_legend = len(pn["series"]) > 1
    if ch.has_legend:
        ch.legend.position = XL_LEGEND_POSITION.TOP
        ch.legend.include_in_layout = False
    ch.category_axis.reverse_order = True
    ch.category_axis.format.line.color.rgb = rgb(LINE)
    ch.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW   # keep labels clear of negative bars
    ch.value_axis.visible = False
    ch.value_axis.has_major_gridlines = False
    for k, s in enumerate(ch.plots[0].series):
        s.format.fill.solid()
        s.format.fill.fore_color.rgb = rgb(SERIES_COLORS[k % 4])
        s.invert_if_negative = False
        for i, c in enumerate(pn["categories"]):
            dl = s.points[i].data_label
            dl.has_text_frame = True
            dl.text_frame.text = c["display"][k]
            dl.font.size = Pt(9)


def pn_donut(sl, box, pn):
    x, y, w, h = box
    top = _head(sl, box, pn.get("title"))
    slices = pn["slices"]
    colors = palette(sl.doc, [s["label"] for s in slices])
    avail = y + h - top
    r = min(avail / 2 - 4, w * 0.22, 95)
    data = CategoryChartData()
    data.categories = [s["label"] for s in slices]
    data.add_series("Share", [s["value"] for s in slices])
    ch = sl.s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Pt(x), Pt(top + avail / 2 - r), Pt(2 * r), Pt(2 * r), data).chart
    ch.has_legend = False
    ch.has_title = False
    for i, s in enumerate(slices):
        pt = ch.plots[0].series[0].points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = rgb(colors[s["label"]])
    if pn.get("center"):
        sl.text(x + r - 45, top + avail / 2 - 8, 90, 16, pn["center"], 12, SEMI, INK, "center")
    lx = x + 2 * r + 18
    row = min(26, avail / len(slices))
    ly = top + avail / 2 - row * len(slices) / 2
    for s in slices:
        sl.rect(lx, ly + row / 2 - 5, 10, 10, colors[s["label"]])
        sl.text(lx + 16, ly + row / 2 - 7, x + w - lx - 90, 14, s["label"], 9.5, REG, INK)
        sl.text(x + w - 80, ly + row / 2 - 7, 80, 14, s["display"], 9.5, SEMI, INK, "right")
        ly += row


def pn_stack(sl, box, pn):
    x, y, w, h = box
    top = _head(sl, box, pn.get("title"))
    segs = pn["segments"]
    colors = palette(sl.doc, [s["label"] for s in segs])
    total = sum(max(0, s["value"]) for s in segs) or 1
    bx = x
    for s in segs:
        sw = w * max(0, s["value"]) / total
        if sw > 0.5:
            sl.rect(bx, top + 4, sw, 22, colors[s["label"]])
            if sw > 34:
                sl.text(bx, top + 9, sw, 12, s["display"], 9, SEMI, INK, "center")
        bx += sw
    ly = top + 40
    row = min(20, (y + h - ly) / len(segs))
    for s in segs:
        sl.rect(x, ly + 3, 9, 9, colors[s["label"]])
        sl.text(x + 15, ly, w - 90, 14, s["label"], 9.5, REG, INK)
        sl.text(x + w - 80, ly, 80, 14, s["display"], 9.5, SEMI, INK, "right")
        ly += row


def pn_table(sl, box, pn):
    x, y, w, h = box
    top = _head(sl, box, pn.get("title"))
    cols, rows = pn["columns"], [[str(v) for v in r] for r in pn["rows"]]
    widths = col_widths(cols, rows, w)
    numeric = [j > 0 and all(is_numeric(r[j]) for r in rows) for j in range(len(cols))]
    row_h = min(22, (y + h - top) / (len(rows) + 1))
    heat_max = max([to_number(r[j]) or 0 for r in rows for j in range(len(cols)) if numeric[j]] or [1]) or 1
    gf = sl.s.shapes.add_table(len(rows) + 1, len(cols), Pt(x), Pt(top), Pt(w), Pt(row_h * (len(rows) + 1)))
    tbl = gf.table
    tbl.first_row = tbl.horz_banding = False
    for j in range(len(cols)):
        tbl.columns[j].width = Pt(widths[j])
    for i, r in enumerate([cols] + rows):
        tbl.rows[i].height = Pt(row_h)
        for j, v in enumerate(r):
            cell = tbl.cell(i, j)
            cell.fill.solid()
            shade = WHITE
            if i == 0:
                shade = blend(WHITE, INDIGO, 0.12)
            elif pn.get("heat") and numeric[j] and to_number(v):
                shade = blend(WHITE, INDIGO, 0.08 + 0.5 * to_number(v) / heat_max)
            cell.fill.fore_color.rgb = rgb(shade)
            cell.margin_left = cell.margin_right = Pt(6)
            cell.margin_top = cell.margin_bottom = Pt(2)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.text_frame.text = ""
            para = cell.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.RIGHT if numeric[j] else PP_ALIGN.LEFT
            run = para.add_run()
            run.text = v
            run.font.size, run.font.name = Pt(9), SEMI if (i == 0 or j == 0) else REG
            run.font.color.rgb = rgb(INK)


def pn_text(sl, box, pn):
    x, y, w, h = box
    ty = _head(sl, box, pn.get("title"))
    tb = sl.s.shapes.add_textbox(Pt(x), Pt(ty), Pt(w), Pt(y + h - ty))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = 0
    for i, b in enumerate(pn["bullets"]):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.space_after = Pt(6)
        mark = para.add_run()
        mark.text = "▪ "
        mark.font.size, mark.font.name = Pt(9), REG
        mark.font.color.rgb = rgb(INDIGO)
        run = para.add_run()
        run.text = b
        run.font.size, run.font.name = Pt(10.5), REG
        run.font.color.rgb = rgb(INK)


def pn_stats(sl, box, pn):
    x, y, w, h = box
    top = _head(sl, box, pn.get("title"))
    items = pn["stats"]
    per_row = 2 if len(items) > 2 and w < 360 else len(items)
    rows_n = -(-len(items) // per_row)
    cw, rh = w / per_row, (y + h - top) / rows_n
    for i, st in enumerate(items):
        cx, cy = x + (i % per_row) * cw, top + (i // per_row) * rh
        sl.text(cx, cy, cw - 8, 26, st["value"], 20, SEMI, INK)
        sl.text(cx, cy + 30, cw - 12, 28, st["label"], 9, REG, GREY)


def pn_line(sl, box, pn):
    x, y, w, h = box
    top = _head(sl, box, pn.get("title"))
    data = CategoryChartData()
    data.categories = pn["x"]
    for sr in pn["series"]:
        data.add_series(sr["name"], sr["values"])
    ch = _plain_chart(sl.s.shapes.add_chart(XL_CHART_TYPE.LINE, Pt(x), Pt(top), Pt(w), Pt(y + h - top), data).chart)
    ch.has_legend = len(pn["series"]) > 1
    if ch.has_legend:
        ch.legend.position = XL_LEGEND_POSITION.TOP
        ch.legend.include_in_layout = False
    ch.value_axis.visible = False
    ch.value_axis.major_gridlines.format.line.color.rgb = rgb(LINE)
    k = 0
    for sr, s in zip(pn["series"], ch.plots[0].series):
        index = sr.get("style") == "index"
        col = INK if index else SERIES_COLORS[0 if k == 0 else (k + 1) % 4]
        k += 0 if index else 1
        s.smooth = False
        s.marker.style = XL_MARKER_STYLE.NONE
        s.format.line.color.rgb = rgb(col)
        s.format.line.width = Pt(1.2 if index else 1.8)
        if index:
            s.format.line.dash_style = MSO_LINE.DASH
        if sr.get("end"):
            dl = s.points[len(sr["values"]) - 1].data_label
            dl.has_text_frame = True
            dl.text_frame.text = sr["end"]
            dl.position = XL_LABEL_POSITION.RIGHT
            dl.font.size = Pt(9)


PANEL = {"bars": pn_bars, "donut": pn_donut, "stack": pn_stack, "table": pn_table,
         "text": pn_text, "stats": pn_stats, "line": pn_line}


def panels(sl, sc):
    top = sl.content_frame(sc)
    bottom = sl.note(sc)
    strip = sc.get("strip") or []
    if strip:
        gap = 12
        cw = (W - 2 * M - gap * (len(strip) - 1)) / len(strip)
        card = blend(WHITE, INDIGO, 0.07)
        for i, st in enumerate(strip):
            sx = M + i * (cw + gap)
            sl.rect(sx, top - 6, cw, 52, card, radius=True)
            sl.text(sx + 12, top - 1, cw - 24, 22, st["value"], 17, SEMI, INK)
            sl.text(sx + 12, top + 26, cw - 24, 12, st["label"], 8.5, REG, GREY)
        top += 52 + 10
    for box, pn in zip(boxes(sc["layout"], top, bottom), sc["panels"]):
        PANEL[pn["kind"]](sl, box, pn)


DRAW = {"cover": cover, "act": act, "statement": statement, "stats": stats, "donut": donut,
        "table": table, "bars": bars, "timeline": timeline, "steps": steps, "text": text,
        "close": close, "fund": fund, "line": line, "panels": panels}


def render(doc, out):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Pt(W), Pt(H)
    prs.core_properties.title = f"Growthvine, {doc.get('meta', {}).get('client', '')}".strip(" ,")
    prs.core_properties.author = "Growthvine"
    scenes = doc["scenes"]
    for n, sc in enumerate(scenes, 1):
        DRAW[sc["type"]](Slide(prs, doc, n, len(scenes)), sc)
    prs.save(str(out))
