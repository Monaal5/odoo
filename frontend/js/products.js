/**
 * StockSense IMS — Products Controller (products.js)
 * Developer 3 — Frontend Integration Layer
 */

let allProducts = [];
let allCategories = [];
let editingProductId = null;

document.addEventListener("DOMContentLoaded", async () => {
    if (!checkAuth()) return;

    renderSidebar("products");
    renderTopbar("Products", "Catalog");
    renderMobileBottomNav("products");
    setupModalHandlers();

    // Event listeners
    setupProductEventListeners();

    // Load initial data
    await loadCategories();
    await loadProducts();
});

function setupProductEventListeners() {
    // Search SKU / Name
    const searchInput = document.getElementById("product-search-input");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase().trim();
            filterProducts(query);
        });
    }

    // Category Filter Dropdown
    const catFilter = document.getElementById("category-filter");
    if (catFilter) {
        catFilter.addEventListener("change", () => {
            filterProducts(document.getElementById("product-search-input")?.value.toLowerCase().trim() || "");
        });
    }

    // Open Add Product Modal
    const addBtn = document.getElementById("btn-add-product");
    if (addBtn) {
        addBtn.addEventListener("click", () => {
            editingProductId = null;
            document.getElementById("modal-product-title").textContent = "Add New Product";
            document.getElementById("product-form").reset();
            document.getElementById("product-id").value = "";
            openModal("modal-product");
        });
    }

    // Form Submit (Create or Update)
    const productForm = document.getElementById("product-form");
    if (productForm) {
        productForm.addEventListener("submit", handleProductSubmit);
    }
}

/**
 * 1. Fetch Categories: GET /categories
 */
async function loadCategories() {
    try {
        const cats = await api("/categories");
        allCategories = Array.isArray(cats) ? cats : [];
    } catch (err) {
        console.warn("[Products] Categories API offline, using defaults:", err.message);
        allCategories = [
            { id: "cat-1", name: "Metal & Raw Materials" },
            { id: "cat-2", name: "Fasteners & Hardware" },
            { id: "cat-3", name: "Electrical & Wiring" },
            { id: "cat-4", name: "Finished Assemblies" }
        ];
    }
    populateCategoryDropdowns();
}

function populateCategoryDropdowns() {
    const modalSelect = document.getElementById("product-category");
    const filterSelect = document.getElementById("category-filter");

    const optionsHtml = allCategories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');

    if (modalSelect) {
        modalSelect.innerHTML = `<option value="">Select Category</option>` + optionsHtml;
    }
    if (filterSelect) {
        filterSelect.innerHTML = `<option value="">All Categories</option>` + optionsHtml;
    }
}

/**
 * 2. Fetch Products: GET /products
 */
async function loadProducts(search = "") {
    const tbody = document.getElementById("products-table-body");
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:32px;">Loading catalog products...</td></tr>`;

    try {
        const endpoint = search ? `/products?search=${encodeURIComponent(search)}` : "/products";
        const products = await api(endpoint);

        allProducts = Array.isArray(products) ? products : [];
        if (allProducts.length === 0) {
            renderSampleProducts();
            return;
        }

        renderProductsTable(allProducts);
    } catch (err) {
        console.warn("[Products] API offline, rendering baseline requirement products:", err.message);
        renderSampleProducts();
    }
}

function renderSampleProducts() {
    allProducts = [
        { id: "p-1", sku: "STL001", name: "Steel Rod 12mm", category_name: "Metal", category_id: "cat-1", qty: 120, unit_of_measure: "pcs", reorder_min: 50 },
        { id: "p-2", sku: "BLT044", name: "Hex Bolt M8x40", category_name: "Hardware", category_id: "cat-2", qty: 450, unit_of_measure: "boxes", reorder_min: 100 },
        { id: "p-3", sku: "ALM089", name: "Aluminum Sheet 2mm", category_name: "Metal", category_id: "cat-1", qty: 35, unit_of_measure: "sheets", reorder_min: 20 },
        { id: "p-4", sku: "CPR012", name: "Copper Wire Spool 50m", category_name: "Electrical", category_id: "cat-3", qty: 18, unit_of_measure: "spools", reorder_min: 10 },
        { id: "p-5", sku: "VLV102", name: "Brass Ball Valve 1/2\"", category_name: "Hardware", category_id: "cat-2", qty: 85, unit_of_measure: "units", reorder_min: 30 }
    ];
    renderProductsTable(allProducts);
}

function renderProductsTable(products) {
    const tbody = document.getElementById("products-table-body");
    const countEl = document.getElementById("products-count");
    if (!tbody) return;

    if (countEl) countEl.textContent = `${products.length} products found`;

    if (products.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="table-empty">
                    <div class="table-empty-icon">📦</div>
                    <div class="table-empty-title">No products match your criteria</div>
                    <p>Try searching for a different SKU or clearing filters.</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = products.map(p => {
        // Resolve category display name
        let catName = p.category_name;
        if (!catName && p.category_id) {
            const foundCat = allCategories.find(c => c.id === p.category_id);
            catName = foundCat ? foundCat.name : "General";
        }
        if (!catName) catName = "Metal";

        const displayQty = p.qty !== undefined ? p.qty : (p.current_stock ?? 120);

        return `
            <tr>
                <td><span class="sku-badge">${p.sku}</span></td>
                <td>
                    <div class="product-cell">
                        <span class="product-name">${p.name}</span>
                        <span class="product-desc">${p.unit_of_measure || 'units'} &bull; Min: ${p.reorder_min || 0}</span>
                    </div>
                </td>
                <td>
                    <span style="font-weight:600; color:var(--text-muted);">${catName}</span>
                </td>
                <td>
                    <strong style="font-size:14px;">${formatNumber(displayQty)}</strong>
                </td>
                <td>
                    <div class="table-actions">
                        <button class="action-btn" onclick="editProduct('${p.id}')">Edit</button>
                        <button class="action-btn btn-delete" onclick="deleteProduct('${p.id}', '${p.sku}')">Delete</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function filterProducts(query) {
    const selectedCat = document.getElementById("category-filter")?.value;
    
    let filtered = allProducts.filter(p => {
        const matchesQuery = !query || 
            p.sku.toLowerCase().includes(query) || 
            p.name.toLowerCase().includes(query);

        const matchesCat = !selectedCat || p.category_id === selectedCat;

        return matchesQuery && matchesCat;
    });

    renderProductsTable(filtered);
}

/**
 * 3. Handle Add / Edit Submission: POST /products or PUT /products/{id}
 */
async function handleProductSubmit(e) {
    e.preventDefault();

    const id = document.getElementById("product-id").value;
    const name = document.getElementById("product-name").value.trim();
    const sku = document.getElementById("product-sku").value.trim().toUpperCase();
    const category_id = document.getElementById("product-category").value || null;
    const unit_of_measure = document.getElementById("product-uom").value.trim() || "units";
    const reorder_min = parseFloat(document.getElementById("product-reorder-min").value) || 0;
    const reorder_max = parseFloat(document.getElementById("product-reorder-max").value) || 0;
    const description = document.getElementById("product-desc").value.trim();

    const payload = {
        name,
        sku,
        category_id,
        unit_of_measure,
        reorder_min,
        reorder_max,
        description
    };

    const submitBtn = document.getElementById("btn-save-product");
    submitBtn.disabled = true;

    try {
        if (id) {
            // Edit: PUT /products/{id}
            await api(`/products/${id}`, "PUT", payload);
            showToast(`Product ${sku} updated successfully!`, "success");
        } else {
            // Create: POST /products
            await api("/products", "POST", payload);
            showToast(`Product ${sku} created successfully!`, "success");
        }

        closeModal("modal-product");
        await loadProducts();
    } catch (err) {
        console.error("Save product error:", err);
        // If backend offline, simulate local update
        if (id) {
            const idx = allProducts.findIndex(p => p.id === id);
            if (idx !== -1) allProducts[idx] = { ...allProducts[idx], ...payload };
            showToast(`Product ${sku} updated (Offline Demo Mode)`, "success");
        } else {
            allProducts.unshift({ id: "p-" + Date.now(), qty: 0, ...payload });
            showToast(`Product ${sku} added (Offline Demo Mode)`, "success");
        }
        closeModal("modal-product");
        renderProductsTable(allProducts);
    } finally {
        submitBtn.disabled = false;
    }
}

/**
 * Open Edit Product Modal
 */
window.editProduct = function(id) {
    const p = allProducts.find(item => item.id === id);
    if (!p) return;

    editingProductId = id;
    document.getElementById("modal-product-title").textContent = `Edit Product: ${p.sku}`;
    document.getElementById("product-id").value = p.id;
    document.getElementById("product-name").value = p.name;
    document.getElementById("product-sku").value = p.sku;
    document.getElementById("product-category").value = p.category_id || "";
    document.getElementById("product-uom").value = p.unit_of_measure || "units";
    document.getElementById("product-reorder-min").value = p.reorder_min || 0;
    document.getElementById("product-reorder-max").value = p.reorder_max || 0;
    document.getElementById("product-desc").value = p.description || "";

    openModal("modal-product");
};

/**
 * 4. Delete Product: DELETE /products/{id}
 */
window.deleteProduct = async function(id, sku) {
    if (!confirm(`Are you sure you want to permanently delete product ${sku}?`)) return;

    try {
        await api(`/products/${id}`, "DELETE");
        showToast(`Product ${sku} deleted.`, "success");
        await loadProducts();
    } catch (err) {
        console.warn("Delete error:", err.message);
        // Fallback local deletion
        allProducts = allProducts.filter(p => p.id !== id);
        renderProductsTable(allProducts);
        showToast(`Product ${sku} deleted (Offline Demo)`, "info");
    }
};
