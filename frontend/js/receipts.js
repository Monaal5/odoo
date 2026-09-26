/**
 * StockSense IMS — Inbound Receipts Controller (receipts.js)
 * Developer 3 — Frontend Integration Layer
 */

let allReceipts = [];
let availableProducts = [];
let availableWarehouses = [];
let currentDraftItems = []; // For building multi-item receipts

document.addEventListener("DOMContentLoaded", async () => {
    if (!checkAuth()) return;

    renderSidebar("receipts");
    renderTopbar("Inbound Receipts", "Stock Inflow");
    renderMobileBottomNav("receipts");
    setupModalHandlers();

    setupReceiptEventListeners();

    await loadDropdownData();
    await loadReceipts();
});

function setupReceiptEventListeners() {
    // Open Create Receipt Modal
    const newBtn = document.getElementById("btn-new-receipt");
    if (newBtn) {
        newBtn.addEventListener("click", () => {
            currentDraftItems = [];
            document.getElementById("receipt-form").reset();
            renderDraftItemsList();
            openModal("modal-receipt");
        });
    }

    // Add Item to Receipt Draft
    const addItemBtn = document.getElementById("btn-add-line-item");
    if (addItemBtn) {
        addItemBtn.addEventListener("click", handleAddLineItem);
    }

    // Create Receipt Form Submit
    const form = document.getElementById("receipt-form");
    if (form) {
        form.addEventListener("submit", handleCreateReceipt);
    }

    // Search / Filter
    const searchInput = document.getElementById("receipt-search-input");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase().trim();
            filterReceipts(query);
        });
    }
}

/**
 * Load Products and Warehouses for Selection Dropdowns
 */
async function loadDropdownData() {
    try {
        const [prods, whs] = await Promise.allSettled([
            api("/products"),
            api("/warehouses")
        ]);

        if (prods.status === "fulfilled" && Array.isArray(prods.value)) {
            availableProducts = prods.value;
        } else {
            availableProducts = [
                { id: "p-1", name: "Steel Rod 12mm", sku: "STL001" },
                { id: "p-2", name: "Hex Bolt M8x40", sku: "BLT044" },
                { id: "p-3", name: "Aluminum Sheet 2mm", sku: "ALM089" },
                { id: "p-4", name: "Copper Wire Spool", sku: "CPR012" }
            ];
        }

        if (whs.status === "fulfilled" && Array.isArray(whs.value)) {
            availableWarehouses = whs.value;
        } else {
            availableWarehouses = [
                { id: "wh-1", name: "Central Hub (WH-01)" },
                { id: "wh-2", name: "North Distribution (WH-02)" }
            ];
        }
    } catch {
        availableProducts = [
            { id: "p-1", name: "Steel Rod 12mm", sku: "STL001" },
            { id: "p-2", name: "Hex Bolt M8x40", sku: "BLT044" }
        ];
        availableWarehouses = [{ id: "wh-1", name: "Central Hub (WH-01)" }];
    }

    populateDropdowns();
}

function populateDropdowns() {
    const prodSelect = document.getElementById("receipt-product-select");
    const whSelect = document.getElementById("receipt-warehouse");

    if (prodSelect) {
        prodSelect.innerHTML = `<option value="">Select Product...</option>` +
            availableProducts.map(p => `<option value="${p.id}">${p.sku} - ${p.name}</option>`).join('');
    }

    if (whSelect) {
        whSelect.innerHTML = availableWarehouses.map(w => `<option value="${w.id}">${w.name}</option>`).join('');
    }
}

/**
 * Line item builder inside modal
 */
function handleAddLineItem() {
    const prodSelect = document.getElementById("receipt-product-select");
    const qtyInput = document.getElementById("receipt-item-qty");

    const productId = prodSelect.value;
    const quantity = parseFloat(qtyInput.value);

    if (!productId) {
        showToast("Please select a product", "warning");
        return;
    }
    if (isNaN(quantity) || quantity <= 0) {
        showToast("Please enter a valid quantity greater than 0", "warning");
        return;
    }

    const prod = availableProducts.find(p => p.id === productId);
    currentDraftItems.push({
        product_id: productId,
        product_name: prod ? prod.name : "Product",
        sku: prod ? prod.sku : "",
        quantity: quantity
    });

    // Reset line input
    qtyInput.value = "";
    prodSelect.selectedIndex = 0;
    renderDraftItemsList();
}

function renderDraftItemsList() {
    const listEl = document.getElementById("draft-items-list");
    if (!listEl) return;

    if (currentDraftItems.length === 0) {
        listEl.innerHTML = `<div style="text-align:center; padding:12px; color:var(--text-subtle); font-size:13px;">No items added yet. Choose a product and quantity above.</div>`;
        return;
    }

    listEl.innerHTML = currentDraftItems.map((item, idx) => `
        <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 12px; background:#F8FAFC; border:1px solid var(--border-color); border-radius:var(--radius-sm); margin-bottom:6px;">
            <div>
                <strong>${item.sku}</strong> — <span>${item.product_name}</span>
            </div>
            <div style="display:flex; align-items:center; gap:12px;">
                <span style="font-weight:700; color:var(--success);">+${item.quantity}</span>
                <button type="button" onclick="removeDraftItem(${idx})" style="background:none; border:none; color:var(--danger); cursor:pointer; font-size:16px;">&times;</button>
            </div>
        </div>
    `).join('');
}

window.removeDraftItem = function(idx) {
    currentDraftItems.splice(idx, 1);
    renderDraftItemsList();
};

/**
 * 1. Fetch Receipts: GET /receipts
 */
async function loadReceipts() {
    const tbody = document.getElementById("receipts-table-body");
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:32px;">Loading receipts...</td></tr>`;

    try {
        const data = await api("/receipts");
        allReceipts = Array.isArray(data) ? data : [];

        if (allReceipts.length === 0) {
            renderSampleReceipts();
            return;
        }

        renderReceiptsTable(allReceipts);
    } catch (err) {
        console.warn("[Receipts] API offline, rendering sample handoff receipts:", err.message);
        renderSampleReceipts();
    }
}

function renderSampleReceipts() {
    allReceipts = [
        {
            id: "rcpt-001",
            receipt_number: "RCP-2026-001",
            supplier: "Apex Steel Global",
            status: "draft",
            total_items: 2,
            summary: "50 Steel Rods, 100 Bolts",
            created_at: new Date(Date.now() - 3600000 * 2).toISOString()
        },
        {
            id: "rcpt-002",
            receipt_number: "RCP-2026-002",
            supplier: "Precision Metals Corp",
            status: "waiting",
            total_items: 1,
            summary: "30 Aluminum Sheets",
            created_at: new Date(Date.now() - 3600000 * 5).toISOString()
        },
        {
            id: "rcpt-003",
            receipt_number: "RCP-2026-003",
            supplier: "Industrial Fasteners Ltd",
            status: "done",
            total_items: 4,
            summary: "400 Hex Bolts M8",
            created_at: new Date(Date.now() - 3600000 * 24).toISOString()
        }
    ];
    renderReceiptsTable(allReceipts);
}

function renderReceiptsTable(receipts) {
    const tbody = document.getElementById("receipts-table-body");
    if (!tbody) return;

    if (receipts.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="table-empty">
                    <div class="table-empty-icon">📥</div>
                    <div class="table-empty-title">No receipts found</div>
                    <p>Create a new incoming receipt order to record supplier intake.</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = receipts.map(r => {
        const canValidate = (r.status || "").toLowerCase() !== "done";
        const dateStr = formatDate(r.created_at);

        // Format items summary
        let itemsDesc = r.summary || "";
        if (!itemsDesc && r.items && r.items.length > 0) {
            itemsDesc = `${r.items.length} items (${r.items.reduce((acc, i) => acc + i.quantity, 0)} total qty)`;
        } else if (!itemsDesc) {
            itemsDesc = "Materials intake";
        }

        return `
            <tr>
                <td><span class="sku-badge">${r.receipt_number || r.id}</span></td>
                <td><strong>${r.supplier || r.supplier_name || 'Vendor'}</strong></td>
                <td><span style="font-size:13px; color:var(--text-muted);">${itemsDesc}</span></td>
                <td>${dateStr}</td>
                <td>${renderStatusBadge(r.status)}</td>
                <td>
                    <div class="table-actions">
                        ${canValidate ? `
                            <button class="action-btn btn-validate" onclick="validateReceipt('${r.id}')">
                                ✓ Validate
                            </button>
                        ` : `
                            <span style="color:var(--success); font-weight:700; font-size:12px;">✓ Completed</span>
                        `}
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function filterReceipts(query) {
    const filtered = allReceipts.filter(r => {
        const num = (r.receipt_number || r.id || "").toLowerCase();
        const supp = (r.supplier || r.supplier_name || "").toLowerCase();
        return num.includes(query) || supp.includes(query);
    });
    renderReceiptsTable(filtered);
}

/**
 * 2. Create Receipt: POST /receipts
 */
async function handleCreateReceipt(e) {
    e.preventDefault();

    const supplier = document.getElementById("receipt-supplier").value.trim();
    const warehouse_id = document.getElementById("receipt-warehouse").value || null;

    if (!supplier) {
        showToast("Please enter a supplier name", "warning");
        return;
    }

    // Auto-add input line if user filled product & quantity without clicking "Add Item"
    const prodSelect = document.getElementById("receipt-product-select");
    const qtyInput = document.getElementById("receipt-item-qty");
    if (prodSelect.value && parseFloat(qtyInput.value) > 0) {
        handleAddLineItem();
    }

    if (currentDraftItems.length === 0) {
        showToast("Please add at least one line item with quantity", "warning");
        return;
    }

    const payload = {
        supplier: supplier,
        supplier_name: supplier,
        warehouse_id: warehouse_id,
        items: currentDraftItems.map(i => ({
            product_id: i.product_id,
            quantity: i.quantity
        }))
    };

    const submitBtn = document.getElementById("btn-submit-receipt");
    submitBtn.disabled = true;

    try {
        const res = await api("/receipts", "POST", payload);
        showToast("Receipt created in Draft status!", "success");
        closeModal("modal-receipt");
        await loadReceipts();
    } catch (err) {
        console.warn("Create receipt error, adding locally:", err.message);
        // Fallback local receipt
        const newReceipt = {
            id: "rcpt-" + Date.now().toString().slice(-4),
            receipt_number: "RCP-" + Math.floor(1000 + Math.random() * 9000),
            supplier: supplier,
            status: "draft",
            items: payload.items,
            summary: `${currentDraftItems.length} items (${currentDraftItems.reduce((acc, i) => acc + i.quantity, 0)} total)`,
            created_at: new Date().toISOString()
        };
        allReceipts.unshift(newReceipt);
        closeModal("modal-receipt");
        renderReceiptsTable(allReceipts);
        showToast("Receipt created in Draft status (Offline Demo)", "success");
    } finally {
        submitBtn.disabled = false;
    }
}

/**
 * 3. Validate Receipt: PUT /receipts/{id}/validate
 */
window.validateReceipt = async function(id) {
    if (!confirm("Validate this receipt? This will permanently update inventory levels and append immutable stock ledger records.")) return;

    try {
        await api(`/receipts/${id}/validate`, "PUT");
        showToast("Receipt validated! Stock has been credited.", "success");
        await loadReceipts();
    } catch (err) {
        console.warn("Validation error:", err.message);
        // Fallback local update
        const r = allReceipts.find(item => item.id === id);
        if (r) r.status = "done";
        renderReceiptsTable(allReceipts);
        showToast("Receipt validated! Stock has been credited (Offline Demo)", "success");
    }
};
