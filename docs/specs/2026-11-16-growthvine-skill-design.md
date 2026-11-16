# Growthvine skill: design spec

Status: draft v2 for review · 2026-11-16 · branch `rewrite/growthvine-skill`

## 1. Goal

One skill, named **`growthvine`**, that lets anyone at Growthvine (mostly
non-technical people) produce a client-ready proposal or report in the Growthvine
brand. It should:

- interview the advisor until it knows exactly what to build and how to show it,
- use the advisor's data exactly as given,
- support that data with Growthvine fund data from the MCP,
- explain everything in plain language a regular client understands,
- check its own numbers against the source before handing the file over,
- let advisors send feedback on the skill itself, which reaches the skill owner.

This is a clean rewrite inside `growthvine-client-docs`. The old C-split factsheet
skill is replaced, not extended.

## 2. Scope

**v1 (this spec)**

| Family | Types |
|---|---|
| Proposal | Allocation proposal: one or more options, at bucket, sleeve or fund level |
| Report | Portfolio assessment (any portfolio: a client's existing holdings, a prospect's statement, a model portfolio) · Fund report · Category report · Market report |

**Later (separate specs):** content posts, content animation, Hindi/Hinglish output.

Build order inside v1: allocation proposal → portfolio assessment → fund →
category → market. Each one ships when its evals pass.

## 3. What advisors actually send

Based on real inputs from a client proposal (Oct 2026: "Investment Options" and
"Investment Plan"). The skill must accept **Excel, PDF, pasted tables or screenshots**, and
expect any mix of these pieces:

| Piece | Example | Notes |
|---|---|---|
| Client profile | Total ₹3 Cr · horizon long-term · liquidity low · risk moderate-to-high / "growth oriented" | Goes on the cover and frames the whole story |
| Buckets | Core Growth · Stability · Diversifier · High Growth Alternatives, each with *why*, vehicles, horizon/liquidity | Growthvine's way of explaining the plan. The skill treats buckets as the main story spine |
| Options | Option 1 (12 holdings) and Option 2, Aggressive (8 holdings) | A proposal may compare options side by side |
| Master allocation | Bucket × asset class × vehicle × sleeve × amount × % × role × liquidity × lock-in/exit | May be **generic sleeves** ("Flexi Cap PMS") before funds are chosen |
| Allocation views | Cross-tabs: asset class × vehicle, bucket × vehicle (₹ lakh, % of corpus) | Good candidates for charts or heat-tables |
| Advisor comments | "Expected blended return 13.5% (option 1), 14.8% (option 2)" | Advisor's own figures. Allowed, always shown with a not-a-guarantee note, never on the cover |

**Three proposal depths**, decided from the input:
- **Bucket level:** only buckets and amounts. Pages explain each bucket's job.
- **Sleeve level:** generic strategies, no fund names. Supporting data comes from
  category-level MCP data (`get_category_stats`), clearly labelled as "typical for
  this category", not as a promise for a specific fund.
- **Fund level:** named funds. Per-fund pages, returns, holdings and overlap from
  the MCP where covered, advisor data or blanks elsewhere.

**Many holdings won't be in the MCP** (AIF, PMS, SIF, MLD / structured products).
Expect this in almost every proposal (section 6, rule 3).

### Reconciling several inputs

When the advisor sends more than one document, the skill cross-checks them
**before** the brief and asks about every mismatch. Real example from the real client
inputs:

- Option 1 holds ISIF Hybrid Long Short (a SIF, ₹10 L, Core Growth). The master
  table and allocation views show Core Growth hybrid as **₹30 L Multi Asset MF** and
  total SIF as **₹50 L**. Option 1's own lines add up to MF ₹50 L / SIF ₹60 L. So
  ₹10 L is counted as MF in one document and as SIF in the other.
- Option 1 labels the Nuvama structured product's asset class **"Debt"**. The
  allocation views put it under **"Alternatives (MLD)"**.

The skill lists these in plain words and asks which is right. It never picks one
silently.

## 4. Who uses it, and how they install it

Mostly non-technical staff on **personal Claude plans**.

- **claude.ai / desktop app:** download `growthvine.zip` from the repo's Releases
  page → Settings → Capabilities → Skills → upload. Code execution must be on.
- **Claude Code:** one copy-paste command (clone into `~/.claude/skills/growthvine`).
- **Updates:** a new zip per release. The skill states its version when asked, and
  includes it in every feedback note.

If the Growthvine fund MCP is not connected, the skill says so up front and offers
to continue with only the advisor's data.

## 4a. Sub-skills: Growthvine leads, the advisor answers

The skill runs the conversation. It doesn't wait for the advisor to dump random
files. Saying "use Growthvine" (or asking for any proposal/report) starts the
**entry sub-skill**, which asks a defined set of questions in a defined order and
then hands over to the right sub-skill.

| Sub-skill | Job | Hands over to |
|---|---|---|
| **growthvine** (entry) | Greets, asks what to make, PDF or PPT, client and RM. Routes by type | proposal / assess / fund / category / market |
| **proposal** | Its own question set: client profile → buckets → options → holdings → advisor views/comments. Asks for each piece by name, and accepts files when offered | design |
| **assess** | Question set for assessing a portfolio | design |
| **fund · category · market** | Question sets for each report (added as each ships) | design |
| **design** | Sections, how to show each one, language, the visible brief, then build | check |
| **check** | Reconcile + verify loop, delivery note | (end) |
| **feedback** | Can be triggered at any time; drafts the anonymised note and gives the form link | (back to where it was) |

**Question sets are fixed and owned by Growthvine.** Each one lists, in order:
the question, why it's needed, the format expected (pick-list, number, file), and
whether it's required. If an answer is missing or unclear, the skill asks again
(data rule 4a). Files are welcome at any point. The skill maps them onto the
question set and asks only for what's still missing.

**Input sheet, made per job (optional):** there is no fixed template, because inputs
differ every time. After the first questions, the skill can offer: "Want an Excel
sheet to fill in instead of answering one by one?" It then generates a sheet
tailored to *this* document. The columns come from this job's question set and
whatever the advisor has already shared, and anything already known is prefilled.
Advisors can always just answer in chat or send their own files.

**Packaging (decided):** one installed skill (`growthvine`) with each sub-skill as
its own folder of instructions, loaded only when needed. One zip and one upload for
advisors on personal plans, and Claude reads only the parts it's using.

## 5. The flow

Nothing is built until step 6 is confirmed. This saves tokens and avoids building a
document the advisor didn't want.

1. **Basics.** What are we making, for whom (client, RM), and **PDF or PPT?** (always
   asked, no default). Then: "Share your files (Excel, PDF, screenshots)."
2. **Read, reconcile, reflect.** Claude summarises the inputs in plain words (client
   profile, options, buckets, holdings, totals, dates) and then:
   - lists **mismatches between documents** and asks which is right (section 3),
   - asks what unclear columns or labels mean,
   - lists **holdings with no data**. For each, the advisor picks one option:
     provide the figures · show an empty "to be added" table · leave it out of data
     pages, with a one-line honest note,
   - gives **Claude's second opinion** (overlap, concentration, cost, liquidity vs the
     stated need, fit with the risk profile). This stays **in chat only**. The advisor
     decides. The document never contains advice the advisor didn't confirm.
3. **Sections.** Claude proposes sections for *this* document, grouped and
   pre-ticked based on the data and the client (section 7). The advisor
   ticks/unticks. Claude suggests extra subtopics the advisor may not have thought
   of. This repeats until the advisor says done.
3a. **Numbers only, or with comments?** Asked for every document, so every word in
   it is intentional. Options: *numbers only* (tables and charts, no commentary) or
   *with comments*. If comments, the advisor picks which kinds from the note menu
   (section 7: sum it up · why this choice · how to read this · the catch · its role
   · the question to ask yourself · not a guarantee), plus any kind they name
   themselves. It's set once for the document and can be overridden per section.
   The "not a guarantee" note is always kept next to any expected-return figure,
   even in numbers-only mode.
4. **How to show it.** For each chosen section, Claude proposes the display and the
   advisor confirms or swaps (section 8). Example: "Allocation by bucket → donut +
   table. Option 1 vs Option 2 → side-by-side bars. Liquidity → timeline diagram."
5. **Language.** Tone (warm / formal), how simple (first-time investor / some
   experience / experienced), length (short / standard / detailed). English only in v1.
6. **Visible brief.** One summary: type, client, inputs and how mismatches were
   resolved, missing-data choices, sections with their display, tone, length,
   format. The advisor says yes or edits it.
7. **Build.**
8. **Self-check loop** (section 10). Fix and rebuild until clean, at most 3 rounds,
   then report what's still unresolved.
9. **Deliver** with a short note (what's in it, data dates, anything left blank) and
   one line: "Anything about how I did this? Say *feedback* and I'll note it for the
   team."

Questions go 2 to 3 at a time, as pick-lists where possible. The brief is open-ended,
but these must be filled before building: **document type, client name, format
(PDF/PPT), and the allocation or portfolio data**.

## 6. Data rules

1. **The advisor's data is locked.** Amounts, holdings, weights, buckets, labels
   and advisor figures go in exactly as given, with no rounding to look cleaner.
   Claude may disagree in chat. It never edits the document's numbers.
2. **MCP supports, never overrides.** It fills facts the advisor didn't give, for
   funds or categories it covers. On conflict the advisor wins, and Claude mentions
   the gap in chat.
3. **Missing data → ask** (the three options in step 2). Never guess, never "N/A"
   inside a chart.
4. **Mismatched inputs → ask** (section 3). Never choose silently.
4a. **Not enough information → ask.** This applies to buckets, labels, roles, or
   anything the document would have to explain. The skill does not fill gaps from
   general knowledge.
5. **Dates everywhere.** Every data page shows its as-of date. When sources have
   different dates, the page says so.
6. **Forecasts only from the advisor.** Expected returns or target values appear only
   if the advisor gave them, with a not-a-guarantee note beside them, never on the
   cover.
7. **Client data stays in the document.** Only the fields the document needs are
   used. No PAN, account numbers or personal contact details.

MCP usage rules (tool map, plan resolution, `get_analysis_guide` before derived
maths) carry over from the old `references/data.md`, trimmed.

## 7. Sections: generated per document, not a fixed menu

The ClickToInvest proposal is a reference for *quality and structure*, not a
template. Labels and subtopics are written fresh each time so two proposals never
read as copy-paste.

What stays fixed is **the jobs a section can do**. Claude picks the jobs that fit,
then writes its own titles:

| Job | What it answers for the client | Typical evidence |
|---|---|---|
| Set the scene | Where things stand now and why it matters to this money | Index levels, recent moves |
| Your profile | What we understood about you | Horizon, liquidity, risk (advisor) |
| The plan | Where the money goes and why that split | Buckets, allocation views |
| Compare the options | How the options differ and what you trade off | Option tables, advisor's expected returns |
| Each bucket / holding's role | What each piece is *for* | Bucket "why", category, style |
| Getting your money out | When each piece can be withdrawn, and what it costs | Liquidity bands, lock-ins, exit loads |
| What to expect | A realistic range, and what a bad year looks like | Advisor's figures only, drawdown history |
| The evidence | Has this worked, and is it really diversified? | Returns vs market, look-through, overlap, cost |
| What happens next | The practical steps from yes to invested | Advisor's process |
| Living with it | How to behave once invested | Advisor + plain guidance |
| Close | Sources, dates, disclaimer, contact | All |

Report types reuse the same jobs with different weight. A portfolio assessment
leans on "the evidence" plus a "what we'd look at" job, written as observations to
discuss, never as instructions.

**Pre-ticking examples:** overlap only when 2+ holdings publish full holdings ·
bond quality only with debt/hybrid holdings · "compare the options" only with 2+
options · "getting your money out" on whenever lock-ins or illiquid products are
present · "what to expect" only if the advisor gave a range · practical topics on by
default for first-time investors.

**Plain-language notes:** each data block can carry one short boxed note. The skill
holds the *kinds* (sum it up · why this choice · how to read this · the catch ·
its role · the question to ask yourself · not a guarantee). Claude writes label
and text fresh each time. The advisor can switch notes off.

**Explainers are practical, not definitions.** No "what is a PMS / AIF / benchmark"
pages. Instead, things like:
- What happens after you sign, and when the money goes in.
- What to do (and not do) when the market falls.
- When you can take money out of each bucket, how long it takes, and what it costs.
- How tax hits when you withdraw, in rupees, not rules.
- Why we're not waiting for a "better time".
- How often we'll check in, and what would make us change something.
- What you'll see in statements and the app, and what to ignore.

Where possible these use the client's own numbers ("₹30 L in the structured product
is locked for 3.5 years").

## 8. How data is shown (step 4)

The skill keeps a small **display menu** and proposes the best fit per section. The
advisor confirms or swaps.

| Data shape | Default display | Alternatives |
|---|---|---|
| Parts of a whole (buckets, asset classes) | Donut + legend table | Stacked bar, waffle |
| Cross-tab (bucket × vehicle) | Heat-table (shaded cells) | Grouped bars |
| Option vs option | Side-by-side bars per bucket | Two-column table with differences highlighted |
| Holdings list | Table with role column | Cards per bucket |
| Returns over periods | Paired bars vs market | Table |
| Liquidity / lock-ins | Timeline (now → 1 wk → 1 yr → 3.5 yr) | Table |
| Overlap between funds | Grid with colour bands | Short list of the highest pairs |
| Single key number | Big-number card | Inline in text |
| Process / steps | Numbered step diagram | List |
| Bucket structure | Diagram: money → buckets → vehicles | Table |

Rules: one main visual per page; every chart has its numbers visible (no
hover-only data); tables for anything the client may want to check line by line.

## 9. Brand and layout

**Fresh layout** designed from `Growthvine Brandbook.pdf` and the official logo
pack. Not the old C-split mint board, not the ClickToInvest layout.

The current in-house plan pages (black header with logo, mint band, indigo table
headers, contact footer) are a useful reference for what advisors already know.
The new layout can keep that recognisable feel while improving hierarchy, charts
and explanation.

- **Colour:** Vine Indigo `#9B81F5` primary, Foundation Grey `#1D1D1B` ink, Clarity
  White `#FFFFFF` ground. Mint `#B1F0DB`, Peach `#FFBB90`, Mustard `#F1F68E` mainly
  for telling chart categories apart (one colour per bucket, the same across the
  whole document).
- **Type:** Poppins Semibold (headings, big numbers), Poppins Regular (body).
  Embedded in PDFs. For PPT, fall back to PDF-safe handling (see output.md).
- **Logo:** primary horizontal lockup by default. Colour on light grounds, reverse
  on dark. Tagline lockup on cover/close only. Clear space = width of the "G".
  Respect minimum sizes. Never the colour logo on Vine Indigo. Never stretched,
  recoloured or with effects. PNG + SVG copied into `assets/logos/`.
- **Texture:** fingerprint texture at 5 to 10% opacity, or the icon as a colour band
  at 10 to 20% white, at most once per page.
- **Footer:** the standard Growthvine contact line (taken from the advisor docs, kept
  in `assets/`, not retyped).
- **Disclaimer:** basic placeholder for now (market risk, past performance, read
  scheme documents). Swap in approved compliance text when it exists.
- **Copy:** no em-dashes, no hype verbs.

## 10. Self-check loop

A small script, `scripts/verify.py`, because arithmetic is where AI quietly goes
wrong:

1. Extract text and numbers from the finished PDF/PPTX.
2. Compare against the confirmed inputs:
   - every holding, amount, weight and bucket matches the source exactly,
   - each option's amounts add up to its total, and weights add to 100% (allowing
     for rounding),
   - bucket and cross-tab totals match the line items,
   - each % equals amount ÷ total,
   - every data page has an as-of date,
   - no forecast figure appears that the advisor didn't give.
3. Output a short list of mismatches. Claude fixes and rebuilds. Stop after 3 rounds
   and report what's left.

The same reconciliation logic powers the step 2 cross-document check. Built
test-first with fixtures based on the real client inputs (anonymised).

## 11. Feedback on the skill

Advisors need an easy way to say "this was wrong / I wanted X", and the skill owner
needs to receive it.

**How it works for the advisor:** at any time they say "feedback" (or the skill
offers it at delivery). The skill asks 2 to 3 short questions (what happened, what
they expected, how much it matters) and drafts a **feedback note** containing:
- skill version, document type, which step it was in,
- what went wrong / what they want changed, in their words,
- **no client data**: names, amounts and holdings are stripped or replaced
  ("a 12-holding proposal with 4 buckets").

The advisor sees the note, approves it, and sends it via one link.

**Where it goes (choose one):**

| Option | Advisor effort | Owner sees it as | Notes |
|---|---|---|---|
| **A. Google Form** (recommended) | Click link, paste note, submit | Rows in a Google Sheet | No login, works on any plan, easy to sort and track |
| B. Email to a feedback address | Copy note into an email | Inbox | Simple but harder to track |
| C. GitHub issue | Needs a GitHub account | Issue in the repo | Best for the owner, too technical for most advisors |

The owner reviews the sheet regularly and turns accepted items into changes and a
new release. The changelog in the README notes which feedback each release addresses.

## 12. Repo layout (after rewrite)

```
growthvine-client-docs/        (repo; skill folder name = growthvine)
  SKILL.md                     entry sub-skill: hard rules, first questions, routing
  proposal/                    question set + proposal specifics
  assess/ · fund/ · category/ · market/
  design/                      sections, display menu, language, brief, brand, output
  check/                       reconcile + verify loop, delivery note
  feedback/                    questions, note format, anonymising rules, form link
  shared/
    data.md                    data rules + MCP tool map
    inputs.md                  input pieces, proposal depths, reconciliation
  scripts/
    charts.py                  donut, bars, heat-table, timeline, overlap grid
    reconcile.py               cross-document and source-vs-output checks
    verify.py                  the self-check (uses reconcile.py)
    tests/
  assets/logos/ · fonts/ · textures/ · footer
  evals/evals.json
  README.md                    install, update, version, changelog, feedback link
```

Old C-split references, components, figures and evals are removed.

## 13. Testing

- `reconcile.py` and `verify.py`: pytest, test-first, with anonymised fixtures built
  from the real client inputs (including the two real mismatches above).
- The skill itself: evals with skill-creator. First set:
  1. The two a real client PDFs → reports both mismatches before the brief; asks PDF or
     PPT; doesn't build before confirmation.
  2. Sleeve-level master table with no fund names → no per-fund pages; category
     data labelled as typical, not promised.
  3. Advisor asks for "13.5% expected return" on the cover → keeps it off the cover,
     offers an inside page with a not-a-guarantee note.
  4. First-time investor → practical explainers pre-ticked, no definition pages.
  5. Finished PDF with one wrong amount seeded → the verify loop catches and fixes it.
  6. "Feedback: the charts were too small" → note drafted with no client names or
     amounts.

## 14. Decisions

1. **Buckets:** there is a standard framework, but the skill holds no definitions
   for it. It uses only what the advisor's inputs say about each bucket (its why,
   vehicles, horizon, liquidity). If a bucket's purpose or data is missing or
   unclear, the skill **must ask** before writing anything about it. It never fills
   in a bucket's meaning from general knowledge.
2. **Feedback channel:** Google Form (option A). The owner creates it with these
   fields: skill version · document type · step it was in · what happened · what
   you expected · how much it matters (low / medium / high). No client fields.
   Link: *pending*. Until it arrives, `feedback/` uses a `FEEDBACK_FORM_URL`
   placeholder, and the skill shows the drafted note for the advisor to send to the
   owner directly.

3. **Several options in one input:** the advisor picks each time ("compare them in
   one document" pre-selected, or "separate documents").

4. **Packaging:** one skill with sub-skill folders.
5. **Input sheet:** no fixed template. Generated per job when the advisor wants one.
6. **Comments:** asked per document (numbers only / with comments, and which kinds).
