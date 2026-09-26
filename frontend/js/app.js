/**
 * StockSense IMS - Frontend Application Logic
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  checkHealth();
  loadItems();
  setupEventListeners();
});

/* -------------------------------------------------------------------------- */
/* Tab Switching                                                              */
/* -------------------------------------------------------------------------- */
function initTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.style.display = 'none');

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.style.display = 'block';
      }
    });
  });
}

/* -------------------------------------------------------------------------- */
/* System Health Monitor                                                      */
/* -------------------------------------------------------------------------- */
async function checkHealth() {
  const apiDot = document.getElementById('api-status-dot');
  const apiText = document.getElementById('api-status-text');
  const dbDot = document.getElementById('db-status-dot');
  const dbText = document.getElementById('db-status-text');

  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (res.ok) {
      const data = await res.json();
      apiDot.className = 'dot online';
      apiText.textContent = 'FastAPI: Online';

      if (data.database === 'Healthy') {
        dbDot.className = 'dot online';
        dbText.textContent = 'Database: Healthy';
      } else {
        dbDot.className = 'dot warning';
        dbText.textContent = 'Database: Warning';
      }
    } else {
      throw new Error('API Unreachable');
    }
  } catch (err) {
    apiDot.className = 'dot offline';
    apiText.textContent = 'FastAPI: Offline';
    dbDot.className = 'dot offline';
    dbText.textContent = 'Database: Offline';
  }
}

/* -------------------------------------------------------------------------- */
/* API Console Runner                                                         */
/* -------------------------------------------------------------------------- */
async function runApiCall(endpoint, method = 'GET', body = null) {
  const statusEl = document.getElementById('console-status');
  const timeEl = document.getElementById('console-time');
  const outputEl = document.getElementById('console-output');

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

    timeEl.textContent = `${duration}ms`;
    statusEl.textContent = `${res.status} ${res.statusText}`;
    statusEl.className = `status-tag status-${res.status === 200 || res.status === 201 ? '200' : '404'}`;

    let data;
    if (res.status === 204) {
      data = { message: 'Item deleted successfully (204 No Content)' };
    } else {
      data = await res.json();
    }

    outputEl.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    statusEl.textContent = 'ERROR';
    statusEl.className = 'status-tag status-404';
    timeEl.textContent = '0ms';
    outputEl.textContent = JSON.stringify({
      error: 'Failed to connect to backend server',
      details: err.message,
      hint: 'Ensure backend server is running on http://localhost:8000'
    }, null, 2);
  }
}

/* -------------------------------------------------------------------------- */
/* Product Catalog Management (CRUD)                                         */
/* -------------------------------------------------------------------------- */
async function loadItems() {
  const tableBody = document.getElementById('items-table-body');
  if (!tableBody) return;

  tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">Loading products...</td></tr>';

  try {
    const res = await fetch(`${API_BASE_URL}/items`);
    if (!res.ok) throw new Error('Failed to fetch catalog products');
    const items = await res.json();

    if (items.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center; color: var(--text-muted);">No products found in catalog. Click "Add New Product" to create one.</td></tr>';
      return;
    }

    tableBody.innerHTML = items.map(item => `
      <tr>
        <td>#${item.id}</td>
        <td><strong>${escapeHtml(item.title)}</strong></td>
        <td>${escapeHtml(item.description || 'N/A')}</td>
        <td><span class="badge badge-cyan">${escapeHtml(item.category)}</span></td>
        <td>${item.is_active ? '<span class="badge badge-primary">Active</span>' : '<span style="color:var(--text-subtle);">Inactive</span>'}</td>
        <td>
          <button class="btn btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.75rem;" onclick="deleteItemById(${item.id})">Delete</button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color: var(--accent-rose);">Error loading catalog: ${err.message}</td></tr>`;
  }
}

async function createNewItem(event) {
  event.preventDefault();
  const title = document.getElementById('item-title').value;
  const description = document.getElementById('item-desc').value;
  const category = document.getElementById('item-category').value;

  try {
    const res = await fetch(`${API_BASE_URL}/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description, category, is_active: true })
    });

    if (res.ok) {
      closeModal();
      loadItems();
      checkHealth();
    } else {
      alert('Failed to create product');
    }
  } catch (err) {
    alert('Error connecting to backend: ' + err.message);
  }
}

async function deleteItemById(id) {
  if (!confirm(`Are you sure you want to delete product #${id}?`)) return;
  try {
    const res = await fetch(`${API_BASE_URL}/items/${id}`, { method: 'DELETE' });
    if (res.ok) {
      loadItems();
    } else {
      alert('Failed to delete product');
    }
  } catch (err) {
    alert('Error: ' + err.message);
  }
}

/* -------------------------------------------------------------------------- */
/* Modal Helpers & Utilities                                                  */
/* -------------------------------------------------------------------------- */
function openModal() {
  document.getElementById('item-modal').classList.add('active');
}

function closeModal() {
  document.getElementById('item-modal').classList.remove('active');
  document.getElementById('create-item-form').reset();
}

function setupEventListeners() {
  const form = document.getElementById('create-item-form');
  if (form) form.addEventListener('submit', createNewItem);
}

function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
