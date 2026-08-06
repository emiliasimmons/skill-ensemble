// Every tunable number for the layout. Change one and reload the page; no
// rebuild, and nothing else in the viewer hard-codes these.
//
// `forces` doubles as the ?debug panel: the range each slider spans, the step
// it moves in, and where it starts.

const Physics = {
  forces: {
    center:       { label: "center force",  value: 0.09, min: 0,  max: 0.6, step: 0.005 },
    repel:        { label: "repel force",   value: 110,  min: 0,  max: 500, step: 5 },
    linkForce:    { label: "link force",    value: 0.5,  min: 0,  max: 0.5, step: 0.01 },
    linkDistance: { label: "link distance", value: 46,   min: 4,  max: 46,  step: 0.5 },
    separation:   { label: "separation",    value: 14,   min: 0,  max: 60,  step: 1 },
    focus:        { label: "focus pull",    value: 0.55, min: 0,  max: 1,   step: 0.05 },
    maxSpeed:     { label: "max speed",     value: 15,   min: 0,  max: 20,  step: 0.5 }
  },

  // how long an arriving node takes to reach full size, and a leaving one to
  // vanish. The link force ramps over the same window, so these set how long an
  // expansion or a collapse takes to resolve.
  anim: { enter: 700, exit: 500 },

  // motion rather than force: how fast the simulation gives up and how hard it
  // damps on the way there
  sim: {
    alphaDecay: 0.02,      // lower runs the layout longer before it stops
    velocityDecay: 0.55,   // steady state
    settleDecay: 0.45,     // while the opening layout is still spreading
    easeFrom: 0.9,         // the first moments after an expand or collapse
    easeSteps: [[350, 0.82], [700, 0.72], [1100, 0.62], [1600, 0.55]]
  },

  // how far from its group a new member is dropped, in multiples of link
  // distance
  seed: { group: 1.7, single: 2.2 }
};
