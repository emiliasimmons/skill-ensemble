// The accreting scene: which nodes are on screen, how they got there, and the
// running force simulation that places them.
//
// Membership is reference-counted, so closing one group leaves behind whatever
// another open group also holds.

const Scene = (function () {
  const nodeObj = new Map();      // id -> the object handed to force-graph, reused
                                  // across rebuilds so positions survive
  const visible = new Map();      // id -> node object
  const refs = new Map();         // id -> Set of holders (group id, or "root"/"read")
  const open = new Map();         // group id -> members currently revealed
  const allEdges = [...Model.edges.values()];

  const order = [...Model.byId.keys()].sort();
  const index = new Map(order.map((id, i) => [id, i]));

  let graph = null;
  let focus = null;
  let types = null;               // null means every type
  let structural = true;
  let onChange = () => {};
  let onControls = () => {};

  const PHYSICS = {};
  Object.keys(Physics.forces).forEach(k => { PHYSICS[k] = Physics.forces[k].value; });
  const SIM = Physics.sim;

  // force-graph does not re-export d3, so the two forces it does not install by
  // default get written here.
  function collide() {
    let nodes = [];
    function force() {
      const pad = PHYSICS.separation;
      const cell = 48;
      const grid = new Map();
      nodes.forEach(n => {
        const key = Math.round(n.x / cell) + ":" + Math.round(n.y / cell);
        if (!grid.has(key)) grid.set(key, []);
        grid.get(key).push(n);
      });
      nodes.forEach(a => {
        const cx = Math.round(a.x / cell), cy = Math.round(a.y / cell);
        for (let i = -1; i <= 1; i++) {
          for (let j = -1; j <= 1; j++) {
            (grid.get((cx + i) + ":" + (cy + j)) || []).forEach(b => {
              if (a === b) return;
              const min = Encode.radius(a) + Encode.radius(b) + pad;
              let dx = b.x - a.x, dy = b.y - a.y;
              let d = Math.hypot(dx, dy);
              if (d === 0) { dx = Math.random() - 0.5; dy = Math.random() - 0.5; d = 1; }
              if (d >= min) return;
              const push = ((min - d) / d) * 0.5;
              b.vx += dx * push;
              b.vy += dy * push;
              a.vx -= dx * push;
              a.vy -= dy * push;
            });
          }
        }
      });
    }
    force.initialize = n => { nodes = n; };
    return force;
  }

  // charge pushes disconnected components apart forever, and a group with no
  // tie to the rest ends up off screen
  function gravity() {
    let nodes = [];
    function force(alpha) {
      const k = PHYSICS.center;
      nodes.forEach(n => {
        n.vx -= n.x * k * alpha;
        n.vy -= n.y * k * alpha;
      });
    }
    force.initialize = n => { nodes = n; };
    return force;
  }

  // registered last so it clamps whatever the other forces just added, which
  // is what keeps a reheat from flinging anything across the pane
  function speedLimit() {
    let nodes = [];
    function force() {
      const max = PHYSICS.maxSpeed;
      if (!max) return;
      nodes.forEach(n => {
        const v = Math.hypot(n.vx, n.vy);
        if (v <= max) return;
        const k = max / v;
        n.vx *= k;
        n.vy *= k;
      });
    }
    force.initialize = n => { nodes = n; };
    return force;
  }

  function obj(id) {
    if (!nodeObj.has(id)) {
      const d = Model.byId.get(id);
      const group = Model.groups.get(id);
      nodeObj.set(id, Object.assign({}, d, {
        isGroup: Boolean(group),
        memberCount: group ? group.members.length : 0
      }));
    }
    return nodeObj.get(id);
  }

  // members of one group go out around a ring rather than to random points, so
  // a release opens evenly instead of clumping on one side
  function ringSeed(anchor, frac, radius) {
    const a = frac * 2 * Math.PI + (Math.random() - 0.5) * 0.5;
    const r = radius * (0.85 + Math.random() * 0.3);
    return { x: anchor.x + Math.cos(a) * r, y: anchor.y + Math.sin(a) * r };
  }

  function hold(id, by, seed) {
    if (!refs.has(id)) refs.set(id, new Set());
    refs.get(id).add(by);
    if (visible.has(id)) return;
    const n = obj(id);
    // a member reads as belonging to whatever brought it in, so it wears that
    // group's hue rather than a type color that means nothing at a glance
    if (Model.groups.has(by)) n.hueFrom = by;
    if (seed) {
      n.x = seed.x;
      n.y = seed.y;
      n.vx = n.vy = 0;
    }
    n.exiting = 0;
    n.enter = Date.now();
    visible.set(id, n);
    animate(Encode.ENTER);
  }

  function release(id, by) {
    const held = refs.get(id);
    if (!held) return;
    held.delete(by);
    if (held.size) return;
    refs.delete(id);
    visible.delete(id);
    open.delete(id);
  }

  function rank(gid) {
    return Model.groups.get(gid).members
      .filter(id => !visible.has(id))
      .map(id => ({
        id: id,
        touching: (Model.adj.get(id) || []).filter(a => visible.has(a.other)).length,
        degree: Model.degree(id)
      }))
      .sort((a, b) => b.touching - a.touching || b.degree - a.degree);
  }

  function expand(gid) {
    const group = Model.groups.get(gid);
    if (!group) return;
    if (group.real) hold(gid, "root");
    const anchor = visible.get(gid);
    // members another group already put on screen count as shown and must be
    // claimed too, or collapsing this group would evict them from under it
    group.members.filter(id => visible.has(id)).forEach(id => hold(id, gid));
    const batch = rank(gid).slice(0, Model.PAGE);
    open.set(gid, group.members.filter(id => visible.has(id)).length + batch.length);

    // all at once: the links they arrive on carry no force yet, so the group
    // unfolds as the ramp brings them up rather than as one shove
    const spread = PHYSICS.linkDistance * Physics.seed.group;
    batch.forEach((c, i) => hold(c.id, gid,
      anchor && ringSeed(anchor, i / batch.length, spread)));
    ease();
    draw(true);
  }

  function collapse(gid) {
    const group = Model.groups.get(gid);
    if (!group) return;
    open.delete(gid);

    // whatever another open group also holds simply loses a reference; the rest
    // shrinks out first, so the group folds up instead of blinking away
    const going = [];
    group.members.forEach(id => {
      const held = refs.get(id);
      if (!held) return;
      if (held.size === 1 && held.has(gid) && visible.has(id)) going.push(id);
      else release(id, gid);
    });
    going.forEach(id => { visible.get(id).exiting = Date.now(); });

    animate(Encode.EXIT);
    ease();
    draw(false);
    graph.d3ReheatSimulation();
    setTimeout(() => {
      going.forEach(id => {
        const n = visible.get(id);
        if (n) n.exiting = 0;
        release(id, gid);
      });
      draw(false);
    }, Encode.EXIT);
  }

  function remaining(gid) {
    const group = Model.groups.get(gid);
    return group ? group.members.filter(id => !visible.has(id)).length : 0;
  }

  function reset() {
    nodeObj.forEach(n => {
      n.fx = n.fy = undefined;
      n.pinned = false;
    });
    visible.clear();
    refs.clear();
    open.clear();
    Model.groups.forEach(g => hold(g.id, "root"));
    Model.loose.forEach(id => hold(id, "root"));
    focus = null;
    // building from nothing has no jolt to damp, and easing here just stops the
    // opening layout from ever spreading
    graph.d3VelocityDecay(SIM.settleDecay);
    draw(true);
    frameOnce();
  }

  // The viewport is the reader's. Nothing moves it on its own — a scene that
  // re-frames itself while you are looking at it reads as the graph lurching —
  // so this runs once, when the canvas first has a size to fit to.
  let framed = false, wantFrame = false;
  function fit() {
    if (framed || !wantFrame || !graph) return;
    if (graph.width() < 2 || graph.height() < 2) return;   // size() will call back
    framed = true;
    wantFrame = false;
    // labels run well past the node bounds zoomToFit measures
    graph.zoomToFit(400, 90);
  }

  // long enough for the opening layout to have spread, so the one framing the
  // reader gets is of something settled
  function frameOnce() {
    if (framed) return;
    wantFrame = true;
    setTimeout(fit, 1200);
  }

  function addNode(id, quiet) {
    if (!Model.byId.has(id)) return false;
    const anchor = [...(Model.memberOf.get(id) || [])]
      .map(g => visible.get(g)).find(Boolean);
    hold(id, "read", anchor &&
      ringSeed(anchor, Math.random(), PHYSICS.linkDistance * Physics.seed.single));
    setFocus(id);
    draw(!quiet);
    return true;
  }

  // selecting changes only which borders are drawn; rebuilding the graph data
  // for that re-initialises every force and shunts the whole scene
  function setFocus(id) {
    focus = id;
    hops();
  }

  // border encodes distance from what is being read; two hops is where the
  // signal stops being useful
  function hops() {
    visible.forEach(n => { n.hop = undefined; });
    if (!focus || !visible.has(focus)) return;
    visible.get(focus).hop = 0;
    (Model.adj.get(focus) || []).forEach(a => {
      const n = visible.get(a.other);
      if (n && n.hop === undefined) n.hop = 1;
    });
  }

  function shown() {
    const nodes = [...visible.values()]
      .filter(n => !types || n.isGroup || types.has(n.type));
    const on = new Set(nodes.map(n => n.id));
    // membership edges stay in the data even when hidden — they are the springs
    // holding the scene together, and dropping them makes it fly apart
    const links = allEdges.filter(e =>
      on.has(e.source.id || e.source) && on.has(e.target.id || e.target));
    return { nodes: nodes, links: links };
  }

  const nodeOf = end => (end && end.id) || end;

  // an expanded topic is what you are looking at: it holds its own members
  // close, and everything still collapsed lets go of them, so the thing you
  // opened sits apart instead of dissolving into the rest. `focus` at 0 turns
  // that off and every edge falls back to the plain link settings.
  // A link is only as strong as the weaker of its two ends is present. An edge
  // arriving with a new node therefore starts at zero force and comes up with
  // the node's size, and one whose node is leaving lets go before it vanishes,
  // so neither event lands on the layout as a step change.
  const ramp = l => Math.min(Encode.phase(l.source), Encode.phase(l.target));

  function pull(l) {
    const P = PHYSICS, f = P.focus;
    if (l.kind === "member") {
      return open.has(nodeOf(l.source))
        ? { d: P.linkDistance * (1 - 0.3 * f), s: P.linkForce * (1 + f) }
        : { d: P.linkDistance * (1 + 2.5 * f), s: P.linkForce * (1 - 0.75 * f) };
    }
    if (l.kind === "aggregate") {
      const near = open.has(nodeOf(l.source)) || open.has(nodeOf(l.target));
      return near
        ? { d: P.linkDistance * 3 * (1 + 2 * f), s: P.linkForce * 0.8 * (1 - 0.9 * f) }
        : { d: P.linkDistance * 3, s: P.linkForce * 0.8 };
    }
    return { d: P.linkDistance * 1.4, s: P.linkForce * 0.3 };
  }

  function applyForces() {
    graph.d3Force("charge")
      .strength(n => -(PHYSICS.repel + 0.11 * PHYSICS.repel * Encode.radius(n)));
    graph.d3Force("link")
      .distance(l => pull(l).d)
      .strength(l => pull(l).s * ramp(l));
  }

  // d3 reads link strengths once, when the force is armed, not on every tick —
  // so the ramp only moves if the force is re-armed. Do that on a clock rather
  // than off the engine, or a scene that has gone quiet bakes in the strengths
  // an arriving node had on its first frame and never lets go of them. The
  // padding past the deadline is what guarantees a last pass at full size.
  let animUntil = 0, animTimer = null;
  function animate(ms) {
    animUntil = Math.max(animUntil, Date.now() + ms + 60);
    if (animTimer) return;
    animTimer = setInterval(() => {
      applyForces();
      if (Date.now() >= animUntil) {
        clearInterval(animTimer);
        animTimer = null;
      }
    }, 40);
  }

  // a reheat starts at full alpha, which throws the scene across the pane.
  // Damping hard and easing back turns the same settle into a drift.
  let easeTimer = null;
  function ease() {
    clearTimeout(easeTimer);
    graph.d3VelocityDecay(SIM.easeFrom);
    SIM.easeSteps.forEach(([ms, v]) =>
      setTimeout(() => graph && graph.d3VelocityDecay(v), ms));
    easeTimer = setTimeout(() => {}, 1600);
  }

  function draw(reheat) {
    if (!graph) return;
    hops();
    graph.graphData(shown());
    if (reheat) graph.d3ReheatSimulation();
    onChange(status());
  }

  const status = () => ({ nodes: visible.size, open: open.size, focus: focus });

  function pin(node) {
    node.fx = node.x;
    node.fy = node.y;
    node.pinned = true;
  }

  function unpin(node) {
    node.fx = node.fy = undefined;
    node.pinned = false;
    graph.d3ReheatSimulation();
  }

  function init(el, hooks) {
    onChange = hooks.onChange || onChange;
    onControls = hooks.onControls || onControls;
    let lastTap = 0, lastId = null;

    graph = ForceGraph()(el)
      .nodeId("id")
      // the default 15s cooldown stops the engine for good; after that every
      // expansion piles new nodes on the anchor with nothing to spread them
      .cooldownTime(Infinity)
      .backgroundColor("rgba(0,0,0,0)")
      // heavier damping and a slower decay turn a reheat into a settle rather
      // than a shove
      .d3VelocityDecay(SIM.velocityDecay)
      .d3AlphaDecay(SIM.alphaDecay)
      .nodeCanvasObject(Encode.drawNode)
      .nodePointerAreaPaint(Encode.pointerArea)
      .nodeLabel(n => n.description || n.label)
      .linkVisibility(l => structural || !Model.STRUCTURAL.has(l.kind))
      .linkColor(Encode.linkColor)
      .linkWidth(Encode.linkWidth)
      .linkDirectionalArrowLength(Encode.linkArrow)
      .linkDirectionalArrowRelPos(1)
      .onNodeDragEnd(pin)
      .onNodeHover(node => bubbleFor(node))
      .onNodeClick(node => {
        const now = Date.now();
        if (node.id === lastId && now - lastTap < 320 && node.pinned) unpin(node);
        lastTap = now;
        lastId = node.id;
        hooks.onSelect(node.id);
      });

    // the pane is measured before layout on first paint, and a zero height
    // makes zoomToFit divide by nothing
    let sized = false;
    const size = () => {
      if (!el.clientWidth || !el.clientHeight) return;
      graph.width(el.clientWidth).height(el.clientHeight);
      if (!sized) { sized = true; fit(); }   // the opening frame may be waiting on this
    };
    new ResizeObserver(size).observe(el);
    size();

    graph.d3Force("collide", collide());
    graph.d3Force("gravity", gravity());
    graph.d3Force("speed", speedLimit());
    applyForces();

    buildBubble(el);
    graph.onRenderFramePost(placeBubble);
    return graph;
  }

  let bubble = null, bubbleNode = null, bubbleTimer = null;

  function buildBubble(el) {
    bubble = document.createElement("div");
    bubble.id = "bubble";
    bubble.hidden = true;
    el.appendChild(bubble);
    bubble.addEventListener("pointerenter", () => clearTimeout(bubbleTimer));
    bubble.addEventListener("pointerleave", () => bubbleFor(null));
    bubble.addEventListener("click", e => {
      const act = e.target.closest("button[data-act]");
      if (!act || !bubbleNode) return;
      const node = bubbleNode;
      if (act.dataset.act === "more") expand(node.id);
      else if (act.dataset.act === "collapse") collapse(node.id);
      else if (act.dataset.act === "unpin") unpin(node);
      else pin(node);
      bubbleFor(visible.get(node.id) ? node : null);
      onControls(node.id);
    });
  }

  function bubbleFor(node) {
    clearTimeout(bubbleTimer);
    if (!node) {
      bubbleTimer = setTimeout(() => {
        bubble.hidden = true;
        bubbleNode = null;
      }, 260);
      return;
    }
    bubbleNode = node;
    const bits = [];
    if (node.isGroup) {
      const left = remaining(node.id);
      bits.push("<span>" + (node.memberCount - left) + "/" + node.memberCount + "</span>");
      if (left) bits.push('<button data-act="more">+' +
        Math.min(left, Model.PAGE) + "</button>");
      if (open.has(node.id)) bits.push('<button data-act="collapse">collapse</button>');
    }
    bits.push(node.pinned ? '<button data-act="unpin">unpin</button>'
                          : '<button data-act="pin">pin</button>');
    bubble.innerHTML = bits.join("");
    bubble.hidden = false;
    placeBubble();
  }

  function placeBubble() {
    if (!bubble || bubble.hidden || !bubbleNode) return;
    const p = graph.graph2ScreenCoords(bubbleNode.x, bubbleNode.y);
    bubble.style.left = p.x + "px";
    bubble.style.top = (p.y - Encode.radius(bubbleNode) * graph.zoom() - 10) + "px";
  }

  // hash text stays in RFC 3986 unreserved characters, so nothing is
  // percent-escaped and the URL survives being pasted anywhere
  const OFF = 32768;
  const b36 = n => n.toString(36);
  const clamp = v => Math.max(0, Math.min(2 * OFF, Math.round(v) + OFF));

  function encodeState() {
    const num = id => index.get(id);
    const ids = list => list.map(num).filter(n => n !== undefined).map(b36).join(".");
    const pins = [...visible.values()]
      .filter(n => n.pinned && num(n.id) !== undefined)
      .map(n => [b36(num(n.id)), b36(clamp(n.x)), b36(clamp(n.y))].join("."))
      .join("-");
    return [
      ids([...open.keys()]),
      ids([...refs.entries()].filter(([, by]) => by.has("read")).map(([id]) => id)),
      focus === null || num(focus) === undefined ? "" : b36(num(focus)),
      pins
    ].join("_");
  }

  function restore(text) {
    const parts = String(text).split("_");
    if (parts.length !== 4) return false;
    const nums = s => s ? s.split(".").map(v => parseInt(v, 36)) : [];
    reset();
    nums(parts[0]).forEach(i => order[i] && expand(order[i]));
    nums(parts[1]).forEach(i => order[i] && addNode(order[i], true));
    (parts[3] ? parts[3].split("-") : []).forEach(triple => {
      const [i, x, y] = triple.split(".").map(v => parseInt(v, 36));
      const n = order[i] && visible.get(order[i]);
      if (!n) return;
      n.x = n.fx = x - OFF;
      n.y = n.fy = y - OFF;
      n.pinned = true;
    });
    const f = parts[2] ? parseInt(parts[2], 36) : -1;
    if (f >= 0 && order[f]) setFocus(order[f]);
    draw(true);
    frameOnce();
    return true;
  }

  return {
    init: init, reset: reset, expand: expand, collapse: collapse,
    addNode: addNode, setFocus: setFocus, remaining: remaining,
    isOpen: gid => open.has(gid), isVisible: id => visible.has(id),
    get: id => visible.get(id),
    setTypes: t => { types = t; draw(false); },
    setStructural: v => { structural = v; graph.linkVisibility(graph.linkVisibility()); },
    encodeState: encodeState, restore: restore, status: status,
    graph: () => graph,
    physics: PHYSICS,
    setPhysics: (key, value) => {
      PHYSICS[key] = value;
      applyForces();
      graph.d3ReheatSimulation();
    },
    reheat: () => graph.d3ReheatSimulation(),
    // the one thing that moves the viewport, and only for a node that would
    // otherwise be off screen entirely
    center: id => {
      const n = visible.get(id);
      if (!n || !graph) return;
      const p = graph.graph2ScreenCoords(n.x, n.y);
      const pad = 40;
      if (p.x > pad && p.y > pad &&
          p.x < graph.width() - pad && p.y < graph.height() - pad) return;
      graph.centerAt(n.x, n.y, 500);
    }
  };
})();
