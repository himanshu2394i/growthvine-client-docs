"""Growthvine film director: film.json + HyperFrames scenes -> finished MP4 with voice, score and effects.

    python film/director.py <film_dir> [--stage all|plan|audio|render|gates]

<film_dir> holds film.json and compositions/*.html (scenes written with film/kit). Steps:
  plan    voice lines -> Kokoro wavs; check each fits its scene; write index.html, timing.js, kit files
  audio   score on the beat grid (silence before the payoff, riser into an impact), CC0 effects on cuts and
          landings (peak one frame after the picture), music ducked under the voice, -14 LUFS, true peak -1 dBTP
  render  HyperFrames render (telemetry off), mux the mix
  gates   hyperframes check, look.py (dead frames, cuts, end hold, audio), seam review sheets

film.json:
{ "bpm": 80, "voice": "af_heart", "speed": 0.95, "client": "Name or null",
  "scenes": [ {"id": "title", "bars": 2, "vo": "text or null", "cut": "whoosh|none",
               "hits": [{"t": 2.4, "sfx": "pop"}], "payoff": false} ] }
Times in "hits" are seconds from the scene's start. Scene ids match compositions/<id>.html.
"""
import argparse
import array
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE / "kit"
# Tools live next to the repo (e.g. D:\App\tools when the repo is D:\App\growthvine-client-docs), never on C:.
TOOLS = Path(os.environ.get("GV_TOOLS", HERE.parents[1] / "tools"))
VOICE_HOME = Path(os.environ.get("GV_VOICE_HOME", TOOLS / "growthvine-voice"))
VOICE_PY = VOICE_HOME / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
ENV = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1", DO_NOT_TRACK="1", GV_VOICE_HOME=str(VOICE_HOME),
           HYPERFRAMES_CACHE_DIR=str(TOOLS / "hf-cache"), npm_config_cache=str(TOOLS / "npm-cache"),
           TMP=str(TOOLS / "tmp"), TEMP=str(TOOLS / "tmp"))
SR, FPS = 48000, 30
HF = str(TOOLS / "hyperframes" / "node_modules" / ".bin" / ("hyperframes.cmd" if os.name == "nt" else "hyperframes"))
SFX = {"whoosh": ["kit-whoosh.ogg", "whoosh-fs-169867-swoosh.ogg", "whoosh-fs-683101-quick-woosh.ogg"],
       "pop": ["kit-pop.ogg", "pop-fs527522.ogg"], "tick": ["kit-tick.ogg", "tick-fs528561.ogg"],
       "riser": ["kit-riser.ogg"], "impact": ["kit-impact.ogg"]}
SFX_GAIN = {"whoosh": 0.55, "pop": 0.6, "tick": 0.35, "riser": 0.5, "impact": 0.8}


def run(cmd, **kw):
    r = subprocess.run(cmd, env=ENV, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode:
        raise SystemExit(f"Command failed: {' '.join(map(str, cmd))}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    return r.stdout


def load(film_dir):
    spec = json.loads((film_dir / "film.json").read_text(encoding="utf-8"))
    bar = 240 / spec["bpm"]
    t = 0.0
    for s in spec["scenes"]:
        s["start"], s["dur"] = round(t, 4), round(s["bars"] * bar, 4)
        t += s["dur"]
    spec["total"], spec["bar"], spec["beat"] = round(t, 4), bar, bar / 4
    return spec


# ---------------------------------------------------------------- plan
def plan(film_dir, spec):
    work = film_dir / "build"
    work.mkdir(exist_ok=True)
    lines = {s["id"]: s["vo"] for s in spec["scenes"] if s.get("vo")}
    vo = {}
    if lines:
        if not VOICE_PY.exists():
            raise SystemExit(f"Voice not installed at {VOICE_HOME} (see film/README.md).")
        (work / "vo_lines.json").write_text(json.dumps(lines, ensure_ascii=False), encoding="utf-8")
        vo = json.loads(run([str(VOICE_PY), str(HERE / "vo_tts.py"), str(work / "vo_lines.json"), str(work / "vo"),
                             spec.get("voice", "af_heart"), str(spec.get("speed", 0.95))]).strip().splitlines()[-1])
    problems = []
    for s in spec["scenes"]:
        if s["id"] in vo:
            s["vo_start"] = round(s["start"] + spec["beat"] * s.get("vo_beat", 1), 3)
            s["vo_dur"] = vo[s["id"]]["dur"]
            # cue times in scene seconds: when the voice reaches each {marker}
            s["cues"] = {k: round(s["vo_start"] - s["start"] + t, 3) for k, t in vo[s["id"]]["cues"].items()}
            room = s["start"] + s["dur"] - 0.4 - s["vo_start"]
            if s["vo_dur"] > room:
                need = s["vo_dur"] - room
                problems.append(f"{s['id']}: voice is {s['vo_dur']:.1f}s, {need:.1f}s too long for {s['bars']} bars "
                                f"(add {int(need // spec['bar']) + 1} bar(s) or shorten the line)")
    if problems:
        raise SystemExit("Voice does not fit:\n- " + "\n- ".join(problems))
    # wording: no AI tells, no loose financial language (content/WRITING.md)
    w = subprocess.run([sys.executable, str(HERE / "gates" / "wording.py"), str(film_dir)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=dict(ENV, PYTHONIOENCODING="utf-8"))
    if w.returncode:
        raise SystemExit("Wording check found lines to rewrite (see content/WRITING.md):\n" + w.stdout)
    print("Wording: " + w.stdout.strip().splitlines()[-1])
    # kit + timing + index
    for f in ("gv.js", "gv.css", "gsap.min.js", "grain.png"):
        shutil.copy(KIT / f, film_dir / f)
    shutil.copytree(KIT / "fonts", film_dir / "fonts", dirs_exist_ok=True)
    (film_dir / "assets").mkdir(exist_ok=True)
    for logo in ("logo-dark-tagline.png", "logo-mono-white.png"):
        shutil.copy(HERE.parent / "assets" / "logos" / logo, film_dir / "assets" / logo)
    timing = {s["id"]: {"start": s["start"], "dur": s["dur"], "vo": [s.get("vo_start", 0) - s["start"], s.get("vo_dur", 0)],
                        "cue": s.get("cues", {})} for s in spec["scenes"]}
    (film_dir / "timing.js").write_text("window.GV_T = " + json.dumps(timing) + ";\n", encoding="utf-8")
    hosts = "\n".join(
        f'      <div id="{s["id"]}" data-composition-id="{s["id"]}" data-composition-src="compositions/{s["id"]}.html" '
        f'data-start="{s["start"]}" data-duration="{s["dur"]}" data-track-index="1" data-track-kind="graphics" '
        f'data-width="1920" data-height="1080"></div>' for s in spec["scenes"])
    T = spec["total"]
    (film_dir / "index.html").write_text(f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="gsap.min.js"></script>
    <script src="gv.js"></script>
    <script src="timing.js"></script>
    {'<script src="data.js"></script>' if (film_dir / "data.js").exists() else ""}
    <link rel="stylesheet" href="gv.css" />
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-width="1920" data-height="1080">
      <div class="gv-world" style="z-index:0"></div>
{hosts}
      <div id="grain" class="gv-grain clip" data-start="0" data-duration="{T}" data-track-index="2" data-layout-ignore style="z-index:50"></div>
      <div class="gv-vignette" data-layout-ignore style="z-index:51"></div>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      GV.grain(tl, '#grain', {T});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
""", encoding="utf-8")
    (work / "plan.json").write_text(json.dumps(spec, indent=1), encoding="utf-8")
    print(f"Plan: {len(spec['scenes'])} scenes, {T:.1f}s at {spec['bpm']} BPM; voice for {len(vo)} scenes, all fit.")
    return spec


# ---------------------------------------------------------------- audio
def peak_offset(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True).stdout
    a = array.array("h", raw)
    if not a:
        return 0.0
    i = max(range(len(a)), key=lambda k: abs(a[k]))
    return i / SR


def sel(var, vals):
    e = str(vals[-1])
    for i in range(len(vals) - 2, -1, -1):
        e = f"if(eq({var},{i}),{vals[i]},{e})"
    return e


def score_expr(bpm):
    """Soft keys arpeggio (8ths) over a warm pad, C - Am - F - G, two bars a chord, locked to the BPM."""
    beat, bar2 = 60 / bpm, 2 * 240 / bpm
    step = beat / 2
    tones = [[0, 4, 7, 11, 12], [0, 3, 7, 10, 12], [0, 4, 7, 11, 12], [0, 4, 7, 9, 12]]
    pattern = [0, 2, 1, 3, 2, 4, 3, 2]
    note = sel("ld(0)", [sel("ld(1)", tn) for tn in tones])
    return (f"st(0,mod(floor(t/{bar2}),4));st(1,{sel(f'mod(floor(t/{step}),8)', pattern)});"
            f"st(2,{sel('ld(0)', [0, -3, -7, -5])});"
            f"st(3,261.63*pow(2,(ld(2)+{note})/12));st(4,mod(t,{step}));st(5,mod(t,{bar2}));"
            f"st(6,65.41*pow(2,ld(2)/12));st(7,{sel('ld(0)', [4, 3, 4, 4])});st(8,mod(t,{beat * 4}));"
            f"0.06*(sin(2*PI*ld(3)*t)+sin(2*PI*ld(3)*1.003*t)+0.18*sin(4*PI*ld(3)*t))*exp(-2.6*ld(4)/{step / 0.75})*min(1,ld(4)*40)*(1-ld(4)/{step})"
            f"+0.06*(sin(2*PI*ld(6)*t)+0.7*sin(2*PI*ld(6)*pow(2,ld(7)/12)*t)+0.7*sin(2*PI*ld(6)*1.4983*t)+0.4*sin(4*PI*ld(6)*t))*pow(sin(PI*ld(5)/{bar2}),0.8)"
            f"+0.07*sin(2*PI*ld(6)*t)*exp(-3*ld(8))*min(1,ld(8)*30)")      # soft pulse on every downbeat


def audio(film_dir, spec):
    work = film_dir / "build"
    plan_spec = json.loads((work / "plan.json").read_text(encoding="utf-8"))
    T, bar = plan_spec["total"], plan_spec["bar"]
    # 1. score, with the bar before the payoff dropped to silence
    expr = score_expr(plan_spec["bpm"])
    vol = "1"
    for s in plan_spec["scenes"]:
        if s.get("payoff"):
            a, b = s["start"] - bar, s["start"]
            vol = f"if(between(t,{a:.3f},{b:.3f}),max(0,1-(t-{a:.3f})*4)*0+0.04,{vol})"
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"aevalsrc='{expr}|{expr}':s={SR}:d={T}",
         "-af", f"lowpass=f=2600,aecho=0.8:0.7:350|620|900:0.32|0.22|0.12,volume='{vol}':eval=frame,afade=t=in:d=2,"
                f"afade=t=out:st={T - 4:.2f}:d=4", str(work / "score.wav")])
    # 2. cues
    cues = []
    takes = {}
    def cue(kind, t, gain=None):
        files = SFX[kind]
        n = takes.get(kind, 0)
        takes[kind] = n + 1
        f = KIT / "sfx" / files[n % len(files)]                            # rotate takes
        at = max(0.0, t + 1 / FPS - peak_offset(f))                          # peak one frame after the picture
        cues.append((f, at, gain or SFX_GAIN[kind]))
    for s in plan_spec["scenes"]:
        if s.get("cut", "whoosh") != "none" and s["start"] > 0:
            cue(s.get("cut", "whoosh"), s["start"])
        for h in s.get("hits", []):                      # a hit lands at a fixed time or on a voice cue
            cue(h["sfx"], s["start"] + (s.get("cues", {})[h["cue"]] if "cue" in h else h["t"]))
        if s.get("payoff"):
            r = KIT / "sfx" / SFX["riser"][0]
            rdur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(r)]).strip())
            cues.append((r, max(0, s["start"] - min(rdur, bar)), SFX_GAIN["riser"]))
            cue("impact", s["start"])
    # 3. voice track
    inputs, filt, mix = ["-i", str(work / "score.wav")], [], []
    vo_parts = [(work / "vo" / f"{s['id']}.wav", s["vo_start"]) for s in plan_spec["scenes"] if s.get("vo_start") is not None]
    k = 1
    for f, at in vo_parts:
        inputs += ["-i", str(f)]
        ms = int(at * 1000)
        filt.append(f"[{k}]aresample={SR},aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{k}]")
        k += 1
    if vo_parts:
        filt.append("".join(f"[v{i}]" for i in range(1, k)) + f"amix=inputs={k - 1}:normalize=0,apad=whole_dur={T}[vo]")
        filt.append("[vo]asplit=2[vo1][vokey]")
        filt.append("[0]volume=0.9[bed0];[bed0][vokey]sidechaincompress=threshold=0.03:ratio=9:attack=25:release=450[bed]")
        mix += ["[bed]", "[vo1]"]
    else:
        filt.append("[0]volume=0.9[bed]")
        mix.append("[bed]")
    for f, at, g in cues:
        inputs += ["-i", str(f)]
        ms = int(at * 1000)
        filt.append(f"[{k}]aresample={SR},aformat=channel_layouts=stereo,volume={g},adelay={ms}|{ms}[c{k}]")
        mix.append(f"[c{k}]")
        k += 1
    filt.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0,atrim=0:{T}[pre]")
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[pre]", "-ar", str(SR), str(work / "premix.wav")])
    # 4. loudness: two-pass loudnorm to -14 LUFS, true peak -1 dBTP
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(work / "premix.wav"), "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    run(["ffmpeg", "-v", "error", "-y", "-i", str(work / "premix.wav"), "-af",
         f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
         f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,alimiter=limit=0.85:level=false", "-ar", str(SR), str(work / "mix.wav")])
    print(f"Audio: score {plan_spec['bpm']} BPM, {len(vo_parts)} voice lines, {len(cues)} effects, normalised to -14 LUFS.")


# ---------------------------------------------------------------- render
def render(film_dir, spec, name):
    work = film_dir / "build"
    # boxes: a padded card with a fixed height spills its text when a line wraps (gates/boxes.py)
    sys.path.insert(0, str(HERE / "gates"))
    import boxes
    found = boxes.check(film_dir)
    if found:
        raise SystemExit("Box check: these cards would spill their text; give them min-height:\n- " + "\n- ".join(found))
    silent = work / "picture.mp4"
    run([HF, "render", str(film_dir), "-o", str(silent), "--crf", "21", "--quiet"], cwd=film_dir)
    out = film_dir / f"{name}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(work / "mix.wav"), "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)])
    print(f"Render: {out.name} ({out.stat().st_size / 1e6:.1f} MB).")
    return out


# ---------------------------------------------------------------- gates
def gates(film_dir, spec, name):
    work = film_dir / "build"
    out = film_dir / f"{name}.mp4"
    report = []
    chk = subprocess.run([HF, "check", str(film_dir), "--json"], env=ENV, capture_output=True, text=True,
                         encoding="utf-8", errors="replace", cwd=film_dir).stdout
    try:
        j = json.loads(chk[chk.index("{"):])
        errs = [f for f in json.dumps(j).split('"severity": "error"')][1:]
        report.append(f"hyperframes check: {len(errs)} error(s)")
    except ValueError:
        report.append("hyperframes check: could not parse output")
    (work / "check.json").write_text(chk, encoding="utf-8")
    look = subprocess.run([sys.executable, str(HERE / "gates" / "look.py"), str(out), "--out", str(work / "look"),
                           "--expect", str(spec["total"]), "--expect-audio"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    report.append("look.py:\n" + "\n".join(l for l in look.stdout.splitlines() if any(g in l for g in ("G0", "G1", "G2", "G3", "G4", "PASS", "FAIL", "WARN")))[:3000])
    subprocess.run([HF, "snapshot", str(film_dir), "--review", "-o", str(work / "review")], env=ENV,
                   capture_output=True, cwd=film_dir)
    lufs = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(out), "-af", "ebur128=peak=true", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    summary = lufs[lufs.rfind("Summary:"):] if "Summary:" in lufs else ""
    report.append("loudness:" + " ".join(l.strip() for l in summary.splitlines() if l.strip().startswith(("I:", "Peak:"))))
    (work / "gates.txt").write_text("\n\n".join(report), encoding="utf-8")
    print("\n\n".join(report))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("film_dir")
    ap.add_argument("--stage", default="all", choices=["all", "plan", "audio", "render", "gates"])
    ap.add_argument("--name", default=None)
    a = ap.parse_args()
    d = Path(a.film_dir).absolute()
    spec = load(d)
    name = a.name or spec.get("name", d.name)
    if a.stage in ("all", "plan"):
        plan(d, spec)
    if a.stage in ("all", "audio"):
        audio(d, spec)
    if a.stage in ("all", "render"):
        render(d, spec, name)
    if a.stage in ("all", "gates"):
        gates(d, spec, name)


if __name__ == "__main__":
    main()
