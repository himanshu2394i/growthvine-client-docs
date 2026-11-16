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
| 1. Where you stand | What we understood, and where markets are | Profile, market snapshot (index returns), what matters to them |
| 2. The plan | Where the money goes and why | Buckets, the split, options compared, each bucket's job, holdings with a "what it does" line each |
| 3. Why it holds up | The evidence, from fund data | Returns vs the market, growth of ₹1 lakh chart, what you'll actually own (look-through), are these funds buying the same shares (overlap), liquidity and lock-ins, what to expect |
| 4. The funds | One page per holding | Fund profile: recent returns, facts, what it does, worth knowing, its role |
| 5. What happens next | From yes to invested, and living with it | Steps, check-ins, what to do in a bad market |
| Close | Sources and dates, disclaimer, contact | |

**Default arcs for reports** (same rules: rename freshly, content-heavy panel
pages, comments that interpret the data):

*Portfolio assessment*

| Act | Purpose | Typical panel pages |
|---|---|---|
| Cover | Whose portfolio, value, the take-away in one line | |
| 1. Where you are today | The portfolio in numbers | Strip (value, holdings, blended charge, as-of); asset mix (`stack`), by holding (`donut` or `table`), progress to goals if given |
| 2. How it has done | Evidence | Returns vs the market (`bars`), growth of ₹1 lakh (`line`), each fund against its category (rank and quartile in a `table`) |
| 3. What you actually own | Look-through | Companies (`table`), industries (`bars`), company size (`stack`), overlap (heat `table`) |
| 4. What it costs and how concentrated it is | Cost and risk | Blended charge in ₹ a year (`stats`), largest holding and top three (`stats`), worst falls (`bars`) |
| 5. What we'd look at | Observations to discuss | `text` panels with observations tied to the client's horizon and risk, plus the advisor's recommendations (D2) if any. Phrased as things worth discussing, never instructions |
| Close | Sources, disclaimer, contact | |

*Fund, category and market reports*: no default arc. The section and
subsection menus live in `fund/QUESTIONS.md`, `category/QUESTIONS.md` and
`market/QUESTIONS.md`. Each section the advisor keeps is an act; each
subsection is a page or a panel. Pre-tick most subsections (rich by default),
offer the "go deeper" extras after each section, and let the advisor decide
where to stop.

Scene jobs to choose from: set the scene, your profile, the plan, compare the
options, each bucket / holding's role, getting your money out, what to expect
(only advisor figures), the evidence, what happens next, living with it,
close. Practical explainers (what happens after you sign, what to do when markets
fall, when you can take money out and what it costs) beat definitions; never
write "what is a mutual fund" pages.

Show the advisor a numbered outline, acts as headers, scenes pre-ticked based on
the data and the client (see pre-tick rules below). Let them tick, untick,
rename, reorder. Then suggest 2-3 extra scenes they may not have thought of.
Repeat until they say done.

**Pre-tick rules.** The default is a rich document; the advisor trims.

- Fund level: **a fund profile scene for every holding** (from fund data, or from
  the advisor's facts for PMS/AIF/MLD; skip only holdings with neither), and a
  "what it does" column in every holdings table.
- **Returns vs the market** and a **growth of ₹1 lakh chart**: on whenever at least
  one holding has a 3-year track record.
- **What you'll actually own** (look-through): on whenever at least one holding
  publishes its portfolio.
- **Overlap**: on with 2+ holdings that publish portfolios. Answer the question
  in the headline ("No, they mostly hold different companies").
- **Market snapshot**: on for proposals (index returns from the TRI series; flows
  or commentary only if the advisor gives them).
- **What to expect**: on if the advisor gave a rate (projection from that rate,
  typical yearly swing and worst recent fall from fund data, not-a-guarantee note).
- "Compare the options" with 2+ options in one document, "getting your money
  out" whenever there are lock-ins or illiquid products, practical explainers
  for first-time investors.
- Philosophy pages ("what we avoid", how we pick funds): only with wording the
  advisor or Growthvine provides. Never invent a firm's philosophy.

**Length:** short = 10-14 scenes, standard = 18-24, detailed = 25-35 (act cards
and cover count). Fund-level proposals default to standard or detailed.

## 2. Numbers only, or with comments?

Ask for every document: **numbers only** (tables and charts, no commentary) or
**with comments**. If comments, which kinds:

sum it up, what this tells us, how it compares, why this choice, how to read
this, what to watch, its role, the question to ask yourself, not a guarantee,
(any kind they name)

Set once for the document; the advisor can override per scene. A comment becomes
the scene's `note` (one short boxed line or two). Write the label and text
freshly; don't reuse stock phrases. The "not a guarantee" note always stays next
to any expected-return figure, even in numbers-only mode.

**What a comment is for.** Comments interpret the data on the page, the way a
CFA would in a written proposal: what the figure means for this client, how it
compares (with the market, the category, the other holdings), what drives it,
and what to watch. Example: "Invesco has returned 20.1% a year over three years
against the market's 9.5%, with about 20% more swing; it earns its place as the
growth engine, not the anchor."

Never use a comment to talk about data that isn't there ("these funds don't
publish...", "we haven't estimated...", "this covers only..."). What to do with
missing data is the advisor's choice (provide it, show an empty "to be added"
table, or leave it out), made in the question set. The document just shows the
result of that choice.

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
| One holding in depth | `fund` (return cards, facts, what it does, worth knowing; its role as the `note`) | `table` |
| Growth over time vs the market | `line` (growth of ₹1 lakh; the index dashed) | `bars` of period returns |
| Returns vs the market by period | `table` with the index as the last row | `bars` |
| What you'll actually own | `table` of top companies (₹ and % of your money) + `bars` of sectors | `table` |
| Overlap between funds | `table` with `heat: true` (fund x fund, %) | short `text` naming the highest pair |
| Projection from the advisor's rate | `stats` (range, value after N years, typical swing) | `table` |
| Several views of one subject (a fund, the plan, the market) | `panels` | separate scenes |
| Many items on two measures (every fund's risk and return) | `scatter` panel, the items that matter highlighted and named | `table` |
| A measure over time (rolling return, P/E, bond yield) | `line` panel | `table` of a few dates |
| What changed (bought, sold, increased, cut) | `table` with a change column | `text` |

**Content-heavy by default.** Think of a CFA preparing the proposal. Most content
scenes should be `panels` scenes: 2-4 panels on one page (a chart, a compact
table, a stacked bar, two or three insight bullets) plus an optional strip of key
numbers on top. Prefer a chart to a sentence and a sentence of insight to empty
space. Only the cover, act cards, and at most one or two `statement` scenes are
sparse, for the cinematic rhythm. A page with one line of big text and nothing
else is a mistake unless it is one of those.

Good panel pages:
- **Fund page:** strip (3y return, fund size, charge, holdings), returns vs the
  market (`bars`), company size or asset mix (`stack`), top holdings (`table`)
  or sectors (`bars`), and "our view" bullets (`text`). Its role as the `note`.
- **The plan:** bucket split (`donut`), bucket jobs (`table`), insight bullets.
- **Market snapshot:** index returns by period (`bars`), growth of ₹1 lakh in the
  index (`line`), what it means (`text`).
- **What you'll actually own:** top companies (`table`), industries (`bars`),
  company size across the plan (`stack`), what it tells us (`text`).
- **Options compared:** each option's split (`bars`), each option's liquidity
  (`stack`), the trade-off (`text`).

When several options are compared in one document, show **every option's
holdings**, not only Option 1's.

**Presentation rules learned from test runs** (keep adding to this list):
- A number alone means little: put a reference next to it (category average,
  the market, its own history). A capture chart shows the category average; a
  fund's swing shows the category's.
- Bars stay compact by themselves (the renderer caps the gap). A bars panel with
  only one or two bars and nothing to compare with is still thin: add a
  reference series, or use `stats` instead.
- A page of only `text` panels gets a `strip` of the key numbers on top.
- Never fill a gap with a "not available" or "not compared" row; drop the row.
- Explain with words, not made-up numbers: "it rose about a third more than the
  market", not "₹100 became ₹134" (an invented example fails the check).
- Long titles shrink to fit on the cover and act pages; still prefer short ones.
- Short names must stay distinct: drop the category words ("Large & Mid Cap")
  but keep what tells funds apart ("Mirae Asset" vs "Mirae Asset ... FOF").
  Don't shorten index names to bare numbers ("50", "500").
- If the text mentions a point on a chart, that point is named on the chart
  (`named: true` on a scatter point names it without highlighting it).
- A table in a quarter-page panel (`2x2`) fits about 6 rows; half-page about 11.
  If the renderer says a panel is too long, it says how many rows fit: trim to
  that and move the rest to another panel.
- Keep reference figures (category, market) on the same as-of date as the
  figures they sit next to, or say both dates.
- No page may be half empty. Short panels (a 3-row table, two bullets, a
  two-bar chart) in a `2` or `3` layout leave the bottom of the page blank.
  When the renderer reports "N% of the page is empty", fill it with real data,
  never by stretching:
  - switch to `2x2` and add a panel that deepens the same point: a chart of the
    table's figures, the reference it lacks (category, market), the path behind
    it (a line), or a stats panel of the extremes (best, worst, how many);
  - add a `strip` of key numbers, or a `note`;
  - merge it with the next small subsection;
  - turn a long `text` panel's figures into a table or chart.
  A key-facts table with blank column headers draws no header row.
  Cover, act, statement and close pages are sparse by design.

Rules: every chart must say what it shows: a panel title naming the measure and unit ("Return a year, 3 and 5 years", "₹ crore after"), and a name for every colour (series, slices, segments). Never leave a reader guessing which line is which. One main idea per scene; every number visible on the page (no
hover-only data); tables for anything the client may check line by line.
Scene field formats and limits: `design/SCENES.md`.

## 4. Language

Ask: tone (warm / formal), simplicity (from the client's experience answer;
confirm), length (short / standard / detailed). English only for now.

**Every word in a PDF or PPT follows `content/WRITING.md`** (an analyst's
specific, measured wording; no AI tells; no fragments, slogans or "not X, but
Y"; explain why, not what; no fake precision), **and every data page uses the
analyses in `content/ANALYSES.md`** (each important percentage translated into
rupees on the client's money; the same data and period for anything compared on
one page; unflattering findings shown; limits stated). Titles, loglines,
bullets and notes are all checked by `film/gates/wording.py <scenes.json>`
before rendering (see `check/CHECK.md`).

Copy rules: no `·` separators anywhere (use commas or new lines; the renderer
rejects them); plain words; explain any unavoidable term in the same sentence; no
em-dashes; no hype ("best", "guaranteed", "superb"); numbers exactly as the
advisor wrote them; Growthvine guides, it doesn't instruct ("one thing worth
watching is...", not "you must...").

## 5. The visible brief

This is step 3 of the **Required steps** in `SKILL.md`: it comes after the advisor has
picked sections and subsections (step 2), never instead of it.

The gate before writing (`shared/wealth-practice.md` §7): with the brief, show
the assumptions, any conflicts between inputs, the gaps, at most three clarifying questions
and the verified key numbers; write only after the advisor confirms.


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
