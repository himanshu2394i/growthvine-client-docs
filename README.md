# growthvine-client-docs

A [Claude Code skill](https://docs.claude.com/en/docs/claude-code/skills) that
turns dumped fund data (or a live Growthvine connector pull) into a client PDF or
PowerPoint that looks like Growthvine: Brand Book tokens plus the **C split /
Mint Billboard** language (mint outdoor cover, pin brief).

It is a full production skill. On trigger it should **ask** what you are making,
where the numbers come from, which sections to include (including chapters it has
not seen), and the tone, then generate the file. It is not a palette dump.

## Install

**Available in every project, for one person:**

```bash
git clone https://github.com/himanshu2394i/growthvine-client-docs ~/.claude/skills/growthvine-client-docs
```
(Windows PowerShell: replace `~` with `$env:USERPROFILE`.)

**Just this one project:**

```bash
git clone https://github.com/himanshu2394i/growthvine-client-docs .claude/skills/growthvine-client-docs
```

**Without a full git clone**, using [`degit`](https://github.com/Rich-Harris/degit):

```bash
npx degit himanshu2394i/growthvine-client-docs ~/.claude/skills/growthvine-client-docs
```

Claude Code auto-discovers `.claude/skills/<name>/SKILL.md`.

## Update (already cloned)

The skill is a git clone of this repo. Pull `master` when you want the latest
C-split / Brand Book notes. Do not copy files by hand.

**If you cloned with git** (user or project folder):

```bash
cd ~/.claude/skills/growthvine-client-docs   # or .claude/skills/growthvine-client-docs
git fetch origin
git checkout master
git pull origin master
```

Windows PowerShell: same commands, with `$env:USERPROFILE\.claude\skills\growthvine-client-docs` instead of `~`.

If you were on an old feature branch, switch to `master` first so you are not
left on a stale pin/rail write-up.

**If you installed with degit** (no `.git` folder):

```bash
npx degit himanshu2394i/growthvine-client-docs ~/.claude/skills/growthvine-client-docs --force
```

`--force` overwrites the existing folder. Degit does not remember a remote, so
this is a fresh copy of `master`, not a merge.

After updating, start a new chat so the agent re-reads `SKILL.md`.

## What's in here

| | |
|---|---|
| `SKILL.md` | Briefing first, then data, C-split design, generate. |
| `references/briefing.md` | The six questions: job, file, source, tone, sections, length. |
| `references/c-split.md` | Mint outdoor board + pin brief. Print translation. Source is the C-split mock. |
| `references/figures.md` | Every mock figure: what is code vs CSS, cover gap, logo bar. |
| `references/new-sections.md` | How to invent a chapter that is not on the menu. |
| `references/data.md` | Dumped data vs Growthvine connector. Which tool to call. |
| `references/design-tokens.md` | Palette, Poppins, logo don'ts, fingerprint rules. |
| `references/components.md` | Donut, waffle, stairs, pin, hairline table, paired bars, quartile tower. |
| `references/pdf-generation.md` | HTML to PDF vs reportlab. Page breaks. |
| `references/pptx-generation.md` | python-pptx. Native chart vs image. |
| `scripts/charts.py` | Donut, waffle, rolling line. `python charts.py` self-check. |
| `assets/` | Inverse logo, G mark, fingerprint arcs. |

## Source of truth

Brand Book for tokens. The C-split mock for layout and figures:
`.superdesign/tmp/mock-c-split.html` and `mock-core.js`. If this skill disagrees
with those files, trust the mock and update this repo. Do not guess a new hex.
