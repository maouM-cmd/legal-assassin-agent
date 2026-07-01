const badge = document.getElementById("status-badge");
const modeBadge = document.getElementById("mode-badge");
const apiKeyWarning = document.getElementById("api-key-warning");
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
const complianceOverview = document.getElementById("compliance-overview");
const counterNotifications = document.getElementById("counter-notifications");
const legalHolds = document.getElementById("legal-holds");
const settingsDialog = document.getElementById("settings-dialog");
const apiKeyInput = document.getElementById("api-key-input");
const btnSettings = document.getElementById("btn-settings");
const settingsSave = document.getElementById("settings-save");
const settingsClear = document.getElementById("settings-clear");
const settingsClose = document.getElementById("settings-close");

const API_KEY_STORAGE = "legal_assassin_api_key";

let ws;
let apiKeyRequired = false;

function getStoredApiKey() {
  return localStorage.getItem(API_KEY_STORAGE) || "";
}

function setStoredApiKey(value) {
  if (value) {
    localStorage.setItem(API_KEY_STORAGE, value);
  } else {
    localStorage.removeItem(API_KEY_STORAGE);
  }
  updateApiKeyWarning();
}

function updateApiKeyWarning() {
  const missing = apiKeyRequired && !getStoredApiKey();
  apiKeyWarning.classList.toggle("hidden", !missing);
}

function showToast(message, danger = false) {
  const el = document.createElement("div");
  el.className = "toast" + (danger ? " danger" : "");
  el.textContent = message;
  toastContainer.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

async function apiFetch(url, options = {}) {
  const headers = { ...(options.headers || {}) };
  const apiKey = getStoredApiKey();
  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }
  const res = await fetch(url, { ...options, headers });
  if (res.status === 401) {
    showToast("API key required or invalid", true);
  }
  return res;
}

async function refreshHealth() {
  const res = await fetch("/api/health");
  const data = await res.json();
  apiKeyRequired = Boolean(data.api_key_required);
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
  updateApiKeyWarning();
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
    } else if (data.type === "COUNTER_NOTIFICATION" || data.type === "LEGAL_HOLD") {
      refreshCompliance();
      refreshTakedowns();
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
      const res = await apiFetch(`/api/hits/${hitId}/approve`, { method: "POST" });
      if (!res.ok) return;
      showToast("TAKEDOWN SENT");
      refreshAll();
    };
  });
  document.querySelectorAll(".btn-reject").forEach((btn) => {
    btn.onclick = async () => {
      const hitId = btn.dataset.hit;
      const res = await apiFetch(`/api/hits/${hitId}/reject`, { method: "POST" });
      if (!res.ok) return;
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
    const url = td.suspect_url || "";
    const counter = td.counter_notification_status || "none";
    const holdBadge = td.legal_hold ? '<span class="legal-hold-badge">LEGAL HOLD</span> ' : "";
    el.innerHTML = `
      <div class="status-${td.status}">${holdBadge}${(td.status || "").toUpperCase()}</div>
      <div>${td.platform} - ${url}</div>
      <div class="meta">${td.timestamp || ""} | counter: ${counter}</div>
      <div class="btn-row">
        <button class="btn-record-counter" data-url="${encodeURIComponent(url)}">RECORD COUNTER</button>
        <button class="btn-legal-hold" data-url="${encodeURIComponent(url)}" data-hold="true">LEGAL HOLD</button>
        <button class="btn-legal-hold-release" data-url="${encodeURIComponent(url)}" data-hold="false">RELEASE HOLD</button>
      </div>
    `;
    takedownsList.appendChild(el);
  }
  bindTakedownComplianceButtons();
}

function bindTakedownComplianceButtons() {
  document.querySelectorAll(".btn-record-counter").forEach((btn) => {
    btn.onclick = () => recordCounterNotification(decodeURIComponent(btn.dataset.url || ""));
  });
  document.querySelectorAll(".btn-legal-hold, .btn-legal-hold-release").forEach((btn) => {
    btn.onclick = () => setLegalHold(
      decodeURIComponent(btn.dataset.url || ""),
      btn.dataset.hold === "true"
    );
  });
}

async function recordCounterNotification(suspectUrl) {
  if (!suspectUrl) return;
  const status = window.prompt(
    "Counter-notification status: received, under_review, restored, dismissed",
    "received"
  );
  if (!status) return;
  const notes = window.prompt("Notes (optional)", "") || "";
  const res = await apiFetch("/api/compliance/counter-notification", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ suspect_url: suspectUrl, status, notes }),
  });
  if (!res.ok) return;
  showToast("COUNTER-NOTIFICATION RECORDED");
  refreshCompliance();
  refreshTakedowns();
}

async function setLegalHold(suspectUrl, legalHold) {
  if (!suspectUrl) return;
  const notes = window.prompt("Legal hold notes (optional)", "") || "";
  const res = await apiFetch("/api/compliance/legal-hold", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ suspect_url: suspectUrl, legal_hold: legalHold, notes }),
  });
  if (!res.ok) return;
  showToast(legalHold ? "LEGAL HOLD SET" : "LEGAL HOLD RELEASED", true);
  refreshCompliance();
  refreshTakedowns();
}

async function refreshCompliance() {
  const [overviewRes, counterRes, holdsRes] = await Promise.all([
    fetch("/api/compliance/overview"),
    fetch("/api/compliance/counter-notifications"),
    fetch("/api/compliance/legal-holds"),
  ]);
  const overview = await overviewRes.json();
  complianceOverview.textContent =
    `Legal holds: ${overview.legal_holds ?? 0} | Counter received: ${overview.counter_received ?? 0} | Under review: ${overview.under_review ?? 0}`;

  counterNotifications.innerHTML = "";
  const counters = (await counterRes.json()).items || [];
  if (!counters.length) {
    counterNotifications.innerHTML = '<div class="event-item muted">None</div>';
  } else {
    for (const td of counters) {
      const el = document.createElement("div");
      el.className = "event-item";
      el.innerHTML = `
        <div class="status-received">${(td.counter_notification_status || "").toUpperCase()}</div>
        <div>${td.platform || ""} - ${td.suspect_url || ""}</div>
        <div class="meta">${td.counter_notification_notes || td.counter_notification_at || ""}</div>
      `;
      counterNotifications.appendChild(el);
    }
  }

  legalHolds.innerHTML = "";
  const holds = (await holdsRes.json()).items || [];
  if (!holds.length) {
    legalHolds.innerHTML = '<div class="event-item muted">None</div>';
  } else {
    for (const td of holds) {
      const el = document.createElement("div");
      el.className = "event-item";
      el.innerHTML = `
        <div class="legal-hold-badge">LEGAL HOLD</div>
        <div>${td.platform || ""} - ${td.suspect_url || ""}</div>
        <div class="meta">${td.legal_hold_notes || td.timestamp || ""}</div>
      `;
      legalHolds.appendChild(el);
    }
  }
}

async function runPatrol(platform) {
  btnPatrol.disabled = true;
  btnPatrol.textContent = "PATROLLING...";
  try {
    const url = platform ? `/api/patrol/${platform}` : "/api/patrol";
    const res = await apiFetch(url, { method: "POST" });
    if (!res.ok) return;
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
  refreshCompliance();
}

btnPatrol.addEventListener("click", () => runPatrol(null));
btnRetry.addEventListener("click", async () => {
  btnRetry.disabled = true;
  try {
    const res = await apiFetch("/api/takedowns/retry", { method: "POST" });
    if (!res.ok) return;
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

btnSettings.addEventListener("click", () => {
  apiKeyInput.value = getStoredApiKey();
  settingsDialog.showModal();
});
settingsSave.addEventListener("click", () => {
  setStoredApiKey(apiKeyInput.value.trim());
  showToast("API key saved");
  settingsDialog.close();
});
settingsClear.addEventListener("click", () => {
  apiKeyInput.value = "";
  setStoredApiKey("");
  showToast("API key cleared");
});
settingsClose.addEventListener("click", () => settingsDialog.close());

connectWs();
refreshHealth();
refreshAll();
setInterval(refreshStats, 30000);
