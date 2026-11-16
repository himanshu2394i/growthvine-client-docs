"""Tests for reconcile.py. Run: python -m unittest discover -s scripts/tests"""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import reconcile  # noqa: E402

FIXTURE = SCRIPTS / "tests" / "fixtures" / "real_two_documents.json"


def small():
    """A tiny, fully consistent input: 2 holdings, 1 table."""
    return {
        "total": 1000000,
        "options": [{
            "name": "Option 1", "source": "test.xlsx", "stated_total": 1000000,
            "holdings": [
                {"name": "Fund A", "vehicle": "MF", "asset_class": "Equity", "amount": 600000, "bucket": "Growth", "percent": 60.0},
                {"name": "Fund B", "vehicle": "PMS", "asset_class": "Debt", "amount": 400000, "bucket": "Stability", "percent": 40.0},
            ],
        }],
        "tables": [{
            "name": "Bucket x Vehicle", "source": "plan.pdf", "option": "Option 1", "unit": "lakh",
            "rows": {"field": "bucket"}, "cols": {"field": "vehicle"},
            "cells": {"Growth": {"MF": 6}, "Stability": {"PMS": 4}},
            "row_totals": {"Growth": 6, "Stability": 4},
            "col_totals": {"MF": 6, "PMS": 4},
            "grand_total": 10,
            "row_percent": {"Growth": 60.0, "Stability": 40.0},
        }],
    }


def kinds(issues):
    return [i["kind"] for i in issues]


class CleanInput(unittest.TestCase):
    def test_consistent_input_has_no_issues(self):
        self.assertEqual(reconcile.check(small()), [])


class OptionChecks(unittest.TestCase):
    def test_holdings_not_adding_up_to_stated_total(self):
        data = small()
        data["options"][0]["stated_total"] = 1100000
        issues = reconcile.check(data)
        self.assertIn("option_total", kinds(issues))

    def test_option_total_differs_from_corpus(self):
        data = small()
        data["total"] = 2000000
        self.assertIn("option_vs_corpus", kinds(reconcile.check(data)))

    def test_stated_percent_wrong(self):
        data = small()
        data["options"][0]["holdings"][0]["percent"] = 65.0
        self.assertIn("holding_percent", kinds(reconcile.check(data)))

    def test_rounded_percent_is_fine(self):
        data = small()
        h = data["options"][0]["holdings"]
        h[0]["amount"], h[1]["amount"] = 333333, 666667
        h[0]["percent"], h[1]["percent"] = 33.3, 66.7
        data["tables"] = []
        self.assertEqual(reconcile.check(data), [])


class TableInternalChecks(unittest.TestCase):
    def test_row_total_not_matching_cells(self):
        data = small()
        data["tables"][0]["row_totals"]["Growth"] = 7
        self.assertIn("table_row_total", kinds(reconcile.check(data)))

    def test_col_total_not_matching_cells(self):
        data = small()
        data["tables"][0]["col_totals"]["PMS"] = 5
        self.assertIn("table_col_total", kinds(reconcile.check(data)))

    def test_grand_total_wrong(self):
        data = small()
        data["tables"][0]["grand_total"] = 11
        self.assertIn("table_grand_total", kinds(reconcile.check(data)))

    def test_row_percent_wrong(self):
        data = small()
        data["tables"][0]["row_percent"]["Growth"] = 50.0
        self.assertIn("table_percent", kinds(reconcile.check(data)))


class TableVsHoldings(unittest.TestCase):
    def test_cell_differs_from_holdings(self):
        data = small()
        t = data["tables"][0]
        t["cells"]["Growth"]["MF"] = 5
        t["row_totals"]["Growth"] = 5
        t["col_totals"]["MF"] = 5
        t["grand_total"] = 9
        t.pop("row_percent")
        issues = reconcile.check(data)
        self.assertIn("table_vs_holdings", kinds(issues))

    def test_holding_label_missing_from_table(self):
        data = small()
        data["options"][0]["holdings"][1]["bucket"] = "Diversifier"
        self.assertIn("label_not_in_table", kinds(reconcile.check(data)))

    def test_map_overriding_a_stated_label_is_a_conflict(self):
        data = small()
        t = data["tables"][0]
        t["rows"] = {"field": "asset_class", "map": [{"match": {"name": "Fund B"}, "to": "Equity"}]}
        t["cells"] = {"Equity": {"MF": 6, "PMS": 4}, "Debt": {}}
        t["row_totals"] = {"Equity": 10, "Debt": 0}
        t["row_percent"] = {"Equity": 100.0, "Debt": 0.0}
        self.assertIn("label_conflict", kinds(reconcile.check(data)))

    def test_table_for_unknown_option(self):
        data = small()
        data["tables"][0]["option"] = "Option 9"
        self.assertIn("unknown_option", kinds(reconcile.check(data)))


class RealWorldFixture(unittest.TestCase):
    """Anonymised real client inputs (Oct 2026). Two real mismatches exist."""

    def setUp(self):
        self.issues = reconcile.check(json.loads(FIXTURE.read_text(encoding="utf-8")))
        self.text = "\n".join(i["message"] for i in self.issues)

    def test_isif_counted_as_mf_in_plan_tables(self):
        # Plan says Core Growth MF = 60 L, holdings give 50 L.
        self.assertIn("Core Growth", self.text)
        self.assertRegex(self.text, r"MF.*₹60\.0 L.*₹50\.0 L")

    def test_hybrid_split_between_mf_and_sif(self):
        self.assertRegex(self.text, r"Hybrid.*SIF.*₹20\.0 L.*₹30\.0 L")

    def test_nuvama_debt_vs_alternatives(self):
        conflicts = [i for i in self.issues if i["kind"] == "label_conflict"]
        self.assertTrue(any("Nuvama" in i["message"] and "Debt" in i["message"]
                            and "Alternatives" in i["message"] for i in conflicts))

    def test_tables_are_internally_consistent(self):
        internal = {"table_row_total", "table_col_total", "table_grand_total", "table_percent"}
        self.assertFalse([i for i in self.issues if i["kind"] in internal])


class Formatting(unittest.TestCase):
    def test_lakh_and_crore(self):
        self.assertEqual(reconcile.fmt(5000000), "₹50.0 L")
        self.assertEqual(reconcile.fmt(30000000), "₹3.00 Cr")
        self.assertEqual(reconcile.fmt(150000), "₹1.5 L")


class Cli(unittest.TestCase):
    def run_cli(self, data, tmp_name):
        path = SCRIPTS / "tests" / tmp_name
        path.write_text(json.dumps(data), encoding="utf-8")
        try:
            return subprocess.run([sys.executable, str(SCRIPTS / "reconcile.py"), str(path)],
                                  capture_output=True, text=True, encoding="utf-8")
        finally:
            path.unlink()

    def test_clean_exits_zero(self):
        r = self.run_cli(small(), "_clean.json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("No issues", r.stdout)

    def test_issues_exit_one(self):
        data = copy.deepcopy(small())
        data["total"] = 2000000
        r = self.run_cli(data, "_bad.json")
        self.assertEqual(r.returncode, 1, r.stderr)


if __name__ == "__main__":
    unittest.main()
