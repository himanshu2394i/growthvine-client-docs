"""Tests for verify.py. Run: python -m unittest discover -s scripts/tests"""
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
import verify  # noqa: E402

FIX = SCRIPTS / "tests" / "fixtures"
INPUTS = json.loads((FIX / "confirmed_inputs.json").read_text(encoding="utf-8"))
SCENES = json.loads((FIX / "sample_scenes.json").read_text(encoding="utf-8"))


class Tokens(unittest.TestCase):
    def values(self, text):
        return [(t.kind, t.value) for t in verify.tokens(text)]

    def test_rupees_with_units(self):
        self.assertEqual(self.values("₹1.00 Cr and ₹70 L"), [("rupees", 1e7), ("rupees", 7e6)])

    def test_rupees_indian_commas_and_words(self):
        self.assertEqual(self.values("₹3,00,00,000 or ₹3 crore"), [("rupees", 3e7), ("rupees", 3e7)])

    def test_percent_and_plain_decimal(self):
        self.assertEqual(self.values("33.3% then 50.0"), [("percent", 33.3), ("plain", 50.0)])

    def test_ignores_counters_dates_and_durations(self):
        self.assertEqual(self.values("05 / 14 · 16 November 2026 · 3.5 years · 1 week · 3+ years"), [])

    def test_precision_from_decimals(self):
        t = verify.tokens("₹1.20 Cr")[0]
        self.assertAlmostEqual(t.tolerance, 50000)


class Allowed(unittest.TestCase):
    def test_includes_holdings_totals_and_group_sums(self):
        rupees, percents = verify.allowed(INPUTS)
        self.assertIn(1.2e7, rupees)        # Option 1, Within 1 week
        self.assertIn(5e6, rupees)          # Option 1, Core Growth x MF
        self.assertIn(3e7, rupees)          # corpus
        self.assertTrue(any(abs(p - 33.333) < 0.01 for p in percents))


class EndToEnd(unittest.TestCase):
    def build(self, scenes, ext=".pdf"):
        self.tmp = tempfile.TemporaryDirectory()
        out = Path(self.tmp.name) / f"doc{ext}"
        render.render(scenes, out)
        return out

    def tearDown(self):
        if hasattr(self, "tmp"):
            self.tmp.cleanup()

    def test_correct_pdf_has_no_issues(self):
        self.assertEqual(verify.check(INPUTS, self.build(SCENES)), [])

    def test_correct_pptx_has_no_issues(self):
        self.assertEqual(verify.check(INPUTS, self.build(SCENES, ".pptx")), [])

    def test_wrong_amount_is_caught_with_page(self):
        bad = copy.deepcopy(SCENES)
        bad["scenes"][4]["slices"][1]["display"] = "₹75 L"
        issues = verify.check(INPUTS, self.build(bad))
        self.assertTrue(any("₹75 L" in i and "page 5" in i for i in issues), issues)

    def test_the_old_timeline_mistake_is_caught(self):
        bad = copy.deepcopy(SCENES)
        bad["scenes"][8]["stops"][0]["text"] = "MF, SIF and PMS holdings · ₹1.70 Cr"
        issues = verify.check(INPUTS, self.build(bad))
        self.assertTrue(any("₹1.70 Cr" in i for i in issues), issues)

    def test_invented_forecast_is_caught(self):
        bad = copy.deepcopy(SCENES)
        bad["scenes"][9]["stats"].append({"value": "18%", "label": "Best case"})
        issues = verify.check(INPUTS, self.build(bad))
        self.assertTrue(any("18%" in i for i in issues), issues)


class Cli(unittest.TestCase):
    def test_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "doc.pdf"
            render.render(SCENES, out)
            r = subprocess.run([sys.executable, str(SCRIPTS / "verify.py"), str(FIX / "confirmed_inputs.json"), str(out)],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("match", r.stdout)


if __name__ == "__main__":
    unittest.main()
