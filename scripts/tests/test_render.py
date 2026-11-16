"""Tests for render.py. Run: python -m unittest discover -s scripts/tests"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import render  # noqa: E402

SAMPLE = json.loads((SCRIPTS / "tests" / "fixtures" / "sample_scenes.json").read_text(encoding="utf-8"))


def sample():
    return copy.deepcopy(SAMPLE)


class Validation(unittest.TestCase):
    def test_sample_is_valid(self):
        self.assertEqual(render.validate(sample()), [])

    def test_unknown_type(self):
        d = sample()
        d["scenes"][2]["type"] = "hologram"
        errors = render.validate(d)
        self.assertTrue(any("Scene 3" in e and "hologram" in e for e in errors), errors)

    def test_missing_required_field(self):
        d = sample()
        del d["scenes"][4]["slices"]
        self.assertTrue(any("Scene 5" in e and "slices" in e for e in render.validate(d)))

    def test_table_too_long(self):
        d = sample()
        d["scenes"][5]["rows"] = [["x"] * 7] * 12
        self.assertTrue(any("Scene 6" in e and "rows" in e for e in render.validate(d)))

    def test_row_width_must_match_columns(self):
        d = sample()
        d["scenes"][5]["rows"][0] = ["Core Growth", "50.0"]
        self.assertTrue(any("Scene 6" in e and "columns" in e for e in render.validate(d)))

    def test_title_too_long(self):
        d = sample()
        d["scenes"][2]["title"] = "x" * 91
        self.assertTrue(any("Scene 3" in e and "title" in e for e in render.validate(d)))

    def test_bars_values_match_series(self):
        d = sample()
        d["scenes"][6]["categories"][0]["values"] = [100]
        self.assertTrue(any("Scene 7" in e for e in render.validate(d)))


class Palette(unittest.TestCase):
    def test_explicit_then_fallback_order(self):
        colors = render.palette({"palette": {"A": "peach"}}, ["A", "B", "C"])
        self.assertEqual(colors["A"], render.COLORS["peach"])
        self.assertEqual(colors["B"], render.COLORS["indigo"])
        self.assertEqual(colors["C"], render.COLORS["mint"])


class Pdf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import fitz
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "out.pdf"
        render.render(sample(), cls.path)
        cls.doc = fitz.open(cls.path)
        # Non-breaking spaces keep amounts on one line; they look like spaces.
        cls.pages = [p.get_text().replace(" ", " ") for p in cls.doc]

    @classmethod
    def tearDownClass(cls):
        cls.doc.close()
        cls.tmp.cleanup()

    def test_one_page_per_scene(self):
        self.assertEqual(len(self.pages), len(SAMPLE["scenes"]))

    def test_widescreen(self):
        r = self.doc[0].rect
        self.assertEqual((round(r.width), round(r.height)), (960, 540))

    def test_titles_on_their_pages(self):
        for i, scene in enumerate(SAMPLE["scenes"]):
            self.assertIn(scene["title"].split()[0], self.pages[i], f"scene {i + 1}")

    def test_numbers_appear_exactly(self):
        text = "\n".join(self.pages)
        for s in ["₹3,00,00,000", "₹1.00 Cr", "33.3%", "13.5%", "₹1.20 Cr", "300.0"]:
            self.assertIn(s, text)

    def test_notes_render(self):
        self.assertIn("not a guarantee", self.pages[9].lower())  # label is set in capitals

    def test_amounts_never_split_across_lines(self):
        for page in self.pages:
            self.assertNotRegex(page, r"\d\n(Cr|L)\b")

    def test_letter_spacing_does_not_leak(self):
        self.assertIn("Private and confidential", self.pages[2])

    def test_dark_scenes_carry_the_mark(self):
        for i, scene in enumerate(SAMPLE["scenes"]):
            if scene["type"] in ("cover", "act", "close"):
                self.assertTrue(self.doc[i].get_images(), f"scene {i + 1} has no mark")

    def test_act_cards_frame_the_mark_differently(self):
        acts = [i for i, s in enumerate(SAMPLE["scenes"], 1) if s["type"] == "act"]
        self.assertEqual(len({render.shot_for(SAMPLE, n) for n in acts}), len(acts))

    def test_poppins_embedded(self):
        fonts = {f[3] for p in self.doc for f in p.get_fonts()}
        self.assertTrue(any("Poppins" in f for f in fonts), fonts)

    def test_preview_images(self):
        out = Path(self.tmp.name) / "previews"
        paths = render.preview(self.path, out)
        self.assertEqual(len(paths), len(SAMPLE["scenes"]))
        self.assertTrue(all(p.exists() for p in paths))


FUND = {"type": "fund", "kicker": "₹10 L, 3.3% of the plan", "title": "Invesco India Large & Mid Cap Fund",
        "as_of": "Returns to 26 Oct 2026, Regular growth",
        "stats": [{"value": "+10.5%", "label": "1 month"}, {"value": "+4.1%", "label": "3 months"},
                  {"value": "+15.9%", "label": "6 months"}],
        "facts": [{"label": "Run by", "value": "Aditya Khemani"}, {"label": "Fund size", "value": "₹12,439 Cr"},
                  {"label": "Annual charge", "value": "1.47%"}, {"label": "Exit charge", "value": "1% within 365 days"}],
        "what": "A concentrated book of 44 large and mid-sized companies, almost fully invested in shares.",
        "watch": "Its worst fall in the last three years was 19.0%, deeper than the market's.",
        "note": {"label": "Its role", "text": "The established-company anchor of Core Growth.", "tone": "info"}}
LINE = {"type": "line", "title": "₹1 lakh in each, five years ago",
        "x": ["Oct 2021", "Oct 2022", "Oct 2023", "Oct 2024", "Oct 2025", "Oct 2026"],
        "series": [{"name": "Invesco India Large & Mid Cap", "values": [100000, 104000, 125000, 170000, 180000, 211000], "end": "₹2.11 L"},
                   {"name": "Nifty 500 TRI", "values": [100000, 102000, 118000, 150000, 152000, 168000], "end": "₹1.68 L", "style": "index"}]}


PANELS = {"type": "panels", "kicker": "The funds", "title": "Invesco India Large & Mid Cap Fund",
          "as_of": "Returns to 30 Sep 2026, Regular growth",
          "strip": [{"value": "+20.1%", "label": "3 years a year"}, {"value": "₹12,439 Cr", "label": "Fund size"},
                    {"value": "1.47%", "label": "Annual charge"}, {"value": "44", "label": "Companies held"}],
          "layout": "2x2",
          "panels": [
              {"kind": "bars", "title": "Returns vs the market", "series": ["Fund", "Nifty 500 TRI"],
               "categories": [{"label": "1 year", "values": [6.4, -2.0], "display": ["+6.4%", "-2.0%"]},
                              {"label": "3 years", "values": [20.1, 9.5], "display": ["+20.1%", "+9.5%"]}]},
              {"kind": "stack", "title": "Company size", "segments": [
                  {"label": "Large", "value": 40.6, "display": "41%"}, {"label": "Mid", "value": 33.6, "display": "34%"},
                  {"label": "Small", "value": 25.8, "display": "26%"}]},
              {"kind": "table", "title": "Top holdings", "columns": ["Company", "Weight"],
               "rows": [["Eternal", "8.6%"], ["InterGlobe Aviation", "7.9%"], ["ICICI Bank", "7.4%"]]},
              {"kind": "text", "title": "Our view", "bullets": [
                  "Beat the market by over 10 points a year across three years.",
                  "Concentrated: the top ten holdings are over half the fund."]}]}
DONUT_PANELS = {"type": "panels", "title": "Where the money goes", "layout": "1+2", "panels": [
    {"kind": "donut", "title": "By bucket", "slices": [{"label": "Core Growth", "value": 100, "display": "₹1.00 Cr"},
                                                      {"label": "Stability", "value": 70, "display": "₹70 L"}], "center": "₹1.70 Cr"},
    {"kind": "stats", "title": "At a glance", "stats": [{"value": "12", "label": "Holdings"}, {"value": "4", "label": "Buckets"}]},
    {"kind": "line", "title": "Growth of ₹1 lakh", "x": ["2021", "2023", "2026"],
     "series": [{"name": "Fund", "values": [100000, 150000, 200000], "end": "₹2.0 L"}]}]}


class Panels(unittest.TestCase):
    def doc(self, *scenes):
        d = sample()
        d["scenes"] = list(scenes)
        return d

    def test_valid(self):
        self.assertEqual(render.validate(self.doc(PANELS, DONUT_PANELS)), [])

    def test_panel_count_must_fit_layout(self):
        bad = json.loads(json.dumps(PANELS))
        bad["panels"] = bad["panels"][:3]
        self.assertTrue(any("Scene 1" in e and "2x2" in e for e in render.validate(self.doc(bad))))

    def test_unknown_panel_kind(self):
        bad = json.loads(json.dumps(PANELS))
        bad["panels"][0]["kind"] = "sparkle"
        self.assertTrue(any("sparkle" in e for e in render.validate(self.doc(bad))))

    def test_middle_dot_separators_are_rejected_anywhere(self):
        bad = json.loads(json.dumps(PANELS))
        bad["as_of"] = "Returns to 30 Sep 2026 · Regular growth"
        self.assertTrue(any("·" in e for e in render.validate(self.doc(bad))))

    def test_pdf_shows_every_panel(self):
        import fitz
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "p.pdf"
            render.render(self.doc(PANELS, DONUT_PANELS), out)
            with fitz.open(out) as d:
                pages = [" ".join(pg.get_text().replace(" ", " ").split()) for pg in d]
        for s in ["+20.1%", "₹12,439 Cr", "Returns vs the market".upper(), "+9.5%", "41%", "Eternal", "8.6%",
                  "Beat the market by over 10 points"]:
            self.assertIn(s, pages[0])
        for s in ["₹1.70 Cr", "Core Growth", "₹70 L", "Holdings", "₹2.0 L"]:
            self.assertIn(s, pages[1])

    def test_every_chart_names_its_colours(self):
        """Every series, slice and segment label must be readable on the page,
        so a reader can tell what each colour means."""
        import fitz
        line = {"kind": "line", "title": "Growth", "x": ["2021", "2026"],
                "series": [{"name": "Invesco L&M", "values": [1, 2], "end": "₹2.0 L"},
                           {"name": "HDFC Value", "values": [1, 1.8], "end": "₹1.8 L"},
                           {"name": "Nifty 500 TRI", "values": [1, 1.5], "end": "₹1.5 L", "style": "index"}]}
        scene = dict(DONUT_PANELS, panels=[DONUT_PANELS["panels"][0], DONUT_PANELS["panels"][1], line])
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "legend.pdf"
            render.render(self.doc(PANELS, scene), out)
            with fitz.open(out) as d:
                pages = [" ".join(pg.get_text().split()) for pg in d]
        labels = {0: ["Fund", "Nifty 500 TRI", "Large", "Mid", "Small"],
                  1: ["Core Growth", "Stability", "Invesco L&M", "HDFC Value", "Nifty 500 TRI"]}
        for page, names in labels.items():
            for name in names:
                self.assertIn(name, pages[page], f"'{name}' has no label on page {page + 1}")

    def test_pptx_uses_native_charts_and_stays_on_slide(self):
        from pptx import Presentation
        from pptx.enum.chart import XL_CHART_TYPE
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "p.pptx"
            render.render(self.doc(PANELS, DONUT_PANELS), out)
            prs = Presentation(out)
        types = [s.chart.chart_type for sl in prs.slides for s in sl.shapes if s.has_chart]
        self.assertIn(XL_CHART_TYPE.BAR_CLUSTERED, types)
        self.assertIn(XL_CHART_TYPE.DOUGHNUT, types)
        self.assertIn(XL_CHART_TYPE.LINE, types)
        W, H = prs.slide_width, prs.slide_height
        for i, sl in enumerate(prs.slides, 1):
            for sh in sl.shapes:
                self.assertTrue(sh.left >= -1 and sh.top >= -1 and sh.left + sh.width <= W + 1
                                and sh.top + sh.height <= H + 1, f"slide {i}: {sh.name} off the slide")


class NewScenes(unittest.TestCase):
    def doc(self, *scenes):
        d = sample()
        d["scenes"] = list(scenes) + [SAMPLE["scenes"][-1]]
        return d

    def test_new_types_validate(self):
        self.assertEqual(render.validate(self.doc(FUND, LINE)), [])

    def test_line_needs_one_value_per_x(self):
        bad = json.loads(json.dumps(LINE))
        bad["series"][0]["values"] = [1, 2]
        self.assertTrue(any("Scene 1" in e for e in render.validate(self.doc(bad))))

    def test_fund_and_line_in_pdf(self):
        import fitz
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "n.pdf"
            render.render(self.doc(FUND, LINE), out)
            with fitz.open(out) as d:
                fund, line = (" ".join(d[i].get_text().replace(" ", " ").split()) for i in (0, 1))
        for s in ["Aditya Khemani", "₹12,439 Cr", "+15.9%", "almost fully invested", "deeper than the market", "Its role".upper()]:
            self.assertIn(s, fund)
        for s in ["₹2.11 L", "₹1.68 L", "Nifty 500 TRI", "Oct 2021", "Oct 2026"]:
            self.assertIn(s, line)

    def test_fund_and_line_in_pptx(self):
        from pptx import Presentation
        from pptx.enum.chart import XL_CHART_TYPE
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "n.pptx"
            render.render(self.doc(FUND, LINE), out)
            prs = Presentation(out)
            fund_text = "\n".join(s.text_frame.text for s in prs.slides[0].shapes if s.has_text_frame)
            fund_text += "\n".join(c.text for s in prs.slides[0].shapes if s.has_table for r in s.table.rows for c in r.cells)
            charts = [s.chart.chart_type for s in prs.slides[1].shapes if s.has_chart]
        self.assertIn("Aditya Khemani", fund_text)
        self.assertIn("almost fully invested", fund_text)
        self.assertIn(XL_CHART_TYPE.LINE, charts)

    def test_close_can_list_sources(self):
        import fitz
        close = dict(SAMPLE["scenes"][-1], sources="Fund data: Growthvine, 15 Nov 2026. Index: Nifty 500 TRI to 26 Oct 2026.")
        d = sample()
        d["scenes"] = [close]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "c.pdf"
            render.render(d, out)
            with fitz.open(out) as f:
                self.assertIn("Nifty 500 TRI to 26 Oct 2026", f[0].get_text().replace("\n", " "))


class LongTextTables(unittest.TestCase):
    """Dry-run finding: long cells were silently cut to their first line."""

    WHY = "Long-term compounding engine, diversified across market caps, asset classes and investment styles"

    def scene_doc(self, rows):
        d = sample()
        d["scenes"] = [{"type": "table", "title": "What each bucket is for",
                        "columns": ["Bucket", "Where", "Why", "Horizon"], "rows": rows}]
        return d

    def test_long_cells_wrap_instead_of_truncating(self):
        import fitz
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "t.pdf"
            render.render(self.scene_doc([["Core Growth", "MF, SIF, PMS", self.WHY, "5+ years, largely liquid"]]), out)
            with fitz.open(out) as doc:
                text = " ".join(doc[0].get_text().replace(" ", " ").split())
        self.assertIn(self.WHY, text)

    def test_text_that_cannot_fit_is_an_error_not_a_crop(self):
        rows = [[f"Bucket {i}", "MF", self.WHY * 4, "5+ years"] for i in range(9)]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError) as ctx:
                render.render(self.scene_doc(rows), Path(tmp) / "t.pdf")
        self.assertIn("Scene 1", str(ctx.exception))

    def test_short_columns_keep_room_for_their_words(self):
        widths = render.col_widths(["Bucket", "Job", "Horizon"],
                                   [["Core Growth", self.WHY, "5+ years"]], 400)
        self.assertGreaterEqual(widths[2], 55)   # "5+ years" fits on one line

    def test_columns_sized_to_content(self):
        widths = render.col_widths(["Bucket", "Where", "Why", "Horizon"],
                                   [["Core Growth", "MF", self.WHY, "5+ years"]], 800)
        self.assertAlmostEqual(sum(widths), 800)
        self.assertEqual(max(widths), widths[2])


class Pptx(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pptx import Presentation
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "out.pptx"
        render.render(sample(), cls.path)
        cls.prs = Presentation(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def slide_text(self, i):
        out = []
        for shape in self.prs.slides[i].shapes:
            if shape.has_text_frame:
                out.append(shape.text_frame.text)
            if shape.has_table:
                out += [c.text for r in shape.table.rows for c in r.cells]
        return "\n".join(out)

    def test_one_slide_per_scene_widescreen(self):
        self.assertEqual(len(self.prs.slides), len(SAMPLE["scenes"]))
        self.assertAlmostEqual(self.prs.slide_width / self.prs.slide_height, 16 / 9, places=2)

    def test_titles(self):
        for i, scene in enumerate(SAMPLE["scenes"]):
            self.assertIn(scene["title"], self.slide_text(i), f"scene {i + 1}")

    def test_nothing_hangs_off_the_slide(self):
        # PowerPoint shows overhanging shapes while editing, so crop instead.
        W, H = self.prs.slide_width, self.prs.slide_height
        for i, slide in enumerate(self.prs.slides, 1):
            for sh in slide.shapes:
                inside = (sh.left >= -1 and sh.top >= -1
                          and sh.left + sh.width <= W + 1 and sh.top + sh.height <= H + 1)
                self.assertTrue(inside, f"slide {i}: '{sh.name}' extends past the slide edge")

    def test_native_table_values(self):
        self.assertIn("300.0", self.slide_text(5))

    def test_native_charts(self):
        def chart_types(i):
            return [s.chart.chart_type for s in self.prs.slides[i].shapes if s.has_chart]
        from pptx.enum.chart import XL_CHART_TYPE
        self.assertIn(XL_CHART_TYPE.DOUGHNUT, chart_types(4))
        self.assertIn(XL_CHART_TYPE.BAR_CLUSTERED, chart_types(6))

    def test_numbers_appear_exactly(self):
        text = "\n".join(self.slide_text(i) for i in range(len(self.prs.slides)))
        for s in ["₹3,00,00,000", "13.5%", "₹1.20 Cr"]:
            self.assertIn(s, text)


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "render.py"), *args],
                              capture_output=True, text=True, encoding="utf-8")

    def test_invalid_scenes_exit_one_with_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = sample()
            d["scenes"][2]["type"] = "hologram"
            src = Path(tmp) / "s.json"
            src.write_text(json.dumps(d), encoding="utf-8")
            r = self.run_cli(str(src), str(Path(tmp) / "o.pdf"))
            self.assertEqual(r.returncode, 1)
            self.assertIn("hologram", r.stdout)
            self.assertFalse((Path(tmp) / "o.pdf").exists())

    def test_layout_overflow_is_a_plain_message_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = sample()
            long = "Long-term compounding engine, diversified across market caps and styles " * 6
            d["scenes"] = [{"type": "table", "title": "Too much", "columns": ["A", "B"],
                            "rows": [[f"Row {i}", long] for i in range(9)]}]
            src = Path(tmp) / "s.json"
            src.write_text(json.dumps(d), encoding="utf-8")
            r = self.run_cli(str(src), str(Path(tmp) / "o.pdf"))
            self.assertEqual(r.returncode, 1)
            self.assertIn("Scene 1", r.stdout)
            self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_bad_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "s.json"
            src.write_text(json.dumps(sample()), encoding="utf-8")
            r = self.run_cli(str(src), str(Path(tmp) / "o.docx"))
            self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()


class CoverTitle(unittest.TestCase):
    def test_short_title_stays_big_on_one_line(self):
        import render_pdf
        size, leading, lines = render_pdf.cover_title("Client A")
        self.assertEqual((size, len(lines)), (60, 1))

    def test_long_title_shrinks_and_leaves_room_for_the_logline(self):
        import render_pdf
        size, leading, lines = render_pdf.cover_title("Invesco India Large & Mid Cap Fund")
        self.assertLess(size, 60)
        self.assertLessEqual(len(lines), 2)
        self.assertLessEqual(172 + leading * len(lines), 270)   # logline starts below the title


class ActTitle(unittest.TestCase):
    def test_long_act_title_shrinks_to_fit(self):
        import render_pdf
        size, leading, lines = render_pdf.fit_title("What the category delivers", 52, 40)
        self.assertEqual(size, 40)
        size, leading, lines = render_pdf.fit_title("Bonds", 52, 40)
        self.assertEqual((size, len(lines)), (52, 1))


class BarSpacing(unittest.TestCase):
    def test_few_bars_stay_compact_in_a_tall_panel(self):
        self.assertLessEqual(render.bar_block(300, 2, 1), 34)   # not 150pt per bar
        self.assertLessEqual(render.bar_block(300, 2, 2), 48)

    def test_many_bars_share_a_short_panel(self):
        self.assertAlmostEqual(render.bar_block(120, 8, 1), 15)


SCATTER = {"kind": "scatter", "title": "Return against swing, 3 years", "x_label": "Typical yearly swing, %",
           "y_label": "Return a year, %", "highlight_name": "Top five", "others_name": "Other funds",
           "points": [{"label": "Invesco", "x": 18.9, "y": 22.0, "highlight": True},
                      {"label": "SBI", "x": 13.9, "y": 12.5, "highlight": True},
                      {"label": "Tata", "x": 16.4, "y": 6.2}, {"label": "Kotak", "x": 15.7, "y": 13.3}]}


class Scatter(unittest.TestCase):
    def doc(self, panel):
        d = sample()
        d["scenes"] = [{"type": "panels", "title": "Risk and return", "layout": "2",
                        "panels": [panel, {"kind": "text", "title": "What this tells us", "bullets": ["One point."]}]}]
        return d

    def test_scatter_needs_points_and_axis_labels(self):
        self.assertEqual(render.validate(self.doc(SCATTER)), [])
        bad = {k: v for k, v in SCATTER.items() if k != "y_label"}
        self.assertTrue(any("y_label" in e for e in render.validate(self.doc(bad))))

    def test_pdf_scatter_names_axes_colours_and_highlights(self):
        import fitz
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "s.pdf"
            render.render(self.doc(SCATTER), out)
            with fitz.open(out) as d:
                text = " ".join(d[0].get_text().split())
        for s in ["Typical yearly swing, %", "Return a year, %", "Top five", "Other funds", "Invesco", "SBI"]:
            self.assertIn(s, text)
        self.assertNotIn("Tata", text)        # only highlighted points get a name

    def test_pptx_scatter_is_a_native_xy_chart(self):
        from pptx import Presentation
        from pptx.enum.chart import XL_CHART_TYPE
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "s.pptx"
            render.render(self.doc(SCATTER), out)
            types = [s.chart.chart_type for sl in Presentation(out).slides for s in sl.shapes if s.has_chart]
        self.assertIn(XL_CHART_TYPE.XY_SCATTER, types)


class TableOverflowMessage(unittest.TestCase):
    def test_overflow_error_says_how_many_rows_fit(self):
        d = sample()
        big = {"kind": "table", "title": "Too long", "columns": ["Company", "Weight"],
               "rows": [[f"Company {i}", f"{i}.0%"] for i in range(11)]}
        txt = {"kind": "text", "title": "Note", "bullets": ["One point."]}
        d["scenes"] = [{"type": "panels", "title": "Overflow", "layout": "2x2", "panels": [big, txt, txt, txt]}]
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError) as cm:
            render.render(d, Path(tmp) / "o.pdf")
        self.assertRegex(str(cm.exception), r"fits (\d+) rows")


class ScatterLabels(unittest.TestCase):
    def render_words(self, points):
        import fitz
        panel = dict(SCATTER, points=points)
        d = Scatter().doc(panel)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "s.pdf"
            render.render(d, out)
            with fitz.open(out) as doc:
                return doc[0].get_text("words"), " ".join(doc[0].get_text().split())

    def test_named_points_get_a_label_without_highlight(self):
        _, text = self.render_words([{"label": "Invesco", "x": 18.9, "y": 22.0, "highlight": True},
                                     {"label": "Motilal", "x": 21.9, "y": 20.0, "named": True},
                                     {"label": "Tata", "x": 16.4, "y": 6.2}])
        self.assertIn("Motilal", text)
        self.assertNotIn("Tata", text)

    def test_close_labels_do_not_overlap(self):
        words, _ = self.render_words([{"label": "DSP", "x": 16.0, "y": 13.2, "highlight": True},
                                      {"label": "Edelweiss", "x": 16.1, "y": 13.3, "highlight": True},
                                      {"label": "Kotak", "x": 15.7, "y": 13.3, "highlight": True},
                                      {"label": "Far", "x": 22.0, "y": 6.0}])
        boxes = [w[:4] for w in words if w[4] in ("DSP", "Edelweiss", "Kotak")]
        self.assertEqual(len(boxes), 3)
        for i in range(3):
            for j in range(i + 1, 3):
                a, b = boxes[i], boxes[j]
                overlap = a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
                self.assertFalse(overlap, f"labels overlap: {a} {b}")

    def test_axes_show_more_than_two_ticks(self):
        words, _ = self.render_words(SCATTER["points"])
        nums = {w[4] for w in words if w[4].isdigit()}
        self.assertGreaterEqual(len(nums), 6)


class BlankHeaderTable(unittest.TestCase):
    """A table whose column headers are all blank draws no header row (no thin
    coloured strip for the first row to overlap)."""
    PANEL = {"kind": "table", "title": "Key facts", "columns": ["", ""],
             "rows": [["Fund manager", "Aditya Khemani"], ["Fund house", "Invesco Mutual Fund"]]}

    def doc(self):
        d = sample()
        txt = {"kind": "text", "title": "Note", "bullets": ["One point."]}
        d["scenes"] = [{"type": "panels", "title": "Facts", "layout": "2", "panels": [self.PANEL, txt]}]
        return d

    def test_pdf_draws_no_header_band(self):
        import fitz
        import render_pdf
        band = render_pdf.blend(render_pdf.WHITE, render_pdf.INDIGO, 0.12).lstrip("#").lower()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "t.pdf"
            render.render(self.doc(), out)
            with fitz.open(out) as doc:
                fills = ["".join(f"{round(c * 255):02x}" for c in d["fill"])
                         for d in doc[0].get_drawings() if d.get("fill")]
        self.assertNotIn(band, fills)

    def test_pptx_table_has_only_body_rows(self):
        from pptx import Presentation
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "t.pptx"
            render.render(self.doc(), out)
            tables = [s.table for s in Presentation(out).slides[0].shapes if s.has_table]
        self.assertEqual(len(tables[0].rows), 2)


class EmptySpace(unittest.TestCase):
    """render.empty_space names content pages whose lower part is mostly blank."""
    def pages(self, scenes):
        d = sample()
        d["scenes"] = scenes
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "e.pdf"
            render.render(d, out)
            return render.empty_space(out, d)

    def test_short_panels_page_is_flagged(self):
        short = {"kind": "text", "title": "Note", "bullets": ["One point."]}
        msgs = self.pages([{"type": "panels", "title": "Half empty", "layout": "2", "panels": [short, short]}])
        self.assertEqual(len(msgs), 1)
        self.assertRegex(msgs[0], r"Scene 1 .*\d+% of the page is empty")

    def test_act_pages_are_not_flagged(self):
        self.assertEqual(self.pages([{"type": "act", "number": "01", "title": "Part one", "logline": "Short."}]), [])

    def test_full_page_is_not_flagged(self):
        line = copy.deepcopy(LINE)
        self.assertEqual(self.pages([line]), [])
