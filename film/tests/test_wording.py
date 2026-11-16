import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gates"))
import wording  # noqa: E402


def rules(text, voice=True):
    return {r for _, r, _, _ in wording.check(text, voice)}


class Wording(unittest.TestCase):
    def test_catches_the_ai_lines_from_our_first_drafts(self):
        self.assertIn("fragment-drama", rules("Three crore rupees. Years of work, in one number."))
        self.assertIn("slogan", rules("Every rupee gets a job before it gets a fund."))
        self.assertIn("false-agency", rules("Markets have gone nowhere."))
        self.assertIn("not-x-but-y", rules("Not into one good fund."))
        self.assertIn("fake-intimacy", rules("Your money has four jobs."))

    def test_disclaimer_is_not_a_promise(self):
        self.assertNotIn("promise", rules("These are estimates, not guarantees."))
        self.assertIn("promise", rules("Returns are guaranteed."))

    def test_analyst_sentences_pass(self):
        self.assertEqual(rules("One AIF and one structured product hold ₹1.30 Cr, 43% of the total, with lock-ins."), set())
        self.assertEqual(rules("The Nifty 500 returned minus two percent over the past year."), set())

    def test_client_questions_on_screen_are_fine(self):
        self.assertEqual(rules("How much of it is in equity?", voice=False), set())


if __name__ == "__main__":
    unittest.main()
