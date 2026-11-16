"""Voiceover with Kokoro (local, free). Run with the voice venv's python:
    <venv>/Scripts/python vo_tts.py <lines.json> <out_dir> <voice> <speed>
lines.json: {"scene_id": "text", ...}. Writes <out_dir>/<scene_id>.wav, prints {"id": seconds} as JSON."""
import json
import os
import sys

import soundfile as sf
from kokoro_onnx import Kokoro

HOME = os.environ["GV_VOICE_HOME"]   # set by director.py (the tools folder next to the repo)


def main(lines_path, out_dir, voice, speed):
    k = Kokoro(os.path.join(HOME, "kokoro-v1.0.onnx"), os.path.join(HOME, "voices-v1.0.bin"))
    lang = "en-us" if voice.startswith("a") else "en-gb"
    lines = json.load(open(lines_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    lengths = {}
    for sid, text in lines.items():
        audio, sr = k.create(text, voice=voice, speed=float(speed), lang=lang)
        sf.write(os.path.join(out_dir, f"{sid}.wav"), audio, sr)
        lengths[sid] = round(len(audio) / sr, 3)
    print(json.dumps(lengths))


if __name__ == "__main__":
    main(*sys.argv[1:5])
