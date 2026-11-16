# Content films

Turn any document this skill makes into a film: a proposal, a portfolio
assessment, a fund, category or market report. **The deliverable is always an MP4 video with music** (16:9, 1920x1080, 30 fps,
2 to 3 minutes, an original ambient score with low hits on key numbers and
whooshes on scene changes). A contact sheet of key frames is only the preview
step before the full render, never the deliverable. Each document type has its own notes, added as we test
them: `content/proposal.md` so far.

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
- Every question scene ends with **Growthvine's voice**: one bold line with a
  mint tick saying what we do and why ("Every rupee gets a job before it gets a
  fund"; "We don't try to time the start"), plus one supporting line. The
  reasons must come from the document and the data, never invented claims.
- Pace for reading: a dense scene needs 12 to 17 seconds.

## The advisor's menu (same approach as the reports)

Suggest more; the advisor picks. Offer:
1. The question chain: an opening question and the follow-ups, built from the
   document's sections, natural reactions to each chart, and anything the
   advisor says this client actually asked. They tick, reorder, reword, and say
   where to go deeper (more follow-up questions).
2. Length (about 2 to 4 minutes for a film) and format: 16:9 film, 9:16 short
   (one or two questions), or a still card (one number).
3. The advisor's closing note, in their own words. Never write it for them;
   leave a marked placeholder.

## Storyboard

For each scene: the question (if any), what the viewer sees and how it moves,
the answer line on screen, the data and its source, and the timing. Render a
still of each scene's final state at 1920x1080, look at every one (overlaps,
long source lines hitting the logo), fix, then render the film.

How it's made: `scripts/film.py` (Pillow draws each frame from the data,
ffmpeg encodes one clip per scene in parallel, joins them and lays the
ffmpeg-made score under it). No other installs needed.

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
