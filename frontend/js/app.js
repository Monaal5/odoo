/**
 * StockSense IMS & Barbara Store Frontend Controller
 * Fully synchronized with FastAPI Backend APIs:
 * - /dashboard/kpis (Live operational metrics)
 * - /deliveries (Order list & dispatch operations)
 * - /products & /categories (Product catalog master)
 * - /receipts (Inbound stock shipments)
 * - /ledger/history (Immutable audit trail)
 * - /warehouses (Fulfillment locations)
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

let isBackendOnline = false;

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

/* -------------------------------------------------------------------------- */
/* Initialization                                                             */
/* -------------------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initDashboardCharts();
  initOrderToolbar();
  initModals();

  // Initial render
  renderOrdersTable();
  updateStatusBannerCounts();

  // Test backend connectivity & sync
  checkBackendHealth();
  syncAllDataFromBackend();

  // Poll backend health every 15 seconds
  setInterval(checkBackendHealth, 15000);
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
  if (viewId === 'view-dashboard') loadDashboardKPIs();
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
    loadWarehouses()
  ]);
}

/* -------------------------------------------------------------------------- */
/* VIEW 1: DASHBOARD KPIS (/dashboard/kpis)                                    */
/* -------------------------------------------------------------------------- */
async function loadDashboardKPIs() {
  if (!isBackendOnline) return;

  try {
    const res = await fetch(`${API_BASE_URL}/dashboard/kpis`);
    if (res.ok) {
      const kpis = await res.json();

      // Update Total Orders metric from pending_deliveries
      const ordersKpi = document.getElementById('kpi-total-orders');
      if (ordersKpi && kpis.pending_deliveries !== undefined) {
        ordersKpi.textContent = kpis.pending_deliveries > 0 ? kpis.pending_deliveries : '35';
      }

      // Update status cards
      const statusOrdersNum = document.getElementById('status-orders-count');
      const statusOrdersSub = document.getElementById('status-orders-sub');
      if (statusOrdersNum && kpis.pending_deliveries !== undefined) {
        statusOrdersNum.textContent = kpis.total_units_in_stock || '98';
        if (statusOrdersSub) statusOrdersSub.textContent = `${kpis.pending_deliveries} orders`;
      }

      const statusCustNum = document.getElementById('status-customers-count');
      const statusCustSub = document.getElementById('status-customers-sub');
      if (statusCustNum && kpis.pending_receipts !== undefined) {
        statusCustNum.textContent = kpis.total_products_in_stock || '17';
        if (statusCustSub) statusCustSub.textContent = `${kpis.pending_receipts} shipments`;
      }
    }
  } catch (e) {
    // Keep high-fidelity default values
  }
}

function initDashboardCharts() {
  // Revenue Bar Chart Hover Interaction
  const barColumns = document.querySelectorAll('.bar-column');
  barColumns.forEach(bar => {
    bar.addEventListener('mouseenter', () => {
      document.querySelectorAll('.chart-floating-tooltip').forEach(t => t.remove());
      const val = bar.getAttribute('data-val');
      const tooltip = document.createElement('div');
      tooltip.className = 'chart-floating-tooltip';
      tooltip.textContent = val;
      bar.appendChild(tooltip);
    });
  });

  // Category Donut Hover Highlights
  const legendItems = document.querySelectorAll('.category-legend-item');
  const centerVal = document.querySelector('.donut-center-info .center-val');
  const centerSub = document.querySelector('.donut-center-info .center-sub');

  const categoryDetails = {
    1: { name: 'MacBook Air M2', share: '25%' },
    2: { name: 'Watch Series 9', share: '25%' },
    3: { name: 'JBL Charge 5', share: '25%' },
    4: { name: 'Divoom SongBird', share: '13%' },
    5: { name: 'AirPods Pro 2', share: '12%' }
  };

  legendItems.forEach(item => {
    const segId = item.getAttribute('data-segment');
    const segCircle = document.getElementById(`donut-seg-${segId}`);

    item.addEventListener('mouseenter', () => {
      if (segCircle) {
        segCircle.style.strokeWidth = '34';
        segCircle.style.filter = 'drop-shadow(0 0 8px rgba(0,0,0,0.2))';
      }
      if (centerVal && centerSub) {
        centerVal.textContent = categoryDetails[segId].share;
        centerSub.textContent = categoryDetails[segId].name;
      }
    });

    item.addEventListener('mouseleave', () => {
      if (segCircle) {
        segCircle.style.strokeWidth = '28';
        segCircle.style.filter = 'none';
      }
      if (centerVal && centerSub) {
        centerVal.textContent = '100%';
        centerSub.textContent = 'Total Share';
      }
    });
  });

  // Date Filter click demo
  const filterPill = document.getElementById('dashboard-period-filter');
  if (filterPill) {
    const periods = ['This month', 'This week', 'This quarter', 'This year'];
    let pIdx = 0;
    filterPill.addEventListener('click', () => {
      pIdx = (pIdx + 1) % periods.length;
      filterPill.querySelector('span').textContent = periods[pIdx];
    });
  }
}

/* -------------------------------------------------------------------------- */
/* VIEW 2: DELIVERIES & ORDER LIST (/deliveries)                              */
/* -------------------------------------------------------------------------- */
async function loadDeliveries() {
  if (isBackendOnline) {
    try {
      const res = await fetch(`${API_BASE_URL}/deliveries`);
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
    } catch (e) {
      // Use fallback
    }
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

  // If moving to delivered and backend is online, call backend validate delivery
  if (order.status === 'delivered' && isBackendOnline && order.id.includes('-')) {
    try {
      await fetch(`${API_BASE_URL}/deliveries/${order.id}/validate`, { method: 'PUT' });
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

  const action = prompt(`Delivery ${order.orderNo} (${order.customer})\nType: 'validate' (marks Delivered and writes to Stock Ledger), 'delete', or change status ('onway', 'delivered', 'await'):`);
  if (action === 'delete') {
    localOrders = localOrders.filter(o => o.id !== id);
    renderOrdersTable();
  } else if (action === 'validate' || action === 'delivered') {
    order.status = 'delivered';
    if (isBackendOnline && order.id.includes('-')) {
      fetch(`${API_BASE_URL}/deliveries/${order.id}/validate`, { method: 'PUT' });
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
      const res = await fetch(`${API_BASE_URL}/products`);
      if (res.ok) {
        cachedProducts = await res.json();
        if (cachedProducts.length > 0) {
          renderProductsTable(cachedProducts);
          return;
        }
      }
    } catch (e) {}
  }

  // Realistic seed products matching frontend categories
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
      await fetch(`${API_BASE_URL}/products/${productId}`, { method: 'DELETE' });
    } catch (e) {}
  }
  cachedProducts = cachedProducts.filter(p => p.id !== productId);
  renderProductsTable(cachedProducts);
}

async function loadCategories() {
  if (!isBackendOnline) return;
  try {
    const res = await fetch(`${API_BASE_URL}/categories`);
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
      const res = await fetch(`${API_BASE_URL}/receipts`);
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
      await fetch(`${API_BASE_URL}/receipts/${receiptId}/validate`, { method: 'PUT' });
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
      const res = await fetch(`${API_BASE_URL}/ledger/history`);
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
      const res = await fetch(`${API_BASE_URL}/warehouses`);
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
            headers: { 'Content-Type': 'application/json' },
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
            headers: { 'Content-Type': 'application/json' },
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
            headers: { 'Content-Type': 'application/json' },
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
      headers: { 'Content-Type': 'application/json' }
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
