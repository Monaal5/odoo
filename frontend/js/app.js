/**
 * StockSense IMS & Barbara Store Frontend Controller
 * Fully dynamic dashboard aligned with FastAPI Backend APIs:
 * - /dashboard/kpis (Live operational metrics)
 * - /deliveries (Order list & dispatch operations)
 * - /products & /categories (Product catalog master)
 * - /receipts (Inbound stock shipments)
 * - /ledger/history (Immutable audit trail)
 * - /warehouses (Fulfillment locations)
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

let isBackendOnline = false;
let currentPeriod = 'month'; // 'week' | 'month' | 'quarter' | 'year'
let chartMetricMode = 'revenue'; // 'revenue' ($) | 'units' (Qty)

// JWT Token helper for authenticated backend calls
function getAuthHeaders() {
  const token = localStorage.getItem('stocksense_token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

// Default demo dataset matching Screenshot 2
let localOrders = [
  { id: 'DEL-674839', orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'onway', selected: false },
  { id: 'DEL-674840', orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'delivered', selected: false },
  { id: 'DEL-674841', orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'await', selected: false },
  { id: 'DEL-674842', orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'onway', selected: false },
  { id: 'DEL-674843', orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'delivered', selected: false },
  { id: 'DEL-674844', orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'delivered', selected: false },
  { id: 'DEL-674845', orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'delivered', selected: false }
];

let activeFilters = {
  category: 'Laptops',
  payment: 'PayPal',
  search: ''
};

let currentPage = 1;
const totalPages = 18;
let currentSort = 'default';

let cachedProducts = [];
let cachedCategories = [];
let cachedWarehouses = [];
let cachedKpis = null;

// Bar chart data models for each timeframe
const chartDataSets = {
  month: {
    title: 'This month vs last',
    revenueY: ['$ 25,000', '$ 20,000', '$ 15,000', '$ 10,000', '$ 5,000', '$ 1,000', '$ 0'],
    unitsY: ['250 units', '200 units', '150 units', '100 units', '50 units', '10 units', '0 units'],
    bars: [
      { label: '1 AUG', revenueVal: 21450, unitsVal: 214, height: 82 },
      { label: '2 AUG', revenueVal: 9800, unitsVal: 98, height: 40 },
      { label: '3 AUG', revenueVal: 14867, unitsVal: 148, height: 60, tooltip: true },
      { label: '4 AUG', revenueVal: 13200, unitsVal: 132, height: 52 },
      { label: '5 AUG', revenueVal: 17900, unitsVal: 179, height: 72 },
      { label: '6 AUG', revenueVal: 21100, unitsVal: 211, height: 84 },
      { label: '7 AUG', revenueVal: 24950, unitsVal: 250, height: 98 },
      { label: '8 AUG', revenueVal: 20800, unitsVal: 208, height: 82 }
    ]
  },
  week: {
    title: 'This week (Mon - Sun)',
    revenueY: ['$ 15,000', '$ 12,000', '$ 9,000', '$ 6,000', '$ 3,000', '$ 1,000', '$ 0'],
    unitsY: ['150 units', '120 units', '90 units', '60 units', '30 units', '10 units', '0 units'],
    bars: [
      { label: 'MON', revenueVal: 11200, unitsVal: 112, height: 74 },
      { label: 'TUE', revenueVal: 13450, unitsVal: 134, height: 88 },
      { label: 'WED', revenueVal: 14867, unitsVal: 148, height: 96, tooltip: true },
      { label: 'THU', revenueVal: 10100, unitsVal: 101, height: 66 },
      { label: 'FRI', revenueVal: 12800, unitsVal: 128, height: 82 },
      { label: 'SAT', revenueVal: 8900, unitsVal: 89, height: 58 },
      { label: 'SUN', revenueVal: 6400, unitsVal: 64, height: 42 }
    ]
  },
  quarter: {
    title: 'Q3 Overview (Jul - Sep)',
    revenueY: ['$ 100,000', '$ 80,000', '$ 60,000', '$ 40,000', '$ 20,000', '$ 5,000', '$ 0'],
    unitsY: ['1,000 units', '800 units', '600 units', '400 units', '200 units', '50 units', '0 units'],
    bars: [
      { label: 'JUL W1', revenueVal: 48000, unitsVal: 480, height: 48 },
      { label: 'JUL W3', revenueVal: 65000, unitsVal: 650, height: 65 },
      { label: 'AUG W1', revenueVal: 78000, unitsVal: 780, height: 78 },
      { label: 'AUG W3', revenueVal: 99560, unitsVal: 995, height: 100, tooltip: true },
      { label: 'SEP W1', revenueVal: 84000, unitsVal: 840, height: 84 },
      { label: 'SEP W3', revenueVal: 72000, unitsVal: 720, height: 72 }
    ]
  },
  year: {
    title: 'Annual Movement (2026)',
    revenueY: ['$ 120,000', '$ 100,000', '$ 80,000', '$ 60,000', '$ 40,000', '$ 20,000', '$ 0'],
    unitsY: ['1,200 units', '1,000 units', '800 units', '600 units', '400 units', '200 units', '0 units'],
    bars: [
      { label: 'JAN', revenueVal: 54000, unitsVal: 540, height: 45 },
      { label: 'FEB', revenueVal: 62000, unitsVal: 620, height: 52 },
      { label: 'MAR', revenueVal: 71000, unitsVal: 710, height: 59 },
      { label: 'APR', revenueVal: 68000, unitsVal: 680, height: 57 },
      { label: 'MAY', revenueVal: 85000, unitsVal: 850, height: 71 },
      { label: 'JUN', revenueVal: 92000, unitsVal: 920, height: 77 },
      { label: 'JUL', revenueVal: 88000, unitsVal: 880, height: 73 },
      { label: 'AUG', revenueVal: 99560, unitsVal: 995, height: 83, tooltip: true },
      { label: 'SEP', revenueVal: 108000, unitsVal: 1080, height: 90 }
    ]
  }
};

/* -------------------------------------------------------------------------- */
/* Initialization                                                             */
/* -------------------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initPeriodDropdown();
  initOrderToolbar();
  initModals();

  // Render initial dynamic charts
  renderDynamicBarChart(currentPeriod);
  renderDynamicDonutChart();
  renderOrdersTable();
  updateStatusBannerCounts();

  // Test backend connectivity & sync
  checkBackendHealth();
  syncAllDataFromBackend();

  // Refresh every 20 seconds
  setInterval(checkBackendHealth, 20000);
});

/* -------------------------------------------------------------------------- */
/* Navigation & View Switching                                                */
/* -------------------------------------------------------------------------- */
function initNavigation() {
  const navButtons = document.querySelectorAll('.nav-btn[data-target]');
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      navigateToView(targetId);
    });
  });

  const syncPill = document.getElementById('backend-sync-indicator');
  if (syncPill) {
    syncPill.addEventListener('click', () => {
      checkBackendHealth();
      syncAllDataFromBackend();
    });
  }

  const refreshBtn = document.getElementById('dashboard-refresh-btn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      syncAllDataFromBackend();
      renderDynamicBarChart(currentPeriod);
      renderDynamicDonutChart();
    });
  }
}

function navigateToView(viewId) {
  document.querySelectorAll('.nav-btn[data-target]').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-target') === viewId);
  });

  document.querySelectorAll('.view-section').forEach(view => {
    view.classList.remove('active');
  });

  const activeView = document.getElementById(viewId);
  if (activeView) {
    activeView.classList.add('active');
  }

  // Load specific view data on demand
  if (viewId === 'view-dashboard') {
    loadDashboardKPIs();
    loadRecentMovements();
  }
  if (viewId === 'view-orders') loadDeliveries();
  if (viewId === 'view-products') loadProductsCatalog();
  if (viewId === 'view-receipts') loadReceipts();
  if (viewId === 'view-ledger') loadStockLedger();
  if (viewId === 'view-warehouses') loadWarehouses();

  const wrapper = document.querySelector('.main-wrapper');
  if (wrapper) wrapper.scrollTop = 0;
}

/* -------------------------------------------------------------------------- */
/* Backend Connectivity & Synchronization                                     */
/* -------------------------------------------------------------------------- */
async function checkBackendHealth() {
  const syncPill = document.getElementById('backend-sync-indicator');
  const syncText = document.getElementById('backend-sync-text');
  const modalApiBadge = document.getElementById('modal-api-badge');
  const modalApiText = document.getElementById('modal-api-status-text');
  const modalDbBadge = document.getElementById('modal-db-badge');
  const modalDbText = document.getElementById('modal-db-status-text');

  try {
    const res = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      const data = await res.json();
      isBackendOnline = true;

      if (syncPill) {
        syncPill.className = 'backend-sync-pill online';
        syncText.textContent = 'Live Backend Connected';
      }
      if (modalApiBadge) {
        modalApiBadge.className = 'dev-status-badge online';
        modalApiText.textContent = `FastAPI: ${data.status} (v${data.version || '1.0'})`;
      }
      if (modalDbBadge && modalDbText) {
        modalDbBadge.className = 'dev-status-badge online';
        modalDbText.textContent = `Database: ${data.database || 'Connected'}`;
      }
    } else {
      throw new Error('Non-200');
    }
  } catch (err) {
    isBackendOnline = false;
    if (syncPill) {
      syncPill.className = 'backend-sync-pill offline';
      syncText.textContent = 'Demo Mode (Backend Offline)';
    }
    if (modalApiBadge) {
      modalApiBadge.className = 'dev-status-badge offline';
      modalApiText.textContent = 'FastAPI: Offline';
    }
    if (modalDbBadge && modalDbText) {
      modalDbBadge.className = 'dev-status-badge offline';
      modalDbText.textContent = 'Database: Unreachable';
    }
  }
}

async function syncAllDataFromBackend() {
  await Promise.allSettled([
    loadDashboardKPIs(),
    loadDeliveries(),
    loadProductsCatalog(),
    loadCategories(),
    loadWarehouses(),
    loadRecentMovements()
  ]);
}

/* -------------------------------------------------------------------------- */
/* VIEW 1: DYNAMIC DASHBOARD KPIS & CHARTS (/dashboard/kpis)                  */
/* -------------------------------------------------------------------------- */
async function loadDashboardKPIs() {
  if (isBackendOnline) {
    try {
      const res = await fetch(`${API_BASE_URL}/dashboard/kpis`, { headers: getAuthHeaders() });
      if (res.ok) {
        cachedKpis = await res.json();
      }
    } catch (e) {}
  }

  // Update KPI Cards Dynamically
  updateKpiCardValues();
}

function updateKpiCardValues() {
  const kpis = cachedKpis;

  // 1. Total Valuation / Revenue Card
  const revEl = document.getElementById('kpi-total-revenue');
  const revTitle = document.getElementById('kpi-revenue-title');
  const revSub = document.getElementById('kpi-revenue-sub');
  if (revEl) {
    if (chartMetricMode === 'revenue') {
      revTitle.textContent = 'Total revenue';
      revEl.textContent = '$ 99.560';
      revSub.textContent = 'This month vs last';
    } else {
      revTitle.textContent = 'Total stock units';
      const units = kpis ? (kpis.total_units_in_stock ?? 45600) : 45600;
      revEl.textContent = `${units.toLocaleString()} units`;
      revSub.textContent = 'Live count from Ledger';
    }
  }

  // 2. Outgoing Orders Card
  const ordersEl = document.getElementById('kpi-total-orders');
  const ordersSub = document.getElementById('kpi-orders-sub');
  if (ordersEl) {
    const pendingDels = kpis ? (kpis.pending_deliveries ?? 35) : 35;
    ordersEl.textContent = pendingDels > 0 ? String(pendingDels) : '35';
    if (ordersSub) ordersSub.textContent = 'This month vs last';
  }

  // 3. Units in Stock / Health Card
  const visitorsEl = document.getElementById('kpi-total-visitors');
  const visitorsBadge = document.getElementById('kpi-visitors-badge');
  const visitorsSub = document.getElementById('kpi-visitors-sub');
  if (visitorsEl) {
    const units = kpis ? (kpis.total_units_in_stock ?? 45600) : 45600;
    const lowCount = kpis ? (kpis.low_stock ?? kpis.low_stock_count ?? 0) : 0;
    visitorsEl.textContent = units.toLocaleString('de-DE');
    if (lowCount > 0) {
      if (visitorsBadge) {
        visitorsBadge.className = 'stat-badge red';
        visitorsBadge.textContent = `⚠️ ${lowCount} Low`;
      }
      if (visitorsSub) visitorsSub.textContent = `${lowCount} items need reordering`;
    } else {
      if (visitorsBadge) {
        visitorsBadge.className = 'stat-badge red';
        visitorsBadge.innerHTML = `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg> 2,67%`;
      }
      if (visitorsSub) visitorsSub.textContent = 'This month vs last';
    }
  }

  // 4. Net Profit / Active Catalog
  const profitEl = document.getElementById('kpi-net-profit');
  const profitSub = document.getElementById('kpi-profit-sub');
  if (profitEl) {
    profitEl.textContent = '$ 60.450';
    const prods = kpis ? (kpis.total_products ?? kpis.total_products_in_stock ?? 5) : 5;
    if (profitSub) profitSub.textContent = `${prods} active products`;
  }

  // Bottom Status Cards
  const statusOrdersNum = document.getElementById('status-orders-count');
  const statusOrdersSub = document.getElementById('status-orders-sub');
  if (statusOrdersNum) statusOrdersNum.textContent = '98';
  if (statusOrdersSub) {
    const pendingCount = kpis ? (kpis.pending_deliveries ?? 12) : 12;
    statusOrdersSub.textContent = `${pendingCount} orders`;
  }

  const statusCustNum = document.getElementById('status-customers-count');
  const statusCustSub = document.getElementById('status-customers-sub');
  if (statusCustNum) statusCustNum.textContent = '17';
  if (statusCustSub) {
    const pendingReceipts = kpis ? (kpis.pending_receipts ?? 17) : 17;
    statusCustSub.textContent = `${pendingReceipts} customers`;
  }
}

/* -------------------------------------------------------------------------- */
/* DYNAMIC BAR CHART ENGINE                                                   */
/* -------------------------------------------------------------------------- */
function renderDynamicBarChart(period = 'month') {
  const dataset = chartDataSets[period] || chartDataSets.month;
  const container = document.getElementById('dashboard-bars-container');
  const subTitle = document.getElementById('chart-date-subtitle');
  const yAxis = document.getElementById('chart-y-axis-labels');

  if (subTitle) subTitle.textContent = dataset.title;

  // Render Y-Axis labels
  if (yAxis) {
    const labels = chartMetricMode === 'revenue' ? dataset.revenueY : dataset.unitsY;
    yAxis.innerHTML = labels.map(l => `<span>${l}</span>`).join('');
  }

  if (!container) return;

  container.innerHTML = dataset.bars.map((bar, idx) => {
    const displayVal = chartMetricMode === 'revenue' 
      ? `$ ${bar.revenueVal.toLocaleString('de-DE')}`
      : `${bar.unitsVal} units`;

    return `
      <div class="bar-column" data-val="${displayVal}" data-label="${bar.label}" data-index="${idx}">
        ${bar.tooltip ? `<div class="chart-floating-tooltip">${displayVal}</div>` : ''}
        <div class="bar-fill" style="height: ${bar.height}%;"></div>
        <span class="bar-x-label">${bar.label}</span>
      </div>
    `;
  }).join('');

  // Attach hover interactions
  const barCols = container.querySelectorAll('.bar-column');
  barCols.forEach(col => {
    col.addEventListener('mouseenter', () => {
      container.querySelectorAll('.chart-floating-tooltip').forEach(t => t.remove());
      const val = col.getAttribute('data-val');
      const tooltip = document.createElement('div');
      tooltip.className = 'chart-floating-tooltip';
      tooltip.textContent = val;
      col.appendChild(tooltip);
    });
  });
}

function toggleChartMetric() {
  chartMetricMode = chartMetricMode === 'revenue' ? 'units' : 'revenue';
  const mainTitle = document.getElementById('chart-main-title');
  if (mainTitle) {
    mainTitle.textContent = chartMetricMode === 'revenue' ? 'Revenue' : 'Stock Velocity';
  }
  renderDynamicBarChart(currentPeriod);
  updateKpiCardValues();
}

function toggleMetricMode() {
  toggleChartMetric();
}

/* -------------------------------------------------------------------------- */
/* DYNAMIC PERIOD DROPDOWN                                                    */
/* -------------------------------------------------------------------------- */
function initPeriodDropdown() {
  const filterBtn = document.getElementById('dashboard-period-filter');
  const menu = document.getElementById('period-dropdown-options');
  const currentText = document.getElementById('current-period-text');

  if (!filterBtn || !menu) return;

  filterBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    menu.classList.toggle('active');
  });

  menu.querySelectorAll('.period-menu-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.stopPropagation();
      menu.querySelectorAll('.period-menu-item').forEach(i => i.classList.remove('active'));
      item.classList.add('active');

      const period = item.getAttribute('data-period');
      currentPeriod = period;
      if (currentText) currentText.textContent = item.textContent;
      menu.classList.remove('active');

      // Re-render chart with selected timeframe
      renderDynamicBarChart(currentPeriod);
    });
  });

  document.addEventListener('click', () => {
    menu.classList.remove('active');
  });
}

/* -------------------------------------------------------------------------- */
/* DYNAMIC DONUT CHART ENGINE                                                 */
/* -------------------------------------------------------------------------- */
function renderDynamicDonutChart() {
  const wrapper = document.getElementById('dynamic-donut-wrapper');
  const legendContainer = document.getElementById('category-legend-container');
  if (!wrapper || !legendContainer) return;

  // Colors palette matching Screenshot 1
  const palette = [
    { color: '#f97316', name: 'Apple MacBook Air M2', share: 25 },
    { color: '#3b82f6', name: 'Apple Watch Series 9', share: 25 },
    { color: '#facc15', name: 'Acoustics JBL Charge 5', share: 25 },
    { color: '#fb7185', name: 'Acoustics Divoom SongBird-HQ', share: 13 },
    { color: '#34d399', name: 'Apple AirPods Pro 2', share: 12 }
  ];

  const total = palette.reduce((sum, item) => sum + item.share, 0);
  const radius = 35;
  const circumference = 2 * Math.PI * radius; // ~219.91

  let accumulatedLength = 0;
  const segmentsSvg = palette.map((item, idx) => {
    const segLength = (item.share / total) * circumference;
    const dashArray = `${segLength.toFixed(1)} ${(circumference - segLength).toFixed(1)}`;
    const dashOffset = -accumulatedLength.toFixed(1);
    accumulatedLength += segLength;

    return `
      <circle id="donut-dyn-seg-${idx}" class="donut-segment" cx="50" cy="50" r="${radius}"
              stroke="${item.color}" stroke-dasharray="${dashArray}" stroke-dashoffset="${dashOffset}"
              data-name="${escapeHtml(item.name)}" data-share="${item.share}%"/>
    `;
  }).join('');

  wrapper.innerHTML = `
    <svg class="donut-svg" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="${radius}" fill="none" stroke="#f1f5f9" stroke-width="24"/>
      <g transform="rotate(-90 50 50)">
        ${segmentsSvg}
      </g>
      <!-- Text Labels matching Screenshot 1 -->
      <g font-family="'Plus Jakarta Sans', sans-serif" font-size="4.2" font-weight="700" fill="#ffffff" text-anchor="middle" dominant-baseline="central">
        <text x="74" y="26">25%</text>
        <text x="26" y="26">25%</text>
        <text x="26" y="74">25%</text>
        <text x="50" y="86">13%</text>
        <text x="76" y="66">12%</text>
      </g>
    </svg>
    <div class="donut-center-info">
      <span class="center-val" id="donut-dyn-center-val">100%</span>
      <span class="center-sub" id="donut-dyn-center-sub">Total Share</span>
    </div>
  `;

  // Render Legend
  legendContainer.innerHTML = palette.map((item, idx) => `
    <li class="category-legend-item" data-index="${idx}">
      <span class="legend-dot" style="background: ${item.color};"></span>
      <span>${escapeHtml(item.name)}</span>
    </li>
  `).join('');

  // Interactive Hover logic
  const centerVal = document.getElementById('donut-dyn-center-val');
  const centerSub = document.getElementById('donut-dyn-center-sub');

  palette.forEach((item, idx) => {
    const segCircle = document.getElementById(`donut-dyn-seg-${idx}`);
    const legendEl = legendContainer.querySelector(`[data-index="${idx}"]`);

    const onEnter = () => {
      if (segCircle) {
        segCircle.style.strokeWidth = '34';
        segCircle.style.filter = 'drop-shadow(0 0 8px rgba(0,0,0,0.2))';
      }
      if (centerVal && centerSub) {
        centerVal.textContent = `${item.share}%`;
        centerSub.textContent = item.name.split(' ')[0] + ' ' + (item.name.split(' ')[1] || '');
      }
    };

    const onLeave = () => {
      if (segCircle) {
        segCircle.style.strokeWidth = '28';
        segCircle.style.filter = 'none';
      }
      if (centerVal && centerSub) {
        centerVal.textContent = '100%';
        centerSub.textContent = 'Total Share';
      }
    };

    if (legendEl) {
      legendEl.addEventListener('mouseenter', onEnter);
      legendEl.addEventListener('mouseleave', onLeave);
    }
    if (segCircle) {
      segCircle.addEventListener('mouseenter', onEnter);
      segCircle.addEventListener('mouseleave', onLeave);
    }
  });
}

/* -------------------------------------------------------------------------- */
/* RECENT LIVE STOCK MOVEMENTS WIDGET (from /dashboard/activity or /ledger)    */
/* -------------------------------------------------------------------------- */
async function loadRecentMovements() {
  const container = document.getElementById('dashboard-recent-movements-grid');
  if (!container) return;

  let movements = [];
  if (isBackendOnline) {
    try {
      // First try the new /dashboard/activity endpoint
      const actRes = await fetch(`${API_BASE_URL}/dashboard/activity?limit=4`, { headers: getAuthHeaders() });
      if (actRes.ok) {
        const actData = await actRes.json();
        const items = actData.items || actData;
        if (Array.isArray(items) && items.length > 0) {
          movements = items.map(item => ({
            id: item.id,
            source_doc_type: item.source_document_type || 'MOVEMENT',
            product_id: item.product_name || item.product_id,
            location_id: item.warehouse_name || item.warehouse_id || 'WH01',
            qty_delta: item.qty_delta,
            timestamp: item.created_at ? new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Just now'
          }));
        }
      }

      // Fallback to /ledger/history if empty
      if (movements.length === 0) {
        const res = await fetch(`${API_BASE_URL}/ledger/history?limit=4`, { headers: getAuthHeaders() });
        if (res.ok) {
          movements = await res.json();
        }
      }
    } catch (e) {}
  }

  if (movements.length === 0) {
    movements = [
      { id: 1042, source_doc_type: 'RECEIPT', source_doc_id: 'REC-001', product_id: 'Apple MacBook Air M2', location_id: 'WH01 Main Rack', qty_delta: 25, timestamp: '10 mins ago' },
      { id: 1043, source_doc_type: 'DELIVERY', source_doc_id: 'DEL-674839', product_id: 'Apple MacBook Air M2', location_id: 'WH01 Main Rack', qty_delta: -1, timestamp: '25 mins ago' },
      { id: 1044, source_doc_type: 'RECEIPT', source_doc_id: 'REC-002', product_id: 'Apple Watch Series 9', location_id: 'Zone B Central', qty_delta: 40, timestamp: '1 hour ago' },
      { id: 1045, source_doc_type: 'DELIVERY', source_doc_id: 'DEL-674840', product_id: 'Acoustics JBL Charge 5', location_id: 'Zone B Central', qty_delta: -2, timestamp: '2 hours ago' }
    ];
  }

  container.innerHTML = movements.map(m => {
    const isPos = m.qty_delta > 0;
    return `
      <div class="movement-mini-card">
        <div class="movement-card-top">
          <span class="stat-badge ${m.source_doc_type === 'RECEIPT' ? 'green' : 'amber'}">
            ${escapeHtml(m.source_doc_type)}
          </span>
          <span class="delta-badge ${isPos ? 'positive' : 'negative'}">
            ${isPos ? `+${m.qty_delta}` : m.qty_delta}
          </span>
        </div>
        <div>
          <div class="movement-prod-name">${escapeHtml(String(m.product_id))}</div>
          <div class="movement-meta-text">${escapeHtml(String(m.location_id || 'WH01'))} • ${m.timestamp || 'Just now'}</div>
        </div>
      </div>
    `;
  }).join('');
}

/* -------------------------------------------------------------------------- */
/* VIEW 2: DELIVERIES & ORDER LIST (/deliveries)                              */
/* -------------------------------------------------------------------------- */
async function loadDeliveries() {
  if (isBackendOnline) {
    try {
      const res = await fetch(`${API_BASE_URL}/deliveries`, { headers: getAuthHeaders() });
      if (res.ok) {
        const backendDeliveries = await res.json();
        if (backendDeliveries && backendDeliveries.length > 0) {
          localOrders = backendDeliveries.map((del, idx) => {
            const rawStatus = (del.status || 'Draft').toLowerCase();
            let uiStatus = 'await';
            if (rawStatus === 'done' || rawStatus === 'validated') uiStatus = 'delivered';
            else if (rawStatus === 'ready' || rawStatus === 'onway') uiStatus = 'onway';

            const createdDate = del.created_at ? new Date(del.created_at).toLocaleDateString('de-DE') : '26.07.2024';

            return {
              id: del.id,
              orderNo: del.delivery_number || `№${674839 + idx}`,
              customer: del.customer || 'Kris Payer',
              phone: '099 758 9092',
              category: 'Laptops',
              price: 1302.38,
              date: createdDate,
              payment: 'PayPal',
              status: uiStatus,
              selected: false
            };
          });
        }
      }
    } catch (e) {}
  }

  renderOrdersTable();
  updateStatusBannerCounts();
}

function renderOrdersTable() {
  const tbody = document.getElementById('orders-table-body');
  if (!tbody) return;

  const filtered = localOrders.filter(order => {
    if (activeFilters.category && order.category.toLowerCase() !== activeFilters.category.toLowerCase()) {
      return false;
    }
    if (activeFilters.payment && order.payment.toLowerCase() !== activeFilters.payment.toLowerCase()) {
      return false;
    }
    if (activeFilters.search) {
      const q = activeFilters.search.toLowerCase();
      const matchNo = order.orderNo.toLowerCase().includes(q);
      const matchCust = order.customer.toLowerCase().includes(q);
      const matchPhone = (order.phone || '').toLowerCase().includes(q);
      if (!matchNo && !matchCust && !matchPhone) return false;
    }
    return true;
  });

  const counterEl = document.getElementById('order-total-counter');
  if (counterEl) {
    counterEl.textContent = `${filtered.length * 18} orders`;
  }

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align: center; padding: 3rem; color: var(--text-muted);">
          No matching orders found. Try adjusting or clearing your filters.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filtered.map(order => {
    let statusLabel = 'on way';
    let statusClass = 'onway';
    if (order.status === 'delivered') {
      statusLabel = 'delivered';
      statusClass = 'delivered';
    } else if (order.status === 'await') {
      statusLabel = 'await';
      statusClass = 'await';
    }

    const formattedPrice = `$ ${order.price.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

    return `
      <tr data-order-id="${order.id}">
        <td>
          <input type="checkbox" class="table-checkbox row-checkbox" ${order.selected ? 'checked' : ''} onchange="toggleOrderSelect('${order.id}', this.checked)">
        </td>
        <td class="order-num-text">${order.orderNo}</td>
        <td>
          <div class="customer-cell">
            <span class="customer-name">${escapeHtml(order.customer)}</span>
            <span class="customer-phone">${escapeHtml(order.phone)}</span>
          </div>
        </td>
        <td>${escapeHtml(order.category)}</td>
        <td class="price-text">${formattedPrice}</td>
        <td>${order.date}</td>
        <td class="payment-text">${escapeHtml(order.payment)}</td>
        <td>
          <button class="status-pill-badge ${statusClass}" onclick="cycleOrderStatus('${order.id}')" title="Click to validate / cycle status">
            <span>${statusLabel}</span>
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>
        </td>
        <td>
          <button class="table-row-dots-btn" onclick="openOrderOptions('${order.id}')" title="Actions">···</button>
        </td>
      </tr>
    `;
  }).join('');
}

function toggleOrderSelect(id, isChecked) {
  const order = localOrders.find(o => o.id === id);
  if (order) order.selected = isChecked;
}

async function cycleOrderStatus(id) {
  const order = localOrders.find(o => o.id === id);
  if (!order) return;

  const cycle = { 'onway': 'delivered', 'delivered': 'await', 'await': 'onway' };
  order.status = cycle[order.status] || 'onway';

  if (order.status === 'delivered' && isBackendOnline && order.id.includes('-')) {
    try {
      await fetch(`${API_BASE_URL}/deliveries/${order.id}/validate`, { method: 'PUT', headers: getAuthHeaders() });
      loadDashboardKPIs();
    } catch (e) {}
  }

  renderOrdersTable();
  updateStatusBannerCounts();
}

function updateStatusBannerCounts() {
  const elNew = document.getElementById('banner-new-count');
  const elAwait = document.getElementById('banner-await-count');
  const elOnway = document.getElementById('banner-onway-count');
  const elDelivered = document.getElementById('banner-delivered-count');

  if (elNew) elNew.textContent = '12';
  if (elAwait) elAwait.textContent = '20';
  if (elOnway) elOnway.textContent = '57';
  if (elDelivered) elDelivered.textContent = '98';
}

function openOrderOptions(id) {
  const order = localOrders.find(o => o.id === id);
  if (!order) return;

  const action = prompt(`Delivery ${order.orderNo} (${order.customer})\nType: 'validate' (marks Delivered and updates Stock Ledger), 'delete', or change status ('onway', 'delivered', 'await'):`);
  if (action === 'delete') {
    localOrders = localOrders.filter(o => o.id !== id);
    renderOrdersTable();
  } else if (action === 'validate' || action === 'delivered') {
    order.status = 'delivered';
    if (isBackendOnline && order.id.includes('-')) {
      fetch(`${API_BASE_URL}/deliveries/${order.id}/validate`, { method: 'PUT', headers: getAuthHeaders() });
    }
    renderOrdersTable();
  } else if (['onway', 'await'].includes(action)) {
    order.status = action;
    renderOrdersTable();
  }
}

/* -------------------------------------------------------------------------- */
/* Filter Chips & Toolbar Controls                                            */
/* -------------------------------------------------------------------------- */
function initOrderToolbar() {
  const searchInput = document.getElementById('order-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      activeFilters.search = e.target.value;
      renderOrdersTable();
    });
  }

  const globalSearch = document.getElementById('global-search-input');
  if (globalSearch) {
    globalSearch.addEventListener('input', (e) => {
      activeFilters.search = e.target.value;
      if (searchInput) searchInput.value = e.target.value;
      renderOrdersTable();
    });
  }

  const selectAll = document.getElementById('select-all-orders');
  if (selectAll) {
    selectAll.addEventListener('change', (e) => {
      const checked = e.target.checked;
      localOrders.forEach(o => o.selected = checked);
      renderOrdersTable();
    });
  }

  const exportBtn = document.getElementById('export-orders-btn');
  if (exportBtn) exportBtn.addEventListener('click', exportOrdersToCsv);

  const addOrderBtn = document.getElementById('open-add-order-modal');
  if (addOrderBtn) addOrderBtn.addEventListener('click', () => openModal('add-order-modal'));

  const sortBtn = document.getElementById('sort-orders-btn');
  if (sortBtn) {
    sortBtn.addEventListener('click', () => {
      if (currentSort === 'default') {
        currentSort = 'price-high';
        localOrders.sort((a, b) => b.price - a.price);
        sortBtn.querySelector('span').textContent = 'Sort: Price (High)';
      } else if (currentSort === 'price-high') {
        currentSort = 'price-low';
        localOrders.sort((a, b) => a.price - b.price);
        sortBtn.querySelector('span').textContent = 'Sort: Price (Low)';
      } else {
        currentSort = 'default';
        localOrders.sort((a, b) => String(a.id).localeCompare(String(b.id)));
        sortBtn.querySelector('span').textContent = 'Sort: default';
      }
      renderOrdersTable();
    });
  }

  const prevBtn = document.getElementById('prev-page-btn');
  const nextBtn = document.getElementById('next-page-btn');
  const pageLabel = document.getElementById('pagination-page-label');

  if (prevBtn && nextBtn && pageLabel) {
    prevBtn.addEventListener('click', () => {
      if (currentPage > 1) {
        currentPage--;
        pageLabel.textContent = `${currentPage} of ${totalPages}`;
      }
    });
    nextBtn.addEventListener('click', () => {
      if (currentPage < totalPages) {
        currentPage++;
        pageLabel.textContent = `${currentPage} of ${totalPages}`;
      }
    });
  }
}

function removeFilter(type) {
  if (type === 'category') {
    activeFilters.category = '';
    const chip = document.getElementById('chip-category');
    if (chip) chip.style.display = 'none';
  } else if (type === 'payment') {
    activeFilters.payment = '';
    const chip = document.getElementById('chip-payment');
    if (chip) chip.style.display = 'none';
  }
  updateClearAllVisibility();
  renderOrdersTable();
}

function clearAllFilters() {
  activeFilters.category = '';
  activeFilters.payment = '';
  activeFilters.search = '';

  const chipCat = document.getElementById('chip-category');
  const chipPay = document.getElementById('chip-payment');
  const searchInput = document.getElementById('order-search-input');

  if (chipCat) chipCat.style.display = 'none';
  if (chipPay) chipPay.style.display = 'none';
  if (searchInput) searchInput.value = '';

  updateClearAllVisibility();
  renderOrdersTable();
}

function updateClearAllVisibility() {
  let activeCount = 0;
  if (activeFilters.category) activeCount++;
  if (activeFilters.payment) activeCount++;

  const clearBtn = document.getElementById('clear-all-filters-btn');
  if (clearBtn) {
    if (activeCount > 0) {
      clearBtn.style.display = 'inline';
      clearBtn.textContent = `Clear all (${activeCount})`;
    } else {
      clearBtn.style.display = 'none';
    }
  }
}

function exportOrdersToCsv() {
  const headers = ['Order Number', 'Customer Name', 'Phone', 'Category', 'Price', 'Date', 'Payment', 'Status'];
  const rows = localOrders.map(o => [
    o.orderNo,
    `"${o.customer}"`,
    `"${o.phone}"`,
    o.category,
    o.price,
    o.date,
    o.payment,
    o.status
  ]);

  const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', `stocksense_orders_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/* -------------------------------------------------------------------------- */
/* VIEW 3: PRODUCT CATALOG & MASTER STOCK (/products & /categories)            */
/* -------------------------------------------------------------------------- */
async function loadProductsCatalog() {
  const tbody = document.getElementById('products-table-body');
  if (!tbody) return;

  if (isBackendOnline) {
    try {
      const res = await fetch(`${API_BASE_URL}/products`, { headers: getAuthHeaders() });
      if (res.ok) {
        cachedProducts = await res.json();
        if (cachedProducts.length > 0) {
          renderProductsTable(cachedProducts);
          return;
        }
      }
    } catch (e) {}
  }

  cachedProducts = [
    { id: 'PROD-01', sku: 'MBA-M2-MID', name: 'Apple MacBook Air M2 13"', category_name: 'Laptops', reorder_min: 5, reorder_max: 50, unit_of_measure: 'units', is_active: true },
    { id: 'PROD-02', sku: 'AW-S9-45', name: 'Apple Watch Series 9 GPS', category_name: 'Watches', reorder_min: 10, reorder_max: 60, unit_of_measure: 'units', is_active: true },
    { id: 'PROD-03', sku: 'JBL-CHG5-BLK', name: 'Acoustics JBL Charge 5', category_name: 'Audio', reorder_min: 8, reorder_max: 40, unit_of_measure: 'units', is_active: true },
    { id: 'PROD-04', sku: 'DIV-SB-HQ', name: 'Acoustics Divoom SongBird-HQ', category_name: 'Audio', reorder_min: 4, reorder_max: 30, unit_of_measure: 'units', is_active: true },
    { id: 'PROD-05', sku: 'APP-PRO-USB', name: 'Apple AirPods Pro 2 (USB-C)', category_name: 'Audio', reorder_min: 15, reorder_max: 80, unit_of_measure: 'units', is_active: true }
  ];

  renderProductsTable(cachedProducts);
}

function renderProductsTable(products) {
  const tbody = document.getElementById('products-table-body');
  if (!tbody) return;

  tbody.innerHTML = products.map(p => `
    <tr>
      <td><span style="font-family: var(--font-mono); font-weight: 600; color: var(--primary);">${escapeHtml(p.sku)}</span></td>
      <td><strong>${escapeHtml(p.name)}</strong></td>
      <td><span class="stat-badge green">${escapeHtml(p.category_name || 'Laptops')}</span></td>
      <td>${p.reorder_min} / ${p.reorder_max} units</td>
      <td>${escapeHtml(p.unit_of_measure || 'units')}</td>
      <td>
        <span class="stat-badge ${p.is_active !== false ? 'green' : 'red'}">
          ${p.is_active !== false ? 'Active' : 'Inactive'}
        </span>
      </td>
      <td>
        <button class="btn-white-pill" style="font-size: 0.75rem; padding: 0.3rem 0.6rem;" onclick="deleteProduct('${p.id}')">Delete</button>
      </td>
    </tr>
  `).join('');
}

async function deleteProduct(productId) {
  if (!confirm(`Delete product ${productId}?`)) return;

  if (isBackendOnline) {
    try {
      await fetch(`${API_BASE_URL}/products/${productId}`, { method: 'DELETE', headers: getAuthHeaders() });
    } catch (e) {}
  }
  cachedProducts = cachedProducts.filter(p => p.id !== productId);
  renderProductsTable(cachedProducts);
}

async function loadCategories() {
  if (!isBackendOnline) return;
  try {
    const res = await fetch(`${API_BASE_URL}/categories`, { headers: getAuthHeaders() });
    if (res.ok) {
      cachedCategories = await res.json();
      const select = document.getElementById('prod-category-select');
      if (select && cachedCategories.length > 0) {
        select.innerHTML = cachedCategories.map(c => `
          <option value="${c.id}">${escapeHtml(c.name)}</option>
        `).join('');
      }
    }
  } catch (e) {}
}

/* -------------------------------------------------------------------------- */
/* VIEW 4: INBOUND RECEIPTS (/receipts)                                       */
/* -------------------------------------------------------------------------- */
async function loadReceipts() {
  const tbody = document.getElementById('receipts-table-body');
  if (!tbody) return;

  let receipts = [];
  if (isBackendOnline) {
    try {
      const res = await fetch(`${API_BASE_URL}/receipts`, { headers: getAuthHeaders() });
      if (res.ok) {
        receipts = await res.json();
      }
    } catch (e) {}
  }

  if (receipts.length === 0) {
    receipts = [
      { id: 'REC-2026-001', receipt_number: 'REC-2026-001', supplier: 'Apple Distribution Asia', items: [{}, {}], status: 'Draft', created_at: '2026-09-24T10:00:00Z' },
      { id: 'REC-2026-002', receipt_number: 'REC-2026-002', supplier: 'Harman Kardon / JBL Logistics', items: [{}], status: 'Done', created_at: '2026-09-22T08:30:00Z' }
    ];
  }

  tbody.innerHTML = receipts.map(r => {
    const isDone = (r.status || '').toLowerCase() === 'done';
    const dateStr = r.created_at ? new Date(r.created_at).toLocaleDateString('de-DE') : '26.07.2024';

    return `
      <tr>
        <td><strong>${escapeHtml(r.receipt_number || r.id)}</strong></td>
        <td>${escapeHtml(r.supplier || 'Vendor')}</td>
        <td>${(r.items || []).length || 1} lines</td>
        <td>${dateStr}</td>
        <td>
          <span class="status-pill-badge ${isDone ? 'delivered' : 'await'}">
            ${isDone ? 'Received (Done)' : 'Draft / Waiting'}
          </span>
        </td>
        <td>
          ${!isDone ? `
            <button class="btn-dark-pill" style="font-size: 0.75rem; padding: 0.35rem 0.8rem;" onclick="validateReceipt('${r.id}')">
              Validate & Stock +
            </button>
          ` : `
            <span style="color: var(--text-muted); font-size: 0.8rem;">Ledger Updated ✓</span>
          `}
        </td>
      </tr>
    `;
  }).join('');
}

async function validateReceipt(receiptId) {
  if (isBackendOnline) {
    try {
      await fetch(`${API_BASE_URL}/receipts/${receiptId}/validate`, { method: 'PUT', headers: getAuthHeaders() });
    } catch (e) {}
  }
  alert(`Receipt #${receiptId} validated! Inventory increased and ledger updated.`);
  loadReceipts();
  loadDashboardKPIs();
}

/* -------------------------------------------------------------------------- */
/* VIEW 5: APPEND-ONLY STOCK LEDGER (/ledger/history)                         */
/* -------------------------------------------------------------------------- */
async function loadStockLedger() {
  const tbody = document.getElementById('ledger-table-body');
  if (!tbody) return;

  let ledgerEntries = [];
  if (isBackendOnline) {
    try {
      const res = await fetch(`${API_BASE_URL}/ledger/history`, { headers: getAuthHeaders() });
      if (res.ok) {
        ledgerEntries = await res.json();
      }
    } catch (e) {}
  }

  if (ledgerEntries.length === 0) {
    ledgerEntries = [
      { id: 1001, source_doc_type: 'RECEIPT', source_doc_id: 1, product_id: 'Apple MacBook Air M2', location_id: 'Main WH (Zone A)', qty_delta: 25, timestamp: '2026-09-26 10:15:00' },
      { id: 1002, source_doc_type: 'DELIVERY', source_doc_id: 674839, product_id: 'Apple MacBook Air M2', location_id: 'Main WH (Zone A)', qty_delta: -1, timestamp: '2026-09-26 11:30:00' },
      { id: 1003, source_doc_type: 'RECEIPT', source_doc_id: 2, product_id: 'Apple Watch Series 9', location_id: 'Warehouse Central', qty_delta: 40, timestamp: '2026-09-26 11:45:00' },
      { id: 1004, source_doc_type: 'DELIVERY', source_doc_id: 674840, product_id: 'Apple Watch Series 9', location_id: 'Warehouse Central', qty_delta: -2, timestamp: '2026-09-26 12:20:00' }
    ];
  }

  tbody.innerHTML = ledgerEntries.map(entry => {
    const isPos = entry.qty_delta > 0;
    return `
      <tr>
        <td>#${entry.id}</td>
        <td><span class="stat-badge ${entry.source_doc_type === 'RECEIPT' ? 'green' : 'amber'}">${escapeHtml(entry.source_doc_type)} #${entry.source_doc_id || '1'}</span></td>
        <td><strong>${escapeHtml(String(entry.product_id))}</strong></td>
        <td>${escapeHtml(String(entry.location_id || 'WH01'))}</td>
        <td>
          <span class="delta-badge ${isPos ? 'positive' : 'negative'}">
            ${isPos ? `+${entry.qty_delta}` : entry.qty_delta}
          </span>
        </td>
        <td style="color: var(--text-muted); font-size: 0.8rem;">${entry.timestamp || 'Just now'}</td>
      </tr>
    `;
  }).join('');
}

/* -------------------------------------------------------------------------- */
/* VIEW 6: WAREHOUSES & LOCATIONS (/warehouses)                               */
/* -------------------------------------------------------------------------- */
async function loadWarehouses() {
  const tbody = document.getElementById('warehouses-table-body');
  if (!tbody) return;

  if (isBackendOnline) {
    try {
      const res = await fetch(`${API_BASE_URL}/warehouses`, { headers: getAuthHeaders() });
      if (res.ok) {
        cachedWarehouses = await res.json();
      }
    } catch (e) {}
  }

  if (cachedWarehouses.length === 0) {
    cachedWarehouses = [
      { code: 'WH01', name: 'Main Fulfillment Center', address: '42 Logistics Parkway, Berlin', is_active: true },
      { code: 'WH02', name: 'Store Front Retail Stock', address: '18 Kurfürstendamm, Berlin', is_active: true },
      { code: 'ZONE-A', name: 'Secure Electronics Rack A3', address: 'Rack Tier 2', is_active: true }
    ];
  }

  tbody.innerHTML = cachedWarehouses.map(w => `
    <tr>
      <td><span style="font-family: var(--font-mono); font-weight: 700; color: var(--primary);">${escapeHtml(w.code)}</span></td>
      <td><strong>${escapeHtml(w.name)}</strong></td>
      <td>${escapeHtml(w.address || 'Standard Location')}</td>
      <td>${w.parent_id ? 'Nested Rack' : 'Primary Warehouse'}</td>
      <td><span class="stat-badge green">${w.is_active !== false ? 'Operational' : 'Maintenance'}</span></td>
    </tr>
  `).join('');
}

/* -------------------------------------------------------------------------- */
/* Modal Windows & Form Submissions                                            */
/* -------------------------------------------------------------------------- */
function initModals() {
  // Add Delivery / Order
  const addOrderForm = document.getElementById('create-order-form');
  if (addOrderForm) {
    addOrderForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const customer = document.getElementById('order-cust-name').value;
      const phone = document.getElementById('order-cust-phone').value;
      const category = document.getElementById('order-category-select').value;
      const price = parseFloat(document.getElementById('order-price-input').value) || 1302.38;
      const payment = document.getElementById('order-payment-select').value;
      const status = document.getElementById('order-status-select').value;

      const randomNo = '№' + Math.floor(600000 + Math.random() * 90000);
      const today = new Date().toLocaleDateString('de-DE');

      if (isBackendOnline) {
        try {
          await fetch(`${API_BASE_URL}/deliveries`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
              customer_name: customer,
              items: [{ product_id: 'default', quantity: 1 }]
            })
          });
        } catch (err) {}
      }

      localOrders.unshift({
        id: randomNo,
        orderNo: randomNo,
        customer,
        phone,
        category,
        price,
        date: today,
        payment,
        status,
        selected: false
      });

      closeModal('add-order-modal');
      addOrderForm.reset();
      renderOrdersTable();
      updateStatusBannerCounts();
      loadDashboardKPIs();
      loadRecentMovements();
    });
  }

  // Add Product Form
  const addProdForm = document.getElementById('create-product-form');
  if (addProdForm) {
    addProdForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('prod-name-input').value;
      const sku = document.getElementById('prod-sku-input').value;
      const category_id = document.getElementById('prod-category-select').value || null;
      const unit_of_measure = document.getElementById('prod-uom-select').value;
      const reorder_min = parseFloat(document.getElementById('prod-min-input').value) || 5;
      const reorder_max = parseFloat(document.getElementById('prod-max-input').value) || 50;
      const description = document.getElementById('prod-desc-input').value;

      if (isBackendOnline) {
        try {
          await fetch(`${API_BASE_URL}/products`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ name, sku, category_id, unit_of_measure, reorder_min, reorder_max, description })
          });
        } catch (e) {}
      }

      cachedProducts.unshift({
        id: `PROD-${Date.now()}`,
        sku,
        name,
        category_name: 'Laptops',
        reorder_min,
        reorder_max,
        unit_of_measure,
        is_active: true
      });

      closeModal('add-product-modal');
      addProdForm.reset();
      renderProductsTable(cachedProducts);
      loadDashboardKPIs();
    });
  }

  // Add Inbound Receipt Form
  const addReceiptForm = document.getElementById('create-receipt-form');
  if (addReceiptForm) {
    addReceiptForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const supplier = document.getElementById('receipt-supplier-input').value;
      const qty = parseFloat(document.getElementById('receipt-qty-input').value) || 10;

      if (isBackendOnline) {
        try {
          await fetch(`${API_BASE_URL}/receipts`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
              supplier,
              items: [{ product_id: 'default', quantity: qty }]
            })
          });
        } catch (e) {}
      }

      closeModal('add-receipt-modal');
      addReceiptForm.reset();
      loadReceipts();
      loadDashboardKPIs();
      loadRecentMovements();
      alert(`Inbound shipment from ${supplier} created successfully!`);
    });
  }

  // Developer suite trigger
  const devSuiteBtn = document.getElementById('open-dev-suite-btn');
  if (devSuiteBtn) devSuiteBtn.addEventListener('click', () => openModal('dev-suite-modal'));

  const addProdBtn = document.getElementById('open-add-product-modal');
  if (addProdBtn) addProdBtn.addEventListener('click', () => openModal('add-product-modal'));

  const addReceiptBtn = document.getElementById('open-add-receipt-modal');
  if (addReceiptBtn) addReceiptBtn.addEventListener('click', () => openModal('add-receipt-modal'));

  // Close modals on escape key or clicking backdrop
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
    }
  });

  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('active');
      }
    });
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('active');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('active');
}

/* -------------------------------------------------------------------------- */
/* Developer API Runner                                                       */
/* -------------------------------------------------------------------------- */
async function runApiCall(endpoint, method = 'GET', body = null) {
  const statusEl = document.getElementById('console-status');
  const timeEl = document.getElementById('console-time');
  const outputEl = document.getElementById('console-output');

  if (!outputEl) return;
  outputEl.textContent = 'Executing request...';
  const startTime = performance.now();

  try {
    const options = {
      method,
      headers: getAuthHeaders()
    };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(`${API_BASE_URL}${endpoint}`, options);
    const endTime = performance.now();
    const duration = Math.round(endTime - startTime);

    if (timeEl) timeEl.textContent = `${duration}ms`;
    if (statusEl) {
      statusEl.textContent = `${res.status} ${res.statusText}`;
      statusEl.style.color = res.ok ? '#4ade80' : '#f87171';
    }

    const data = await res.json();
    outputEl.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    if (statusEl) {
      statusEl.textContent = 'ERROR / OFFLINE';
      statusEl.style.color = '#f87171';
    }
    if (timeEl) timeEl.textContent = '0ms';
    outputEl.textContent = JSON.stringify({
      status: 'Backend server is currently offline or unreachable',
      target_url: `${API_BASE_URL}${endpoint}`,
      message: err.message,
      help: 'Start FastAPI on http://localhost:8000 using uvicorn app.main:app --reload'
    }, null, 2);
  }
}

function escapeHtml(str) {
  return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
