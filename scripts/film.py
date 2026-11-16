"""Tiny film engine: scenes draw frames with Pillow, ffmpeg encodes one clip per scene
(in parallel), joins them, and lays an ffmpeg-synthesised ambient score with hits under it."""
import subprocess
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
SKILL = Path(r"D:\App\growthvine-client-docs")
BG, PANEL = (20, 20, 19), (35, 35, 33)
WHITE, GREY, DIM = (244, 244, 239), (140, 140, 134), (74, 74, 70)
MINT, INDIGO, PEACH, MUSTARD = (177, 240, 219), (155, 129, 245), (255, 187, 144), (241, 246, 142)
FONTS = {400: str(SKILL / "assets/fonts/Poppins-Regular.ttf"), 600: str(SKILL / "assets/fonts/Poppins-SemiBold.ttf")}


@lru_cache(None)
def font(size, weight=400):
    return ImageFont.truetype(FONTS[weight], size)


def clamp(x):
    return max(0.0, min(1.0, x))


def ease(x):                       # ease-out cubic
    x = clamp(x)
    return 1 - (1 - x) ** 3


def inout(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def p(t, start, length=1.0, f=ease):
    return f((t - start) / length)


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def text(d, x, y, s, size, col=WHITE, w=400, anchor="ls", a=1.0, bg=BG):
    if a <= 0:
        return
    d.text((x, y), s, font=font(size, w), fill=mix(bg, col, clamp(a)), anchor=anchor)


def spaced(d, x, y, s, size, col, w=600, gap=4, a=1.0, center=False):
    f = font(size, w)
    total = sum(f.getlength(c) + gap for c in s) - gap
    cx = x - total / 2 if center else x
    for c in s:
        text(d, cx, y, c, size, col, w, a=a)
        cx += f.getlength(c) + gap


def words_up(d, x, y, s, size, col, t, t0, w=400, step=0.07, anchor_center=False):
    """Words fade up one after another."""
    f = font(size, w)
    ws = s.split(" ")
    total = f.getlength(s)
    cx = x - total / 2 if anchor_center else x
    for i, wd in enumerate(ws):
        k = p(t, t0 + i * step, 0.6)
        text(d, cx, y + 18 * (1 - k), wd, size, col, w, a=k)
        cx += f.getlength(wd + " ")


def question(d, t, s, t0=0.3, size=58, y=250, label="THE QUESTION ON YOUR MIND"):
    spaced(d, 96, y - 70, label, 20, INDIGO, a=p(t, t0, 0.6))
    words_up(d, 96, y, s, size, WHITE, t, t0 + 0.4)


def source(d, t, s, t0=1.0):
    text(d, 96, 1028, s, 19, GREY, a=p(t, t0, 1.0))


def inr(n):
    s = str(int(round(n)))
    last, rest, g = s[-3:], s[:-3], []
    while rest:
        g.insert(0, rest[-2:])
        rest = rest[:-2]
    return ",".join(g + [last])


def sprite(draw_fn, w, h, scale=2):
    """Draw at 2x on transparent, downscale: antialiased shapes."""
    im = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(im), scale)
    return im.resize((w, h), Image.LANCZOS)


def paste(img, spr, x, y, a=1.0, crop_w=None):
    if a <= 0:
        return
    s = spr if crop_w is None else spr.crop((0, 0, max(1, int(crop_w)), spr.height))
    if a < 1:
        s = s.copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * a)))
    img.paste(s, (int(x), int(y)), s)


def dashed(d, pts, fill, width, dash=20, gapl=16):
    on, left = True, dash
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        seg = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        pos = 0.0
        while pos < seg:
            step = min(left, seg - pos)
            if on:
                a, b = pos / seg, (pos + step) / seg
                d.line([(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a), (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)], fill=fill, width=width)
            pos += step
            left -= step
            if left <= 0:
                on, left = not on, (gapl if on else dash)


# ---- finishing: vignette, grain, fades -----------------------------------------
_vig = None
_grain = []


def finish(img, t, dur, letterbox=False):
    global _vig
    if _vig is None:
        g = Image.radial_gradient("L").resize((W, H), Image.BILINEAR)
        _vig = g.point(lambda v: int(max(0, (v - 150)) * 1.4))
        for i in range(6):
            _grain.append(Image.effect_noise((W, H), 28).convert("RGB"))
    img.paste((0, 0, 0), (0, 0, W, H), _vig)
    img = Image.blend(img, _grain[int(t * FPS) % 6], 0.035)
    if letterbox:
        ImageDraw.Draw(img).rectangle((0, 0, W, 130), fill=(0, 0, 0))
        ImageDraw.Draw(img).rectangle((0, 950, W, H), fill=(0, 0, 0))
    fade = min(p(t, 0, 0.6, inout), 1 - p(t, dur - 0.6, 0.6, inout))
    if fade < 1:
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, fade)
    return img


def render_scene(args):
    """Worker: render one scene to its own clip."""
    idx, module, out = args
    import importlib
    mod = importlib.import_module(module)
    sc = mod.SCENES[idx]
    dur, draw_fn = sc["dur"], sc["draw"]
    n = int(dur * FPS)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", str(out)],
                            stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        img = Image.new("RGB", (W, H), BG)
        draw_fn(img, ImageDraw.Draw(img), t)
        img = finish(img, t, dur, sc.get("letterbox", False))
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    return out


def still(module, idx, t):
    import importlib
    sc = importlib.import_module(module).SCENES[idx]
    img = Image.new("RGB", (W, H), BG)
    sc["draw"](img, ImageDraw.Draw(img), t)
    return finish(img, t, sc["dur"], sc.get("letterbox", False))


# ---- music ---------------------------------------------------------------------------
def score(total, booms, whooshes, out):
    """Original ambient score: two slow alternating chords with swells, a soft high shimmer,
    low booms on key numbers and filtered-noise whooshes on scene changes."""
    chord_a = [73.42, 110.0, 146.83, 185.0, 220.0]          # D, A, D, F#, A
    chord_b = [65.41, 98.0, 130.81, 164.81, 246.94]         # C, G, C, E, B
    va = "+".join(f"sin(2*PI*{f}*t)*(0.6+0.4*sin(2*PI*0.05*t+{i}))" for i, f in enumerate(chord_a))
    vb = "+".join(f"sin(2*PI*{f}*t)*(0.6+0.4*sin(2*PI*0.04*t+{i}))" for i, f in enumerate(chord_b))
    pad = (f"0.05*(({va})*(0.5+0.5*cos(2*PI*t/32))+({vb})*(0.5-0.5*cos(2*PI*t/32)))"
           f"+0.012*sin(2*PI*880*t)*(0.5+0.5*sin(2*PI*0.07*t))")
    inputs = ["-f", "lavfi", "-i", f"aevalsrc='{pad}|{pad}':s=44100:d={total}"]
    filt = ["[0]lowpass=f=1400,aecho=0.8:0.7:120|260:0.35|0.25,afade=t=in:d=4,afade=t=out:st={:.2f}:d=5,volume=1.0[pad]".format(total - 5)]
    mixes = ["[pad]"]
    k = 1
    for at in booms:
        inputs += ["-f", "lavfi", "-i", "aevalsrc='0.8*sin(2*PI*(38+70*exp(-9*t))*t)*exp(-2.2*t)|0.8*sin(2*PI*(38+70*exp(-9*t))*t)*exp(-2.2*t)':s=44100:d=3.5"]
        ms = int(at * 1000)
        filt.append(f"[{k}]lowpass=f=300,adelay={ms}|{ms}[b{k}]")
        mixes.append(f"[b{k}]")
        k += 1
    for at in whooshes:
        inputs += ["-f", "lavfi", "-i", "anoisesrc=color=pink:d=1.4:a=0.5:r=44100"]
        ms = int(max(0, at - 0.9) * 1000)
        filt.append(f"[{k}]highpass=f=500,lowpass=f=5000,afade=t=in:d=0.9,afade=t=out:st=0.9:d=0.5,volume=0.35,aformat=channel_layouts=stereo,adelay={ms}|{ms}[w{k}]")
        mixes.append(f"[w{k}]")
        k += 1
    filt.append("".join(mixes) + f"amix=inputs={len(mixes)}:normalize=0,alimiter=limit=0.9,atrim=0:{total}[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]", "-ar", "44100", str(out)], check=True)


def build(module, out_mp4, workdir, workers=12, reuse=False):
    import importlib
    from multiprocessing import Pool
    mod = importlib.import_module(module)
    workdir = Path(workdir).resolve()           # concat reads paths relative to the list file: use absolute ones
    workdir.mkdir(exist_ok=True)
    jobs = [(i, module, workdir / f"scene_{i:02d}.mp4") for i in range(len(mod.SCENES))]
    todo = [j for j in jobs if not (reuse and j[2].exists())]
    if todo:
        with Pool(min(workers, len(todo))) as pool:
            pool.map(render_scene, todo)
    lst = workdir / "list.txt"
    lst.write_text("".join(f"file '{j[2].as_posix()}'\n" for j in jobs), encoding="utf-8")
    silent = workdir / "silent.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)], check=True)
    starts, acc = [], 0.0
    for sc in mod.SCENES:
        starts.append(acc)
        acc += sc["dur"]
    booms = [starts[i] + b for i, sc in enumerate(mod.SCENES) for b in sc.get("booms", [])]
    whooshes = starts[1:]
    music = workdir / "score.wav"
    score(acc, booms, whooshes, music)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(music), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", str(out_mp4)], check=True)
    return acc
