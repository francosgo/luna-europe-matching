const $ = (id) => document.getElementById(id);
let state,
  current,
  kind = "cv";
const el = (tag, text, cls) => {
  const e = document.createElement(tag);
  if (text !== undefined) e.textContent = text;
  if (cls) e.className = cls;
  return e;
};
async function api(path, data) {
  const r = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Luna-Token": state.csrf },
    body: JSON.stringify(data),
  });
  const body = await r.json();
  if (!r.ok) throw Error(body.error);
  return body;
}
const safeURL = (url) => {
  try {
    const u = new URL(url);
    return ["http:", "https:"].includes(u.protocol) ? u.href : "#";
  } catch {
    return "#";
  }
};
function render() {
  const term = $("filter").value.toLowerCase();
  $("jobs").replaceChildren();
  for (const job of state.jobs) {
    if (
      !JSON.stringify([job.title, job.company, job.location])
        .toLowerCase()
        .includes(term)
    )
      continue;
    const card = el("article", undefined, "card");
    card.append(
      el("div", job.company, "company"),
      el("h3", job.title),
      el("p", job.location + " · " + job.category),
    );
    const row = el("div", undefined, "row");
    const score = el("div", job.match.score + " ", "score");
    score.append(el("small", "/100 evidence fit"));
    row.append(score, el("span", job.match.eligibility, "tag"));
    card.append(row);
    const bar = el("div", undefined, "bar"),
      fill = el("i");
    fill.style.width = job.match.score + "%";
    bar.append(fill);
    card.append(bar, el("p", job.reason));
    const details = el("details");
    details.append(
      el(
        "summary",
        `Why this score · ${job.match.coverage}% assessed coverage`,
      ),
    );
    const table = el("table");
    for (const r of job.match.requirements) {
      const tr = el("tr"),
        cell = el("td", r.label);
      for (const id of r.evidence_ids || []) {
        const e = state.evidence.find((e) => e.id === id);
        cell.append(el("small", e.text + " — " + e.source));
      }
      tr.append(cell, el("td", r.assessment + (r.hard ? " · required" : "")));
      table.append(tr);
    }
    details.append(
      table,
      el(
        "p",
        "Weights and assessments are human judgments. Unknowns remain visible; scores do not predict offers.",
      ),
    );
    card.append(details);
    const act = el("div", undefined, "actions"),
      review = el("button", "Review application");
    review.onclick = () => openReview(job);
    const link = el("a", "Employer listing ↗");
    link.href = safeURL(job.url);
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    act.append(review, link);
    card.append(act);
    $("jobs").append(card);
  }
}
function openReview(job) {
  current = job;
  kind = "cv";
  $("review").showModal();
  showDocument();
}
function showDocument() {
  const doc = state.documents[current.id + ":" + kind];
  $("doc-title").textContent =
    current.company + " · " + (kind === "cv" ? "CV" : "Motivation letter");
  $("doc-meta").textContent = current.title;
  $("doc-state").textContent =
    `Version ${doc.revision} · ${doc.status} · SHA-256 ${doc.hash.slice(0, 12)}`;
  $("editor").value = doc.body;
  $("facts").checked = false;
  $("edit-panel").hidden = true;
  $("message").textContent = "";
  const paper = $("paper");
  paper.replaceChildren();
  paper.className = "paper " + kind;
  if (kind === "cv") {
    const side = el("aside");
    if (state.portrait) {
      const img = el("img");
      img.src = "/portrait.png";
      img.alt = "Profile portrait";
      side.append(img);
    }
    side.append(
      el(
        "div",
        state.sidebar || "YOUR PROFILE\n\nPrivate, evidence-led applications",
      ),
    );
    paper.append(side, el("div", doc.body, "body"));
  } else paper.textContent = doc.body;
}
async function guarded(fn) {
  try {
    await fn();
  } catch (e) {
    $("message").textContent = e.message;
  }
}
$("close").onclick = () => $("review").close();
$("tab-cv").onclick = () => {
  kind = "cv";
  showDocument();
};
$("tab-letter").onclick = () => {
  kind = "letter";
  showDocument();
};
$("change").onclick = () => {
  $("edit-panel").hidden = false;
  $("editor").focus();
};
$("print").onclick = () => window.print();
$("save").onclick = () =>
  guarded(async () => {
    const id = current.id + ":" + kind;
    state.documents[id] = await api("/api/review", {
      document: id,
      body: $("editor").value,
      revision: state.documents[id].revision,
    });
    showDocument();
    $("message").textContent =
      "Revised draft saved. Check this version, then approve.";
  });
$("approve").onclick = () =>
  guarded(async () => {
    const id = current.id + ":" + kind,
      doc = state.documents[id];
    state.documents[id] = await api("/api/approve", {
      document: id,
      revision: doc.revision,
      hash: doc.hash,
      facts_confirmed: $("facts").checked,
    });
    showDocument();
    $("message").textContent =
      "Approved and saved locally. No application has been submitted.";
  });
$("request").onclick = () =>
  guarded(async () => {
    const id = current.id + ":" + kind;
    await api("/api/request", {
      document: id,
      revision: state.documents[id].revision,
      instruction: $("instruction").value,
    });
    $("message").textContent =
      "Request saved for your agent. Approval is paused until a new revision is saved.";
  });
$("download").onclick = () => {
  const d = state.documents[current.id + ":" + kind],
    url = URL.createObjectURL(new Blob([d.body], { type: "text/plain" })),
    a = el("a");
  a.href = url;
  a.download = current.id + "-" + kind + "-v" + d.revision + ".txt";
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};
$("filter").oninput = render;
$("calculate").onclick = async () => {
  try {
    $("result").textContent = JSON.stringify(
      await api("/api/match", JSON.parse($("payload").value)),
      null,
      2,
    );
  } catch (e) {
    $("result").textContent = e.message;
  }
};
fetch("/api/workspace")
  .then((r) => r.json())
  .then((data) => {
    state = data;
    $("rewrite").hidden = !state.local_model_enabled;
    for (const [value, label] of [
      [state.jobs.length, "roles reviewed"],
      ["You", "make the final decision"],
      ["Local", "personal documents & revisions"],
    ]) {
      const m = el("div", undefined, "metric");
      m.append(el("strong", value), el("span", label));
      $("metrics").append(m);
    }
    for (const w of state.warnings || []) $("warnings").append(el("li", w));
    $("payload").value = JSON.stringify(
      {
        evidence: [
          {
            id: "demo",
            text: "Conducted five user interviews",
            source: "Project notes",
          },
        ],
        requirements: [
          {
            label: "User research",
            weight: 3,
            assessment: "supported",
            evidence_ids: ["demo"],
          },
          {
            label: "Work authorization",
            weight: 1,
            assessment: "unknown",
            hard: true,
          },
        ],
      },
      null,
      2,
    );
    render();
  })
  .catch((e) => {
    $("jobs").textContent = "Could not load workspace: " + e.message;
  });

$("rewrite").onclick = () =>
  guarded(async () => {
    const id = current.id + ":" + kind;
    $("rewrite").disabled = true;
    $("message").textContent = "Revising with your local model…";
    try {
      state.documents[id] = await api("/api/rewrite", {
        document: id,
        revision: state.documents[id].revision,
        instruction: $("instruction").value,
      });
      showDocument();
      $("message").textContent =
        "AI revision saved as a draft. Review every factual claim before approval.";
    } finally {
      $("rewrite").disabled = false;
    }
  });
window.addEventListener("beforeprint", () => {
  document.getElementById("print-sheet")?.remove();
  const sheet = $("paper").cloneNode(true);
  sheet.id = "print-sheet";
  document.body.append(sheet);
});
window.addEventListener("afterprint", () =>
  document.getElementById("print-sheet")?.remove(),
);
