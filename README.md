# growthvine

A Claude skill that helps Growthvine advisors turn their allocation views into
client-ready proposals and reports (PDF or PPT) and content films (MP4 with
voice and music). It leads a structured interview, shows every section to pick
from, gets the brief or storyboard approved, and only then builds.

Version: 0.12.0. Makes allocation proposals, portfolio assessments, and fund,
category and market reports, as PDF, PPT or film. Every figure comes from the
advisor's inputs or Growthvine fund data and is checked before delivery.

**Films need a computer, not claude.ai:** they are built with Claude Code and
local tools (HyperFrames, the Kokoro voice, ffmpeg, Node 22+, Chrome). Setup is
in `film/README.md`. Point `GV_TOOLS` at the tools folder if it is not next to
the skill folder. PDF and PPT work in both.

## Install

**claude.ai or the Claude desktop app** (PDF and PPT):

1. Get `growthvine.zip` (from whoever shared the skill, or this repo's Releases page).
2. Settings → Capabilities: turn on **Create and edit files** (skills need it).
   Turning on **Use the internet while making files** lets Claude install a
   missing PDF or PPT package if it needs to.
3. In the Skills section of the same page, upload the zip.
4. Start a new chat and say "use Growthvine".

**Claude Code** (PDF, PPT and films):

```bash
git clone https://github.com/himanshu2394i/growthvine-client-docs ~/.claude/skills/growthvine
```

(Windows PowerShell: use `"$env:USERPROFILE\.claude\skills\growthvine"` as the last part.
Or unzip `growthvine.zip` into the skills folder so `skills/growthvine/SKILL.md` exists.)

Then start a session and say **"set up Growthvine"**. Claude runs
`setup_growthvine.py` (after asking), which installs everything the skill uses:

| What | Why | How it gets there |
|---|---|---|
| reportlab, python-pptx, pymupdf | PDF, PPT, page previews | installed by the setup (pip) |
| HyperFrames 0.9.58 + its Chrome | turns film scenes into video | installed by the setup (npm), into `tools/` |
| Kokoro voice (about 350 MB) | the film's narration, offline | installed by the setup, into `tools/` |
| Node 22+ | runs HyperFrames | you install it once; the setup prints the command |
| ffmpeg | sound and video files | you install it once; the setup prints the command |

`tools/` sits beside the skill folder (set `GV_TOOLS` to put it elsewhere).
Running the setup again is safe; it skips what is already there.

**Both:** connect the Growthvine fund data connector (MCP) for fund pages,
rankings and market comparisons.

## Update

- Zip install: upload the new zip again.
- Claude Code: `cd ~/.claude/skills/growthvine && git pull`, then say "set up Growthvine" again.

Start a new chat afterwards.

## Use

Say "use Growthvine" or ask for a proposal or report. To report a problem or
suggest a change, say "feedback".

## What's inside

| Path | Job |
|---|---|
| `SKILL.md` | Entry: hard rules, first questions, routing |
| `proposal/QUESTIONS.md` | Proposal question set |
| `shared/data.md` | Data rules + fund data tool map |
| `shared/inputs.md` | Reading advisor files, writing `inputs.json` |
| `design/DESIGN.md` | Story, comments, display, language, brief, build |
| `design/SCENES.md` | `scenes.json` format for the renderer |
| `check/CHECK.md` | Input reconcile, verification, delivery |
| `feedback/FEEDBACK.md` | Feedback note, anonymising, form link |
| `scripts/reconcile.py` | Cross-checks advisor inputs |
| `scripts/render.py` | Renders `scenes.json` to PDF or PPT (`render_pdf.py`, `render_pptx.py`) |
| `scripts/verify.py` | Checks every figure in the finished document against the inputs |
| `scripts/analyse.py` | Look-through, overlap, returns vs index, growth, projections from saved fund data |
| `assets/` | Official logos and Poppins (SIL Open Font License) |
| `docs/specs/` | Design spec |
| `docs/dry-runs/` | What each real-data dry run found and fixed |

Rendering needs `reportlab` (PDF), `python-pptx` (PPT) and `pymupdf` (previews).
Not yet verified inside claude.ai's code environment; if one is missing there,
install it with pip. Locally: `pip install reportlab python-pptx pymupdf`.

## Tests

```bash
python -m unittest discover -s scripts/tests
```
