"""PDF drawing for render.py (reportlab). Layout uses top-left coordinates;
`_y` flips them for reportlab, whose origin is bottom-left."""
import re

from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from render import (bar_block, ASSETS, MARK, MARK_RATIO, shot_for, BAR, COLORS, CONTENT_BOTTOM, FOOT_Y, GREY, H, LINE, M,
                    MINT_TINT, NOTE_H, PEACH_TINT, SOFT, W, blend, boxes, col_widths, is_numeric, palette,
                    to_number)

REG, SEMI = "Poppins", "Poppins-SemiBold"
INK, INDIGO, WHITE = COLORS["ink"], COLORS["indigo"], COLORS["white"]


def _fonts():
    if REG not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(REG, str(ASSETS / "fonts" / "Poppins-Regular.ttf")))
        pdfmetrics.registerFont(TTFont(SEMI, str(ASSETS / "fonts" / "Poppins-SemiBold.ttf")))


def _y(top):
    return H - top


_UNIT = re.compile(r"(?<=\d)\s+(?=(Cr|L|lakh|crore|years?|yrs?)\b)")


def keep_amounts(s):
    """Non-breaking space between a number and its unit, so '₹1.70 Cr' never splits."""
    return _UNIT.sub(" ", s)


def wrap(s, font, size, width):
    """Greedy line wrap on ordinary spaces only (reportlab's simpleSplit also
    breaks on non-breaking spaces, which would split amounts from units)."""
    lines, line = [], ""
    for word in keep_amounts(s).split(" "):
        trial = f"{line} {word}" if line else word
        if line and pdfmetrics.stringWidth(trial, font, size) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + ([line] if line else [])


class Page:
    def __init__(self, c, doc, n, total):
        self.c, self.doc, self.n, self.total = c, doc, n, total

    # --- primitives (top-left coordinates) ---
    def rect(self, x, y, w, h, fill, radius=0):
        self.c.setFillColor(HexColor(fill))
        if radius:
            self.c.roundRect(x, _y(y + h), w, h, radius, stroke=0, fill=1)
        else:
            self.c.rect(x, _y(y + h), w, h, stroke=0, fill=1)

    def text(self, x, y, s, size, font=REG, color=INK, align="left", spacing=0):
        """Single line; y is the top of the text."""
        c = self.c
        c.setFillColor(HexColor(color))
        base = _y(y + size * 0.82)
        if spacing:
            t = c.beginText()
            t.setFont(font, size)
            t.setCharSpace(spacing)
            width = pdfmetrics.stringWidth(s, font, size) + spacing * len(s)
            t.setTextOrigin(x - (width if align == "right" else 0), base)
            t.textLine(s)
            t.setCharSpace(0)  # char spacing persists in PDF text state otherwise
            c.drawText(t)
            return
        c.setFont(font, size)
        {"left": c.drawString, "right": c.drawRightString, "center": c.drawCentredString}[align](x, base, s)

    def para(self, x, y, s, width, size, font=REG, color=INK, leading=None, align="left"):
        """Wrapped text; returns the height used."""
        leading = leading or size * 1.45
        lines = wrap(s, font, size, width)
        for i, line in enumerate(lines):
            self.text(x if align == "left" else x + width, y + i * leading, line, size, font, color, align)
        return len(lines) * leading

    def image(self, name, x, y, h):
        img = ImageReader(str(ASSETS / "logos" / name))
        iw, ih = img.getSize()
        w = h * iw / ih
        self.c.drawImage(img, x, _y(y + h), w, h, mask="auto")
        return w

    def mark(self):
        x, y, h = shot_for(self.doc, self.n)
        self.c.drawImage(ImageReader(str(MARK)), x, _y(y + h), h * MARK_RATIO, h, mask="auto")

    # --- frames ---
    def dark(self):
        self.rect(0, 0, W, H, INK)
        self.mark()

    def counter(self, color):
        self.text(W - M, FOOT_Y, f"{self.n:02d} / {self.total:02d}", 8, REG, color, "right")

    def content_frame(self, s):
        """White scene with letterbox bars, header and footer. Returns content top."""
        self.rect(0, 0, W, H, WHITE)
        self.rect(0, 0, W, BAR, INK)
        self.rect(0, H - BAR, W, BAR, INK)
        top = 40
        if s.get("kicker"):
            self.text(M, top, s["kicker"].upper(), 9, SEMI, INDIGO, spacing=1.2)
            top += 20
        if s.get("as_of"):
            self.text(W - M, 42, s["as_of"], 8.5, REG, GREY, "right")
        top += self.para(M, top, s["title"], W - 2 * M - 150, 25, SEMI, INK, leading=31)
        lw = self.image("logo-light.png", M, FOOT_Y - 3, 13)
        footer = self.doc.get("meta", {}).get("footer", "")
        if footer:
            self.text(M + lw + 12, FOOT_Y, footer, 8, REG, GREY)
        self.counter(GREY)
        return top + 26

    def note(self, s):
        """Draw the note box if present; returns the bottom limit for content."""
        n = s.get("note")
        if not n:
            return CONTENT_BOTTOM
        y = CONTENT_BOTTOM - NOTE_H
        fill = PEACH_TINT if n.get("tone") == "caution" else MINT_TINT
        self.rect(M, y, W - 2 * M, NOTE_H, fill, radius=6)
        self.text(M + 20, y + 12, n.get("label", "").upper(), 8.5, SEMI, INK, spacing=1)
        self.para(M + 20, y + 28, n["text"], W - 2 * M - 40, 11, REG, INK, leading=15)
        return y - 18


# ---------- scenes ----------

COVER_TITLE_W = 640


def fit_title(title, big, small, width=COVER_TITLE_W):
    """(size, leading, lines): `big` if it fits on one line, else `small` (wrapping)."""
    _fonts()
    size = big if len(wrap(title, SEMI, big, width)) == 1 else small
    return size, round(size * 1.1), wrap(title, SEMI, size, width)


def cover_title(title):
    return fit_title(title, 60, 44)


def cover(p, s):
    p.dark()
    p.image("logo-dark.png", M, 44, 30)
    p.text(M, 150, s["eyebrow"].upper(), 11, SEMI, INDIGO, spacing=2)
    size, leading, lines = cover_title(s["title"])
    p.para(M, 172, s["title"], COVER_TITLE_W, size, SEMI, WHITE, leading=leading)
    top = max(262, 172 + leading * len(lines) + 16)
    h = p.para(M, top, s["logline"], 560, 17, REG, SOFT, leading=26)
    p.rect(M, top + h + 18, 64, 3, INDIGO)
    facts = s["facts"]
    col = (W - 2 * M) / len(facts)
    for i, f in enumerate(facts):
        x = M + i * col
        p.text(x, 420, f["label"].upper(), 8.5, SEMI, SOFT, spacing=1)
        p.para(x, 438, f["value"], col - 16, 17, SEMI, WHITE, leading=22)
    meta = p.doc.get("meta", {})
    credit = ", ".join(v for v in (meta.get("rm") and f"Prepared by {meta['rm']}", meta.get("date")) if v)
    if credit:
        p.text(M, FOOT_Y, credit, 8.5, REG, SOFT)


def act(p, s):
    p.dark()
    p.text(M, 196, s["number"], 13, SEMI, INDIGO)
    p.rect(M + 30, 203, 48, 2, INDIGO)
    size, leading, tl = fit_title(s["title"], 52, 40)
    p.para(M, 222, s["title"], COVER_TITLE_W, size, SEMI, WHITE, leading=leading)
    top = max(296, 222 + leading * len(tl) + 16)
    width = 600
    lines = wrap(s["logline"], REG, 18, width)
    if len(lines) == 2 and len(lines[1].split()) <= 2:   # avoid a lonely last word
        width = pdfmetrics.stringWidth(s["logline"], REG, 18) / 2 + 40
    p.para(M, top, s["logline"], width, 18, REG, SOFT, leading=27)
    p.counter(SOFT)


def statement(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    mid = top + (bottom - top) / 2 - 50
    p.rect(M, mid, 4, 96, INDIGO)
    h = p.para(M + 28, mid, s["text"], 700, 30, SEMI, INK, leading=40)
    if s.get("sub"):
        p.para(M + 28, mid + h + 14, s["sub"], 640, 14, REG, GREY, leading=21)


def stats(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    items = s["stats"]
    col = (W - 2 * M) / len(items)
    y = top + max(0, (bottom - top - 150) / 2)
    for i, st in enumerate(items):
        x = M + i * col
        p.rect(x, y, 28, 3, INDIGO)
        p.para(x, y + 22, st["value"], col - 24, 46 if len(items) < 4 else 38, SEMI, INK, leading=52)
        p.para(x, y + 90, st["label"], col - 36, 14, REG, GREY, leading=20)


def donut(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    slices = s["slices"]
    colors = palette(p.doc, [sl["label"] for sl in slices])
    r = min(130, (bottom - top) / 2 - 4)
    cx, cy = M + 150, top + (bottom - top) / 2
    total = sum(sl["value"] for sl in slices) or 1
    c, ang = p.c, 90.0
    c.setStrokeColor(HexColor(WHITE))
    c.setLineWidth(2.5)
    for sl in slices:
        ext = -360.0 * sl["value"] / total
        c.setFillColor(HexColor(colors[sl["label"]]))
        c.wedge(cx - r, _y(cy + r), cx + r, _y(cy - r), ang, ext, stroke=1, fill=1)
        ang += ext
    c.setFillColor(HexColor(WHITE))
    c.circle(cx, _y(cy), r * 0.58, stroke=0, fill=1)
    if s.get("center"):
        p.text(cx, cy - 12, s["center"], 19, SEMI, INK, "center")
    # legend
    x0, x1 = M + 360, W - M
    row = min(44, (bottom - top) / len(slices))
    y = cy - row * len(slices) / 2
    for sl in slices:
        p.rect(x0, y + row / 2 - 6, 12, 12, colors[sl["label"]], radius=2)
        p.text(x0 + 24, y + row / 2 - 8, sl["label"], 13, REG, INK)
        p.text(x1 - 90, y + row / 2 - 8, sl["display"], 13, SEMI, INK, "right")
        p.text(x1, y + row / 2 - 8, sl["share"], 13, REG, GREY, "right")
        p.rect(x0, y + row - 1, x1 - x0, 1, LINE)
        y += row


def table(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    cols, rows = s["columns"], [[str(v) for v in r] for r in s["rows"]]
    total = [str(v) for v in s["total"]] if s.get("total") else None
    body = rows + ([total] if total else [])
    n = len(cols)
    width = W - 2 * M
    widths = col_widths(cols, body, width)
    numeric = [j > 0 and all(is_numeric(r[j]) for r in body) for j in range(n)]
    heat_max = max([to_number(r[j]) or 0 for r in rows for j in range(1, n) if numeric[j]] or [1]) or 1
    pad = 10

    def layout(size):
        """Wrapped lines per cell and row heights at a font size."""
        lead = size * 1.35
        grid = [[[c] if numeric[j] else wrap(c, SEMI if (i == 0 or j == 0) else REG, size, widths[j] - 2 * pad)
                 for j, c in enumerate(r)] for i, r in enumerate([cols] + body)]
        heights = [max(14, max(len(c) for c in r) * lead) + 14 for r in grid]
        return grid, heights, lead

    for size in (11, 10, 9):
        grid, heights, lead = layout(size)
        if sum(heights) <= bottom - top:
            break
    else:
        raise ValueError(f"Scene {p.n} (table): the text doesn't fit on one page. "
                         f"Shorten the longest cells or split the table into two scenes.")

    last_is_total = cols[-1].lower() == "total"
    y = top
    for i, (r, lines_row, h) in enumerate(zip([cols] + body, grid, heights)):
        header, is_total = i == 0, total is not None and i == len(body)
        if header:
            p.rect(M, y, width, h, INK)
        elif is_total:
            p.rect(M, y, width, h, MINT_TINT)
        x = M
        for j, (value, lines) in enumerate(zip(r, lines_row)):
            if s.get("heat") and not header and not is_total and numeric[j] and not (last_is_total and j == n - 1):
                val = to_number(value)
                if val:
                    p.rect(x, y, widths[j], h, blend(WHITE, INDIGO, 0.1 + 0.5 * val / heat_max))
            font = SEMI if (header or is_total or j == 0) else REG
            color = WHITE if header else INK
            ty = y + 7 + (h - 14 - len(lines) * lead) / 2
            for k, line in enumerate(lines):
                if numeric[j]:
                    p.text(x + widths[j] - pad, ty + k * lead, line, size, font, color, "right")
                else:
                    p.text(x + pad, ty + k * lead, line, size, font, color)
            x += widths[j]
        if not header and not is_total:
            p.rect(M, y + h - 1, width, 1, LINE)
        y += h


def bars(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    series, cats = s["series"], s["categories"]
    scolors = [INDIGO, INK, COLORS["peach"]][:len(series)]
    # legend
    x = W - M
    for name, col in reversed(list(zip(series, scolors))):
        w = 22 + len(name) * 6.5
        x -= w
        p.rect(x, top - 4, 10, 10, col, radius=2)
        p.text(x + 16, top - 6, name, 10, REG, INK)
        x -= 18
    top += 22
    label_w, val_w = 230, 90
    x0, x1 = M + label_w, W - M - val_w
    vmax = max(v for c in cats for v in c["values"]) or 1
    block = min((bottom - top) / len(cats), len(series) * 23 + 30)   # don't let a few bars float apart
    bh = min(20, block * 0.72 / len(series))
    y = top
    for c in cats:
        group_h = bh * len(series) + 4 * (len(series) - 1)
        gy = y + (block - group_h) / 2
        p.para(M, gy + group_h / 2 - 9, c["label"], label_w - 20, 12.5, SEMI, INK, leading=16)
        for k, (v, d) in enumerate(zip(c["values"], c["display"])):
            by = gy + k * (bh + 4)
            bw = max(2, (x1 - x0) * v / vmax)
            p.rect(x0, by, bw, bh, scolors[k], radius=2)
            p.text(x0 + bw + 8, by + (bh - 11) / 2, d, 11, SEMI if k == 0 else REG, INK)
        y += block


def timeline(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    stops = s["stops"]
    gap = (W - 2 * M) / len(stops)
    line_y = top + max(50, (bottom - top - 190) / 2)
    p.rect(M + gap / 2, line_y - 1, gap * (len(stops) - 1), 2, LINE)
    for i, st in enumerate(stops):
        cx = M + gap * i + gap / 2
        p.text(cx, line_y - 40, f"{i + 1:02d}", 12, SEMI, INDIGO, "center")
        p.c.setFillColor(HexColor(INDIGO if i == 0 else INK))
        p.c.circle(cx, _y(line_y), 7, stroke=0, fill=1)
        lines = wrap(st["label"], SEMI, 18, gap - 24)
        for k, ln in enumerate(lines):
            p.text(cx, line_y + 26 + k * 24, ln, 18, SEMI, INK, "center")
        ty = line_y + 36 + len(lines) * 24
        for k, ln in enumerate(wrap(st["text"], REG, 13.5, gap - 28)):
            p.text(cx, ty + k * 20, ln, 13.5, REG, GREY, "center")


def steps(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    items = s["steps"]
    col = (W - 2 * M) / len(items)
    y = top + max(0, (bottom - top - 200) / 2)
    for i, st in enumerate(items):
        x = M + i * col
        p.rect(x, y, col - 28, 2, LINE)
        p.text(x, y + 18, f"{i + 1:02d}", 46, SEMI, INDIGO)
        h = p.para(x, y + 84, st["title"], col - 32, 19, SEMI, INK, leading=24)
        p.para(x, y + 92 + h, st["text"], col - 36, 14, REG, GREY, leading=20)


def text(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    y = top + 6
    for para in s["paragraphs"]:
        y += p.para(M, y, para, 700, 19, REG, INK, leading=30) + 18
        if y > bottom:
            break


def close(p, s):
    p.dark()
    p.image("logo-dark-tagline.png", M, 52, 44)
    p.para(M, 190, s["title"], 640, 52, SEMI, WHITE, leading=58)
    y = 262
    if s.get("rm"):
        p.text(M, y, s["rm"], 15, SEMI, WHITE)
        y += 26
    p.text(M, y, s["contact"], 14, REG, SOFT)
    y = 352
    if s.get("sources"):
        p.text(M, y, "SOURCES", 8, SEMI, SOFT, spacing=1)
        y += 14 + p.para(M, y + 14, s["sources"], 760, 8.5, REG, SOFT, leading=13) + 8
    p.para(M, max(y, 398 if not s.get("sources") else y), s["disclaimer"], 760, 8.5, REG, SOFT, leading=13)


def _box(p, x, y, w, label, text, fill, size=11.5):
    """Tinted box with a small capital label; returns its height."""
    lines = wrap(text, REG, size, w - 32)
    h = 34 + len(lines) * size * 1.45 + 10
    p.rect(x, y, w, h, fill, radius=6)
    p.text(x + 16, y + 12, label.upper(), 8.5, SEMI, INK, spacing=1)
    for k, line in enumerate(lines):
        p.text(x + 16, y + 30 + k * size * 1.45, line, size, REG, INK)
    return h


def fund(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    stats_ = s["stats"]
    gap = 16
    cw = (W - 2 * M - gap * (len(stats_) - 1)) / len(stats_)
    card = blend(WHITE, INDIGO, 0.07)
    for i, st in enumerate(stats_):
        x = M + i * (cw + gap)
        p.rect(x, top, cw, 66, card, radius=6)
        p.text(x + 18, top + 12, st["value"], 24, SEMI, INK)
        p.text(x + 18, top + 44, st["label"], 10, REG, GREY)
    y0 = top + 66 + 18
    half = (W - 2 * M - 20) / 2
    # facts (left)
    y = y0
    label_w = half * 0.38
    for f in s["facts"]:
        vlines = wrap(f["value"], SEMI, 10.5, half - label_w - 16)
        h = max(26, 10 + len(vlines) * 14 + 6)
        p.text(M + 10, y + 8, f["label"], 10.5, REG, GREY)
        for k, line in enumerate(vlines):
            p.text(M + label_w, y + 8 + k * 14, line, 10.5, SEMI, INK)
        p.rect(M, y + h - 1, half, 1, LINE)
        y += h
    left_bottom = y
    # what it does / worth knowing (right)
    x2 = M + half + 20
    y = y0
    y += _box(p, x2, y, half, s.get("what_label", "What it does"), s["what"], MINT_TINT) + 12
    if s.get("watch"):
        y += _box(p, x2, y, half, s.get("watch_label", "Worth knowing"), s["watch"], PEACH_TINT)
    if max(left_bottom, y) > bottom + 4:
        raise ValueError(f"Scene {p.n} (fund): too much text for one page. Shorten the facts, "
                         f"'what' or 'watch' text.")


def line(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    xs, series = s["x"], s["series"]
    palette_ = [INDIGO, COLORS["peach"], blend(COLORS["mint"], INK, 0.35), blend(COLORS["mustard"], INK, 0.4)]
    colors, k = [], 0
    for sr in series:
        if sr.get("style") == "index":
            colors.append(INK)
        else:
            colors.append(palette_[k % len(palette_)])
            k += 1
    # legend
    lx = M
    for sr, col in zip(series, colors):
        p.rect(lx, top - 2, 14, 3, col)
        p.text(lx + 20, top - 8, sr["name"], 10, REG, INK)
        lx += 34 + pdfmetrics.stringWidth(sr["name"], REG, 10)
    x0, x1 = M, W - M - 110
    y0, y1 = top + 26, bottom - 26
    vals = [v for sr in series for v in sr["values"]]
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.08 or 1
    lo, hi = lo - pad, hi + pad

    def X(i):
        return x0 + (x1 - x0) * i / (len(xs) - 1)

    def Y(v):
        return y1 - (y1 - y0) * (v - lo) / (hi - lo)

    for g in range(4):
        p.rect(x0, y0 + (y1 - y0) * g / 3, x1 - x0, 0.6, LINE)
    c = p.c
    ends = []
    for sr, col in zip(series, colors):
        c.setStrokeColor(HexColor(col))
        c.setLineWidth(2.4 if sr.get("style") != "index" else 1.6)
        c.setDash(4, 3) if sr.get("style") == "index" else c.setDash()
        path = c.beginPath()
        for i, v in enumerate(sr["values"]):
            (path.moveTo if i == 0 else path.lineTo)(X(i), _y(Y(v)))
        c.drawPath(path, stroke=1, fill=0)
        ends.append([Y(sr["values"][-1]), sr.get("end", ""), col])
    c.setDash()
    ends.sort()
    for i in range(1, len(ends)):                       # keep end labels apart
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + 16)
    for yv, text, col in ends:
        if text:
            p.text(x1 + 10, yv - 7, text, 12, SEMI, INK)
    show = range(len(xs)) if len(xs) <= 8 else sorted({0, len(xs) // 2, len(xs) - 1})
    for i in show:
        align = "left" if i == 0 else ("right" if i == len(xs) - 1 else "center")
        p.text(X(i), y1 + 10, xs[i], 9.5, REG, GREY, align)


# ---------- panels: several charts, tables and notes on one page ----------

SERIES_COLORS = [INDIGO, INK, COLORS["peach"], blend(COLORS["mint"], INK, 0.35)]


def _panel_head(p, box, title):
    x, y, w, h = box
    if not title:
        return y
    p.text(x, y, title.upper(), 8.5, SEMI, INDIGO, spacing=1)
    p.rect(x, y + 16, w, 0.8, LINE)
    return y + 26


def pn_bars(p, box, pn):
    x, y, w, h = box
    top = _panel_head(p, box, pn.get("title"))
    series, cats = pn["series"], pn["categories"]
    cols = SERIES_COLORS[:len(series)]
    if len(series) > 1:                                   # legend
        lx = x
        for name, col in zip(series, cols):
            p.rect(lx, top, 9, 9, col, radius=1.5)
            p.text(lx + 13, top - 1, name, 8.5, REG, INK)
            lx += 26 + pdfmetrics.stringWidth(name, REG, 8.5)
        top += 18
    label_w = min(w * 0.36, 150)
    val_w = 52
    x0, x1 = x + label_w, x + w - val_w
    vals = [v for c in cats for v in c["values"]]
    lo, hi = min(0, min(vals)), max(0, max(vals)) or 1
    zero = x0 + (x1 - x0) * (-lo) / (hi - lo)
    block = bar_block(y + h - top, len(cats), len(series))
    bh = min(14, block * 0.7 / len(series))
    for i, c in enumerate(cats):
        by0 = top + i * block + (block - bh * len(series) - 3 * (len(series) - 1)) / 2
        for ln, line_ in enumerate(wrap(c["label"], REG, 9.5, label_w - 8)[:2]):
            p.text(x, by0 + ln * 12 + (bh * len(series) - 12 * min(2, len(wrap(c["label"], REG, 9.5, label_w - 8)))) / 2,
                   line_, 9.5, REG, INK)
        for k, (v, d) in enumerate(zip(c["values"], c["display"])):
            by = by0 + k * (bh + 3)
            bw = (x1 - x0) * abs(v) / (hi - lo)
            bx = zero if v >= 0 else zero - bw
            p.rect(bx, by, max(bw, 1.5), bh, cols[k], radius=1.5)
            if v >= 0:
                p.text(bx + bw + 5, by + (bh - 9) / 2, d, 9, SEMI if k == 0 else REG, INK)
            else:
                p.text(bx - 5, by + (bh - 9) / 2, d, 9, SEMI if k == 0 else REG, INK, "right")
    if lo < 0:
        p.rect(zero, top - 2, 0.8, y + h - top + 2, LINE)


def pn_donut(p, box, pn):
    x, y, w, h = box
    top = _panel_head(p, box, pn.get("title"))
    slices = pn["slices"]
    colors = palette(p.doc, [s["label"] for s in slices])
    avail = y + h - top
    r = min(avail / 2 - 4, w * 0.22, 95)
    cx, cy = x + r + 4, top + avail / 2
    total = sum(s["value"] for s in slices) or 1
    c, ang = p.c, 90.0
    c.setStrokeColor(HexColor(WHITE))
    c.setLineWidth(2)
    for s in slices:
        ext = -360.0 * s["value"] / total
        c.setFillColor(HexColor(colors[s["label"]]))
        c.wedge(cx - r, _y(cy + r), cx + r, _y(cy - r), ang, ext, stroke=1, fill=1)
        ang += ext
    c.setFillColor(HexColor(WHITE))
    c.circle(cx, _y(cy), r * 0.58, stroke=0, fill=1)
    if pn.get("center"):
        p.text(cx, cy - 7, pn["center"], 12, SEMI, INK, "center")
    lx = cx + r + 18
    row = min(26, avail / len(slices))
    ly = cy - row * len(slices) / 2
    for s in slices:
        p.rect(lx, ly + row / 2 - 5, 10, 10, colors[s["label"]], radius=1.5)
        p.text(lx + 16, ly + row / 2 - 6, s["label"], 9.5, REG, INK)
        p.text(x + w, ly + row / 2 - 6, s["display"], 9.5, SEMI, INK, "right")
        ly += row


def pn_stack(p, box, pn):
    x, y, w, h = box
    top = _panel_head(p, box, pn.get("title"))
    segs = pn["segments"]
    colors = palette(p.doc, [s["label"] for s in segs])
    total = sum(max(0, s["value"]) for s in segs) or 1
    bx = x
    for s in segs:
        sw = w * max(0, s["value"]) / total
        p.rect(bx, top + 4, sw, 22, colors[s["label"]])
        if sw > 34:
            p.text(bx + sw / 2, top + 10, s["display"], 9, SEMI, INK, "center")
        bx += sw
    ly = top + 40
    row = min(20, (y + h - ly) / len(segs))
    for s in segs:
        p.rect(x, ly + 3, 9, 9, colors[s["label"]], radius=1.5)
        p.text(x + 15, ly + 1, s["label"], 9.5, REG, INK)
        p.text(x + w, ly + 1, s["display"], 9.5, SEMI, INK, "right")
        ly += row


def pn_table(p, box, pn):
    x, y, w, h = box
    top = _panel_head(p, box, pn.get("title"))
    cols, rows = pn["columns"], [[str(v) for v in r] for r in pn["rows"]]
    widths = col_widths(cols, rows, w)
    numeric = [j > 0 and all(is_numeric(r[j]) for r in rows) for j in range(len(cols))]
    heat_max = max([to_number(r[j]) or 0 for r in rows for j in range(len(cols)) if numeric[j]] or [1]) or 1
    for size in (9.5, 8.5, 8):
        lead = size * 1.3
        grid = [[[c] if (numeric[j] and i > 0) else wrap(c, SEMI if i == 0 else REG, size, widths[j] - 12)
                 for j, c in enumerate(r)] for i, r in enumerate([cols] + rows)]   # headers always wrap
        heights = [max(len(cl) for cl in r) * lead + 7 for r in grid]
        if sum(heights) <= y + h - top:
            break
    else:
        raise ValueError(f"Scene {p.n}: the '{pn.get('title', 'table')}' panel has too much text. Trim rows or shorten cells.")
    ty = top
    for i, (r, cells, rh) in enumerate(zip([cols] + rows, grid, heights)):
        cx = x
        if i == 0:
            p.rect(x, ty, w, rh, blend(WHITE, INDIGO, 0.12))
        elif pn.get("heat"):
            hx = x
            for j, v in enumerate(r):
                val = to_number(v) if numeric[j] else None
                if val:
                    p.rect(hx, ty, widths[j], rh, blend(WHITE, INDIGO, 0.08 + 0.5 * val / heat_max))
                hx += widths[j]
        for j, lines in enumerate(cells):
            for k, ln in enumerate(lines):
                yy = ty + 4 + k * lead
                if numeric[j]:
                    p.text(cx + widths[j] - 6, yy, ln, size, SEMI if i == 0 else REG, INK, "right")
                else:
                    p.text(cx + 6, yy, ln, size, SEMI if (i == 0 or j == 0) else REG, INK)
            cx += widths[j]
        if i:
            p.rect(x, ty + rh - 0.6, w, 0.6, LINE)
        ty += rh


def pn_text(p, box, pn):
    x, y, w, h = box
    ty = _panel_head(p, box, pn.get("title"))
    for size in (10.5, 9.5, 9):                       # shrink a step before giving up
        lead = size * 1.42
        need = sum(len(wrap(b, REG, size, w - 14)) * lead + 7 for b in pn["bullets"])
        if ty + need <= y + h + 4:
            break
    else:
        raise ValueError(f"Scene {p.n}: the '{pn.get('title', 'text')}' panel has too much text. Shorten the bullets.")
    for b in pn["bullets"]:
        p.rect(x, ty + size * 0.45, 6, 2.4, INDIGO)
        ty += p.para(x + 14, ty, b, w - 14, size, REG, INK, leading=lead) + 7


def pn_stats(p, box, pn):
    x, y, w, h = box
    top = _panel_head(p, box, pn.get("title"))
    items = pn["stats"]
    per_row = 2 if len(items) > 2 and w < 360 else len(items)
    rows_n = -(-len(items) // per_row)
    cw, rh = w / per_row, (y + h - top) / rows_n
    for i, st in enumerate(items):
        cx, cy = x + (i % per_row) * cw, top + (i // per_row) * rh
        p.text(cx, cy + 4, st["value"], 20, SEMI, INK)
        p.para(cx, cy + 32, st["label"], cw - 12, 9, REG, GREY, leading=12)


def pn_line(p, box, pn):
    x, y, w, h = box
    top = _panel_head(p, box, pn.get("title"))
    xs, series = pn["x"], pn["series"]
    cols, k = [], 0
    for sr in series:
        if sr.get("style") == "index":
            cols.append(INK)
        else:
            cols.append(SERIES_COLORS[0] if k == 0 else SERIES_COLORS[(k + 1) % 4])
            k += 1
    # legend: every line is named, so each colour means something
    lx, ly = x, top
    for sr, col in zip(series, cols):
        item_w = 26 + pdfmetrics.stringWidth(sr["name"], REG, 8.5)
        if lx + item_w > x + w and lx > x:
            lx, ly = x, ly + 13
        if sr.get("style") == "index":
            p.rect(lx, ly + 4, 4, 2, col)
            p.rect(lx + 6, ly + 4, 4, 2, col)
        else:
            p.rect(lx, ly + 3, 10, 3, col)
        p.text(lx + 14, ly, sr["name"], 8.5, REG, INK)
        lx += item_w
    top = ly + 16
    x0, x1, y0, y1 = x, x + w - 62, top + 4, y + h - 16
    vals = [v for sr in series for v in sr["values"]]
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.08 or 1
    lo, hi = lo - pad, hi + pad
    c = p.c
    ends = []
    for sr, col in zip(series, cols):
        c.setStrokeColor(HexColor(col))
        c.setLineWidth(1.8 if sr.get("style") != "index" else 1.2)
        c.setDash(3, 2) if sr.get("style") == "index" else c.setDash()
        path = c.beginPath()
        for i, v in enumerate(sr["values"]):
            px = x0 + (x1 - x0) * i / (len(xs) - 1)
            py = y1 - (y1 - y0) * (v - lo) / (hi - lo)
            (path.moveTo if i == 0 else path.lineTo)(px, _y(py))
        c.drawPath(path, stroke=1, fill=0)
        ends.append([y1 - (y1 - y0) * (sr["values"][-1] - lo) / (hi - lo), sr.get("end", ""), col])
    c.setDash()
    ends.sort()
    for i in range(1, len(ends)):
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + 12)
    for yv, t, col in ends:
        if t:
            p.rect(x1 + 5, yv - 2, 6, 6, col)               # ties each value to its line
            p.text(x1 + 14, yv - 5, t, 9, SEMI, INK)
    p.text(x0, y1 + 4, xs[0], 8, REG, GREY)
    p.text(x1, y1 + 4, xs[-1], 8, REG, GREY, "right")


PANEL = {"bars": pn_bars, "donut": pn_donut, "stack": pn_stack, "table": pn_table,
         "text": pn_text, "stats": pn_stats, "line": pn_line}


def panels(p, s):
    top = p.content_frame(s)
    bottom = p.note(s)
    strip = s.get("strip") or []
    if strip:
        gap = 12
        cw = (W - 2 * M - gap * (len(strip) - 1)) / len(strip)
        card = blend(WHITE, INDIGO, 0.07)
        for i, st in enumerate(strip):
            sx = M + i * (cw + gap)
            p.rect(sx, top - 6, cw, 52, card, radius=5)
            p.text(sx + 12, top + 2, st["value"], 17, SEMI, INK)
            p.text(sx + 12, top + 27, st["label"], 8.5, REG, GREY)
        top += 52 + 10
    for box, pn in zip(boxes(s["layout"], top, bottom), s["panels"]):
        PANEL[pn["kind"]](p, box, pn)


DRAW = {"cover": cover, "act": act, "statement": statement, "stats": stats, "donut": donut,
        "table": table, "bars": bars, "timeline": timeline, "steps": steps, "text": text,
        "close": close, "fund": fund, "line": line, "panels": panels}


def render(doc, out):
    _fonts()
    c = canvas.Canvas(str(out), pagesize=(W, H))
    meta = doc.get("meta", {})
    c.setTitle(f"Growthvine, {meta.get('client', '')}".strip(" ,"))
    c.setAuthor("Growthvine")
    scenes = doc["scenes"]
    for n, s in enumerate(scenes, 1):
        DRAW[s["type"]](Page(c, doc, n, len(scenes)), s)
        c.showPage()
    c.save()
