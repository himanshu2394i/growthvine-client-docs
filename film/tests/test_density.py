import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gates"))
import density  # noqa: E402


def frame(lines):
    im = Image.new("RGB", (1920, 1080), (20, 20, 19))
    d = ImageDraw.Draw(im)
    for i in range(lines):
        for j in range(12):
            d.text((60 + j * 150, 40 + i * 26), "₹12.9% 1st", fill=(244, 244, 239))
    return im


class Density(unittest.TestCase):
    def test_empty_frame_is_clean(self):
        self.assertLess(density.ink(frame(0)), 0.01)

    def test_more_text_scores_higher(self):
        self.assertGreater(density.ink(frame(38)), density.ink(frame(6)))

    def test_crowded_frames_are_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            frame(6).save(Path(d) / "frame-00-at-1.0s.png")
            frame(38).save(Path(d) / "frame-01-at-2.0s.png")
            found = density.check(Path(d), limit=density.ink(frame(20)))
        self.assertEqual(len(found), 1)
        self.assertIn("2.0s", found[0])


    def test_borderline_frames_are_a_warning_not_a_failure(self):
        with tempfile.TemporaryDirectory() as d:
            frame(20).save(Path(d) / "frame-00-at-1.0s.png")
            mid = density.ink(frame(20))
            self.assertEqual(density.check(Path(d), limit=mid + 0.01), [])
            self.assertEqual(len(density.review(Path(d), warn=mid - 0.01, limit=mid + 0.01)), 1)


if __name__ == "__main__":
    unittest.main()
