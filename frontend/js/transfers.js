/**
 * StockSense IMS — Transfers Controller (transfers.js)
 * Developer 3 — Frontend Integration Layer
 */

let allTransfers = [];
let availableProducts = [];
let availableWarehouses = [];

document.addEventListener("DOMContentLoaded", async () => {
    if (!checkAuth()) return;

    renderSidebar("transfers");
    renderTopbar("Internal Transfers", "Inter-Warehouse Relocation");
    renderMobileBottomNav("transfers");
    setupModalHandlers();

    setupTransferEventListeners();

    await loadDropdownData();
    await loadTransfers();
});

function setupTransferEventListeners() {
    const newBtn = document.getElementById("btn-new-transfer");
    if (newBtn) {
        newBtn.addEventListener("click", () => {
            document.getElementById("transfer-form").reset();
            openModal("modal-transfer");
        });
    }

    const form = document.getElementById("transfer-form");
    if (form) {
        form.addEventListener("submit", handleCreateTransfer);
    }
}

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
                { id: "p-3", name: "Aluminum Sheet 2mm", sku: "ALM089" }
            ];
        }

        if (whs.status === "fulfilled" && Array.isArray(whs.value)) {
            availableWarehouses = whs.value;
        } else {
            availableWarehouses = [
                { id: "wh-1", name: "Central Hub (WH-01)" },
                { id: "wh-2", name: "North Distribution (WH-02)" },
                { id: "wh-3", name: "South Yard Depot (WH-03)" }
            ];
        }
    } catch {
        availableProducts = [{ id: "p-1", name: "Steel Rod 12mm", sku: "STL001" }];
        availableWarehouses = [
            { id: "wh-1", name: "Central Hub (WH-01)" },
            { id: "wh-2", name: "North Distribution (WH-02)" }
        ];
    }

    populateDropdowns();
}

function populateDropdowns() {
    const prodSelect = document.getElementById("transfer-product");
    const fromSelect = document.getElementById("transfer-from-wh");
    const toSelect = document.getElementById("transfer-to-wh");

    if (prodSelect) {
        prodSelect.innerHTML = `<option value="">Select Product...</option>` +
            availableProducts.map(p => `<option value="${p.id}">${p.sku} - ${p.name}</option>`).join('');
    }

    const whOptions = availableWarehouses.map(w => `<option value="${w.id}">${w.name}</option>`).join('');
    if (fromSelect) {
        fromSelect.innerHTML = whOptions;
        fromSelect.selectedIndex = 0;
    }
    if (toSelect) {
        toSelect.innerHTML = whOptions;
        toSelect.selectedIndex = availableWarehouses.length > 1 ? 1 : 0;
    }
}

/**
 * 1. Fetch Transfers: GET /transfers
 */
async function loadTransfers() {
    const tbody = document.getElementById("transfers-table-body");
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:32px;">Loading internal transfers...</td></tr>`;

    try {
        const data = await api("/transfers");
        allTransfers = Array.isArray(data) ? data : [];

        if (allTransfers.length === 0) {
            renderSampleTransfers();
            return;
        }

        renderTransfersTable(allTransfers);
    } catch (err) {
        console.warn("[Transfers] API offline, rendering sample transfers:", err.message);
        renderSampleTransfers();
    }
}

function renderSampleTransfers() {
    allTransfers = [
        {
            id: "tr-001",
            transfer_number: "TR-2026-001",
            product_name: "Steel Rod 12mm",
            from_warehouse_name: "Central Hub (WH-01)",
            to_warehouse_name: "North Distribution (WH-02)",
            quantity: 25,
            status: "draft",
            created_at: new Date(Date.now() - 3600000 * 3).toISOString()
        },
        {
            id: "tr-002",
            transfer_number: "TR-2026-002",
            product_name: "Hex Bolt M8x40",
            from_warehouse_name: "South Yard Depot (WH-03)",
            to_warehouse_name: "Central Hub (WH-01)",
            quantity: 100,
            status: "done",
            created_at: new Date(Date.now() - 3600000 * 18).toISOString()
        }
    ];
    renderTransfersTable(allTransfers);
}

function renderTransfersTable(transfers) {
    const tbody = document.getElementById("transfers-table-body");
    if (!tbody) return;

    if (transfers.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="table-empty">
                    <div class="table-empty-icon">🔄</div>
                    <div class="table-empty-title">No stock transfers found</div>
                    <p>Relocate goods between bins and warehouses.</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = transfers.map(t => {
        const canValidate = (t.status || "").toLowerCase() !== "done";
        const dateStr = formatDate(t.created_at);

        // Resolve product name
        let prodTitle = t.product_name;
        if (!prodTitle && t.product_id) {
            const p = availableProducts.find(item => item.id === t.product_id);
            prodTitle = p ? `${p.sku} - ${p.name}` : t.product_id;
        }

        // Resolve warehouses
        let fromWh = t.from_warehouse_name || t.from_warehouse || "Central Hub (WH-01)";
        let toWh = t.to_warehouse_name || t.to_warehouse || "North Depot (WH-02)";

        return `
            <tr>
                <td><span class="sku-badge">${t.transfer_number || t.id}</span></td>
                <td><strong>${prodTitle || 'Product Material'}</strong></td>
                <td><span style="color:var(--text-muted); font-size:13px;">${fromWh}</span></td>
                <td><span style="color:var(--primary); font-weight:600; font-size:13px;">➔ ${toWh}</span></td>
                <td><strong>${formatNumber(t.quantity)}</strong></td>
                <td>${renderStatusBadge(t.status)}</td>
                <td>
                    <div class="table-actions">
                        ${canValidate ? `
                            <button class="action-btn btn-validate" onclick="validateTransfer('${t.id}')">
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

/**
 * 2. Create Transfer: POST /transfers
 */
async function handleCreateTransfer(e) {
    e.preventDefault();

    const product_id = document.getElementById("transfer-product").value;
    const from_warehouse = document.getElementById("transfer-from-wh").value;
    const to_warehouse = document.getElementById("transfer-to-wh").value;
    const quantity = parseFloat(document.getElementById("transfer-qty").value);

    if (!product_id) {
        showToast("Please choose a product", "warning");
        return;
    }
    if (from_warehouse === to_warehouse) {
        showToast("Source and Destination warehouses cannot be identical", "warning");
        return;
    }
    if (isNaN(quantity) || quantity <= 0) {
        showToast("Please enter a valid quantity", "warning");
        return;
    }

    const payload = {
        product_id,
        from_warehouse,
        from_warehouse_id: from_warehouse,
        to_warehouse,
        to_warehouse_id: to_warehouse,
        quantity
    };

    const submitBtn = document.getElementById("btn-submit-transfer");
    submitBtn.disabled = true;

    try {
        await api("/transfers", "POST", payload);
        showToast("Stock transfer initiated in Draft!", "success");
        closeModal("modal-transfer");
        await loadTransfers();
    } catch (err) {
        console.warn("Create transfer error, adding locally:", err.message);
        const prod = availableProducts.find(p => p.id === product_id);
        const fWh = availableWarehouses.find(w => w.id === from_warehouse);
        const tWh = availableWarehouses.find(w => w.id === to_warehouse);

        allTransfers.unshift({
            id: "tr-" + Date.now().toString().slice(-4),
            transfer_number: "TR-" + Math.floor(1000 + Math.random() * 9000),
            product_name: prod ? `${prod.sku} - ${prod.name}` : "Product Item",
            from_warehouse_name: fWh ? fWh.name : "WH-01",
            to_warehouse_name: tWh ? tWh.name : "WH-02",
            quantity,
            status: "draft",
            created_at: new Date().toISOString()
        });

        closeModal("modal-transfer");
        renderTransfersTable(allTransfers);
        showToast("Stock transfer created (Offline Demo)", "success");
    } finally {
        submitBtn.disabled = false;
    }
}

/**
 * 3. Validate Transfer: PUT /transfers/{id}/validate
 */
window.validateTransfer = async function(id) {
    if (!confirm("Validate internal transfer? Stock will be debited from source and credited to destination.")) return;

    try {
        await api(`/transfers/${id}/validate`, "PUT");
        showToast("Transfer validated and completed!", "success");
        await loadTransfers();
    } catch (err) {
        console.warn("Validation error:", err.message);
        const t = allTransfers.find(item => item.id === id);
        if (t) t.status = "done";
        renderTransfersTable(allTransfers);
        showToast("Transfer validated (Offline Demo)", "success");
    }
};
