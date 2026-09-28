/* SVG chart builders for the deck and the video.
   Mark specs follow the data-viz method: thin bars (<= 26px) with a 4px rounded data-end
   and a square baseline, 2px surface gaps between stacked segments, hairline solid grid,
   text in text tokens (never in the series color), legends for >= 2 series.
   Every builder takes {progress} (0..1) so the video can animate the same chart. */
(function () {
  const NS = "http://www.w3.org/2000/svg";

  function el(tag, attrs, parent) {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs || {}) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function text(parent, x, y, str, cls, attrs) {
    const t = el("text", Object.assign({ x, y, class: cls }, attrs || {}), parent);
    t.textContent = str;
    return t;
  }
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const ease = (t) => 1 - Math.pow(1 - clamp(t, 0, 1), 3);
  // staggered progress for item i of n
  const stag = (p, i, n, spread) => ease((p - (i / n) * (spread || 0.45)) / (1 - (spread || 0.45)));

  const fmt = (n) => Math.round(n).toLocaleString("ko-KR");
  function man(n) { // 만원 -> "1억 2,595만원"
    n = Math.round(n);
    if (n >= 10000) {
      const eok = Math.floor(n / 10000), rest = n % 10000;
      return eok + "억" + (rest ? " " + fmt(rest) + "만원" : "원");
    }
    return fmt(n) + "만원";
  }
  function won(n) { return fmt(n) + "원"; }

  // bar with rounded data-end (right side), square baseline (left)
  function hbar(parent, x, y, w, h, fill, opts) {
    opts = opts || {};
    const r = Math.min(opts.r == null ? 4 : opts.r, w / 2, h / 2);
    if (w <= 0.5) return null;
    const roundEnd = opts.roundEnd !== false;
    const d = roundEnd
      ? `M${x},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h - r}Q${x + w},${y + h} ${x + w - r},${y + h}H${x}Z`
      : `M${x},${y}H${x + w}V${y + h}H${x}Z`;
    return el("path", { d, fill, "fill-opacity": opts.opacity == null ? 1 : opts.opacity }, parent);
  }
  function vbar(parent, x, y0, w, h, fill, opts) { // grows up from baseline y0
    opts = opts || {};
    const r = Math.min(4, w / 2, h / 2);
    if (h <= 0.5) return null;
    const y = y0 - h;
    const d = `M${x},${y0}V${y + r}Q${x},${y} ${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y0}Z`;
    return el("path", { d, fill, "fill-opacity": opts.opacity == null ? 1 : opts.opacity }, parent);
  }

  function colors(dark) {
    return dark
      ? { s1: "#3E92C4", s2: "#B58A3A", ctx: "#4A5866", grid: "#26384A", base: "#3A4B5C", surface: "#14202B", band: "#8A96A1" }
      : { s1: "#1B709E", s2: "#AA7D2D", ctx: "#CFC6B8", grid: "#E2DACD", base: "#C3B9A9", surface: "#F7F3EC", band: "#85817A" };
  }

  function prep(svg, w, h) {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.setAttribute("width", w);
    svg.setAttribute("height", h);
    svg.classList.add("viz");
  }

  /* ---------------------------------------------------------------- revenue */
  function revenue(svg, o) {
    o = Object.assign({ w: 1000, h: 470, progress: 1, dark: false, labelW: 150 }, o);
    const C = colors(o.dark), P = window.PLAN;
    prep(svg, o.w, o.h);
    const x0 = o.labelW, x1 = o.w - 170, top = 52, bottom = o.h - 44;
    const max = 22000, sx = (v) => x0 + (v / max) * (x1 - x0);
    // grid + ticks
    for (let v = 0; v <= 20000; v += 5000) {
      el("line", { x1: sx(v), x2: sx(v), y1: top - 10, y2: bottom, stroke: v === 0 ? C.base : C.grid, "stroke-width": 1 }, svg);
      text(svg, sx(v), bottom + 30, v === 0 ? "0" : fmt(v), "tick", { "text-anchor": "middle" });
    }
    text(svg, x1 + 10, bottom + 30, "(만원)", "tick", { "text-anchor": "start" });
    // BEP band
    const bp = ease(o.progress * 1.6 - 0.2);
    el("rect", { x: sx(P.bep.min), y: top - 10, width: sx(P.bep.max) - sx(P.bep.min), height: (bottom - top + 10) * bp, fill: C.band, "fill-opacity": 0.16 }, svg);
    el("line", { x1: sx(P.bep.max), x2: sx(P.bep.max), y1: top - 10, y2: top - 10 + (bottom - top + 10) * bp, stroke: C.band, "stroke-width": 1, "stroke-opacity": 0.55 }, svg);
    const bt = text(svg, sx(P.bep.max) + 10, top - 22, "손익분기 목표 6,500~7,000만", "sub", { "text-anchor": "start" });
    bt.setAttribute("opacity", bp);
    // bars
    const n = P.scenarios.length, band = (bottom - top) / n, bh = 26;
    P.scenarios.forEach((s, i) => {
      const p = stag(o.progress, i, n, 0.4);
      const cy = top + band * i + band / 2;
      const y = cy - bh / 2;
      text(svg, 0, cy + 8, s.name, "lbl", { "font-size": 24 });
      const addOn = s.total - s.spa;
      const wSpa = (sx(s.spa) - x0) * p;
      const wAdd = (sx(s.total) - sx(s.spa)) * p;
      hbar(svg, x0, y, Math.max(0, wSpa - 1), bh, C.s1, { roundEnd: false });
      hbar(svg, x0 + wSpa + 1, y, Math.max(0, wAdd - 1), bh, C.s2);
      // total at tip
      const tv = text(svg, x0 + wSpa + wAdd + 14, cy + 7, man(s.total * p), "val", { "font-size": 22 });
      tv.setAttribute("opacity", clamp(p * 2 - 0.2, 0, 1));
      // share of add-on sales under the bar
      const sh = text(svg, x0, y + bh + 26, `결합·부가 상품 비중 ${Math.round((addOn / s.total) * 100)}%`, "sub");
      sh.setAttribute("opacity", clamp(p * 2 - 1, 0, 1));
    });
    return svg;
  }

  /* ---------------------------------------------------------------- price ladder */
  function priceLadder(svg, o) {
    o = Object.assign({ w: 1040, h: 560, progress: 1, dark: false, labelW: 330 }, o);
    const C = colors(o.dark), rows = window.PLAN.prices2p;
    prep(svg, o.w, o.h);
    const x0 = o.labelW, x1 = o.w - 20, top = 16, bottom = o.h - 40;
    const max = 400000, sx = (v) => x0 + (v / max) * (x1 - x0);
    for (let v = 0; v <= max; v += 100000) {
      el("line", { x1: sx(v), x2: sx(v), y1: top, y2: bottom, stroke: v === 0 ? C.base : C.grid, "stroke-width": 1 }, svg);
      text(svg, sx(v), bottom + 30, v === 0 ? "0" : (v / 10000) + "만원", "tick", { "text-anchor": "middle" });
    }
    const n = rows.length, band = (bottom - top) / n, bh = 22;
    rows.forEach((r, i) => {
      const p = stag(o.progress, i, n, 0.5);
      const cy = top + band * i + band / 2, y = cy - bh / 2;
      text(svg, 0, cy - 2, r.name, "lbl", { "font-size": 22, "font-weight": r.hero ? 700 : 500 });
      text(svg, 0, cy + 24, r.basis + " · " + r.role, "sub");
      const col = r.hero ? C.s2 : C.s1;
      const wMin = (sx(r.min) - x0) * p;
      const range = r.max > r.min;
      hbar(svg, x0, y, wMin, bh, col, { roundEnd: !range });
      if (range) hbar(svg, x0 + wMin + 2, y, Math.max(0, (sx(r.max) - sx(r.min) - 2) * p), bh, col, { opacity: 0.38 });
      const label = range ? `${fmt(r.min / 10000)}~${fmt(r.max / 10000)}만원` : `${fmt(r.min / 10000)}만원`;
      const t = text(svg, x0 + (sx(r.max) - x0) * p + 14, cy + 7, label, "val", { "font-size": 21 });
      t.setAttribute("opacity", clamp(p * 2 - 0.4, 0, 1));
    });
    return svg;
  }

  /* ---------------------------------------------------------------- generic sorted bars */
  function barList(svg, items, o) {
    o = Object.assign({ w: 900, h: 700, progress: 1, dark: false, labelW: 260, max: null, unit: "", bh: 18, highlight: 0, fontSize: 19, valFmt: fmt }, o);
    const C = colors(o.dark);
    prep(svg, o.w, o.h);
    const max = o.max || Math.max(...items.map((d) => d.v));
    const x0 = o.labelW, x1 = o.w - 90, top = 4, bottom = o.h - 4;
    const sx = (v) => x0 + (v / max) * (x1 - x0);
    el("line", { x1: x0, x2: x0, y1: top, y2: bottom, stroke: C.base, "stroke-width": 1 }, svg);
    const n = items.length, band = (bottom - top) / n;
    items.forEach((d, i) => {
      const p = stag(o.progress, i, n, 0.5);
      const cy = top + band * i + band / 2;
      text(svg, x0 - 16, cy + o.fontSize * 0.36, d.name, "lbl", { "text-anchor": "end", "font-size": o.fontSize });
      const col = i < o.highlight ? C.s1 : C.s1;
      hbar(svg, x0 + 1, cy - o.bh / 2, (sx(d.v) - x0 - 1) * p, o.bh, col, { opacity: i < o.highlight || !o.highlight ? 1 : 0.55 });
      const t = text(svg, sx(d.v) * 1 - (sx(d.v) - x0) * (1 - p) + 12, cy + o.fontSize * 0.36, o.valFmt(d.v), "val-m", { "font-size": o.fontSize - 1 });
      t.setAttribute("opacity", clamp(p * 2 - 0.4, 0, 1));
    });
    return svg;
  }

  /* ---------------------------------------------------------------- turns */
  function turns(svg, o) {
    o = Object.assign({ w: 820, h: 300, progress: 1, dark: false, labelW: 200 }, o);
    const C = colors(o.dark);
    prep(svg, o.w, o.h);
    const rows = [
      { name: "이론 최대", lo: 4, hi: 4, ctx: true, label: "4회" },
      { name: "안정화 목표", lo: 2.2, hi: 2.5, label: "2.2~2.5회" },
      { name: "초기 목표", lo: 1.5, hi: 2.0, label: "1.5~2.0회" }
    ];
    const x0 = o.labelW, x1 = o.w - 150, top = 10, bottom = o.h - 44;
    const sx = (v) => x0 + (v / 4) * (x1 - x0);
    for (let v = 0; v <= 4; v++) {
      el("line", { x1: sx(v), x2: sx(v), y1: top, y2: bottom, stroke: v === 0 ? C.base : C.grid }, svg);
      text(svg, sx(v), bottom + 30, v + "회", "tick", { "text-anchor": "middle" });
    }
    const band = (bottom - top) / rows.length, bh = 24;
    rows.forEach((r, i) => {
      const p = stag(o.progress, i, rows.length, 0.4);
      const cy = top + band * i + band / 2;
      text(svg, 0, cy + 8, r.name, "lbl", { "font-size": 22 });
      const col = r.ctx ? C.ctx : C.s1;
      const wLo = (sx(r.lo) - x0) * p;
      const range = r.hi > r.lo;
      hbar(svg, x0 + 1, cy - bh / 2, wLo - 1, bh, col, { roundEnd: !range });
      if (range) hbar(svg, x0 + wLo + 2, cy - bh / 2, Math.max(0, (sx(r.hi) - sx(r.lo) - 2) * p), bh, col, { opacity: 0.38 });
      const t = text(svg, x0 + (sx(r.hi) - x0) * p + 14, cy + 8, r.label, "val", { "font-size": 22 });
      t.setAttribute("opacity", clamp(p * 2 - 0.4, 0, 1));
    });
    return svg;
  }

  /* ---------------------------------------------------------------- roadmap columns */
  function roadmap(svg, o) {
    o = Object.assign({ w: 640, h: 440, progress: 1, dark: false }, o);
    const C = colors(o.dark), rows = window.PLAN.roadmap;
    prep(svg, o.w, o.h);
    const base = o.h - 70, top = 70, max = 16000;
    const sy = (v) => (v / max) * (base - top);
    el("line", { x1: 0, x2: o.w, y1: base, y2: base, stroke: C.base }, svg);
    const n = rows.length, band = o.w / n, bw = 26;
    rows.forEach((r, i) => {
      const p = stag(o.progress, i, n, 0.45);
      const cx = band * i + band / 2;
      const hLo = sy(r.lo) * p, hHi = sy(r.hi) * p;
      const range = r.hi > r.lo;
      if (range) {
        vbar(svg, cx - bw / 2, base, bw, hHi, C.s2, { opacity: 0.38 });
        el("rect", { x: cx - bw / 2, y: base - hLo, width: bw, height: hLo, fill: C.s2 }, svg);
        el("line", { x1: cx - bw / 2, x2: cx + bw / 2, y1: base - hLo - 1, y2: base - hLo - 1, stroke: C.surface, "stroke-width": 2 }, svg);
      } else {
        vbar(svg, cx - bw / 2, base, bw, hLo, C.s2);
      }
      const tv = text(svg, cx, base - hHi - 18, r.target.replace("월 ", ""), "val", { "text-anchor": "middle", "font-size": 24 });
      tv.setAttribute("opacity", clamp(p * 2 - 0.5, 0, 1));
      text(svg, cx, base + 36, r.stage, "lbl", { "text-anchor": "middle", "font-size": 22 });
    });
    return svg;
  }

  window.Charts = { revenue, priceLadder, barList, turns, roadmap, man, won, fmt, ease, clamp };
})();
