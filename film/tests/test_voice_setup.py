"""Guards the voice setup: the voice model can be installed by script, the advisor picks from a fixed menu of
voices (heard as samples first), and a film never runs with a voice that is not on the menu."""
import sys
import unittest
from pathlib import Path

FILM = Path(__file__).resolve().parents[1]
ROOT = FILM.parent
sys.path.insert(0, str(FILM))
import director  # noqa: E402
import setup_voice  # noqa: E402


class VoiceMenu(unittest.TestCase):
    def test_menu_voice_is_accepted(self):
        self.assertEqual(director.check_voice("af_heart"), "af_heart")

    def test_unknown_voice_stops_with_the_menu(self):
        with self.assertRaises(SystemExit) as e:
            director.check_voice("xx_nobody")
        self.assertIn("af_heart", str(e.exception))

    def test_every_menu_voice_is_offered_in_the_film_rules(self):
        s = (ROOT / "content" / "CONTENT.md").read_text(encoding="utf-8")
        for v in director.VOICES:
            self.assertIn(v, s)

    def test_basics_ask_which_voice(self):
        s = (ROOT / "content" / "CONTENT.md").read_text(encoding="utf-8")
        basics = s.split("1. **The basics**")[1].split("2. **")[0]
        self.assertIn("voice", basics.lower())


class Setup(unittest.TestCase):
    def test_model_files_have_known_sizes(self):
        names = {f[0] for f in setup_voice.FILES}
        self.assertEqual(names, {"kokoro-v1.0.onnx", "voices-v1.0.bin"})
        for name, url, size in setup_voice.FILES:
            self.assertTrue(url.startswith("https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"))
            self.assertGreater(size, 1_000_000)

    def test_readme_points_to_the_setup_script(self):
        self.assertIn("setup_voice.py", (FILM / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
