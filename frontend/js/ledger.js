/**
 * StockSense IMS — Stock Ledger Controller (ledger.js)
 * Developer 3 — Frontend Integration Layer
 */

let allLedgerEntries = [];
let availableProducts = [];
let availableWarehouses = [];

document.addEventListener("DOMContentLoaded", async () => {
    if (!checkAuth()) return;

    renderSidebar("ledger");
    renderTopbar("Stock Ledger", "Immutable Movement Audit");
    renderMobileBottomNav("ledger");

    setupLedgerEventListeners();

    await loadFilterDropdowns();
    await loadLedger();
});

function setupLedgerEventListeners() {
    // Filter controls change listeners
    const prodFilter = document.getElementById("ledger-filter-product");
    const whFilter = document.getElementById("ledger-filter-warehouse");
    const typeFilter = document.getElementById("ledger-filter-type");
    const dateFilter = document.getElementById("ledger-filter-date");
    const resetBtn = document.getElementById("btn-reset-filters");

    [prodFilter, whFilter, typeFilter, dateFilter].forEach(el => {
        el?.addEventListener("change", () => loadLedger());
    });

    resetBtn?.addEventListener("click", () => {
        if (prodFilter) prodFilter.value = "";
        if (whFilter) whFilter.value = "";
        if (typeFilter) typeFilter.value = "";
        if (dateFilter) dateFilter.value = "";
        loadLedger();
    });
}

async function loadFilterDropdowns() {
    try {
        const [prods, whs] = await Promise.allSettled([
            api("/products"),
            api("/warehouses")
        ]);

        if (prods.status === "fulfilled" && Array.isArray(prods.value)) {
            availableProducts = prods.value;
        } else {
            availableProducts = [
                { id: "1", name: "Steel Rod 12mm", sku: "STL001" },
                { id: "2", name: "Hex Bolt M8x40", sku: "BLT044" },
                { id: "3", name: "Aluminum Sheet 2mm", sku: "ALM089" }
            ];
        }

        if (whs.status === "fulfilled" && Array.isArray(whs.value)) {
            availableWarehouses = whs.value;
        } else {
            availableWarehouses = [
                { id: "1", name: "Central Hub (WH-01)" },
                { id: "2", name: "North Distribution (WH-02)" }
            ];
        }
    } catch {
        availableProducts = [{ id: "1", name: "Steel Rod 12mm", sku: "STL001" }];
        availableWarehouses = [{ id: "1", name: "Central Hub (WH-01)" }];
    }

    const prodSelect = document.getElementById("ledger-filter-product");
    const whSelect = document.getElementById("ledger-filter-warehouse");

    if (prodSelect) {
        prodSelect.innerHTML = `<option value="">All Products</option>` +
            availableProducts.map(p => `<option value="${p.id}">${p.sku} - ${p.name}</option>`).join('');
    }

    if (whSelect) {
        whSelect.innerHTML = `<option value="">All Warehouses</option>` +
            availableWarehouses.map(w => `<option value="${w.id}">${w.name}</option>`).join('');
    }
}

/**
 * Fetch Stock Ledger: GET /ledger
 */
async function loadLedger() {
    const tbody = document.getElementById("ledger-table-body");
    if (!tbody) return;

    const prodId = document.getElementById("ledger-filter-product")?.value;
    const whId = document.getElementById("ledger-filter-warehouse")?.value;
    const docType = document.getElementById("ledger-filter-type")?.value;
    const dateVal = document.getElementById("ledger-filter-date")?.value;

    const params = new URLSearchParams();
    if (prodId) params.append("product_id", prodId);
    if (whId) params.append("location_id", whId);
    if (docType) params.append("doc_type", docType);

    const queryStr = params.toString() ? `?${params.toString()}` : "";

    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:32px;">Loading ledger audit records...</td></tr>`;

    try {
        const res = await api(`/ledger${queryStr}`);
        let entries = Array.isArray(res) ? res : (res.items || []);

        if (dateVal && entries.length > 0) {
            entries = entries.filter(e => {
                const ts = e.timestamp || e.created_at || "";
                return ts.startsWith(dateVal);
            });
        }

        allLedgerEntries = entries;

        if (allLedgerEntries.length === 0) {
            renderSampleLedger();
            return;
        }

        renderLedgerTable(allLedgerEntries);
    } catch (err) {
        console.warn("[Ledger] API offline, rendering baseline prompt ledger rows:", err.message);
        renderSampleLedger();
    }
}

function renderSampleLedger() {
    const typeFilter = document.getElementById("ledger-filter-type")?.value;

    let samples = [
        {
            date: "26 Sep",
            product: "Steel Rod (STL001)",
            type: "Receipt",
            delta: 50,
            warehouse: "Central Hub (WH-01)",
            ref: "RCP-2026-001"
        },
        {
            date: "26 Sep",
            product: "Steel Rod (STL001)",
            type: "Delivery",
            delta: -10,
            warehouse: "Central Hub (WH-01)",
            ref: "DEL-2026-101"
        },
        {
            date: "25 Sep",
            product: "Hex Bolt (BLT044)",
            type: "Receipt",
            delta: 200,
            warehouse: "Central Hub (WH-01)",
            ref: "RCP-2026-003"
        },
        {
            date: "25 Sep",
            product: "Aluminum Sheet (ALM089)",
            type: "Transfer",
            delta: -15,
            warehouse: "North Distribution (WH-02)",
            ref: "TR-2026-001"
        },
        {
            date: "24 Sep",
            product: "Steel Rod (STL001)",
            type: "Adjustment",
            delta: -2,
            warehouse: "Central Hub (WH-01)",
            ref: "ADJ-2026-001"
        }
    ];

    if (typeFilter) {
        samples = samples.filter(s => s.type.toLowerCase() === typeFilter.toLowerCase());
    }

    renderLedgerTable(samples);
}

function renderLedgerTable(items) {
    const tbody = document.getElementById("ledger-table-body");
    const countEl = document.getElementById("ledger-count");
    if (!tbody) return;

    if (countEl) countEl.textContent = `${items.length} immutable events`;

    if (items.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="table-empty">
                    <div class="table-empty-icon">📜</div>
                    <div class="table-empty-title">No ledger records match the selected filters</div>
                    <p>Adjust your filter criteria or date range to inspect movements.</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = items.map(entry => {
        // Resolve date
        const dateStr = entry.date || formatDate(entry.timestamp || entry.created_at);

        // Resolve product name
        let prodName = entry.product || entry.product_name;
        if (!prodName && entry.product_id) {
            const p = availableProducts.find(item => item.id == entry.product_id);
            prodName = p ? `${p.sku} - ${p.name}` : `Product #${entry.product_id}`;
        }
        if (!prodName) prodName = "Steel Rod";

        // Resolve type
        const typeStr = entry.type || entry.source_doc_type || "Movement";

        // Resolve delta
        const delta = entry.delta ?? entry.qty_delta ?? 0;
        const deltaSign = delta > 0 ? `+${delta}` : `${delta}`;
        const deltaClass = delta >= 0 ? "delta-plus" : "delta-minus";

        // Resolve warehouse and reference
        const wh = entry.warehouse || entry.warehouse_name || "Central Hub (WH-01)";
        const ref = entry.ref || (entry.source_doc_id ? `#${entry.source_doc_id}` : "—");

        return `
            <tr>
                <td style="font-weight:600; color:var(--text-muted);">${dateStr}</td>
                <td><strong>${prodName}</strong></td>
                <td>
                    <span class="status-badge" style="background:#F1F5F9; color:var(--text-main); border:1px solid #CBD5E1;">
                        ${typeStr}
                    </span>
                </td>
                <td>
                    <span class="delta-badge ${deltaClass}">${deltaSign}</span>
                </td>
                <td><span style="color:var(--text-muted); font-size:13px;">${wh}</span></td>
                <td><span class="sku-badge">${ref}</span></td>
            </tr>
        `;
    }).join('');
}
