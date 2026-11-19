# Growthvine films

Every content film is an MP4 with a voice, an original score and sound effects,
built from HyperFrames scenes in the Growthvine look. Rules for what goes in a
film: `../content/CONTENT.md`. Rules for every word: `../content/WRITING.md`.

## Tools (on D:, next to the repo, never C:)

Everything lives in a `tools` folder beside the repo (`D:\App\tools` when the
repo is `D:\App\growthvine-client-docs`; override with `GV_TOOLS`):

| Folder | What | Set up with |
|---|---|---|
| `tools/hyperframes` | HyperFrames renderer (npm) | `npm install hyperframes` there, with `cache=<tools>\npm-cache` in its `.npmrc` |
| `tools/growthvine-voice` | Kokoro voice: `venv` + `kokoro-v1.0.onnx` + `voices-v1.0.bin` | `python film/setup_voice.py` (one step: makes the venv with Python 3.10 to 3.12, installs `kokoro-onnx` and `soundfile`, downloads the two model files from the kokoro-onnx `model-files-v1.0` release and checks their sizes, speaks a test line) |
| `tools/hf-cache`, `npm-cache`, `pip-cache`, `tmp` | caches | created by the director |

Also needed: Node 22+, ffmpeg, Chrome. HyperFrames telemetry is switched off on
every run (`HYPERFRAMES_NO_TELEMETRY=1`, `DO_NOT_TRACK=1`).

## Making a film

A film folder (outside the repo, e.g. `D:\App\films\<name>`) holds:

- `data.js`: `window.GV_D = {...}`, every figure the film shows, computed from the
  confirmed inputs (one data module, so the numbers agree everywhere);
- `film.json`: BPM, voice, and the scenes in order (id, bars, voice line, the cut
  sound, hits, which scene is the payoff);
- `compositions/<id>.html`: one scene each, written with `scene.py` (`write`, plus the shared `Q` question heading, `FIND` finding, `END` exit and `FIND_T` timing) and the kit.

Then:

```
python film/director.py <film_dir>                  # plan, audio, render, gates
python film/setup_voice.py                          # once: install the voice
python film/director.py <film_dir> --stage voices   # samples of each voice for the advisor to pick
python film/director.py <film_dir> --stage plan     # voice + wording check + timing only
```

`plan` stops if a voice line does not fit its scene or the wording check finds a
HARD problem. `gates` runs HyperFrames' check, `gates/look.py` (dead frames, cuts,
end hold, loudness) and writes review sheets to `<film_dir>/build/`.
Output: `<name>.mp4` (1080p, -14 LUFS, about 16 MB for 3 minutes). One file only.

## The kit (`kit/`)

`gv.css` (the look: lit ink ground, grain, vignette, type sizes with a 28px floor),
`gv.js` (measured eases, varied text entrances, counters, bar growth, line
drawing, highlight walks, exits that cut on motion), Poppins, GSAP, grain texture,
CC0 sound effects. Credits and licences: `NOTICE.md`.
