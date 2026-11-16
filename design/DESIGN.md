# Design: turn the answers into a cinematic document

You arrive here with the question set done and the inputs reconciled. Now plan
the document like a short film, agree it with the advisor, then build it.

**The idea:** the client should *watch* their plan unfold. An opening scene,
chapters with full-page title cards, one idea per page, big numbers, and a clear
arc from "where you stand" to "what happens next". Calm, confident, never flashy.

Work through steps 1-6 in order. Ask 2-3 things at a time.

## 1. The story (sections)

Build an outline of **acts** and **scenes**. Every scene does one job (see the
table) and has a *headline that says the takeaway*, not a label:
"Most of your money goes to steady, long-term growth", not "Allocation".

Default arc for a proposal (rename everything, freshly, every time):

| Act | Purpose | Typical scenes |
|---|---|---|
| Cover | Who it's for, the plan in one line | Client name, logline, profile facts |
| 1. Where you stand | What we understood | Profile, the starting point, what matters to them |
| 2. The plan | Where the money goes and why | Buckets, the split, options compared, each bucket's job |
| 3. Why it holds up | Evidence and honesty | Holdings, liquidity and lock-ins, what to expect, the catch |
| 4. What happens next | From yes to invested, and living with it | Steps, check-ins, what to do in a bad market |
| Close | Sources, disclaimer, contact | |

Scene jobs to choose from: set the scene · your profile · the plan · compare the
options · each bucket / holding's role · getting your money out · what to expect
(only advisor figures) · the evidence · what happens next · living with it ·
close. Practical explainers (what happens after you sign, what to do when markets
fall, when you can take money out and what it costs) beat definitions; never
write "what is a mutual fund" pages.

Show the advisor a numbered outline, acts as headers, scenes pre-ticked based on
the data and the client (see pre-tick rules below). Let them tick, untick,
rename, reorder. Then suggest 2-3 extra scenes they may not have thought of.
Repeat until they say done.

**Pre-tick rules:** "compare the options" only with 2+ options in one document ·
"getting your money out" whenever there are lock-ins or illiquid products ·
"what to expect" only if the advisor gave figures · practical explainers on for
first-time investors · per-holding scenes only at fund level and only if asked.

**Length:** short = 8-10 scenes · standard = 12-16 · detailed = 18-25 (act cards
and cover count).

## 2. Numbers only, or with comments?

Ask for every document: **numbers only** (tables and charts, no commentary) or
**with comments**. If comments, which kinds:

sum it up · why this choice · how to read this · the catch · its role · the
question to ask yourself · not a guarantee · (any kind they name)

Set once for the document; the advisor can override per scene. A comment becomes
the scene's `note` (one short boxed line or two). Write the label and text
freshly; don't reuse stock phrases. The "not a guarantee" note always stays next
to any expected-return figure, even in numbers-only mode.

## 3. How to show each scene

Propose a display per scene from this menu; the advisor confirms or swaps.

| Data | Default scene type | Alternatives |
|---|---|---|
| One sentence that matters | `statement` | `text` |
| 1-4 key numbers | `stats` | `statement` |
| Parts of a whole (buckets, asset classes) | `donut` | `bars`, `table` |
| Cross-tab (bucket x vehicle) | `table` with `heat: true` | `bars` |
| Option vs option | `bars` (one series per option) | `table` |
| Holdings list | `table` | split by bucket into several `table` scenes |
| Liquidity, lock-ins, horizons | `timeline` | `table` |
| Process from yes to invested | `steps` | `text` |
| Explanation | `text` | `statement` |

Rules: one main visual per scene; every number visible on the page (no
hover-only data); tables for anything the client may check line by line.
Scene field formats and limits: `design/SCENES.md`.

## 4. Language

Ask: tone (warm / formal) · simplicity (from the client's experience answer;
confirm) · length (short / standard / detailed). English only for now.

Copy rules: plain words; explain any unavoidable term in the same sentence; no
em-dashes; no hype ("best", "guaranteed", "superb"); numbers exactly as the
advisor wrote them; Growthvine guides, it doesn't instruct ("one thing worth
watching is...", not "you must...").

## 5. The visible brief

Show one summary and wait for a clear yes:

```
Making: <type> for <client>, prepared by <RM>, as <PDF | PPT>
Inputs: <files>, reconciled (<issues resolved / differences kept>)
Missing data: <holding → choice>
Story: <acts and scene headlines, numbered, with display type>
Comments: <numbers only | kinds chosen>
Tone / language / length: <...>
```

Changes → update and show again. Nothing is built before the yes.

## 6. Build

1. Write `scenes.json` (format: `design/SCENES.md`). Every figure comes from the
   confirmed `inputs.json` or advisor answers, copied exactly as text.
2. Render: `python scripts/render.py scenes.json <name>.pdf` (or `.pptx`).
   If it reports validation errors, fix `scenes.json` and run again (usually:
   split a long table, shorten a line).
3. **Look at it.** For PDF, turn pages into images and view every one:
   `python scripts/render.py scenes.json out.pdf --preview previews/`. Fix
   anything cramped, overflowing or unclear, and render again.
4. Go to `check/CHECK.md` part B (automatic number check + your own re-read),
   then deliver.

## Brand (built into the renderer, don't override)

- Widescreen 16:9 pages, like film frames. Thin letterbox bars on content scenes.
- Foundation Grey `#1D1D1B` grounds for cover, act cards and close; Clarity White
  for content scenes. Vine Indigo `#9B81F5` for emphasis. Mint, Peach, Mustard
  tell categories apart. Each bucket keeps one colour through the whole document
  (set `palette` in `scenes.json`).
- Poppins Semibold for headlines and big numbers, Poppins Regular for body.
- Official logos only (`assets/logos/`): white wordmark on dark scenes, dark
  wordmark on light ones, tagline lockup on cover and close.
- Fingerprint-arc motif on dark scenes only, subtle.
- Disclaimer: the basic one in `design/SCENES.md` until compliance wording exists.

In PPT, Poppins shows only where it's installed; tell the advisor that, and offer
the PDF when the deck goes to a client.
