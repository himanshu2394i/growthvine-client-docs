# Writing: sound like a CFA wrote it by hand

Every word in a film (on screen and spoken) and in a document must read as if a
careful investment professional wrote it for this one client: specific,
measured, plain, and exact about what the numbers are. If a line could appear
in any company's marketing, or in any AI video, rewrite it.

## The test for every line

1. **Is it specific?** It names the figure, the period, the basis and the
   source: "20.1% a year over three years to 30 September 2026, regular plan",
   not "strong returns".
2. **Would an analyst say it out loud to a client?** No slogans, no drama, no
   rhetorical set-ups. Calm sentences with a subject and a verb.
3. **Does it claim only what the data shows?** Past returns are described,
   never projected. Limits are stated plainly ("The SIFs and the AIF do not
   publish a comparable record, so they are not shown").
4. **Is it the right term?** Annualised return, drawdown, standard deviation,
   Sharpe ratio, look-through, overlap, lock-in, exit load. Explain a term once,
   in a few words, the first time it appears; do not avoid it.

## Banned (AI tells), with what to write instead

| Tell | Example from our own drafts | Write instead |
|---|---|---|
| Sentence fragments for drama | "Three crore rupees. Years of work, in one number." | "This note covers how your ₹3 crore is proposed to be invested." |
| Slogans and taglines | "Every rupee gets a job before it gets a fund." | "Each bucket is defined by its purpose and by how quickly its money can be redeemed." |
| Staccato lists of fragments | "Stability, seventy lakh. The Diversifier, thirty lakh." | One sentence: "one crore each in Core Growth and High Growth Alternatives, seventy lakh in Stability and thirty lakh in the Diversifier." |
| Vague verdicts | "The funds overlap little." | "The highest overlap between any two of the four funds is 28%, between HDFC Value and Nippon Multi Asset." |
| Tricolons and lists of three for rhythm | "to grow, to cushion the falls, to move differently, and to aim higher" | Name each bucket with what it holds: "Core Growth: diversified equity and hybrid funds." |
| "Not X. Y." reveals | "Not into one good fund." | State the fact: "The proposal spreads the money across four buckets." |
| Rhetorical questions answered by the narrator | "So where should it all go?" (spoken) | Questions belong on screen, in the client's plain words. The voice answers with facts. |
| Hype and feeling words | "built for growth, with a cushion", "steady tilting", "pays up for it", "premium" | Plain description with the number: "75% in equity; 18% in bonds." |
| Personification | "the fund buys growth", "markets have gone nowhere" | "The fund's holdings trade at 44 times earnings"; "The Nifty 500 TRI returned -2.0% over the year." |
| Vague comparatives | "fell a little more", "much of the work" | "Down-capture of 108% against the category's 99%." |
| Reassurance nobody said | "Nothing urgent.", "Yes, so far" | Leave it out. Only the advisor's own words go in. |
| Colon reveals and punchlines | "Size isn't rank: the largest fund is 7th." | "The largest fund by assets, Mirae Asset, ranks 7th of 41." |
| Fake intimacy | "Your money has four jobs", "Let's go through it together" | "The proposal divides the ₹3 crore into four buckets." |
| Filler openers and closers | "Here's the thing", "In short", "At the end of the day" | Start with the fact. |
| Rounded words for numbers | "about a third more", "over half" | The number: "134% up-capture"; "53.6% in three industries". Approximate only when the source is approximate. |
| Em dashes, "·", "&" in sentences | | Commas, full stops, "and". |

## Voiceover (spoken)

- The advisor's voice: first person plural for Growthvine ("we propose", "we
  have looked through"), second person for the client's money, never "your
  journey".
- One or two plain sentences per scene, about 15 to 22 words, each carrying a
  number or a fact from the screen. Do not read the screen word for word; say
  what the chart means.
- Write numbers for speech: "three crore", "twenty point one percent a year",
  "one lakh became one point eight to two lakh".
- No questions in the voice. The screen asks; the voice answers.

## On-screen text

- The question at the top of a scene: how a client would actually ask it, in
  plain words ("What can I withdraw, and when?"), not a hook.
- Labels state the measure, the unit and the period: "Annualised return, 3 years
  to 30 Sep 2026".
- The closing line of a scene is a finding, not a slogan: "All three funds with
  a five-year record returned more than the Nifty 500 TRI over three and five
  years."
- Sources: plan, basis, date, data provider.

## An analyst's discipline (from financial research practice)

- **Explain why, not what.** A comment gives the reason behind a number, from
  the underlying data; it does not restate the number. "The multi-asset fund fell
  10.9%, against 18.5% and 19.0% for the equity funds" states it; the reason is
  that it holds bonds and gold. If the data does not show the reason, say
  nothing, or write "reason not established". Never invent one.
- **Check every causal claim against the inputs.** "X is why Y" must be true in
  the data. (A test film said the multi-asset fund was why Stability held
  ₹70 L; the fund sits in Core Growth. The checker cannot see this; you must.)
- **No fake precision, no orphan numbers.** Every figure has a basis (plan,
  period, date, source). A figure you cannot trace is left out, not rounded into
  "about". "Approximately X" is never a way round not knowing X.
- **The advisor's reasoning only in their words.** Where it is missing, leave a
  marked placeholder.
- **The benchmark is the one the client's profile names**, never the one that
  flatters.
- **Lead with the most important fact.** Then the supporting figures.

## Rhythm and grammar (from the anti-slop skills)

- A subject doing something in every sentence; name who did it. Prefer the
  active voice; a passive is fine when the actor is unknown or irrelevant
  ("₹1.30 Cr is locked for three years").
- Mix sentence lengths; do not stack short punchy sentences; do not end every
  scene on a one-liner.
- Two items beat three. A list of three adjectives or verbs for rhythm is a
  tell; a full factual list (the five product types) is fine.
- No adverbs used for emphasis (really, just, simply, actually, truly, deeply,
  significantly). No sweeping words (every, always, never) unless literally true.
- No sentence that sounds like a pull-quote. If it would look good on a poster,
  rewrite it as a finding.

## Before rendering

1. `film/director.py` runs `film/gates/wording.py` on every spoken and on-screen
   line and stops on any HARD finding. REVIEW findings stay only with a reason.
2. Then read every line yourself against this page: the checker catches
   patterns, not wrong reasoning or false causes.
3. Check every figure against the inputs.

Sources of these rules: stop-slop (Hardik Pandya), FeedHive's ai-slop-detector,
slop-guard (Eric Tramel) and plain-writing-skill (all MIT); ideas only from
no_ai_slop_writing_rules, anti-ai-slop-writing and quiron; Anthropic's
financial-services and claude-for-financial-advisors skills (Apache-2.0); and the
equity-research skills by GeniusTrader-Harry and rollingSirius (MIT).
