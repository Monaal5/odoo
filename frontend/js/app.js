/**
 * Modern E-Commerce & Inventory Management System
 * Front-end Controller for Barbara's Store Dashboard & Order List
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Initial state for Order List
let ordersData = [
  { id: 1, orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'onway', selected: false },
  { id: 2, orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'delivered', selected: false },
  { id: 3, orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'await', selected: false },
  { id: 4, orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'onway', selected: false },
  { id: 5, orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'delivered', selected: false },
  { id: 6, orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'delivered', selected: false },
  { id: 7, orderNo: '№674839', customer: 'Kris Payer', phone: '099 758 9092', category: 'Laptops', price: 1302.38, date: '26.07.2024', payment: 'PayPal', status: 'delivered', selected: false },
  { id: 8, orderNo: '№674840', customer: 'Sarah Connor', phone: '099 443 1920', category: 'Watches', price: 420.00, date: '25.07.2024', payment: 'Apple Pay', status: 'delivered', selected: false },
  { id: 9, orderNo: '№674841', customer: 'Elena Rostova', phone: '098 112 4432', category: 'Audio', price: 180.50, date: '24.07.2024', payment: 'Credit Card', status: 'onway', selected: false },
  { id: 10, orderNo: '№674842', customer: 'Liam Neeson', phone: '097 556 9912', category: 'Laptops', price: 2199.00, date: '23.07.2024', payment: 'PayPal', status: 'await', selected: false }
];

let activeFilters = {
  category: 'Laptops',
  payment: 'PayPal',
  search: ''
};

let currentPage = 1;
const totalPages = 18;
let currentSort = 'default';

/* -------------------------------------------------------------------------- */
/* Initialization                                                             */
/* -------------------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initDashboardCharts();
  renderOrdersTable();
  updateStatusBannerCounts();
  initOrderToolbar();
  initModals();
  checkBackendHealth();
  loadProductsCatalog();
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
}

function navigateToView(viewId) {
  // Update sidebar active state
  document.querySelectorAll('.nav-btn[data-target]').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-target') === viewId);
  });

  // Switch view section
  document.querySelectorAll('.view-section').forEach(view => {
    view.classList.remove('active');
  });

  const activeView = document.getElementById(viewId);
  if (activeView) {
    activeView.classList.add('active');
  }

  // Scroll to top
  const wrapper = document.querySelector('.main-wrapper');
  if (wrapper) wrapper.scrollTop = 0;
}

/* -------------------------------------------------------------------------- */
/* Dashboard Charts & Interactivity                                           */
/* -------------------------------------------------------------------------- */
function initDashboardCharts() {
  // Revenue Bar Chart Hover Interaction
  const barColumns = document.querySelectorAll('.bar-column');
  const defaultBar = document.querySelector('.bar-column[data-label="3 AUG"]');

  barColumns.forEach(bar => {
    bar.addEventListener('mouseenter', () => {
      // Clear tooltips
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
/* Orders Management & Table Rendering (Image 2)                             */
/* -------------------------------------------------------------------------- */
function renderOrdersTable() {
  const tbody = document.getElementById('orders-table-body');
  if (!tbody) return;

  // Filter dataset
  const filtered = ordersData.filter(order => {
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
      const matchPhone = order.phone.toLowerCase().includes(q);
      if (!matchNo && !matchCust && !matchPhone) return false;
    }
    return true;
  });

  // Update counter
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
          <input type="checkbox" class="table-checkbox row-checkbox" ${order.selected ? 'checked' : ''} onchange="toggleOrderSelect(${order.id}, this.checked)">
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
          <button class="status-pill-badge ${statusClass}" onclick="cycleOrderStatus(${order.id})">
            <span>${statusLabel}</span>
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>
        </td>
        <td>
          <button class="table-row-dots-btn" onclick="openOrderOptions(${order.id})" title="More Options">···</button>
        </td>
      </tr>
    `;
  }).join('');
}

function toggleOrderSelect(id, isChecked) {
  const order = ordersData.find(o => o.id === id);
  if (order) order.selected = isChecked;
}

function cycleOrderStatus(id) {
  const order = ordersData.find(o => o.id === id);
  if (!order) return;

  const cycle = { 'onway': 'delivered', 'delivered': 'await', 'await': 'onway' };
  order.status = cycle[order.status] || 'onway';

  renderOrdersTable();
  updateStatusBannerCounts();
}

function updateStatusBannerCounts() {
  const newCount = ordersData.filter(o => o.status === 'await').length * 4 + 8;
  const awaitCount = ordersData.filter(o => o.status === 'await').length * 5 + 10;
  const onWayCount = ordersData.filter(o => o.status === 'onway').length * 8 + 41;
  const deliveredCount = ordersData.filter(o => o.status === 'delivered').length * 14 + 42;

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
  const order = ordersData.find(o => o.id === id);
  if (!order) return;

  const action = prompt(`Order ${order.orderNo} for ${order.customer}\nType: 'delete' to remove, or change status to 'onway', 'delivered', 'await':`);
  if (action === 'delete') {
    ordersData = ordersData.filter(o => o.id !== id);
    renderOrdersTable();
  } else if (['onway', 'delivered', 'await'].includes(action)) {
    order.status = action;
    renderOrdersTable();
    updateStatusBannerCounts();
  }
}

/* -------------------------------------------------------------------------- */
/* Filter Chips & Toolbar Controls                                            */
/* -------------------------------------------------------------------------- */
function initOrderToolbar() {
  // Search input
  const searchInput = document.getElementById('order-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      activeFilters.search = e.target.value;
      renderOrdersTable();
    });
  }

  // Global search also syncs with order list
  const globalSearch = document.getElementById('global-search-input');
  if (globalSearch) {
    globalSearch.addEventListener('input', (e) => {
      activeFilters.search = e.target.value;
      if (searchInput) searchInput.value = e.target.value;
      renderOrdersTable();
    });
  }

  // Select all checkbox
  const selectAll = document.getElementById('select-all-orders');
  if (selectAll) {
    selectAll.addEventListener('change', (e) => {
      const checked = e.target.checked;
      ordersData.forEach(o => o.selected = checked);
      renderOrdersTable();
    });
  }

  // Export CSV
  const exportBtn = document.getElementById('export-orders-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', exportOrdersToCsv);
  }

  // Add Order button
  const addOrderBtn = document.getElementById('open-add-order-modal');
  if (addOrderBtn) {
    addOrderBtn.addEventListener('click', () => openModal('add-order-modal'));
  }

  // Sort Orders button
  const sortBtn = document.getElementById('sort-orders-btn');
  if (sortBtn) {
    sortBtn.addEventListener('click', () => {
      if (currentSort === 'default') {
        currentSort = 'price-high';
        ordersData.sort((a, b) => b.price - a.price);
        sortBtn.querySelector('span').textContent = 'Sort: Price (High)';
      } else if (currentSort === 'price-high') {
        currentSort = 'price-low';
        ordersData.sort((a, b) => a.price - b.price);
        sortBtn.querySelector('span').textContent = 'Sort: Price (Low)';
      } else {
        currentSort = 'default';
        ordersData.sort((a, b) => a.id - b.id);
        sortBtn.querySelector('span').textContent = 'Sort: default';
      }
      renderOrdersTable();
    });
  }

  // Pagination buttons
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
  const rows = ordersData.map(o => [
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
  link.setAttribute('download', `barbara_orders_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/* -------------------------------------------------------------------------- */
/* Modal Helpers & Event Handling                                             */
/* -------------------------------------------------------------------------- */
function initModals() {
  // Form submit for Add Order
  const addOrderForm = document.getElementById('create-order-form');
  if (addOrderForm) {
    addOrderForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const customer = document.getElementById('order-cust-name').value;
      const phone = document.getElementById('order-cust-phone').value;
      const category = document.getElementById('order-category-select').value;
      const price = parseFloat(document.getElementById('order-price-input').value) || 1200;
      const payment = document.getElementById('order-payment-select').value;
      const status = document.getElementById('order-status-select').value;

      const newId = ordersData.length ? Math.max(...ordersData.map(o => o.id)) + 1 : 1;
      const randomNo = '№' + Math.floor(600000 + Math.random() * 90000);

      const today = new Date();
      const day = String(today.getDate()).padStart(2, '0');
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const year = today.getFullYear();
      const dateStr = `${day}.${month}.${year}`;

      ordersData.unshift({
        id: newId,
        orderNo: randomNo,
        customer,
        phone,
        category,
        price,
        date: dateStr,
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

  // Developer suite button click
  const devSuiteBtn = document.getElementById('open-dev-suite-btn');
  if (devSuiteBtn) {
    devSuiteBtn.addEventListener('click', () => openModal('dev-suite-modal'));
  }

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
/* Backend Integration & Odoo Explorer                                        */
/* -------------------------------------------------------------------------- */
async function checkBackendHealth() {
  const modalApiBadge = document.getElementById('modal-api-badge');
  const modalApiText = document.getElementById('modal-api-status-text');
  const modalOdooBadge = document.getElementById('modal-odoo-badge');
  const modalOdooText = document.getElementById('modal-odoo-status-text');

  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (res.ok) {
      const data = await res.json();
      if (modalApiBadge) {
        modalApiBadge.className = 'dev-status-badge online';
        modalApiText.textContent = 'FastAPI: Online';
      }
      if (modalOdooBadge && modalOdooText) {
        if (data.odoo_connection && data.odoo_connection.includes('Connected')) {
          modalOdooBadge.className = 'dev-status-badge online';
          modalOdooText.textContent = 'Odoo ERP: Connected';
        } else {
          modalOdooBadge.className = 'dev-status-badge offline';
          modalOdooText.textContent = 'Odoo ERP: Disconnected';
        }
      }
    }
  } catch (err) {
    if (modalApiBadge) {
      modalApiBadge.className = 'dev-status-badge offline';
      modalApiText.textContent = 'FastAPI: Offline';
    }
  }
}

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
      statusEl.textContent = 'ERROR';
      statusEl.style.color = '#f87171';
    }
    if (timeEl) timeEl.textContent = '0ms';
    outputEl.textContent = JSON.stringify({
      error: 'Backend is currently offline or unreachable',
      message: err.message,
      target: `${API_BASE_URL}${endpoint}`
    }, null, 2);
  }
}

async function loadProductsCatalog() {
  const tbody = document.getElementById('products-table-body');
  if (!tbody) return;

  try {
    const res = await fetch(`${API_BASE_URL}/items`);
    if (res.ok) {
      const items = await res.json();
      if (items.length > 0) {
        tbody.innerHTML = items.map(item => `
          <tr>
            <td><strong>#${item.id}</strong></td>
            <td><strong style="color: var(--text-dark);">${escapeHtml(item.title)}</strong></td>
            <td>${escapeHtml(item.description || 'N/A')}</td>
            <td><span class="stat-badge green">${escapeHtml(item.category)}</span></td>
            <td>${item.odoo_ref_id ? `Odoo #${item.odoo_ref_id}` : '<span style="color:var(--text-muted);">None</span>'}</td>
            <td>
              <button class="btn-white-pill" style="font-size: 0.75rem; padding: 0.3rem 0.6rem;" onclick="deleteProductItem(${item.id})">Delete</button>
            </td>
          </tr>
        `).join('');
        return;
      }
    }
  } catch (e) {
    // Fallback to default catalog items
  }

  // Default demo products if backend is empty/offline
  const demoProducts = [
    { id: 101, title: 'Apple MacBook Air M2 13"', desc: 'Midnight, 8-Core CPU, 16GB RAM, 512GB SSD', cat: 'Laptops', ref: 'OD-7721' },
    { id: 102, title: 'Apple Watch Series 9 GPS', desc: '45mm Midnight Aluminum Case with Sport Band', cat: 'Watches', ref: 'OD-7722' },
    { id: 103, title: 'Acoustics JBL Charge 5', desc: 'Portable Waterproof Bluetooth Speaker', cat: 'Audio', ref: 'OD-7723' },
    { id: 104, title: 'Acoustics Divoom SongBird-HQ', desc: 'Retro Bluetooth Speaker with Dual Microphones', cat: 'Audio', ref: 'OD-7724' },
    { id: 105, title: 'Apple AirPods Pro 2 (USB-C)', desc: 'Active Noise Cancellation with MagSafe Case', cat: 'Audio', ref: 'OD-7725' }
  ];

  tbody.innerHTML = demoProducts.map(p => `
    <tr>
      <td><strong>#${p.id}</strong></td>
      <td><strong style="color: var(--text-dark);">${p.title}</strong></td>
      <td>${p.desc}</td>
      <td><span class="stat-badge green">${p.cat}</span></td>
      <td><span style="color: var(--primary); font-weight: 600;">${p.ref}</span></td>
      <td>
        <button class="btn-white-pill" style="font-size: 0.75rem; padding: 0.3rem 0.6rem;">Edit</button>
      </td>
    </tr>
  `).join('');
}

function deleteProductItem(id) {
  if (confirm(`Delete product #${id}?`)) {
    fetch(`${API_BASE_URL}/items/${id}`, { method: 'DELETE' })
      .then(() => loadProductsCatalog());
  }
}

function escapeHtml(str) {
  return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
