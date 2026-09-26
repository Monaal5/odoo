/**
 * StockSense IMS — Dynamic Landing Page Controller (landing.js)
 * Slideshow animations, dynamic dashboard switcher, AI Copilot simulation, and moving buttons.
 */

// Slide Data Collections
const slidesData = [
  {
    tabTitle: "📊 Live Inventory & KPIs",
    badgeText: "● CONNECTED • REAL-TIME TELEMETRY",
    headline: "Consolidated warehouse telemetry, automated stock records metrics, and instantaneous adjustments in one unified view.",
    metrics: [
      { title: "Total Stock Valuation", value: "$4.2M", sub: "+8.4% from last month", deltaColor: "#16A34A" },
      { title: "On-Hand Inventory", value: "1,420 units", sub: "across 3 warehouses", deltaColor: "#5E35B1" },
      { title: "Order Fill Rate", value: "98.2%", sub: "99.8% target threshold", deltaColor: "#16A34A" },
      { title: "Active Alerts", value: "3 items", sub: "require auto-reorder", deltaColor: "#DC2626" }
    ],
    tableRows: [
      { name: "Industrial Steel Rebars", sku: "STL-001", wh: "WH-01 Central", qty: "1,200 pcs", status: "In Stock", statusColor: "badge-done", val: "$48,000" },
      { name: "Titanium Fasteners M8", sku: "BLT-044", wh: "WH-02 North", qty: "450 bxs", status: "Low Stock", statusColor: "badge-waiting", val: "$12,400" },
      { name: "304 Stainless Steel Plates", sku: "ALM-089", wh: "WH-01 Central", qty: "1,800 kg", status: "In Stock", statusColor: "badge-done", val: "$92,500" },
      { name: "Industrial Chemical Solvents", sku: "SOL-102", wh: "WH-03 South", qty: "90 L", status: "Critical", statusColor: "badge-danger", val: "$4,800" }
    ],
    alertBox: {
      title: "AI Reorder Recommendation",
      desc: "Low stock alert: BLT-044 (Titanium Fasteners) below safety threshold. Restock order PO-8821 recommended.",
      btnText: "Generate Purchase Order"
    },
    liveFeed: [
      { icon: "📥", text: "PO-8821 Received (+50 Steel)", time: "2m ago" },
      { icon: "📤", text: "Dispatched SO-4109 to Matrix", time: "8m ago" },
      { icon: "🛡️", text: "Safety Threshold Verified", time: "14m ago" }
    ],
    chartBars: [45, 78, 62, 90, 85, 95, 70]
  },
  {
    tabTitle: "📥 Inbound Intake (Receipts)",
    badgeText: "● DOCK VERIFICATION • LIVE INFLOW",
    headline: "Automated dock intake, supplier consignment verification, and instant inventory credit upon receipt.",
    metrics: [
      { title: "Incoming Intake Scheduled", value: "$1.8M", sub: "14 POs pending intake", deltaColor: "#5E35B1" },
      { title: "Units Scheduled Today", value: "890 units", sub: "92% arrived at dock", deltaColor: "#16A34A" },
      { title: "Intake Accuracy", value: "99.4%", sub: "Zero manual barcode errors", deltaColor: "#16A34A" },
      { title: "Active Receiving Bays", value: "4 bays", sub: "Dock 1, 2, 3 & 4 active", deltaColor: "#F59E0B" }
    ],
    tableRows: [
      { name: "High-Tensile Rebar 12mm", sku: "STL-001", wh: "Dock Bay 2", qty: "+50 pcs", status: "Received", statusColor: "badge-done", val: "$6,200" },
      { name: "Hex Bolts Grade 8.8", sku: "BLT-044", wh: "Dock Bay 1", qty: "+200 bxs", status: "Validated", statusColor: "badge-done", val: "$4,800" },
      { name: "Aluminum 2mm Coils", sku: "ALM-089", wh: "Dock Bay 4", qty: "+35 rolls", status: "In Transit", statusColor: "badge-waiting", val: "$18,500" },
      { name: "Copper Wire Spools 50m", sku: "CPR-012", wh: "Dock Bay 3", qty: "+18 spools", status: "Inspection", statusColor: "badge-waiting", val: "$3,400" }
    ],
    alertBox: {
      title: "Dock Intake Synchronized",
      desc: "Supplier Apex Steel shipment #PO-8821 verified with zero variance against bill of lading.",
      btnText: "Commit Inbound Intake"
    },
    liveFeed: [
      { icon: "🚚", text: "Apex Steel Truck docked at Bay 2", time: "Just now" },
      { icon: "✅", text: "Scan verified 50x Rebar", time: "3m ago" },
      { icon: "📥", text: "PO-8820 validated and closed", time: "18m ago" }
    ],
    chartBars: [60, 85, 70, 95, 65, 80, 88]
  },
  {
    tabTitle: "📤 Outbound Dispatches (Deliveries)",
    badgeText: "● CARRIER DISPATCH • OUTFLOW",
    headline: "Fast pick-and-pack routing, carrier coordination, and automated real-time ledger debiting.",
    metrics: [
      { title: "Dispatched Goods Today", value: "$2.4M", sub: "Fulfilling 28 customer orders", deltaColor: "#16A34A" },
      { title: "Units Dispatched", value: "830 units", sub: "Across 12 carrier routes", deltaColor: "#5E35B1" },
      { title: "On-Time Dispatch Rate", value: "99.8%", sub: "Carrier SLA compliant", deltaColor: "#16A34A" },
      { title: "Pending Orders", value: "4 orders", sub: "Ready for dock pickup", deltaColor: "#F59E0B" }
    ],
    tableRows: [
      { name: "Matrix Infrastructure Delivery", sku: "DEL-101", wh: "Bay 3 (FedEx)", qty: "-10 units", status: "Dispatched", statusColor: "badge-done", val: "$14,000" },
      { name: "Skyline Engineering Dispatch", sku: "DEL-102", wh: "Bay 1 (DHL)", qty: "-15 units", status: "Packed", statusColor: "badge-waiting", val: "$8,500" },
      { name: "Vanguard Heavy Order", sku: "DEL-103", wh: "Bay 2 (Freight)", qty: "-100 units", status: "In Transit", statusColor: "badge-done", val: "$32,000" },
      { name: "Apex Commercial Supply", sku: "DEL-104", wh: "Bay 4 (Local)", qty: "-5 units", status: "Ready", statusColor: "badge-waiting", val: "$2,900" }
    ],
    alertBox: {
      title: "Outbound Order Packaged",
      desc: "Courier Freight-04 departed Central Hub with order DEL-101. Stock Ledger updated instantly.",
      btnText: "Track Real-time Fleet"
    },
    liveFeed: [
      { icon: "🚛", text: "Carrier departed for Matrix Infra", time: "1m ago" },
      { icon: "📦", text: "Packing verified for Skyline Eng", time: "6m ago" },
      { icon: "💨", text: "15 Aluminum sheets debited", time: "12m ago" }
    ],
    chartBars: [75, 60, 85, 70, 90, 85, 98]
  },
  {
    tabTitle: "📜 Stock Ledger & Audit Log",
    badgeText: "● IMMUTABLE AUDIT • ZERO DISCREPANCY",
    headline: "Cryptographically verifiable ledger recording every receipt, transfer, and adjustment with mathematical traceability.",
    metrics: [
      { title: "Audit Verification", value: "100%", sub: "Cryptographic hash verified", deltaColor: "#16A34A" },
      { title: "Logged Transactions", value: "18,420", sub: "Append-only database journal", deltaColor: "#5E35B1" },
      { title: "Audit Discrepancies", value: "0 errors", sub: "Perfect physical reconciliation", deltaColor: "#16A34A" },
      { title: "Query Latency", value: "0.04s", sub: "Real-time ledger audit", deltaColor: "#5E35B1" }
    ],
    tableRows: [
      { name: "Steel Rods PO Receipt", sku: "RCP-001", wh: "WH-01 Central", qty: "+50 units", status: "Committed", statusColor: "badge-done", val: "Delta +50" },
      { name: "Matrix Delivery Order", sku: "DEL-101", wh: "WH-01 Central", qty: "-10 units", status: "Committed", statusColor: "badge-done", val: "Delta -10" },
      { name: "North Yard Inter-Transfer", sku: "TR-001", wh: "WH-02 North", qty: "+25 units", status: "Committed", statusColor: "badge-done", val: "Delta +25" },
      { name: "Physical Cycle Count Reconcile", sku: "ADJ-001", wh: "WH-01 Central", qty: "-2 units", status: "Audited", statusColor: "badge-done", val: "Delta -2" }
    ],
    alertBox: {
      title: "Immutable Ledger Integrity",
      desc: "SHA-256 block chain verified: 0x8f2a...c31b. All transactions comply with SOX & ISO-9001 inventory audits.",
      btnText: "Download Audit Certificate"
    },
    liveFeed: [
      { icon: "🔒", text: "Block #18420 committed to ledger", time: "Just now" },
      { icon: "📜", text: "Physical adjustment verified", time: "5m ago" },
      { icon: "🛡️", text: "Audit report signed off", time: "22m ago" }
    ],
    chartBars: [90, 88, 92, 94, 96, 95, 99]
  }
];

let currentSlideIndex = 0;
let slideInterval = null;
let progressVal = 0;
let progressTimer = null;
const SLIDE_DURATION = 4500; // 4.5 seconds per slide

document.addEventListener("DOMContentLoaded", () => {
  initSlideshow();
  initAIChat();
  initPricingToggle();
  initHeroBarAnimations();
});

/* ── 1. Slideshow & Dynamic Dashboard Controller ────────── */
function initSlideshow() {
  const tabsContainer = document.getElementById("slides-tabs-bar");
  if (!tabsContainer) return;

  // Build tab buttons dynamically
  tabsContainer.innerHTML = slidesData.map((s, idx) => `
    <button type="button" class="slide-tab-btn ${idx === 0 ? 'active' : ''}" data-slide-index="${idx}">
      <span>${s.tabTitle}</span>
    </button>
  `).join('');

  // Event listeners for tabs
  tabsContainer.querySelectorAll(".slide-tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const idx = parseInt(btn.getAttribute("data-slide-index"), 10);
      switchSlide(idx);
    });
  });

  // Start auto-play
  renderSlideContent(0);
  startAutoPlay();

  // Pause on hover over dashboard showcase
  const showcaseBoard = document.getElementById("interactive-showcase-board");
  if (showcaseBoard) {
    showcaseBoard.addEventListener("mouseenter", pauseAutoPlay);
    showcaseBoard.addEventListener("mouseleave", resumeAutoPlay);
  }
}

function switchSlide(index) {
  currentSlideIndex = index;
  
  // Update active tab buttons
  document.querySelectorAll(".slide-tab-btn").forEach((btn, idx) => {
    btn.classList.toggle("active", idx === index);
  });

  renderSlideContent(index);
  resetProgressTimer();
}

function renderSlideContent(index) {
  const data = slidesData[index];
  const board = document.getElementById("interactive-showcase-board");
  if (!board || !data) return;

  // Add subtle fade animation
  board.style.opacity = "0.75";
  board.style.transform = "scale(0.995)";

  setTimeout(() => {
    // 1. Header info
    document.getElementById("showcase-live-badge").textContent = data.badgeText;
    document.getElementById("showcase-headline").textContent = data.headline;

    // 2. Metrics
    const metricsGrid = document.getElementById("showcase-metrics-grid");
    metricsGrid.innerHTML = data.metrics.map(m => `
      <div class="showcase-metric-card">
        <div class="showcase-metric-title">${m.title}</div>
        <div class="showcase-metric-value" style="color:${m.deltaColor};">${m.value}</div>
        <div class="showcase-metric-sub">${m.sub}</div>
      </div>
    `).join('');

    // 3. Table Rows
    const tbody = document.getElementById("showcase-table-body");
    tbody.innerHTML = data.tableRows.map(r => `
      <tr>
        <td><strong>${r.name}</strong><br><span style="font-size:11px; color:var(--text-subtle);">${r.sku}</span></td>
        <td><span style="color:var(--text-muted); font-size:13px;">${r.wh}</span></td>
        <td><strong>${r.qty}</strong></td>
        <td><span class="status-badge ${r.statusColor}">${r.status}</span></td>
        <td><span style="font-weight:700; color:var(--text-main); font-size:13px;">${r.val}</span></td>
      </tr>
    `).join('');

    // 4. Alert Box
    document.getElementById("showcase-alert-title").textContent = data.alertBox.title;
    document.getElementById("showcase-alert-desc").textContent = data.alertBox.desc;
    document.getElementById("showcase-alert-btn").textContent = data.alertBox.btnText;

    // 5. Live Feed
    const feedList = document.getElementById("showcase-live-feed");
    feedList.innerHTML = data.liveFeed.map(f => `
      <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 0; border-bottom:1px solid #F1F5F9; font-size:12.5px;">
        <span style="display:flex; align-items:center; gap:8px;">${f.icon} ${f.text}</span>
        <span style="color:var(--text-subtle); font-size:11px;">${f.time}</span>
      </div>
    `).join('');

    // 6. Update chart bars heights
    const barCols = document.querySelectorAll(".hero-chart-bar");
    barCols.forEach((bar, i) => {
      const h = data.chartBars[i] || 60;
      bar.style.height = `${h}%`;
    });

    board.style.opacity = "1";
    board.style.transform = "scale(1)";
  }, 120);
}

function startAutoPlay() {
  resetProgressTimer();
}

function resetProgressTimer() {
  clearInterval(progressTimer);
  progressVal = 0;
  const progressBar = document.getElementById("slide-progress-bar");
  
  const step = 50; // update every 50ms
  const increment = (step / SLIDE_DURATION) * 100;

  progressTimer = setInterval(() => {
    progressVal += increment;
    if (progressBar) progressBar.style.width = `${Math.min(progressVal, 100)}%`;

    if (progressVal >= 100) {
      clearInterval(progressTimer);
      const nextIndex = (currentSlideIndex + 1) % slidesData.length;
      switchSlide(nextIndex);
    }
  }, step);
}

function pauseAutoPlay() {
  clearInterval(progressTimer);
}

function resumeAutoPlay() {
  resetProgressTimer();
}

/* ── 2. Interactive AI Assistant Copilot ─────────────────── */
function initAIChat() {
  const sendBtn = document.getElementById("ai-chat-send");
  const input = document.getElementById("ai-chat-input");
  const botBubble = document.getElementById("ai-bot-response");

  if (!sendBtn || !input) return;

  function sendQuery(text) {
    if (!text.trim()) return;
    
    // Animate user message
    const userBubble = document.getElementById("ai-user-query");
    if (userBubble) {
      userBubble.textContent = text;
      userBubble.style.opacity = "0.7";
      setTimeout(() => userBubble.style.opacity = "1", 150);
    }

    input.value = "";
    botBubble.innerHTML = `<span style="color:#A855F7;">⚡ StockSense AI thinking...</span>`;

    setTimeout(() => {
      let reply = "";
      const lower = text.toLowerCase();

      if (lower.includes("steel") || lower.includes("rebar")) {
        reply = `<strong>82 Steel Rods Available</strong> (Safe Stock Threshold: 50). Last replenished 2 hours ago from Apex Steel. Consumption velocity: 20 units/week.`;
      } else if (lower.includes("po") || lower.includes("purchase") || lower.includes("order")) {
        reply = `<strong>Purchase Order #PO-8822 Drafted!</strong> Auto-calculated quantity: 50 units for Central Hub (WH-01). Sent to procurement queue for manager approval.`;
      } else if (lower.includes("bolt") || lower.includes("fastener")) {
        reply = `<strong>Hex Bolts M8x40 On-Hand: 450 boxes.</strong> Located in Rack A-2, Bin 14. Stock is healthy and requires no replenishment.`;
      } else {
        reply = `<strong>Analyzed warehouse inventory across 3 depots.</strong> Total 1,420 items on-hand, 98.2% fulfillment rate. All safety levels operational.`;
      }

      botBubble.innerHTML = `
        <div style="font-weight:700; color:#D8B4FE; margin-bottom:4px;">✨ StockSense Intelligence:</div>
        <div>${reply}</div>
      `;
    }, 600);
  }

  sendBtn.addEventListener("click", () => sendQuery(input.value));
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendQuery(input.value);
  });

  // Action chips click
  document.querySelectorAll(".chat-chip-btn").forEach(chip => {
    chip.addEventListener("click", () => {
      sendQuery(chip.textContent.trim());
    });
  });
}

/* ── 3. Pricing Period Toggle ────────────────────────────── */
function initPricingToggle() {
  const monthlyBtn = document.getElementById("pricing-monthly");
  const yearlyBtn = document.getElementById("pricing-yearly");
  const priceBusiness = document.getElementById("price-business-val");
  const periodBusiness = document.getElementById("price-business-period");

  if (!monthlyBtn || !yearlyBtn) return;

  monthlyBtn.addEventListener("click", () => {
    monthlyBtn.classList.add("active");
    yearlyBtn.classList.remove("active");
    if (priceBusiness) priceBusiness.textContent = "$29";
    if (periodBusiness) periodBusiness.textContent = "/ month";
  });

  yearlyBtn.addEventListener("click", () => {
    yearlyBtn.classList.add("active");
    monthlyBtn.classList.remove("active");
    if (priceBusiness) priceBusiness.textContent = "$23";
    if (periodBusiness) periodBusiness.textContent = "/ month (billed annually)";
  });
}

/* ── 4. Hero Live Charts & Floating Animations ───────────── */
function initHeroBarAnimations() {
  setInterval(() => {
    const bars = document.querySelectorAll(".hero-chart-bar-live");
    bars.forEach(b => {
      const currentH = parseInt(b.style.height || "60", 10);
      const randomH = Math.max(30, Math.min(100, currentH + (Math.floor(Math.random() * 20) - 10)));
      b.style.height = `${randomH}%`;
    });
  }, 3000);
}
