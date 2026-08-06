// Canvas drawing for nodes and edges. Size carries degree, color carries type,
// border carries distance from the focused node, shape carries pinning.
//
// The type palette lives here rather than in the build, so a color change is
// picked up without recompiling every bundle.

const Encode = (function () {
  const css = name =>
    getComputedStyle(document.documentElement).getPropertyValue("--" + name).trim();

  const theme = {};
  const readTheme = () => {
    ["fg", "bg", "muted", "edge", "accent", "line"].forEach(k => theme[k] = css(k));
  };
  readTheme();

  // AntV G2 categorical ten, which holds its separation on both light and dark
  // backgrounds and keeps the bulk type (source) quiet
  const PALETTE = {
    source:     "#5B8FF9",
    concept:    "#9270CA",
    topic:      "#E8684A",
    decision:   "#F6BD16",
    finding:    "#5AD8A6",
    provenance: "#269A99",
    experiment: "#FF99C3",
    summary:    "#6DC8EC",
    register:   "#8595AB",
    glossary:   "#8595AB",
    index:      "#8595AB",
    group:      "#8595AB"
  };
  const DEFAULT = "#A6B3C2";

  // every group is type `topic`, so on the opening screen a type palette says
  // nothing; each group takes its own hue instead, and its members keep theirs
  const GROUPS = ["#E8684A", "#5B8FF9", "#5AD8A6", "#F6BD16", "#9270CA", "#269A99",
                  "#FF9D4D", "#6DC8EC", "#FF99C3", "#7262FD", "#78D3F8", "#B6E3B5",
                  "#D3C6EA", "#F08BB4", "#B4A3D8", "#98DCA9"];
  const groupHue = new Map();

  // keyed off a sorted group list, not draw order, so a shared URL comes back
  // in the colors it was sent in
  const hueOf = id => {
    if (!groupHue.size) {
      [...Model.groups.keys()].sort()
        .forEach((g, i) => groupHue.set(g, GROUPS[i % GROUPS.length]));
    }
    return groupHue.get(id) || DEFAULT;
  };

  // types inside one group still have to read apart — experiment against
  // summary — so type moves lightness while the group owns the hue
  const TYPE_SHIFT = {
    topic: 0, concept: -14, source: 0, decision: 14, finding: -8,
    provenance: -20, experiment: 10, summary: -12, register: 6, glossary: 6
  };

  function shift(hex, pct) {
    if (!pct) return hex;
    const n = parseInt(hex.slice(1), 16);
    const mix = pct > 0 ? 255 : 0;
    const k = Math.abs(pct) / 100;
    const ch = i => {
      const v = (n >> (16 - 8 * i)) & 255;
      return Math.round(v + (mix - v) * k);
    };
    return "#" + [ch(0), ch(1), ch(2)]
      .map(v => v.toString(16).padStart(2, "0")).join("");
  }

  function color(node) {
    if (typeof node === "string") return PALETTE[node] || DEFAULT;
    if (node.isGroup) return hueOf(node.id);
    if (!node.hueFrom) return PALETTE[node.type] || DEFAULT;
    return shift(hueOf(node.hueFrom), TYPE_SHIFT[node.type] || 0);
  }

  const KIND = {
    link:         { color: () => theme.edge, width: 0.8, arrow: true  },
    derived_from: { color: () => "#3F9E8C",  width: 1.2, arrow: true  },
    bears_on:     { color: () => "#C99A2E",  width: 1.2, arrow: true  },
    supersedes:   { color: () => "#C4553F",  width: 1.8, arrow: true  },
    member:       { color: () => theme.line, width: 0.5, arrow: false },
    aggregate:    { color: () => theme.edge, width: 1,   arrow: false }
  };

  const ENTER = Physics.anim.enter;
  const EXIT = Physics.anim.exit;

  const smooth = t => t * t * (3 - 2 * t);

  // How far along a node is between absent and present: 0 the instant it
  // arrives, 1 once settled, back down to 0 as it leaves. Radius, opacity and
  // the strength of every link touching it all read this, so a node grows into
  // its space and pulls on its neighbours only as hard as it is visible.
  function phase(node) {
    if (typeof node !== "object") return 1;
    const now = Date.now();
    if (node.exiting) return Math.max(0, 1 - (now - node.exiting) / EXIT);
    if (!node.enter) return 1;
    const t = (now - node.enter) / ENTER;
    if (t >= 1) { node.enter = 0; return 1; }
    return smooth(t);
  }

  const fullRadius = node =>
    node.isGroup ? 5 + Math.sqrt(node.memberCount || 1) * 1.4
                 : 3 + Math.sqrt(Model.degree(node.id)) * 0.9;

  const radius = node => Math.max(0.6, fullRadius(node) * phase(node));

  function drawNode(node, ctx, scale) {
    const r = radius(node);
    const alpha = phase(node);
    if (alpha < 1) ctx.globalAlpha = alpha;
    ctx.beginPath();
    if (node.pinned) {
      const s = r * 0.9;
      ctx.rect(node.x - s, node.y - s, s * 2, s * 2);
    } else {
      ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
    }
    ctx.fillStyle = color(node);
    ctx.fill();

    if (node.hop === 0 || node.hop === 1) {
      ctx.lineWidth = (node.hop === 0 ? 3 : 1.5) / scale;
      ctx.strokeStyle = theme.accent;
      ctx.stroke();
    }

    if (!node.isGroup && node.hop !== 0 && scale < 1.6) { ctx.globalAlpha = 1; return; }
    const label = node.isGroup ? node.label + " · " + node.memberCount : node.label;
    const size = Math.max(9 / scale, node.isGroup ? 3.2 : 2.2);
    ctx.font = (node.isGroup ? "600 " : "") + size + "px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    // labels cross edges and each other; a halo keeps them legible without
    // pushing the layout around
    ctx.lineWidth = 3 / scale;
    ctx.strokeStyle = theme.bg;
    ctx.lineJoin = "round";
    ctx.strokeText(clip(label), node.x, node.y + r + 1.5 / scale);
    ctx.fillStyle = theme.fg;
    ctx.fillText(clip(label), node.x, node.y + r + 1.5 / scale);
    ctx.globalAlpha = 1;
  }

  const clip = s => (s.length > 44 ? s.slice(0, 42) + "…" : s);

  function pointerArea(node, paint, ctx) {
    const r = radius(node) + 2;
    ctx.fillStyle = paint;
    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
    ctx.fill();
  }

  return {
    radius: radius, drawNode: drawNode, pointerArea: pointerArea,
    readTheme: readTheme, KIND: KIND, PALETTE: PALETTE, color: color,
    ENTER: ENTER, EXIT: EXIT, phase: phase,
    linkColor: l => KIND[l.kind].color(),
    linkWidth: l => l.kind === "aggregate"
      ? 0.4 + 3 * (l.weight / Model.maxWeight) : KIND[l.kind].width,
    linkArrow: l => KIND[l.kind].arrow ? 3 : 0
  };
})();
