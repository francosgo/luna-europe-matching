const $ = (id) => document.getElementById(id);
function rotate() {
  $("layers").style.transform =
    `rotateX(${$("tilt").value}deg) rotateZ(${$("rotation").value}deg)`;
}
for (const id of ["rotation", "tilt"]) $(id).oninput = rotate;
const texts = [
  [
    "Evidence stays with its source",
    "Private CV facts and employer requirements are structured with provenance. A human resolves contradictory sources; no unsupported skill is invented. Retrieval here means looking up explicit evidence IDs, not training on customer documents.",
  ],
  [
    "Every score can be inspected",
    "Python engine.py computes weighted evidence fit, assessed coverage, unknown upper bound, and hard eligibility gaps. No protected characteristics, personality inference, or moral scores enter this calculation.",
  ],
  [
    "Approval belongs to a version",
    "SQLite stores document revisions and SHA-256 hashes. Editing invalidates prior approval; stale saves are rejected. Changes requested in natural language wait for an agent; direct edits save immediately.",
  ],
];
document.querySelectorAll("[data-layer]").forEach(
  (b) =>
    (b.onclick = () => {
      const t = texts[Number(b.dataset.layer)];
      $("layer-title").textContent = t[0];
      $("layer-info").textContent = t[1];
    }),
);
function equation() {
  const a = Number($("x1").value),
    b = Number($("x2").value),
    w = Number($("w1").value);
  $("equation").textContent =
    `y = 100 × (${w} × ${a} + 2 × ${b}) / (${w} + 2) = ${((100 * (w * a + 2 * b)) / (w + 2)).toFixed(1)}`;
}
for (const id of ["x1", "x2", "w1"]) $(id).oninput = equation;
equation();
