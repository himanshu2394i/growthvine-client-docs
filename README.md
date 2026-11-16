# growthvine

A Claude skill that helps Growthvine advisors turn their allocation views into
client-ready proposals and reports (PDF or PPT). It leads a structured interview,
checks the advisor's inputs against each other, and only builds once the advisor
confirms the brief.

Version: 0.4.0 (proposals work end to end and use Growthvine fund data fully:
fund pages, returns vs the market, growth charts, look-through, overlap,
projections; interview, input check, cinematic PDF/PPT, number check, feedback.
Coming: other report types).

## Install

**claude.ai or the Claude desktop app:** download `growthvine.zip` from this
repo's Releases page, then go to Settings → Capabilities → Skills → upload. Turn on
code execution.

**Claude Code:**

```bash
git clone https://github.com/himanshu2394i/growthvine-client-docs ~/.claude/skills/growthvine
```

(Windows PowerShell: use `$env:USERPROFILE\.claude\skills\growthvine`.)

The Growthvine fund data connector (MCP) should be connected for fund data pages.

## Update

- Zip install: download the new zip and upload it again.
- Claude Code: `cd ~/.claude/skills/growthvine && git pull`

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
