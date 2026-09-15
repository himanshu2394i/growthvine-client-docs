# Briefing

Ask once, wait, then build. Skip any slot the user already answered in the same
message. Do not start layout or code until **source**, **file type**, and **tone**
are known.

## The six slots

### 1. Job

What is the document *for*?

- Fund fact sheet / scheme one-pager
- Portfolio review (several funds, one client)
- Sales proposal or house overview
- Internal research pack
- Something they name that is not on this list (allowed)

### 2. File

PDF, PPTX, both, or HTML meant to print. Default is PDF if they only say "document"
and the audience is a client who will forward a file.

### 3. Source

Always ask, even if they pasted a blob:

- **This dump is the source.** Use only what they pasted or attached.
- **Pull live from the Growthvine connector.** They named a fund or category and
  want current figures.
- **Dump for the story, connector for holes.** Dump wins on conflict.

If they dumped data, confirm with one line: "I'll treat this paste as canonical
unless you want a live refresh." Then proceed on the other slots.

If they named a fund and dumped nothing, say you will use the Growthvine connector
and name the scheme you resolved (direct vs regular, growth vs IDCW) before pulling.

Full connector rules: **`data.md`**.

### 4. Tone

Pick one. Map it to copy and density, not to a new brand.

| Tone | Voice | Design |
|---|---|---|
| **Advisor-to-client** (default) | Calm, factual, no product hype. Explain what a number means in one short line. | Full C split: mint board + white brief. |
| **Sales proposal** | Still factual. One reason to talk to Growthvine. | Same C split. One CTA only. |
| **Internal research** | Denser tables, fewer sentences. | White brief can run tighter. Cover can skip the outdoor-board stairs if they want a pack, not a poster. |
| **SEBI-cautious** | Facts only. No "you should invest," no implied advice. | Same C split. Drop the app CTA unless they insist. |

Do not mix registers on one document (mono-tech captions next to manifesto prose).

### 5. Sections

Show this menu. Ask which to keep, skip, and **what to add that is not here**.

**Cover (mint board)**
- Scheme name, category, as-of
- Headline stairs: typically 3Y, 5Y, AUM (or the three numbers they care about)
- Exit load line
- Optional CTA

**White brief**
- Rank within category
- Returns vs benchmark (periods)
- Rolling returns (chart + summary)
- Calendar-year returns
- Quartile profile
- Asset allocation
- Market-cap split
- Credit quality
- Instrument breakdown
- Concentration / top holdings
- Risk ratios
- Portfolio statistics (yield, duration)
- Max drawdown and recovery
- Riskometer
- Fund info (NAV, TER, AUM, dates)
- Fund managers
- About / objective
- AMC
- FAQs
- Close / contact

They may ask for chapters this list has never seen (SIP illustration, tax note,
peer set, manager tenure timeline, "why this category"). That is expected. Invent
the *chapter* with the existing layout families. Do not invent a sixth color or a
new typeface. Recipe: **`new-sections.md`**.

Skip any chapter the source cannot support. Do not pad with empty frames.

### 6. Length

- Let the data decide (default): one chapter per page/slide, skip empties.
- Fixed count: they name N pages or slides; you cut or combine chapters, still
  one layout family per page.

## How to ask (shape)

One message, numbered, short. Example when they dumped a sheet and said "make a PDF":

> Treating this paste as the data source. Before I build:
> 1. PDF only, or PPTX as well?
> 2. Tone: advisor-to-client, sales, internal, or SEBI-cautious?
> 3. Sections: I'll default to cover, performance, composition, risk, fund info.
>    Keep that, cut some, or add chapters (name them)?
> 4. One fund or a pack?

Do not dump a 40-line questionnaire. Do not ask them to pick hex colors. Brand is
not a briefing slot.

## After they answer

Repeat the brief in 4–6 lines (job, file, source, tone, section list, length), then
build. If they change a slot mid-way, update that slot only. Do not silently restyle
the mint board.
