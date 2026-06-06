// SystemMonitor frontend logic.
// Talks to the Rust backend through Tauri's global invoke API and renders
// the Resources and Processes views.

const invoke =
  window.__TAURI__ && window.__TAURI__.core
    ? window.__TAURI__.core.invoke
    : null;

// --- Inline Lucide icons (no external assets, no emoji) ---
const LUCIDE = {
  activity:
    '<path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"/>',
  list:
    '<path d="M3 5h.01"/><path d="M3 12h.01"/><path d="M3 19h.01"/><path d="M8 5h13"/><path d="M8 12h13"/><path d="M8 19h13"/>',
  cpu:
    '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/>',
  gpu:
    '<rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/>',
  ram:
    '<path d="M6 19v-3"/><path d="M10 19v-3"/><path d="M14 19v-3"/><path d="M18 19v-3"/><path d="M8 11V9"/><path d="M16 11V9"/><path d="M12 11V9"/><path d="M2 15h20"/><path d="M2 7a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v1.1a2 2 0 0 0 0 3.837V17a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-5.1a2 2 0 0 0 0-3.837Z"/>',
  storage:
    '<line x1="22" x2="2" y1="12" y2="12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/><line x1="6" x2="6.01" y1="16" y2="16"/><line x1="10" x2="10.01" y1="16" y2="16"/>',
  network:
    '<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/>',
  download:
    '<path d="M12 15V3"/><path d="m6 11 6 6 6-6"/><path d="M19 21H5"/>',
  upload:
    '<path d="M12 3v12"/><path d="m6 9 6-6 6 6"/><path d="M19 21H5"/>',
};

function iconSvg(name) {
  return (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" ' +
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" ' +
    'stroke-linejoin="round">' +
    (LUCIDE[name] || "") +
    "</svg>"
  );
}

function mountIcons() {
  document.querySelectorAll("[data-icon]").forEach((el) => {
    el.innerHTML = iconSvg(el.getAttribute("data-icon"));
  });
}

// --- Formatting helpers ---
function formatBytes(bytes) {
  if (!bytes || bytes < 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB", "PB"];
  let value = bytes;
  let i = 0;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i += 1;
  }
  const decimals = value >= 100 || i === 0 ? 0 : 1;
  return value.toFixed(decimals) + " " + units[i];
}

function formatRate(bytesPerSecond) {
  return formatBytes(bytesPerSecond) + "/s";
}

// --- Sparkline charts (canvas) ---
const MAX_POINTS = 60;
const histories = {
  cpu: [],
  net: [],
};

function pushHistory(key, value) {
  const arr = histories[key];
  arr.push(value);
  if (arr.length > MAX_POINTS) arr.shift();
}

function drawSparkline(canvas, data, color, maxOverride) {
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const ratio = window.devicePixelRatio || 1;
  const cssWidth = canvas.clientWidth || canvas.width;
  const cssHeight = canvas.clientHeight || canvas.height;
  if (canvas.width !== cssWidth * ratio || canvas.height !== cssHeight * ratio) {
    canvas.width = cssWidth * ratio;
    canvas.height = cssHeight * ratio;
  }
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.clearRect(0, 0, cssWidth, cssHeight);

  if (data.length < 2) return;

  const max =
    maxOverride !== undefined
      ? maxOverride
      : Math.max(1, ...data) * 1.15;
  const stepX = cssWidth / (MAX_POINTS - 1);
  const offset = MAX_POINTS - data.length;

  const pointX = (i) => (offset + i) * stepX;
  const pointY = (v) => cssHeight - (Math.min(v, max) / max) * cssHeight;

  // Filled area.
  ctx.beginPath();
  ctx.moveTo(pointX(0), cssHeight);
  data.forEach((v, i) => ctx.lineTo(pointX(i), pointY(v)));
  ctx.lineTo(pointX(data.length - 1), cssHeight);
  ctx.closePath();
  ctx.fillStyle = color + "22";
  ctx.fill();

  // Line.
  ctx.beginPath();
  data.forEach((v, i) => {
    const x = pointX(i);
    const y = pointY(v);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.stroke();
}

// --- Resources rendering ---
function renderResources(data) {
  // CPU
  const cpu = data.cpu;
  document.getElementById("cpu-usage").textContent =
    cpu.usage.toFixed(1) + "%";
  document.getElementById("cpu-model").textContent = cpu.model;
  document.getElementById("cpu-vendor").textContent = cpu.vendor || "-- --";
  document.getElementById("cpu-cores").textContent =
    cpu.logical_cores + " logical cores";
  document.getElementById("cpu-phys-cores").textContent =
    (cpu.physical_cores || cpu.logical_cores) + " physical";
  document.getElementById("cpu-freq").textContent =
    cpu.frequency_mhz > 0 ? cpu.frequency_mhz + " MHz" : "-- MHz";
  document.getElementById("cpu-maxfreq").textContent =
    cpu.max_frequency_mhz > 0 ? cpu.max_frequency_mhz + " Max MHz" : "-- Max";
  document.getElementById("cpu-temp").textContent =
    cpu.temperature_c !== undefined ? cpu.temperature_c.toFixed(1) + " °C" : "-- °C";
  pushHistory("cpu", cpu.usage);
  drawSparkline(
    document.getElementById("cpu-chart"),
    histories.cpu,
    "#4f8cff",
    100
  );

  // GPU
  const gpu = data.gpu;
  document.getElementById("gpu-name").textContent = gpu.name;
  document.getElementById("gpu-vendor").textContent = gpu.vendor || "-- --";
  document.getElementById("gpu-vram").textContent =
    gpu.vram_mb > 0 ? gpu.vram_mb + " MB VRAM" : "-- VRAM";
  document.getElementById("gpu-driver").textContent =
    gpu.driver_version || "-- Driver";

  // Memory
  const mem = data.memory;
  document.getElementById("ram-usage").textContent =
    mem.usage.toFixed(1) + "%";
  document.getElementById("ram-bar").style.width =
    Math.min(mem.usage, 100) + "%";
  document.getElementById("ram-used").textContent =
    formatBytes(mem.used) + " / " + formatBytes(mem.total);
  document.getElementById("ram-available").textContent =
    formatBytes(mem.available) + " free";
  document.getElementById("ram-speed").textContent =
    mem.speed_mhz > 0 ? mem.speed_mhz + " MHz" : "-- MHz";
  document.getElementById("ram-type").textContent =
    mem.memory_type || "-- --";

  // Storage
  const diskList = document.getElementById("disk-list");
  diskList.innerHTML = "";
  data.disks.forEach((disk) => {
    const el = document.createElement("div");
    el.className = "disk";
    const label = disk.mount_point || disk.name || "Disk";
    el.innerHTML =
      '<div class="disk-head">' +
      '<span class="disk-name"></span>' +
      '<span class="card-value" style="font-size:14px"></span>' +
      "</div>" +
      '<div class="bar"><div class="bar-fill"></div></div>' +
      '<div class="disk-sub"></div>' +
      '<div class="disk-info"></div>';
    el.querySelector(".disk-name").textContent = label;
    el.querySelector(".card-value").textContent = disk.usage.toFixed(0) + "%";
    el.querySelector(".bar-fill").style.width =
      Math.min(disk.usage, 100) + "%";
    el.querySelector(".disk-sub").textContent =
      formatBytes(disk.used) +
      " / " +
      formatBytes(disk.total) +
      (disk.file_system ? "  ·  " + disk.file_system : "");
    
    const infoStr = 
      (disk.disk_type ? disk.disk_type : "Unknown") + 
      (disk.model ? "  ·  " + disk.model : "");
    el.querySelector(".disk-info").textContent = infoStr;
    
    diskList.appendChild(el);
  });
  if (data.disks.length === 0) {
    diskList.textContent = "No disks detected.";
  }

  // Network: sum rates across interfaces, list active ones.
  let totalDown = 0;
  let totalUp = 0;
  data.networks.forEach((n) => {
    totalDown += n.down_rate;
    totalUp += n.up_rate;
  });
  document.getElementById("net-down").textContent = formatRate(totalDown);
  document.getElementById("net-up").textContent = formatRate(totalUp);
  pushHistory("net", totalDown + totalUp);
  drawSparkline(
    document.getElementById("net-chart"),
    histories.net,
    "#34d399"
  );

  const ifaceList = document.getElementById("iface-list");
  ifaceList.innerHTML = "";
  data.networks
    .filter((n) => n.total_received > 0 || n.total_transmitted > 0)
    .sort((a, b) => b.down_rate + b.up_rate - (a.down_rate + a.up_rate))
    .slice(0, 4)
    .forEach((n) => {
      const row = document.createElement("div");
      row.className = "iface";
      const left = document.createElement("span");
      left.textContent = n.interface;
      const right = document.createElement("span");
      right.textContent =
        formatRate(n.down_rate) + "  /  " + formatRate(n.up_rate);
      row.appendChild(left);
      row.appendChild(right);
      ifaceList.appendChild(row);
    });
}

// --- Processes rendering ---
let lastProcesses = [];
let processRowCache = new Map(); // pid -> tr element

function renderProcesses(list) {
  lastProcesses = list;
  applyProcessFilter();
}

function applyProcessFilter() {
  const filter = document
    .getElementById("proc-filter")
    .value.trim()
    .toLowerCase();
  const body = document.getElementById("proc-body");
  const rows = filter
    ? lastProcesses.filter((p) => p.name.toLowerCase().includes(filter))
    : lastProcesses;

  document.getElementById("proc-count").textContent =
    rows.length + " processes";

  const visiblePids = new Set(rows.map((p) => p.pid));

  // Remove rows for processes no longer visible
  body.querySelectorAll("tr").forEach((tr) => {
    const pid = parseInt(tr.children[0].textContent);
    if (!visiblePids.has(pid)) {
      tr.remove();
      processRowCache.delete(pid);
    }
  });

  // Update or create rows for visible processes
  rows.forEach((p) => {
    let tr = processRowCache.get(p.pid);
    if (!tr) {
      // Create new row
      tr = document.createElement("tr");
      tr.innerHTML =
        '<td class="num"></td><td></td><td class="num"></td>' +
        '<td class="num"></td><td></td>';
      processRowCache.set(p.pid, tr);
      body.appendChild(tr);
    }
    // Update cells
    const cells = tr.children;
    cells[0].textContent = p.pid;
    cells[1].textContent = p.name;
    cells[2].textContent = p.cpu_usage.toFixed(1);
    cells[3].textContent = formatBytes(p.memory);
    cells[4].textContent = p.status;
  });
}

// --- Polling control: only the active view polls ---
let activeView = "resources";
let pollTimer = null;

async function pollOnce() {
  if (!invoke) return;
  try {
    if (activeView === "resources") {
      const data = await invoke("get_resources");
      renderResources(data);
    } else {
      const list = await invoke("get_processes");
      renderProcesses(list);
    }
  } catch (err) {
    console.error("poll failed", err);
  }
}

function startPolling() {
  stopPolling();
  const interval = activeView === "resources" ? 1000 : 2000;
  pollOnce();
  pollTimer = setInterval(pollOnce, interval);
}

function stopPolling() {
  if (pollTimer !== null) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

function switchView(view) {
  activeView = view;
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.getAttribute("data-view") === view);
  });
  document.querySelectorAll(".view").forEach((section) => {
    section.classList.toggle("active", section.id === "view-" + view);
  });
  startPolling();
}

// --- Init ---
window.addEventListener("DOMContentLoaded", () => {
  mountIcons();

  document.getElementById("tabs").addEventListener("click", (e) => {
    const tab = e.target.closest(".tab");
    if (tab) switchView(tab.getAttribute("data-view"));
  });

  document
    .getElementById("proc-filter")
    .addEventListener("input", applyProcessFilter);

  if (!invoke) {
    document.getElementById("cpu-model").textContent =
      "Tauri API unavailable (run with npm run tauri dev).";
  }

  startPolling();
});
