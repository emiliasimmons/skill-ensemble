// The two non-graph panes: the file list on the left, the reader on the right,
// plus the bar controls that drive them.

const Panes = (function () {
  const C = Model.corpus;
  const filesEl = document.getElementById("files");
  const reader = document.getElementById("reader");
  const back = document.getElementById("back");
  const history = [];
  const links = [];

  let onSelect = () => {};

  function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, c =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }

  function entry(d) {
    const a = document.createElement("a");
    a.textContent = d.label;
    a.dataset.node = d.id;
    a.dataset.hay = (d.label + " " + (d.description || "")).toLowerCase();
    a.dataset.type = d.type;
    a.dataset.tags = (d.tags || []).join(" ");
    a.title = d.type + (d.description ? " · " + d.description : "");
    a.addEventListener("click", () => onSelect(d.id));
    links.push(a);
    return a;
  }

  function buildFiles() {
    const bar = document.createElement("div");
    bar.id = "files-bar";
    // everything starts collapsed, so the button has to offer the move it will
    // actually make
    bar.innerHTML = '<button data-act="fold">expand all</button>';
    bar.addEventListener("click", e => {
      const button = e.target.closest("button");
      if (!button) return;
      const boxes = [...filesEl.querySelectorAll("details")];
      const anyOpen = boxes.some(b => b.open);
      boxes.forEach(b => { b.open = !anyOpen; });
      button.textContent = anyOpen ? "expand all" : "collapse all";
    });
    filesEl.appendChild(bar);

    const bySource = new Map();
    const rootPages = [];
    Model.byId.forEach(d => {
      if (Model.groups.has(d.id) && !Model.groups.get(d.id).real) return;
      const src = d.source || C.sources[0];
      // the corpus front door does not belong behind a disclosure triangle
      if (src === C.sources[0] && !d.group) { rootPages.push(d); return; }
      if (!bySource.has(src)) bySource.set(src, new Map());
      const groups = bySource.get(src);
      if (!groups.has(d.group)) groups.set(d.group, []);
      groups.get(d.group).push(d);
    });

    const top = document.createElement("div");
    top.className = "pinned";
    rootPages
      .sort((a, b) => (a.id === "index" ? -1 : b.id === "index" ? 1
                       : a.label.localeCompare(b.label)))
      .forEach(d => top.appendChild(entry(d)));
    filesEl.appendChild(top);

    for (const [source, groups] of bySource) {
      const h = document.createElement("h3");
      h.textContent = source;
      filesEl.appendChild(h);
      for (const group of [...groups.keys()].sort()) {
        const box = document.createElement("details");
        const head = document.createElement("summary");
        head.textContent = group + " (" + groups.get(group).length + ")";
        box.appendChild(head);
        groups.get(group)
          .sort((a, b) => a.label.localeCompare(b.label))
          .forEach(d => box.appendChild(entry(d)));
        filesEl.appendChild(box);
      }
    }
  }

  function groupControls(id) {
    const group = Model.groups.get(id);
    if (!group) return "";
    const left = Scene.remaining(id);
    const total = group.members.length;
    const bits = ['<span>' + (total - left) + " of " + total + " shown</span>"];
    if (left) bits.push('<button data-act="more">show ' +
      Math.min(left, Model.PAGE) + " more</button>");
    if (Scene.isOpen(id)) bits.push('<button data-act="collapse">collapse</button>');
    else bits.push('<button data-act="more">expand</button>');
    return '<div class="controls">' + bits.join("") + "</div>";
  }

  function render(id) {
    const d = Model.byId.get(id);
    if (!d) return false;
    const parts = ['<div class="type">' + escapeHtml(d.type) + " · " +
                   escapeHtml(d.source || "") + "</div>",
                   "<h2>" + escapeHtml(d.label) + "</h2>"];
    if (d.description) parts.push('<p class="meta">' + escapeHtml(d.description) + "</p>");
    if (d.resource) {
      parts.push('<p class="meta"><a href="' + escapeHtml(d.resource) +
                 '" target="_blank" rel="noopener">' + escapeHtml(d.resource) + "</a></p>");
    }
    if (d.tags && d.tags.length) {
      parts.push('<p class="meta">' + d.tags
        .map(t => "<code>" + escapeHtml(t) + "</code>").join(" ") + "</p>");
    }
    parts.push(groupControls(id));
    parts.push('<div class="md">' + marked.parse(C.bodies[id] || "") + "</div>");
    reader.innerHTML = parts.join("");
    reader.scrollTop = 0;
    links.forEach(a => a.classList.toggle("on", a.dataset.node === id));
    return true;
  }

  function select(id, push) {
    if (!render(id)) return;
    const current = history[history.length - 1];
    if (push !== false && current !== id) history.push(id);
    back.hidden = history.length < 2;
  }

  function refresh() {
    const current = history[history.length - 1];
    if (current) render(current);
  }

  // `tag:x type:y free words` — facets narrow, the rest matches title and blurb
  function query(text) {
    const facets = { tag: [], type: [] };
    const words = [];
    text.trim().toLowerCase().split(/\s+/).filter(Boolean).forEach(part => {
      const m = /^(tag|type):(.+)$/.exec(part);
      if (m) facets[m[1]].push(m[2]);
      else words.push(part);
    });
    return { facets: facets, words: words,
             empty: !facets.tag.length && !facets.type.length && !words.length };
  }

  function search(text) {
    const q = query(text);
    links.forEach(a => {
      const tags = a.dataset.tags.split(" ");
      a.hidden = !q.empty && !(
        q.facets.type.every(t => a.dataset.type === t) &&
        q.facets.tag.every(t => tags.includes(t)) &&
        q.words.every(w => a.dataset.hay.includes(w)));
    });
    filesEl.querySelectorAll("details").forEach(box => {
      box.open = !q.empty && [...box.querySelectorAll("a")].some(a => !a.hidden);
    });
  }

  function init(hooks) {
    onSelect = hooks.onSelect;
    buildFiles();

    reader.addEventListener("click", e => {
      const act = e.target.closest("button[data-act]");
      if (act) {
        const id = history[history.length - 1];
        if (act.dataset.act === "more") Scene.expand(id);
        else Scene.collapse(id);
        refresh();
        return;
      }
      const a = e.target.closest("a[data-node]");
      if (!a) return;
      e.preventDefault();
      onSelect(a.dataset.node);
    });

    back.addEventListener("click", () => {
      history.pop();
      const prev = history[history.length - 1];
      if (prev) onSelect(prev);
      back.hidden = history.length < 2;
    });

    document.getElementById("search")
      .addEventListener("input", e => search(e.target.value));
  }

  return { init: init, select: select, refresh: refresh };
})();
