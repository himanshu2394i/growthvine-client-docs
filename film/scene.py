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
