# growthvine-client-docs

A [Claude Code skill](https://docs.claude.com/en/docs/claude-code/skills) that teaches
Claude Growthvine's brand system — palette, type, logo rules, and the
donut/waffle/hairline-table component vocabulary from the fund-detail product — so
that every client-facing PDF or PowerPoint it generates looks consistent, without
re-deriving the design from scratch each time.

Not a design tool by itself. It only does anything once loaded into a Claude Code
session, where it triggers automatically whenever someone asks for a fund fact sheet,
a portfolio review deck, a client one-pager, or similar.

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

Either way, no further setup — Claude Code auto-discovers anything at
`.claude/skills/<name>/SKILL.md` (personal `~/.claude/skills/` or project-level).

## What's in here

| | |
|---|---|
| `SKILL.md` | The skill itself — when to trigger, the brand tokens, the page/slide grammar, pointers to everything else. |
| `references/design-tokens.md` | Full palette (hex/RGB/CMYK), type rules, logo lockups and minimum sizes, the brand book's "don'ts". |
| `references/components.md` | How to build the donut+legend, the 100-square waffle grid, hairline tables, paired bars, the quartile tower. |
| `references/pdf-generation.md` | PDF generation routes — HTML→PDF vs. reportlab, font-embedding gotchas. |
| `references/pptx-generation.md` | PPTX generation via python-pptx — native charts vs. image drop-in, font caveats. |
| `scripts/charts.py` | Dependency-free Python port of the donut/waffle drawing math, with a runnable self-check (`python charts.py`). |
| `assets/` | The white/inverse logo lockup and the fingerprint-arcs decorative motif, ready to embed. |

## Source of truth

The tokens here were read from Growthvine's internal Brand Book and the fund-detail
product's own prototype code — both live in Growthvine's private product repo, not
here. If something here goes stale, update it from there, not by guessing.
