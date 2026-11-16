import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import film  # noqa: E402


class Film(unittest.TestCase):
    def test_indian_grouping(self):
        self.assertEqual(film.inr(30000000), "3,00,00,000")
        self.assertEqual(film.inr(12000000), "1,20,00,000")
        self.assertEqual(film.inr(999), "999")

    def test_fades_from_and_to_black(self):
        img = film.Image.new("RGB", (film.W, film.H), film.WHITE)
        self.assertEqual(film.finish(img.copy(), 0, 5).getpixel((960, 540)), (0, 0, 0))
        self.assertGreater(film.finish(img.copy(), 2.5, 5).getpixel((960, 540))[0], 200)


if __name__ == "__main__":
    unittest.main()
