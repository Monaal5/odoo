/**
 * StockSense IMS — Dynamic Landing Page Controller (landing.js)
 * Typewriter headline animation, scroll-reveal image/card occurrences,
 * dynamic slideshow, live inventory event toaster, AI Copilot, and interactive pricing.
 */

// ── 1. Typewriter Animation Engine ────────────────────────
const typewriterPhrases = [
  "Smarter Inventory.",
  "Faster Decisions.",
  "Zero Stock Chaos."
];

let phraseIndex = 0;
let charIndex = 0;
let isDeleting = false;
const TYPE_SPEED = 75;      // Typing speed (ms per char)
const DELETE_SPEED = 38;    // Cutting/deleting speed (ms per char)
const PAUSE_END = 1800;     // Pause after completing phrase
const PAUSE_START = 350;    // Pause before typing next phrase

function initTypewriter() {
  const el = document.getElementById("typewriter-output");
  if (!el) return;

  function typeTick() {
    const currentPhrase = typewriterPhrases[phraseIndex];

    if (isDeleting) {
      // Cutting / Deleting characters
      charIndex--;
      el.textContent = currentPhrase.substring(0, charIndex);
    } else {
      // Typing characters
      charIndex++;
      el.textContent = currentPhrase.substring(0, charIndex);
    }

    let nextDelay = isDeleting ? DELETE_SPEED : TYPE_SPEED;

    if (!isDeleting && charIndex === currentPhrase.length) {
      // Finished typing phrase, hold for a moment
      nextDelay = PAUSE_END;
      isDeleting = true;
    } else if (isDeleting && charIndex === 0) {
      // Finished cutting phrase, move to next phrase
      isDeleting = false;
      phraseIndex = (phraseIndex + 1) % typewriterPhrases.length;
      nextDelay = PAUSE_START;
    }

    setTimeout(typeTick, nextDelay);
  }

  typeTick();
}

// ── 2. Scroll Reveal Animations ("Images and Cards Occurring") ──
function initScrollReveal() {
  const reveals = document.querySelectorAll(".reveal-item, .reveal-left, .reveal-right");
  if (!reveals.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("revealed");
        
        // Trigger count-up animation for numbers if present
        const counter = entry.target.querySelector("[data-count-target]");
        if (counter && !counter.dataset.animated) {
          animateCounter(counter);
        }
      }
    });
  }, {
    threshold: 0.12,
    rootMargin: "0px 0px -40px 0px"
  });

  reveals.forEach(el => observer.observe(el));
}

function animateCounter(el) {
  el.dataset.animated = "true";
  const target = parseFloat(el.getAttribute("data-count-target"));
  const prefix = el.getAttribute("data-prefix") || "";
  const suffix = el.getAttribute("data-suffix") || "";
  const isFloat = target % 1 !== 0;
  
  let current = 0;
  const duration = 1600;
  const stepTime = 30;
  const steps = duration / stepTime;
  const increment = target / steps;

  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      current = target;
      clearInterval(timer);
    }
    el.textContent = prefix + (isFloat ? current.toFixed(1) : Math.round(current).toLocaleString()) + suffix;
  }, stepTime);
}

// ── 3. Live Inventory Event Toaster ("Occurring in Real-Time") ─
const liveEventsPool = [
  { icon: "🟢", text: "PO-8821 verified: +50 Steel Rods received at Bay 2", time: "Just now" },
  { icon: "📦", text: "Dispatch DEL-101: 10 Hex Bolts shipped to Matrix Infra", time: "1m ago" },
  { icon: "🔄", text: "Transfer TR-001 completed: 25 Rebars moved to WH-02", time: "3m ago" },
  { icon: "✨", text: "StockSense Copilot auto-generated Reorder PO #8824", time: "4m ago" },
  { icon: "🛡️", text: "Physical cycle count verified: 100% ledger alignment", time: "6m ago" },
  { icon: "🚚", text: "Consignment delivery from Apex Steel entered intake bay", time: "Just now" }
];

let eventIdx = 0;

function initLiveEventToast() {
  const toast = document.getElementById("live-inventory-toast");
  const msgEl = document.getElementById("live-toast-msg");
  if (!toast || !msgEl) return;

  function showNextEvent() {
    const item = liveEventsPool[eventIdx];
    eventIdx = (eventIdx + 1) % liveEventsPool.length;

    msgEl.innerHTML = `${item.icon} <span>${item.text}</span>`;
    toast.classList.add("show");

    setTimeout(() => {
      toast.classList.remove("show");
    }, 4200);
  }

  // First occurrence after 3 seconds, then every 8.5 seconds
  setTimeout(() => {
    showNextEvent();
    setInterval(showNextEvent, 8500);
  }, 3000);
}

// ── 4. Slideshow & Dynamic Dashboard Controller ───────────
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
let progressVal = 0;
let progressTimer = null;
const SLIDE_DURATION = 4500; // 4.5s per slide

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

  board.style.opacity = "0.7";
  board.style.transform = "scale(0.995)";

  setTimeout(() => {
    document.getElementById("showcase-live-badge").textContent = data.badgeText;
    document.getElementById("showcase-headline").textContent = data.headline;

    const metricsGrid = document.getElementById("showcase-metrics-grid");
    metricsGrid.innerHTML = data.metrics.map(m => `
      <div class="showcase-metric-card">
        <div class="showcase-metric-title">${m.title}</div>
        <div class="showcase-metric-value" style="color:${m.deltaColor};">${m.value}</div>
        <div class="showcase-metric-sub">${m.sub}</div>
      </div>
    `).join('');

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

    document.getElementById("showcase-alert-title").textContent = data.alertBox.title;
    document.getElementById("showcase-alert-desc").textContent = data.alertBox.desc;
    document.getElementById("showcase-alert-btn").textContent = data.alertBox.btnText;

    const feedList = document.getElementById("showcase-live-feed");
    feedList.innerHTML = data.liveFeed.map(f => `
      <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 0; border-bottom:1px solid #F1F5F9; font-size:12.5px;">
        <span style="display:flex; align-items:center; gap:8px;">${f.icon} ${f.text}</span>
        <span style="color:var(--text-subtle); font-size:11px;">${f.time}</span>
      </div>
    `).join('');

    const barCols = document.querySelectorAll(".hero-chart-bar-live");
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
  
  const step = 50;
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

// ── 5. Interactive AI Assistant Copilot ───────────────────
function initAIChat() {
  const sendBtn = document.getElementById("ai-chat-send");
  const input = document.getElementById("ai-chat-input");
  const botBubble = document.getElementById("ai-bot-response");

  if (!sendBtn || !input) return;

  async function sendQuery(text) {
    if (!text.trim()) return;
    
    const userBubble = document.getElementById("ai-user-query");
    if (userBubble) {
      userBubble.textContent = text;
      userBubble.style.opacity = "0.7";
      setTimeout(() => userBubble.style.opacity = "1", 150);
    }

    input.value = "";
    botBubble.innerHTML = `<span style="color:#A855F7;">⚡ StockSense AI computing answer...</span>`;

    try {
      const res = await api("/ai/chat", {
        method: "POST",
        body: { query: text }
      });
      const answer = (res && res.answer) ? res.answer : "Analyzed inventory telemetry. All current stock bins are within safe operational thresholds.";
      botBubble.innerHTML = `
        <div style="font-weight:700; color:#D8B4FE; margin-bottom:4px;">✨ StockSense Intelligence:</div>
        <div>${answer}</div>
      `;
    } catch (err) {
      botBubble.innerHTML = `
        <div style="font-weight:700; color:#D8B4FE; margin-bottom:4px;">✨ StockSense Intelligence:</div>
        <div>Analyzed warehouse telemetry. Total 1,420 items on-hand, 98.2% fulfillment rate. All safety levels operational.</div>
      `;
    }
  }

  sendBtn.addEventListener("click", () => sendQuery(input.value));
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendQuery(input.value);
  });

  document.querySelectorAll(".chat-chip-btn").forEach(chip => {
    chip.addEventListener("click", () => {
      sendQuery(chip.textContent.trim());
    });
  });
}

// ── 6. Pricing Period Toggle ──────────────────────────────
function initPricingToggle() {
  const monthlyBtn = document.getElementById("pricing-monthly");
  const yearlyBtn = document.getElementById("pricing-yearly");
  const priceBusiness = document.getElementById("price-business-val");
  const periodBusiness = document.getElementById("price-business-period");

  if (!monthlyBtn || !yearlyBtn) return;

  monthlyBtn.addEventListener("click", () => {
    monthlyBtn.classList.add("active");
    yearlyBtn.classList.remove("active");
    if (priceBusiness) priceBusiness.textContent = "₹2,499";
    if (periodBusiness) periodBusiness.textContent = "/ month";
  });

  yearlyBtn.addEventListener("click", () => {
    yearlyBtn.classList.add("active");
    monthlyBtn.classList.remove("active");
    if (priceBusiness) priceBusiness.textContent = "₹1,999";
    if (periodBusiness) periodBusiness.textContent = "/ month (billed annually, save 20%)";
  });
}

// ── 7. Hero Live Bar Fluctuations ─────────────────────────
function initHeroBarAnimations() {
  setInterval(() => {
    const bars = document.querySelectorAll(".hero-chart-bar-live");
    bars.forEach(b => {
      const currentH = parseInt(b.style.height || "60", 10);
      const randomH = Math.max(30, Math.min(100, currentH + (Math.floor(Math.random() * 24) - 12)));
      b.style.height = `${randomH}%`;
    });
  }, 2800);
}

// ── 8. Background Ambient Video Auto-Play Safeguard ───────
function initBackgroundVideo() {
  const bgVideo = document.querySelector(".landing-video-bg");
  if (!bgVideo) return;
  bgVideo.muted = true;
  bgVideo.defaultMuted = true;
  bgVideo.playsInline = true;

  const startPlay = () => {
    const playPromise = bgVideo.play();
    if (playPromise !== undefined) {
      playPromise.catch(() => {
        const playOnUserGesture = () => {
          bgVideo.play();
          window.removeEventListener("scroll", playOnUserGesture);
          window.removeEventListener("click", playOnUserGesture);
          window.removeEventListener("touchstart", playOnUserGesture);
        };
        window.addEventListener("scroll", playOnUserGesture, { once: true, passive: true });
        window.addEventListener("click", playOnUserGesture, { once: true });
        window.addEventListener("touchstart", playOnUserGesture, { once: true, passive: true });
      });
    }
  };

  if (bgVideo.readyState >= 2) {
    startPlay();
  } else {
    bgVideo.addEventListener("loadeddata", startPlay, { once: true });
    startPlay();
  }
}

// ── Initialize All Capabilities on Load ───────────────────
document.addEventListener("DOMContentLoaded", () => {
  initBackgroundVideo();
  initTypewriter();
  initScrollReveal();
  initLiveEventToast();
  initSlideshow();
  initAIChat();
  initPricingToggle();
  initHeroBarAnimations();
});
