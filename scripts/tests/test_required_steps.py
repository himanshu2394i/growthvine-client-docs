"""Guards the required steps: every document and film waits for the advisor at each step, and the section menu is
never skipped. Run: python -m unittest discover -s scripts/tests"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TYPES = ["proposal", "assess", "fund", "category", "market"]


class RequiredSteps(unittest.TestCase):
    def test_skill_lists_the_four_required_steps(self):
        s = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Required steps", s)
        for step in ("The basics", "Sections and subsections", "Storyboard", "Build"):
            self.assertIn(step, s)
        self.assertIn("clarifying questions only", s)

    def test_every_question_set_points_to_the_required_steps(self):
        for t in TYPES:
            s = (ROOT / t / "QUESTIONS.md").read_text(encoding="utf-8")
            self.assertIn("Required steps", s, t)

    def test_films_and_documents_follow_them(self):
        for p in ("content/CONTENT.md", "design/DESIGN.md"):
            self.assertIn("Required steps", (ROOT / p).read_text(encoding="utf-8"), p)


if __name__ == "__main__":
    unittest.main()
