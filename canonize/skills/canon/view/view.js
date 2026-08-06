const C = Model.corpus;

document.title = C.name + " — knowledge graph";
document.getElementById("title").textContent = C.name;

const sceneEl = document.getElementById("scene");

function selectNode(id) {
  Panes.select(id);
  if (Scene.isVisible(id)) {
    Scene.setFocus(id);
    Scene.center(id);
  } else {
    Scene.addNode(id);
  }
}

Scene.init(document.getElementById("cy"), {
  onSelect: id => { selectNode(id); Panes.refresh(); },
  onControls: () => Panes.refresh(),
  onChange: s => {
    sceneEl.textContent = s.nodes + " nodes · " + s.open + " open";
    writeHash();
  }
});
Panes.init({ onSelect: selectNode });

document.getElementById("clear").addEventListener("click", () => {
  Scene.reset();
  Panes.refresh();
});

const typesEl = document.getElementById("types");
const active = new Set(C.types);
C.types.forEach(t => {
  const label = document.createElement("label");
  label.innerHTML = '<input type="checkbox" checked><span class="dot" style="background:'
    + Encode.color(t) + '"></span>' + t;
  typesEl.appendChild(label);
  label.querySelector("input").addEventListener("change", e => {
    e.target.checked ? active.add(t) : active.delete(t);
    Scene.setTypes(active.size === C.types.length ? null : active);
  });
});

const edgesEl = document.getElementById("edges");
const structural = document.createElement("label");
structural.innerHTML = '<input type="checkbox" checked>membership &amp; similarity';
edgesEl.appendChild(structural);
structural.querySelector("input")
  .addEventListener("change", e => Scene.setStructural(e.target.checked));

const legend = document.createElement("div");
legend.className = "legend";
legend.innerHTML = ["derived_from", "bears_on", "supersedes"]
  .map(name => '<span><i style="background:' + Encode.KIND[name].color() + '"></i>'
               + name + "</span>").join("");
edgesEl.appendChild(legend);

if (new URLSearchParams(location.search).has("debug")) {
  const box = document.getElementById("physics");
  box.hidden = false;
  Object.keys(Physics.forces).forEach(key => {
    const f = Physics.forces[key];
    const row = document.createElement("label");
    const value = Scene.physics[key];
    row.innerHTML = f.label + ' <input type="range" min="' + f.min + '" max="' + f.max +
                    '" step="' + f.step + '" value="' + value + '"><output>' +
                    value + "</output>";
    box.appendChild(row);
    row.querySelector("input").addEventListener("input", e => {
      row.querySelector("output").textContent = e.target.value;
      Scene.setPhysics(key, Number(e.target.value));
    });
  });
}

const paneState = JSON.parse(localStorage.getItem("canon-panes") || "null")
  || { files: window.innerWidth > 1200, graph: true, read: true };
const paneEl = { files: "files", graph: "cy", read: "panel" };

function applyPanes() {
  Object.keys(paneEl).forEach(name => {
    document.getElementById(paneEl[name]).hidden = !paneState[name];
    document.querySelector('#panes button[data-pane="' + name + '"]')
      .classList.toggle("on", paneState[name]);
  });
  // a divider only earns its place between two panes that are both showing
  const handles = document.querySelectorAll(".drag");
  handles[0].hidden = !(paneState.files && (paneState.graph || paneState.read));
  handles[1].hidden = !(paneState.graph && paneState.read);
  // whichever pane is last takes the slack, so no pane is left with dead space
  document.getElementById("panel").classList.toggle("fill", !paneState.graph);
  localStorage.setItem("canon-panes", JSON.stringify(paneState));
}

document.querySelectorAll("#panes button").forEach(b => {
  b.addEventListener("click", () => {
    paneState[b.dataset.pane] = !paneState[b.dataset.pane];
    applyPanes();
  });
});

document.querySelectorAll(".drag").forEach(handle => {
  const name = handle.dataset.pane === "files" ? "files" : "panel";
  const el = document.getElementById(name);
  const stored = Number(localStorage.getItem("canon-w-" + name));
  if (stored) el.style.width = stored + "px";
  handle.addEventListener("pointerdown", start => {
    start.preventDefault();
    const move = e => {
      const width = name === "files"
        ? e.clientX - el.getBoundingClientRect().left
        : window.innerWidth - e.clientX;
      el.style.width = Math.min(Math.max(width, 200), window.innerWidth - 320) + "px";
    };
    const stop = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", stop);
      localStorage.setItem("canon-w-" + name, parseInt(el.style.width, 10));
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", stop);
  });
});

applyPanes();

// canvas colours are read from CSS variables once; without this a light/dark
// switch leaves the edges painted for the old scheme
window.matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", () => { Encode.readTheme(); Scene.reheat(); });

let hashTimer = null;
function writeHash() {
  clearTimeout(hashTimer);
  hashTimer = setTimeout(() => {
    history.replaceState(null, "", "#s=" + Scene.encodeState());
  }, 400);
}

const initial = /^#s=(.*)$/.exec(location.hash);
if (initial && Scene.restore(initial[1])) Panes.refresh();
else Scene.reset();
