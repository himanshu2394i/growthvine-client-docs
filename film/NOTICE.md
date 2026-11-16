# Third-party work in film/

| What | Where | From | Licence |
|---|---|---|---|
| Rendering (installed, not bundled) | `tools/hyperframes` via npm | HyperFrames by HeyGen, github.com/heygen-com/hyperframes | Apache-2.0 |
| Motion rules (paraphrased in `../content/CONTENT.md` and `kit/gv.js`) | | HyperFrames `skills/hyperframes/references/motion.md`, `spec.md`, `sound.md`, `types/data.md`, `types/explainer.md` | Apache-2.0 |
| 11 measured easing curves | `kit/gv.js` (`EASE`) | motionmaxxing by Tejas Makwana, github.com/Tejashmakwana/motionmaxxing (`runtime/motion.js`) | Apache-2.0 |
| Film checker `look.py`, unchanged | `gates/look.py` | motionmaxxing `scripts/look.py` | Apache-2.0 |
| Cut, transition and dead-frame findings (paraphrased) | `../content/CONTENT.md` | motionmaxxing `references/transitions.md`, `slop.md`, `README.md` | Apache-2.0 |
| Sound effects (whoosh, pop, tick, riser, impact) | `kit/sfx/` | Barty-Bart/motion-graphics `skills/sound-effects/sfx/` (qubodup, ethernel0, Narjara, Squirrel_404, Jummit, BeaconStudio, peoplearehappy, Kenney) | CC0 1.0, see `kit/sfx/LICENSES-barty-bart.md` |
| Score on a beat grid, effects one frame after the picture, -14 LUFS (approach) | `director.py` | Mort1d/motion-graphics-skills (method only, no code) | MIT |
| Voice | `tools/growthvine-voice` (not bundled) | Kokoro-82M via kokoro-onnx | Apache-2.0 |
| GSAP | `kit/gsap.min.js` | GreenSock | GreenSock Standard "No Charge" License, gsap.com/standard-license |
| Poppins | `kit/fonts/` | Indian Type Foundry | SIL Open Font License 1.1 |

Wording check `gates/wording.py` and `../content/WRITING.md`: our own rules and code. Pattern categories
drawn from hardikpandya/stop-slop, FeedHive/ai-slop-detector, eric-tramel/slop-guard and
docwriter-org/plain-writing-skill (all MIT); ideas only (no text copied) from
realrossmanngroup/no_ai_slop_writing_rules and jalaalrd/anti-ai-slop-writing (no licence) and
ilien-dev/quiron (AGPL-3.0); source discipline from anthropics/financial-services and
anthropics/claude-for-financial-advisors (Apache-2.0) and the equity-research skills of
GeniusTrader-Harry and rollingSirius (MIT).

Ideas also drawn from charlie947/motion-graphics-skills (MIT: sound is required, a frame check after
every build), nicglazkov/Chalkboard (MIT: the voice paces the visuals) and haidrrrry/claude-remotion-skill
(MIT: render, inspect frames, fix, render again). No code was copied from those.

Apache-2.0 notice for motionmaxxing: "motionmaxxing: looksmaxxing for motion graphics. Made by Tejas
Makwana. This product is licensed under the Apache License, Version 2.0." Full licence:
https://www.apache.org/licenses/LICENSE-2.0
