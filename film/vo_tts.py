"""Voiceover with Kokoro (local, free), with cue times. Run with the voice venv's python:
    <venv>/Scripts/python vo_tts.py <lines.json> <out_dir> <voice> <speed>

lines.json: {"scene_id": "text with {cue} markers", ...}. A marker names the moment the next word is spoken:
"one crore each in {core}Core Growth and {hga}High Growth Alternatives".
Writes <out_dir>/<scene_id>.wav and prints {"id": {"dur": seconds, "cues": {"core": seconds, ...}}} as JSON.

Kokoro reports no word timings, so each cue is measured: the text up to the marker is spoken on its own and its
length is the cue's time (accurate to about a tenth of a second, since the words before it are the same)."""
import json
import os
import re
import sys

import soundfile as sf
from kokoro_onnx import Kokoro

HOME = os.environ["GV_VOICE_HOME"]   # set by director.py (the tools folder next to the repo)
MARK = re.compile(r"\{([a-z0-9_]+)\}")


def main(lines_path, out_dir, voice, speed):
    k = Kokoro(os.path.join(HOME, "kokoro-v1.0.onnx"), os.path.join(HOME, "voices-v1.0.bin"))
    lang = "en-us" if voice.startswith("a") else "en-gb"
    say = lambda t: k.create(t, voice=voice, speed=float(speed), lang=lang)
    lines = json.load(open(lines_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    out = {}
    for sid, raw in lines.items():
        text = MARK.sub("", raw)
        audio, sr = say(text)
        sf.write(os.path.join(out_dir, f"{sid}.wav"), audio, sr)
        dur = len(audio) / sr
        cues, removed = {}, 0
        for m in MARK.finditer(raw):
            pos = m.start() - removed
            removed += len(m.group(0))
            prefix = text[:pos].strip()
            t = 0.0
            if prefix:
                a, s = say(prefix)
                t = len(a) / s
            cues[m.group(1)] = round(min(t, dur), 3)
        out[sid] = {"dur": round(dur, 3), "cues": cues}
    print(json.dumps(out))


if __name__ == "__main__":
    main(*sys.argv[1:5])
