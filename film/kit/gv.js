/* gv.js - Growthvine film kit for HyperFrames scenes. Needs gsap (kit/gsap.min.js).
 *
 * Seek contract: every helper adds fromTo tweens with explicit start values to the timeline it is given,
 * so any frame can be drawn on its own. Text is split into word spans once, before the timeline is built.
 *
 * Eases: the 12 measured curves are copied from motionmaxxing's runtime/motion.js (Apache-2.0,
 * (c) Tejas Makwana), fitted to 53 professional films. See film/NOTICE.md.
 * Motion rules follow HyperFrames' motion reference (Apache-2.0, HeyGen): arrive slow on a long tail,
 * leave fast and 40-50% shorter, cut on motion, vary entrances, landed titles stay still.
 */
(function (root) {
  'use strict';
  const powerOut = p => t => 1 - Math.pow(1 - t, p);
  const powerIn = p => t => Math.pow(t, p);
  const expoOut = k => { const d = 1 - Math.exp(-k); return t => (1 - Math.exp(-k * t)) / d; };
  const snapRamp = (w, tau) => { const n = w * (1 - Math.exp(-1 / tau)) + (1 - w); return t => (w * (1 - Math.exp(-t / tau)) + (1 - w) * t) / n; };
  const snapOver = (A, ta, td) => { const f = t => (1 + A * Math.exp(-t / td)) * (1 - Math.exp(-t / ta)); const n = f(1); return t => f(t) / n; };
  const spring = (c, om) => { const f = t => 1 - Math.exp(-c * t) * (Math.cos(om * t) + (c / om) * Math.sin(om * t)); const n = f(1); return t => f(t) / n; };
  const smoothP = p => t => { const a = Math.pow(t, p), b = Math.pow(1 - t, p); return a / (a + b); };
  const guard = f => t => (t <= 0 ? 0 : t >= 1 ? 1 : f(t));
  const EASE = {
    crashIn: guard(snapOver(2.0, 0.19, 0.218)),   // hits and slightly passes its mark at once
    popOver: guard(spring(2.67, 4.36)),           // slow late overshoot (premium, damping ~0.75)
    snapSettle: guard(snapRamp(0.942, 0.118)),    // default hero entry
    softLand: guard(expoOut(3.41)),               // firm decelerate: text and panels
    whip: guard(powerOut(2.52)),                  // hard decelerating big move
    glide: guard(powerOut(1.7)),                  // gentle ease-out for medium moves
    cruise: guard(t => t),                        // linear: fades, counters
    softInOut: guard(smoothP(1.42)),              // symmetric: camera moves, colour floods
    gentleIn: guard(powerIn(2.07)),
    accelExit: guard(powerIn(2.6)),               // the leaving curve
    crashOut: guard(powerIn(3.97)),               // hard acceleration into a cut
  };
  const E = e => (typeof e === 'function' ? e : EASE[e] || e);
  const $ = s => (typeof s === 'string' ? Array.from(document.querySelectorAll(s)) : [].concat(s));

  /* Split an element's text into word spans (once), text nodes only: nested markup and layout are kept. */
  function words(sel) {
    const out = [];
    $(sel).forEach(el => {
      if (el.dataset.split) { out.push(...el.querySelectorAll('.w')); return; }
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT), nodes = [];
      while (walker.nextNode()) if (walker.currentNode.nodeValue.trim()) nodes.push(walker.currentNode);
      nodes.forEach(n => {
        const frag = document.createDocumentFragment();
        n.nodeValue.split(/(\s+)/).forEach(part => {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
          const sp = document.createElement('span'); sp.className = 'w'; sp.textContent = part; frag.appendChild(sp);
        });
        n.parentNode.replaceChild(frag, n);
      });
      el.dataset.split = '1';
      out.push(...el.querySelectorAll('.w'));
    });
    return out;
  }

  /* Entrances apply their hidden start state as soon as the timeline is built (immediateRender true), so an
 * element is never visible before it enters. Pass {ir: false} when an element already entered earlier.
 * Exits, walks and camera moves always wait for their time (immediateRender false).
 *
 * Text entrances. Vary them within a film (never the same fade-and-slide for every line).
   *  blur: per word, blur 8px -> 0 and fade, 0.07 s apart, no movement (HyperFrames title move)
   *  ink:  per word from dim grey to its colour, 0.08 s apart, no movement
   *  land: whole line settles from 1.12x, decelerating from oversize (nothing grows from zero)
   *  rise: per word up 24px on softLand (use sparingly)                                         */
  function textIn(tl, sel, t, mode = 'blur', o = {}) {
    if (mode === 'land') {
      tl.fromTo(sel, { opacity: 0, scale: o.from || 1.12, filter: 'blur(6px)' },
        { opacity: 1, scale: 1, filter: 'blur(0px)', duration: o.dur || 0.5, ease: E('softLand'), immediateRender: o.ir ?? true }, t);
      return t + (o.dur || 0.5);
    }
    const ws = words(sel), step = o.step || (mode === 'ink' ? 0.08 : 0.07);
    // ink: hidden until entered, then the whole line appears dim just before the words light up
    if (mode === 'ink') tl.fromTo(ws, { opacity: 0 }, { opacity: 0.16, duration: 0.2, ease: E('softInOut'), immediateRender: o.ir ?? true }, Math.max(0, t - 0.2));
    ws.forEach((w, i) => {
      const at = t + i * step;
      if (mode === 'blur') tl.fromTo(w, { opacity: 0, filter: 'blur(8px)' }, { opacity: 1, filter: 'blur(0px)', duration: 0.16, ease: E('softInOut'), immediateRender: o.ir ?? true }, at);
      else if (mode === 'ink') tl.fromTo(w, { opacity: 0.16 }, { opacity: 1, duration: 0.22, ease: E('softInOut'), immediateRender: false }, at);
      else tl.fromTo(w, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.4, ease: E('softLand'), immediateRender: o.ir ?? true }, at);
    });
    return t + ws.length * step + 0.2;
  }

  /* Leave: accelerate out along the film's current (default left) with motion blur; 40-50% of an entry. */
  function out(tl, sel, t, o = {}) {
    const dir = o.dir || 'left', d = o.dist || 260, dur = o.dur || 0.28;
    const to = { opacity: o.keep ? 1 : 0, filter: `blur(${o.blur ?? 10}px)`, duration: dur, ease: E(o.ease || 'crashOut'), immediateRender: false };
    if (dir === 'left') to.x = -d; else if (dir === 'right') to.x = d; else if (dir === 'up') to.y = -d; else if (dir === 'down') to.y = d;
    else if (dir === 'push') to.scale = o.scale || 1.6;            // Z forward: grows past camera
    tl.fromTo(sel, { x: 0, y: 0, scale: 1, opacity: 1, filter: 'blur(0px)' }, to, t);
    return t + dur;
  }

  /* Enter already moving, continuing the previous scene's vector (default from the right). */
  function enter(tl, sel, t, o = {}) {
    const dir = o.dir || 'right', d = o.dist || 220, dur = o.dur || 0.5;
    const from = { opacity: 0, filter: `blur(${o.blur ?? 8}px)` };
    if (dir === 'right') from.x = d; else if (dir === 'left') from.x = -d; else if (dir === 'up') from.y = d; else if (dir === 'down') from.y = -d;
    else if (dir === 'arrive') from.scale = o.scale || 1.35;       // Z backward: something bigger lands
    tl.fromTo(sel, from, { x: 0, y: 0, scale: 1, opacity: 1, filter: 'blur(0px)', duration: dur, ease: E(o.ease || 'softLand'), immediateRender: o.ir ?? true }, t);
    return t + dur;
  }

  /* Count a number up on tabular figures (1.2-1.6 s, then it holds). fmt(v) returns the text. */
  function count(tl, sel, t, to, o = {}) {
    const el = $(sel)[0], st = { v: o.from || 0 }, fmt = o.fmt || (v => v.toFixed(o.dp ?? 0));
    el.textContent = fmt(o.from || 0);
    tl.fromTo(st, { v: o.from || 0 }, { v: to, duration: o.dur || 1.4, ease: E(o.ease || 'softLand'), immediateRender: o.ir ?? true,
      onUpdate: () => { el.textContent = fmt(st.v); } }, t);
    return t + (o.dur || 1.4);
  }

  /* Grow bars along x (or y) from their origin. Data bars may grow from zero: the length is the value. */
  function grow(tl, sel, t, o = {}) {
    const axis = o.axis || 'x', p = axis === 'x' ? 'scaleX' : 'scaleY';
    $(sel).forEach((el, i) => {
      el.style.transformOrigin = o.origin || (axis === 'x' ? 'left center' : 'center bottom');
      tl.fromTo(el, { [p]: 0 }, { [p]: 1, duration: o.dur || 0.8, ease: E(o.ease || 'whip'), immediateRender: o.ir ?? true }, t + i * (o.stagger ?? 0.12));
    });
    return t + (o.dur || 0.8) + ($(sel).length - 1) * (o.stagger ?? 0.12);
  }

  /* Draw an SVG path or line along its length. */
  function draw(tl, sel, t, o = {}) {
    $(sel).forEach((el, i) => {
      const L = el.getTotalLength ? el.getTotalLength() : 2000;
      el.style.strokeDasharray = o.dash || `${L} ${L}`;
      tl.fromTo(el, { strokeDashoffset: L }, { strokeDashoffset: 0, duration: o.dur || 2, ease: E(o.ease || 'softInOut'), immediateRender: o.ir ?? true }, t + i * (o.stagger || 0));
    });
    return t + (o.dur || 2);
  }

  /* Walk a highlight across items during a hold, so the frame keeps performing while it is read:
   * each item lifts to full ink in turn, the rest sit at `dim`. Ends with all items lit. */
  function walk(tl, sel, t, o = {}) {
    const items = $(sel), each = o.each || 1.1, dim = o.dim ?? 0.35;
    tl.fromTo(items, { opacity: 1 }, { opacity: dim, duration: 0.3, ease: E('softInOut'), immediateRender: false }, t);
    items.forEach((el, i) => {
      const at = t + 0.3 + i * each;
      tl.fromTo(el, { opacity: dim }, { opacity: 1, duration: 0.25, ease: E('softInOut'), immediateRender: false }, at);
      if (!o.keep && i < items.length - 1) tl.fromTo(el, { opacity: 1 }, { opacity: dim, duration: 0.25, ease: E('softInOut'), immediateRender: false }, at + each);
    });
    const end = t + 0.3 + items.length * each;
    tl.fromTo(items, { opacity: dim }, { opacity: 1, duration: 0.35, ease: E('softInOut'), immediateRender: false }, end);
    return end + 0.35;
  }

  /* Spotlight what the voice is saying, at the moment it says it. groups[i] (a selector, element or list) lights at
   * times[i] (voice cue times from T.cue); everything else in `all` dims. At `release` everything returns to full.
   * Only spotlight what the voice names; never walk items on a timer the voice does not follow. */
  function spotlight(tl, all, groups, times, o = {}) {
    // Dim the items' contents, not the items: entrances animate the item itself, so a row that arrives after the
    // spotlight starts still sits dim, and the two tweens never fight over one opacity.
    const kids = el => (el.children && el.children.length ? Array.from(el.children) : [el]);
    const flat = sel => [].concat(...$(sel).map(kids));
    const dim = o.dim ?? 0.3, items = flat(all), G = groups.map(flat);
    const others = items.filter(el => !G[0].includes(el));     // the first named item never dims
    tl.fromTo(others, {opacity: 1}, {opacity: dim, duration: 0.25, ease: E('softInOut'), immediateRender: false}, times[0] - 0.12);
    G.forEach((g, i) => {
      if (i > 0) tl.fromTo(g, {opacity: dim}, {opacity: 1, duration: 0.2, ease: E('softInOut'), immediateRender: false}, times[i] - 0.1);
      if (i < G.length - 1 && !o.keep) {
        const next = G[i + 1], leaving = g.filter(el => !next.includes(el));
        tl.fromTo(leaving, {opacity: 1}, {opacity: dim, duration: 0.25, ease: E('softInOut'), immediateRender: false}, times[i + 1] - 0.12);
      }
    });
    if (o.release != null) {                                   // bring back only what is dim (the last lit group stays lit)
      const lit = o.keep ? [].concat(...G) : G[G.length - 1];
      tl.fromTo(items.filter(el => !lit.includes(el)), {opacity: dim}, {opacity: 1, duration: 0.35, ease: E('softInOut'), immediateRender: false}, o.release);
    }
  }

  /* A voice cue time, with a fallback when the line has no such marker. */
  const at = (T, name, fallback) => (T.cue && T.cue[name] != null ? T.cue[name] : fallback);

  /* Purposeful camera move between two framings of one wide stage (never a slow creep on a title). */
  function camera(tl, sel, t, to, o = {}) {
    tl.fromTo(sel, o.from || { x: 0, y: 0, scale: 1 }, Object.assign({ duration: o.dur || 1.2, ease: E(o.ease || 'softInOut'), immediateRender: false }, to), t);
    return t + (o.dur || 1.2);
  }

  /* Film grain: a noise layer stepped every frame (deterministic). */
  function grain(tl, sel, dur, fps = 30) {
    const el = $(sel)[0]; if (!el) return;
    const st = { f: 0 };
    tl.fromTo(st, { f: 0 }, { f: dur * fps, duration: dur, ease: 'none', immediateRender: false,
      onUpdate: () => { const f = Math.floor(st.f); el.style.backgroundPosition = `${(f * 137) % 512}px ${(f * 251) % 512}px`; } }, 0);
  }

  /* Indian number grouping: 30000000 -> 3,00,00,000 */
  function inr(n) {
    const s = String(Math.round(n)), last = s.slice(-3); let rest = s.slice(0, -3); const g = [];
    while (rest.length) { g.unshift(rest.slice(-2)); rest = rest.slice(0, -2); }
    return g.length ? g.join(',') + ',' + last : last;
  }

  /* Amounts the way the documents write them: ₹1.20 Cr, ₹70 L */
  const amt = v => (v >= 1e7 ? '₹' + (v / 1e7).toFixed(2) + ' Cr' : v >= 1e6 ? '₹' + Math.round(v / 1e5) + ' L' : '₹' + (v / 1e5).toFixed(1) + ' L');

  root.GV = { EASE, E, words, textIn, out, enter, count, grow, draw, walk, spotlight, at, camera, grain, inr, amt };
})(window);
