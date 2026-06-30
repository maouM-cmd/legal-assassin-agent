const badge = document.getElementById("status-badge");
const modeBadge = document.getElementById("mode-badge");
const hitsTotal = document.getElementById("hits-total");
const takedownsSubmitted = document.getElementById("takedowns-submitted");
const pendingApproval = document.getElementById("pending-approval");
const refsTotal = document.getElementById("refs-total");
const patrolGrid = document.getElementById("patrol-grid");
const reviewQueue = document.getElementById("review-queue");
const refsList = document.getElementById("refs-list");
const hitsList = document.getElementById("hits-list");
const pendingManual = document.getElementById("pending-manual");
const failedTakedowns = document.getElementById("failed-takedowns");
const btnRetry = document.getElementById("btn-retry");
const takedownsList = document.getElementById("takedowns-list");
const btnPatrol = document.getElementById("btn-patrol");
const toastContainer = document.getElementById("toast-container");
const dmcaDialog = document.getElementById("dmca-dialog");
const dmcaBody = document.getElementById("dmca-body");
const dmcaClose = document.getElementById("dmca-close");
const compareDialog = document.getElementById("compare-dialog");
const compareReference = document.getElementById("compare-reference");
const compareSuspect = document.getElementById("compare-suspect");
const compareClose = document.getElementById("compare-close");
const btnAuditExport = document.getElementById("btn-audit-export");

let ws;

function showToast(message, danger = false) {
  const el = document.createElement("div");
  el.className = "toast" + (danger ? " danger" : "");
  el.textContent = message;
  toastContainer.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

async function refreshHealth() {
  const res = await fetch("/api/health");
  const data = await res.json();
  if (data.demo_mode) {
    modeBadge.textContent = "DEMO MODE";
    modeBadge.className = "badge warn";
  } else {
    modeBadge.textContent = "PRODUCTION";
    modeBadge.className = "badge prod";
  }
  if (data.hybrid_match) {
    modeBadge.textContent += " | kNN";
  }
  if (data.webhook_enabled) {
    modeBadge.textContent += " | Webhook";
  }
  if (data.api_key_required) {
    modeBadge.textContent += " | API Key";
  }
}

function connectWs() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws/events`);

  ws.onopen = () => {
    badge.textContent = "ONLINE";
    badge.className = "badge online";
  };

  ws.onclose = () => {
    badge.textContent = "OFFLINE";
    badge.className = "badge offline";
    setTimeout(connectWs, 3000);
  };

  ws.onmessage = (ev) => {
    const data = JSON.parse(ev.data);
    if (data.type === "TARGET_ACQUIRED") {
      showToast("TARGET ACQUIRED", true);
      refreshAll();
    } else if (data.type === "TAKEDOWN_SENT") {
      showToast("TAKEDOWN SENT");
      refreshAll();
    } else if (data.type === "PENDING_APPROVAL") {
      showToast("PENDING APPROVAL", true);
      refreshReviewQueue();
      refreshStats();
    } else if (data.type === "PENDING_MANUAL") {
      showToast("CAPTCHA - MANUAL REQUIRED", true);
      refreshPendingManual();
    } else if (data.type === "PATROL_COMPLETE") {
      refreshStats();
    }
  };
}

async function refreshStats() {
  const res = await fetch("/api/stats");
  const data = await res.json();
  hitsTotal.textContent = data.hits_total ?? 0;
  takedownsSubmitted.textContent = data.takedowns_submitted ?? 0;
  pendingApproval.textContent = data.pending_approval ?? 0;
  refsTotal.textContent = data.references_total ?? 0;

  patrolGrid.innerHTML = "";
  const patrol = data.patrol || {};
  for (const [platform, info] of Object.entries(patrol)) {
    const card = document.createElement("div");
    card.className = "patrol-card";
    card.innerHTML = `
      <div class="platform">${platform}</div>
      <div class="meta">Last: ${info.last_scan || "-"}</div>
      <div class="meta">Candidates: ${info.candidates ?? 0}</div>
      ${info.error ? `<div class="meta warn-text">${info.error}</div>` : ""}
    `;
    patrolGrid.appendChild(card);
  }
}

async function refreshReviewQueue() {
  const res = await fetch("/api/review-queue");
  const data = await res.json();
  reviewQueue.innerHTML = "";
  const items = data.items || [];
  if (!items.length) {
    reviewQueue.innerHTML = '<div class="event-item muted">No items pending approval</div>';
    return;
  }
  for (const hit of items) {
    const el = document.createElement("div");
    el.className = "event-item queue-item";
    const evasion = (hit.evasion_types || []).join(", ") || "none";
    el.innerHTML = `
      <div><span class="score">${(hit.final_score * 100).toFixed(1)}%</span> - ${hit.reference_title || hit.content_id}</div>
      <div>${hit.platform} - ${hit.suspect_url || ""}</div>
      <div class="evasion">Evasion: ${evasion} | Status: ${hit.status}</div>
      <div class="btn-row">
        <button class="btn-approve" data-hit="${hit.hit_id}">APPROVE & STRIKE</button>
        <button class="btn-reject" data-hit="${hit.hit_id}">REJECT</button>
        <button class="btn-preview" data-hit="${hit.hit_id}">DMCA PREVIEW</button>
        <button class="btn-compare" data-hit="${hit.hit_id}">COMPARE</button>
      </div>
    `;
    reviewQueue.appendChild(el);
  }
  bindQueueButtons();
}

function bindQueueButtons() {
  document.querySelectorAll(".btn-approve").forEach((btn) => {
    btn.onclick = async () => {
      const hitId = btn.dataset.hit;
      await fetch(`/api/hits/${hitId}/approve`, { method: "POST" });
      showToast("TAKEDOWN SENT");
      refreshAll();
    };
  });
  document.querySelectorAll(".btn-reject").forEach((btn) => {
    btn.onclick = async () => {
      const hitId = btn.dataset.hit;
      await fetch(`/api/hits/${hitId}/reject`, { method: "POST" });
      showToast("REJECTED");
      refreshAll();
    };
  });
  document.querySelectorAll(".btn-preview").forEach((btn) => {
    btn.onclick = async () => {
      const hitId = btn.dataset.hit;
      const res = await fetch(`/api/hits/${hitId}/dmca-preview`);
      const data = await res.json();
      dmcaBody.textContent = data.body || "";
      dmcaDialog.showModal();
    };
  });
  document.querySelectorAll(".btn-compare").forEach((btn) => {
    btn.onclick = () => openCompare(btn.dataset.hit);
  });
}

async function openCompare(hitId) {
  const res = await fetch(`/api/hits/${hitId}/thumbnails`);
  if (!res.ok) {
    showToast("THUMBNAILS UNAVAILABLE", true);
    return;
  }
  const data = await res.json();
  compareReference.src = data.reference_thumbnail
    ? `data:image/jpeg;base64,${data.reference_thumbnail}`
    : "";
  compareSuspect.src = data.suspect_thumbnail
    ? `data:image/jpeg;base64,${data.suspect_thumbnail}`
    : "";
  compareReference.alt = data.reference_title || "Reference";
  compareSuspect.alt = "Suspect";
  compareDialog.showModal();
}

async function refreshRefs() {
  const res = await fetch("/api/references");
  const data = await res.json();
  refsList.innerHTML = "";
  for (const ref of data.items || []) {
    const el = document.createElement("div");
    el.className = "event-item";
    el.innerHTML = `
      <div><strong>${ref.title || ref.content_id}</strong></div>
      <div class="meta">${ref.frame_hash_count ?? 0} frame hashes | ${(ref.duration_sec || 0).toFixed(0)}s</div>
    `;
    refsList.appendChild(el);
  }
}

async function refreshHits() {
  const res = await fetch("/api/hits?limit=20");
  const data = await res.json();
  hitsList.innerHTML = "";
  for (const hit of data.items || []) {
    const el = document.createElement("div");
    el.className = "event-item";
    const evasion = (hit.evasion_types || []).join(", ") || "none";
    const badges = (hit.evasion_types || []).map((e) => `<span class="evasion-badge">${e}</span>`).join(" ");
    el.innerHTML = `
      <div><span class="score">${(hit.final_score * 100).toFixed(1)}%</span> - ${hit.reference_title || hit.content_id}</div>
      <div>${hit.platform} - ${hit.suspect_url || ""}</div>
      <div class="evasion">Evasion: ${evasion} ${badges} | ${hit.workflow_status || hit.status}</div>
      <div class="btn-row">
        <button class="btn-compare" data-hit="${hit.hit_id}">COMPARE</button>
      </div>
    `;
    hitsList.appendChild(el);
  }
  document.querySelectorAll("#hits-list .btn-compare").forEach((btn) => {
    btn.onclick = () => openCompare(btn.dataset.hit);
  });
}

async function refreshPendingManual() {
  const res = await fetch("/api/pending-manual");
  const data = await res.json();
  pendingManual.innerHTML = "";
  const items = data.items || [];
  if (!items.length) {
    pendingManual.innerHTML = '<div class="event-item muted">None</div>';
    return;
  }
  for (const td of items) {
    const el = document.createElement("div");
    el.className = "event-item";
    el.innerHTML = `
      <div class="status-pending_manual">MANUAL REQUIRED</div>
      <div>${td.platform} - ${td.suspect_url || ""}</div>
      <div class="meta">${td.reason || "CAPTCHA detected"}</div>
    `;
    pendingManual.appendChild(el);
  }
}

async function refreshFailedTakedowns() {
  const res = await fetch("/api/takedowns?status=failed&limit=20");
  const data = await res.json();
  failedTakedowns.innerHTML = "";
  const items = data.items || [];
  if (!items.length) {
    failedTakedowns.innerHTML = '<div class="event-item muted">None</div>';
    return;
  }
  for (const td of items) {
    const el = document.createElement("div");
    el.className = "event-item";
    el.innerHTML = `
      <div class="status-failed">FAILED (retries: ${td.retry_count || 0})</div>
      <div>${td.platform} - ${td.suspect_url || ""}</div>
      <div class="meta">${td.error || td.timestamp || ""}</div>
    `;
    failedTakedowns.appendChild(el);
  }
}

async function refreshTakedowns() {
  const res = await fetch("/api/takedowns?limit=20");
  const data = await res.json();
  takedownsList.innerHTML = "";
  for (const td of data.items || []) {
    const el = document.createElement("div");
    el.className = "event-item";
    el.innerHTML = `
      <div class="status-${td.status}">${(td.status || "").toUpperCase()}</div>
      <div>${td.platform} - ${td.suspect_url || ""}</div>
      <div class="meta">${td.timestamp || ""}</div>
    `;
    takedownsList.appendChild(el);
  }
}

async function runPatrol(platform) {
  btnPatrol.disabled = true;
  btnPatrol.textContent = "PATROLLING...";
  try {
    const url = platform ? `/api/patrol/${platform}` : "/api/patrol";
    await fetch(url, { method: "POST" });
    showToast("PATROL COMPLETE");
    refreshAll();
  } finally {
    btnPatrol.disabled = false;
    btnPatrol.textContent = "RUN ALL PATROLS";
  }
}

function refreshAll() {
  refreshStats();
  refreshReviewQueue();
  refreshRefs();
  refreshHits();
  refreshPendingManual();
  refreshFailedTakedowns();
  refreshTakedowns();
}

btnPatrol.addEventListener("click", () => runPatrol(null));
btnRetry.addEventListener("click", async () => {
  btnRetry.disabled = true;
  try {
    await fetch("/api/takedowns/retry", { method: "POST" });
    showToast("RETRY COMPLETE");
    refreshAll();
  } finally {
    btnRetry.disabled = false;
  }
});
document.querySelectorAll(".btn-secondary[data-platform]").forEach((btn) => {
  btn.addEventListener("click", () => runPatrol(btn.dataset.platform));
});
dmcaClose.addEventListener("click", () => dmcaDialog.close());
compareClose.addEventListener("click", () => compareDialog.close());
btnAuditExport.addEventListener("click", () => {
  window.location.href = "/api/audit/export";
});

connectWs();
refreshHealth();
refreshAll();
setInterval(refreshStats, 30000);
