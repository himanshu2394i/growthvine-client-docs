# Content films

Turn any document this skill makes into a film: a proposal, a portfolio
assessment, a fund, category or market report. **The deliverable is always an MP4 video with music** (16:9, 1920x1080, 30 fps,
length set by the content (often 2 to 4 minutes; longer when every scene earns its place), an original score (soft keys arpeggio over a warm pad, C, Am, F, G) with low hits on key numbers and
whooshes on scene changes). A contact sheet of key frames is only the preview
step before the full render, never the deliverable. Each document type has its own notes, added as we test
them: `content/proposal.md`, `content/assess.md`, `content/fund.md`, `content/category.md`.

## What these films are

- **Question-led exploration.** The film moves from one question to the next,
  each one a question the viewer would have on seeing the data before it. The
  answer is shown with data and leads into the next question. A doc's sections
  become questions in the client's voice ("Why not put it all in one good
  fund?"), not headings ("Allocation").
- **Premium, exclusive, personal.** It feels like a private briefing for one
  person, not marketing:
  - **Personal:** their name, their question in their words, their numbers,
    their advisor's own note at the end.
  - **Exclusive:** opens with "A private briefing for <name>, prepared <date>".
    Sent as a private link, never posted.
  - **Premium:** restraint. One idea per frame, generous space, slow precise
    motion, fine type, an original ambient score. No stock footage, clip art or
    anything loud. (Unlike a report page, space on screen reads as premium.)
- **Private by default.** A film with a client's name or money (proposal,
  assessment) is for that client only. Fund, category and market films can
  also have a general brand version.

## Detailed, useful, in our voice

A film exists because it explains something useful, not to look nice. Each
question gets a full answer with real supporting data, so the client's doubts
are actually cleared:
- Answer with two or three linked pieces of data, not one number: e.g. "Are
  these funds any good?" = growth of ₹1 lakh against the market **plus** 3- and
  5-year returns **plus** what has no comparable record.
- Add the questions a client would ask next (what's inside each part, how bad a
  fall can get and what cushions it, which industries they'd own).
- Every question scene ends with a **finding**: one bold line with a mint tick
  stating what the data shows and why the plan is built that way, in an
  analyst's words ("Each bucket has a defined role, time horizon and
  liquidity"), never a slogan. Reasons come from the document and the data.
- **Every answer uses the analyses in `content/ANALYSES.md`**: each important
  percentage translated into rupees on the client's money, same data and period
  for anything compared, unflattering findings shown, limits stated. When the
  voice names an item, that item lights at that moment (voice cues).
- **Every word follows `content/WRITING.md`**: specific, measured, the right
  terms, no AI tells. A client should believe a CFA wrote each line by hand.
- Pace for reading: a dense scene needs 12 to 17 seconds.

## The advisor's menu (same approach as the reports)

Suggest more; the advisor picks. Offer:
1. The question chain: an opening question and the follow-ups, built from the
   document's sections, natural reactions to each chart, and anything the
   advisor says this client actually asked. They tick, reorder, reword, and say
   where to go deeper (more follow-up questions).
2. Length (set by the content: do not cut a useful scene or squeeze a line to hit a time) and format: 16:9 film, 9:16 short
   (one or two questions), or a still card (one number).
3. The advisor's closing note, in their own words. Never write it for them;
   leave a marked placeholder.
4. **Costs: always ask, every film.** "Should the film mention costs (fees,
   expense ratio / annual charge, commission, regular vs direct)?" The default
   is **no**: leave out every cost figure, cost scene, cost card and cost-based
   score (e.g. a "Cost" part of a ranking), even if the document has them.
   Include them only when the advisor says yes for this film.

## Storyboard

For each scene: the question (if any), what the viewer sees and how it moves,
the answer line on screen, the data and its source, and the timing. Render a
still of each scene's final state at 1920x1080, look at every one (overlaps,
long source lines hitting the logo), fix, then render the film.

How it's made: HyperFrames scenes written with the Growthvine kit, rendered and
scored by `film/director.py` (setup and commands: `film/README.md`).

Motion rules (from HyperFrames' motion reference and motionmaxxing's measured
films):
- **No slide layouts:** no small label above a left headline on every scene, no
  corner logo (the logo appears on the title and end card only), no page counters.
- **Cut on motion:** a scene leaves accelerating along the film's direction (left
  by default) and the next arrives already moving the same way. Use 3 to 5 kinds
  of transition, each with a cause: a carried object (the ₹3 Cr number becomes
  the bar the next scene splits), a push forward, an upward exit for the
  conclusion. Never a fade through black between scenes.
- **No still stretches over 3 seconds:** once a title lands it stays still, and
  the motion moves on: a highlight walks through the rows the voice is
  discussing, a line draws, a counter runs. Mark a deliberate hold (end card,
  advisor's note) with `data-hold`.
- **Ease by role:** arrivals land on a long tail (`softLand`, `snapSettle`),
  exits accelerate and take 40-50% of the entry time (`crashOut`), camera moves
  ease both ways. Vary text entrances (blur-in, grey-to-ink, settle from
  oversize); never fade-and-slide-up for every line.
- **Elements are hidden until they enter:** entrances apply their start state
  at once (`GV.textIn`, `GV.enter`); later moves wait for their time.
- **Readable:** text at least 28px; a line holds 0.5 s plus 0.3 s a word; the
  first frame shows the title (it is the thumbnail).
- **Sound:** the voice is the clock; the score is on a beat grid with scenes in
  whole bars; effects peak one frame after their picture; the music drops out
  in the bar before the payoff, then a riser and an impact; -14 LUFS, peaks
  under -1 dB.

Screen grammar used so far:
- Private title card (letterboxed) → cold open with the main amount counting
  up and faint questions drifting around it → question scenes → the advisor's
  note → end card with disclosures.
- Each question scene: a small indigo label ("THE QUESTION ON YOUR MIND"), the
  question, then the answer as a chart or one big number, then one plain line
  of meaning.
- A source line at the bottom of every data screen.
- Brand: Poppins; ink background; indigo, mint and peach for data; mustard
  sparingly. No em dashes, no concentric circles.

## Rules

Every report rule still applies: the advisor's data is locked, every figure
comes from the inputs or fund data, computed in code, expected returns only
from the advisor with "not a guarantee" on screen, no forecasts. Honest answers:
if the data can't answer a question ("Will it fall again?"), say what it can
show (how often falls happen), not when.

End card: Growthvine Capital, AMFI-registered Mutual Fund Distributor,
ARN-176753; market-risk and past-performance lines; "not a recommendation".
Someone with compliance responsibility signs off before anything is sent.

## Presentation rules learned from test runs

- Labels under a split bar go in even columns, not under each segment: a narrow
  segment (₹30 L of ₹3 Cr) otherwise squeezes its label into the next one.
- A source line stays one short line; long caveats go in the supporting line
  above it, or they run into the corner logo.
- Table columns on screen: leave room for the longest name before the first
  number column.
- In a network of funds (overlap), put a crossing line's label off-centre (about
  a third along) with a dark backing, or the two middle labels collide. Circles
  must fit the longest name.
