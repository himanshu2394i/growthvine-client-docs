"""Wording check: flags AI tells and loose financial language in film or document text.

    python film/gates/wording.py <film_dir>          # voice lines (film.json) + on-screen text (compositions/*.html)
    python film/gates/wording.py --text "a line"     # one line

Our own rules, written for Growthvine; the categories draw on stop-slop (Hardik Pandya, MIT), FeedHive's
ai-slop-detector (MIT), slop-guard (Eric Tramel, MIT), plain-writing-skill (MIT), the anti-slop repos read for
ideas only, and the source discipline in Anthropic's financial-services skills and equity-research skills
(no fabricated figures, no fake precision, explain why not what). See content/WRITING.md.

HARD findings must be fixed before rendering. REVIEW findings need a human look: keep them only with a reason.
Exit code 1 when any HARD finding remains."""
import html
import json
import re
import sys
from pathlib import Path

RULES = [
    # ---- vocabulary that shows up in generated text far more than in an analyst's note
    ("HARD", "ai-vocabulary", r"\b(delve|tapestry|landscape|realm|testament to|beacon|pivotal|crucial|vital|paramount|showcase|underscore|"
     r"foster|cultivate|leverage|utili[sz]e|harness|elevate|empower|supercharge|unlock|amplify|seamless|robust|cutting-edge|state-of-the-art|"
     r"best-in-class|meticulous|intricate|multifaceted|vibrant|journey|embark|game.?changer|holistic|synergy|curated|navigate|"
     r"ever-evolving|in today's|deep dive|dive into|unpack)\b", "Use the plain word, or name the fact."),
    ("HARD", "empty-adverb", r"\b(really|just|simply|actually|truly|deeply|genuinely|honestly|literally|quietly|incredibly|remarkably|"
     r"extremely|very|fundamentally|inherently|inevitably|interestingly|importantly|crucially|essentially)\b", "Delete it; the sentence is stronger without."),
    ("HARD", "stock-phrase", r"(here's (the thing|what|why|how)|it'?s worth noting|at its core|when it comes to|at the end of the day|"
     r"the truth is|the reality is|make no mistake|let'?s (dive|look|explore|break)|imagine (a|if)|whether you'?re|look no further|"
     r"in a world where|plays? a (key |vital |crucial )?role|stands as|peace of mind|financial freedom|sleep (well|easy)|rest easy|"
     r"secure your future|wealth creation journey|time in the market)", "Cut it and state the point."),
    # ---- structures
    ("HARD", "not-x-but-y", r"(^|[.!?]\s)Not (into|a|an|the|just|because|only)\b|\b(not|isn't|aren't|wasn't)\b[^.!?]{1,60}?[,;.]\s*(but|it's|it is|they're|rather)\b|"
     r"\bnot just\b[^.]{1,60}\bbut\b|\bthe (question|answer|point|problem) (isn't|is not)\b", "State the second half directly."),
    ("HARD", "colon-reveal", r"(^|[.!?]\s)[A-Z][^.:!?]{2,38}:\s+(the|a|an|it|that|this)\b[^.]{0,60}\.", "Write it as one plain sentence."),
    ("HARD", "em-dash", r"[—–·]", "Use a comma or a full stop."),
    ("HARD", "exclamation", r"!", "Remove it."),
    ("HARD", "promise", r"\b(guarantee[sd]?|assured|risk-free|riskless|safe bet|can'?t lose|will (grow|return|earn|double|deliver|beat)|sure to)\b",
     "No promises. If it is an estimate, say whose and add 'not a guarantee'."),
    ("HARD", "false-agency", r"\b(the )?markets? (rewards?|punish(es)?|gave|went nowhere|ha(s|ve) gone nowhere|decided|wants?|loves?|hates?)\b|"
     r"\bthe data (tells|says|shows us)\b|\b(the fund|it) (buys|loves|wants|believes) (growth|value|quality)\b|\bpays up\b",
     "Name what was measured: 'The Nifty 500 TRI returned -2.0% over the year'."),
    ("HARD", "fake-intimacy", r"\b(your money has|let'?s go through|we'?ll do it together|together, we|your (financial )?journey|"
     r"every rupee|you deserve|we've got you)\b", "Plain advisory language."),
    ("HARD", "slogan", r"\b(every \w+ gets a|built for \w+, with|nothing urgent|size isn't rank|one fund does one job)\b|\bso far\.",
     "Replace the slogan with the finding."),
    # ---- needs a human look
    ("REVIEW", "vague-quantity", r"\b(about|around|nearly|roughly|almost|over half|a third|a quarter|most of|much of|a lot|significant(ly)?|"
     r"substantial(ly)?|considerabl[ey]|many|several)\b", "Use the figure; approximate only when the source is approximate."),
    ("REVIEW", "hype-adjective", r"\b(strong|solid|impressive|healthy|stellar|outstanding|superior|excellent|exceptional|attractive|premium|"
     r"best|great|huge|massive|tiny)\b", "Replace with the number that shows it."),
    ("REVIEW", "sweeping", r"\b(every|always|never|everyone|nobody|no one|all)\b", "Check it is literally true; else be specific."),
    ("REVIEW", "rhetorical-question", None, "Spoken questions belong on screen; the voice answers with facts."),
    ("REVIEW", "rule-of-three", r"\b(\w+), (\w+),? and (\w+)\b(?! (crore|lakh|percent|years?))", "Two items, or the full list with figures, not a rhythm of three."),
    ("REVIEW", "wh-opener", r"(^|[.!?]\s)(What|Why|How|Where|When|Which) [a-z]+ (is|are|makes|matters)\b", "Lead with the subject."),
]
CASE_SENSITIVE = {"colon-reveal", "not-x-but-y"}
NEGATED = re.compile(r"(?:^|\W)(?:not|no|never)\W[^.]{0,12}$", re.I)       # "not a guarantee" is the disclaimer, not a promise

VERBS = set("""is are was were be been being has have had do does did can could will would should may might must returned return
returns fell fall falls rose rise rises grew grow grows holds hold held takes take took adds add added gives give gave sits sit shows show
showed make makes made invest invested redeem redeemed explains explain answers answer covers cover share shares beat beats compounds
compounded locked lowers lower moves move expect expects account accounts overlap overlaps raise raises divided split propose buys buy
pays pay""".split())


def visible_text(path):
    raw = Path(path).read_text(encoding="utf-8")
    s = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S)
    s = re.sub(r'<div[^>]*class="src"[^>]*>.*?</div>', " ", s, flags=re.S)      # source lines are citations, not prose
    s = re.sub(r'<div[^>]*data-wording-ignore[^>]*>.*?</div>', " ", s, flags=re.S)  # set legal wording (disclosures)
    s = re.sub(r"<[^>]+>", "\n", s)
    lines = [html.unescape(l).strip() for l in s.splitlines()]
    out = [l for l in lines if l and not l.startswith(("{", "}", "(")) and re.search("[A-Za-z]", l)]
    for m in re.finditer(r"'([A-Z][^'<>{}$]{12,})'|\"([A-Z][^\"<>{}$]{12,})\"", raw):   # prose built inside scripts
        t = m.group(1) or m.group(2)
        if " " in t and "class=" not in t and not t.startswith(("Invesco", "Nippon", "HDFC", "Nifty")):
            out.append(t)
    return out


def fragments(text):
    """Sentences (ending in a full stop) of up to eight words with no verb: drama, not information."""
    out = []
    for sent in re.findall(r"(?:[^.!?]|(?<=\d)\.(?=\d))+\.", text):          # a decimal point is not a full stop
        ws = re.findall(r"[A-Za-z']+", sent)
        if 0 < len(ws) <= 8 and not any(w.lower() in VERBS or w.lower().endswith("ed") for w in ws):
            out.append(sent.strip())
    return out


def check(text, voice=False):
    hits = [("HARD", "fragment-drama", f, "Write a full sentence with a subject and a verb.") for f in fragments(text)]
    question = text.rstrip().endswith("?")
    for level, rid, rx, fix in RULES:
        if question and rid in ("wh-opener", "vague-quantity"):
            continue
        if rid == "rhetorical-question":
            if voice and "?" in text:
                hits.append((level, rid, text[:text.index("?") + 1][-60:], fix))
            continue
        for m in re.finditer(rx, text, flags=0 if rid in CASE_SENSITIVE else re.I):
            if rid == "promise" and NEGATED.search(text[:m.start()]):
                continue
            hits.append((level, rid, m.group(0).strip(), fix))
    return hits


def collect(film_dir):
    d = Path(film_dir)
    items = []
    spec = json.loads((d / "film.json").read_text(encoding="utf-8")) if (d / "film.json").exists() else {"scenes": []}
    for s in spec["scenes"]:
        if s.get("vo"):
            items.append((f"voice {s['id']}", s["vo"], True))
    for f in sorted((d / "compositions").glob("*.html")):
        for line in visible_text(f):
            items.append((f"screen {f.stem}", line, False))
    return items


def main(argv):
    items = [("text", " ".join(argv[1:]), True)] if argv[:1] == ["--text"] else collect(argv[0])
    hard = review = 0
    for where, text, voice in items:
        for level, rid, frag, fix in check(text, voice):
            hard += level == "HARD"
            review += level == "REVIEW"
            print(f"{level:6} {rid:20} [{where}] \"{frag}\"  ->  {fix}")
    print(f"\n{len(items)} lines checked: {hard} hard, {review} to review.")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
