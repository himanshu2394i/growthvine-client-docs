"""Crowding check: how much of a frame is covered by edges (text, lines, marks), on each scene's last frame.
A crowded screen has many edges; a clean one has a few large shapes and a little text.

    python film/gates/density.py <snapshot_dir>      exit 1 when a frame is over LIMIT

Set on the fund film (Nov 2026). Scenes the advisor called crowded scored 0.042-0.054; the cleaned two-beat
scenes 0.029-0.039; a tidy table of large numbers can still score 0.043-0.045. So the measure blocks only clear
crowding (over LIMIT) and asks for a look in the band between WARN and LIMIT. A scene meant to be dense (the
one-page summary) sets "dense": true in film.json and is not scored.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageFilter

WARN, LIMIT = 0.040, 0.046


def ink(im):
    """Share of pixels on an edge, measured at half size to ignore grain and anti-aliasing."""
    g = im.convert("L").resize((960, 540)).filter(ImageFilter.FIND_EDGES)
    hist = g.histogram()
    return sum(hist[48:]) / (960 * 540)


def scores(snap_dir):
    return [(f.name, ink(Image.open(f))) for f in sorted(Path(snap_dir).glob("frame-*.png"))]


def check(snap_dir, limit=LIMIT):
    """Frames over the limit: split them into two beats or move numbers to the summary."""
    return [f"{n}: {v:.3f} of the frame is edges (limit {limit}); split the scene into two beats or move numbers to the summary"
            for n, v in scores(snap_dir) if v > limit]


def review(snap_dir, warn=WARN, limit=LIMIT):
    """Frames in the borderline band: look at each and decide."""
    return [f"{n}: {v:.3f}, look again: one idea on screen?" for n, v in scores(snap_dir) if warn < v <= limit]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("snap_dir")
    a = ap.parse_args()
    for n, v in scores(a.snap_dir):
        print(f"{v:.3f}  {n}")
    found, look = check(a.snap_dir), review(a.snap_dir)
    print("\n".join(look + found) or "Density: no crowded frames.")
    sys.exit(1 if found else 0)
