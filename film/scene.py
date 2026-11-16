"""Write one HyperFrames scene file from its markup and motion, with the Growthvine shell around it.

    from scene import write
    write(film_dir, "jobs", body_html, script_js, css="", source="Option 1, from your proposal.")

Inside script_js these are defined: tl (the scene's paused timeline), T (this scene's timing from timing.js:
T.dur, T.vo = [voice start, voice length] in scene seconds), D (the film's data module, data.js), GV (the kit).
Prefix every element id with the scene id: ids must be unique across the whole film.
The scene root is transparent: the world, grain and vignette come from index.html. A chapter scene paints its
own ground (<div class="gv-mint"></div>) as its first child.
"""
from pathlib import Path


def write(film_dir, sid, body, script, css="", source=None):
    src = f'<div id="{sid}-src" class="src" data-layout-ignore>{source}</div>' if source else ""
    html = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
{css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">
    <div class="gv" id="{sid}-stage">
{body}
      {src}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const T = window.GV_T["{sid}"], D = window.GV_D;
{script}
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""
    p = Path(film_dir) / "compositions" / f"{sid}.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    return p


# ---- shared pieces every film uses (question heading, finding, scene exit)
def Q(sid, text, top=150):
    """The scene's question, as the client would ask it."""
    return f'<div id="{sid}-q" class="q" style="position:absolute;left:96px;top:{top}px;width:1728px">{text}</div>'


def FIND(sid, bold, sub=None, top=890):
    """The finding: a mint rule, one bold line and an optional sub-line. Keep each to one line (see CONTENT.md)."""
    s = f'<div class="voice-sub" style="position:absolute;left:28px;top:56px;width:1700px">{sub}</div>' if sub else ""
    return (f'<div id="{sid}-find" data-hold style="position:absolute;left:96px;top:{top}px;width:1728px">'
            f'<div style="position:absolute;left:0;top:6px;width:6px;height:44px;background:var(--mint)"></div>'
            f'<div class="voice" style="position:absolute;left:28px;top:0;width:1700px">{bold}</div>{s}</div>')


VO_END = "Math.min(T.vo[0] + T.vo[1] + 0.2, T.dur - 3.4)"
# the finding enters just after the voice's last cue, with at least 6.6 s to read it before the scene leaves
FIND_T = "Math.max(1.5, Math.min(Math.max(0, ...Object.values(T.cue || {})) + 1.4, T.dur - 6.6))"


def END(sid, t=FIND_T):
    """Finding enters at t; the whole scene (#<sid>-all) leaves left at the end."""
    return f"""
      GV.enter(tl, '#{sid}-find', {t}, {{dir: 'right', dist: 60, dur: 0.6}});
      GV.out(tl, '#{sid}-all', T.dur - 0.3, {{dir: 'left'}});"""
