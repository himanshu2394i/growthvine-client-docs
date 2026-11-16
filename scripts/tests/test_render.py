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

    def test_bad_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "s.json"
            src.write_text(json.dumps(sample()), encoding="utf-8")
            r = self.run_cli(str(src), str(Path(tmp) / "o.docx"))
            self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
