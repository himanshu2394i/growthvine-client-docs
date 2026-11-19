"""Guards "set up Growthvine": one script checks the system tools (with an install command for each platform),
installs the rest, and the skill knows the phrase. Run: python -m unittest discover -s scripts/tests"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import setup_growthvine as setup  # noqa: E402


class SystemTools(unittest.TestCase):
    def test_node_must_be_22_or_newer(self):
        self.assertTrue(setup.node_ok("v22.19.0"))
        self.assertTrue(setup.node_ok("v24.1.0"))
        self.assertFalse(setup.node_ok("v20.11.1"))
        self.assertFalse(setup.node_ok(""))

    def test_missing_lists_only_what_is_absent(self):
        have = {"node", "npm", "ffmpeg", "ffprobe"}
        self.assertEqual(setup.missing(lambda t: t in have, "v22.0.0"), [])
        self.assertEqual(setup.missing(lambda t: t in have - {"ffmpeg"}, "v22.0.0"), ["ffmpeg"])
        self.assertEqual(setup.missing(lambda t: t in have, "v18.0.0"), ["node"])

    def test_every_missing_tool_has_an_install_command_on_each_platform(self):
        for tool in ("node", "ffmpeg"):
            for plat in ("win32", "darwin", "linux"):
                self.assertTrue(setup.hint(tool, plat).strip(), (tool, plat))

    def test_hyperframes_is_pinned_to_the_tested_version(self):
        self.assertEqual(setup.HYPERFRAMES, "0.9.58")


class Skill(unittest.TestCase):
    def test_skill_knows_the_phrase_and_the_script(self):
        s = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("set up Growthvine", s)
        self.assertIn("setup_growthvine.py", s)

    def test_readme_names_the_claude_ai_setting(self):
        r = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Create and edit files", r)
        self.assertIn("set up Growthvine", r)


if __name__ == "__main__":
    unittest.main()
