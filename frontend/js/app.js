/**
 * Odoo Hackathon Boilerplate - Frontend Application Logic
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
  const odooDot = document.getElementById('odoo-status-dot');
  const odooText = document.getElementById('odoo-status-text');

  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (res.ok) {
      const data = await res.json();
      apiDot.className = 'dot online';
      apiText.textContent = 'FastAPI: Online';

      if (data.odoo_connection.includes('Connected')) {
        odooDot.className = 'dot online';
        odooText.textContent = 'Odoo: Connected';
      } else {
        odooDot.className = 'dot warning';
        odooText.textContent = 'Odoo: Disconnected';
      }
    } else {
      throw new Error('API Unreachable');
    }
  } catch (err) {
    apiDot.className = 'dot offline';
    apiText.textContent = 'FastAPI: Offline';
    odooDot.className = 'dot offline';
    odooText.textContent = 'Odoo: Offline';
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
/* Items Management (CRUD)                                                   */
/* -------------------------------------------------------------------------- */
async function loadItems() {
  const tableBody = document.getElementById('items-table-body');
  if (!tableBody) return;

  tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">Loading items...</td></tr>';

  try {
    const res = await fetch(`${API_BASE_URL}/items`);
    if (!res.ok) throw new Error('Failed to fetch items');
    const items = await res.json();

    if (items.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center; color: var(--text-muted);">No items found in database. Click "Add Item" to create one.</td></tr>';
      return;
    }

    tableBody.innerHTML = items.map(item => `
      <tr>
        <td>#${item.id}</td>
        <td><strong>${escapeHtml(item.title)}</strong></td>
        <td>${escapeHtml(item.description || 'N/A')}</td>
        <td><span class="badge badge-cyan">${escapeHtml(item.category)}</span></td>
        <td>${item.odoo_ref_id ? `<span class="badge badge-primary">Odoo #${item.odoo_ref_id}</span>` : '<span style="color:var(--text-subtle);">None</span>'}</td>
        <td>
          <button class="btn btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.75rem;" onclick="deleteItemById(${item.id})">Delete</button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color: var(--accent-rose);">Error loading items: ${err.message}</td></tr>`;
  }
}

async function createNewItem(event) {
  event.preventDefault();
  const title = document.getElementById('item-title').value;
  const description = document.getElementById('item-desc').value;
  const category = document.getElementById('item-category').value;
  const odoo_ref_id = document.getElementById('item-odoo-ref').value ? parseInt(document.getElementById('item-odoo-ref').value) : null;

  try {
    const res = await fetch(`${API_BASE_URL}/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description, category, is_active: true, odoo_ref_id })
    });

    if (res.ok) {
      closeModal();
      loadItems();
      checkHealth();
    } else {
      alert('Failed to create item');
    }
  } catch (err) {
    alert('Error connecting to backend: ' + err.message);
  }
}

async function deleteItemById(id) {
  if (!confirm(`Are you sure you want to delete item #${id}?`)) return;
  try {
    const res = await fetch(`${API_BASE_URL}/items/${id}`, { method: 'DELETE' });
    if (res.ok) {
      loadItems();
    } else {
      alert('Failed to delete item');
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
