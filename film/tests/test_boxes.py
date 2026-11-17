import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gates"))
import boxes  # noqa: E402


def scan(html):
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "compositions").mkdir()
        (Path(d) / "compositions" / "s.html").write_text(html, encoding="utf-8")
        return boxes.check(Path(d))


class Boxes(unittest.TestCase):
    def test_text_card_with_fixed_height_is_flagged(self):
        f = scan('<div id="wh-m" style="position:absolute;width:840px;height:180px;padding:28px 32px">Nifty LargeMidcap 250</div>')
        self.assertEqual(len(f), 1)
        self.assertIn("wh-m", f[0])

    def test_cards_built_in_script_strings_are_flagged(self):
        self.assertEqual(len(scan("x += `<div class=\"rc-c\" style=\"top:280px;height:400px;border-radius:14px;padding:40px\">${c[1]}</div>`;")), 1)

    def test_min_height_cards_and_bars_pass(self):
        self.assertEqual(scan('<div style="min-height:180px;padding:28px">text</div>'
                              '<div class="bar" style="left:0;top:0;width:200px;height:40px;background:#9B81F5"></div>'
                              '<div style="position:absolute;height:130px;background:#232321"></div>'), [])


if __name__ == "__main__":
    unittest.main()
