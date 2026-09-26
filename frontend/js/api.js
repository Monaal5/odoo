/**
 * StockSense IMS — Shared Fetch Wrapper (api.js)
 * Developer 3 — Frontend Integration Layer
 */

const BASE_URL = window.STOCKSENSE_BASE_URL || "http://localhost:8000";

// In-memory / localStorage fallback storage for offline simulation
const STORAGE_PREFIX = "stocksense_mock_";

function getMockStorage(key, defaultVal = []) {
    try {
        const stored = localStorage.getItem(STORAGE_PREFIX + key);
        return stored ? JSON.parse(stored) : defaultVal;
    } catch {
        return defaultVal;
    }
}

function setMockStorage(key, val) {
    try {
        localStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(val));
    } catch (e) {
        console.warn("Storage error", e);
    }
}

/**
 * Normalizes endpoints between Developer 3 prompt spec and FastAPI backend router mounts.
 * - e.g. "/login" -> "/api/v1/auth/login"
 * - e.g. "/dashboard/kpis" -> "/api/v1/dashboard/kpis"
 * - e.g. "/products" -> "/api/v1/products"
 */
function resolveEndpoint(endpoint) {
    if (endpoint.startsWith("http://") || endpoint.startsWith("https://")) {
        return endpoint;
    }
    
    let path = endpoint.startsWith("/") ? endpoint : "/" + endpoint;

    // If already prefixed with /api/v1, use directly
    if (path.startsWith("/api/v1")) {
        return BASE_URL + path;
    }

    // Map Auth routes
    const authRoutes = ["/login", "/signup", "/forgot-password", "/reset-password"];
    for (const r of authRoutes) {
        if (path === r || path.startsWith(r + "/")) {
            return BASE_URL + "/api/v1/auth" + path;
        }
    }

    // All other business routes are mounted at /api/v1
    return BASE_URL + "/api/v1" + path;
}

/**
 * Primary API invocation function
 * @param {string} endpoint - API path (e.g. "/products", "/dashboard/kpis")
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE, etc.)
 * @param {object|null} body - Request payload
 * @returns {Promise<any>} Parsed response data
 */
async function api(endpoint, method = "GET", body = null) {
    const token = localStorage.getItem("token");
    const fullUrl = resolveEndpoint(endpoint);

    const headers = {};
    if (body !== null && !(body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }
    if (token) {
        headers["Authorization"] = "Bearer " + token;
    }

    const options = {
        method,
        headers,
    };

    if (body !== null) {
        options.body = (body instanceof FormData) ? body : JSON.stringify(body);
    }

    try {
        const res = await fetch(fullUrl, options);

        // Handle unauthorized or missing backend auth by falling back to offline simulation
        if (res.status === 401) {
            console.warn(`[StockSense API] 401 Unauthorized for ${endpoint}. Falling back to demo mode.`);
            return handleOfflineSimulation(endpoint, method, body);
        }


        // Check if response is empty (e.g., 204 No Content)
        if (res.status === 204) {
            return { success: true };
        }

        const contentType = res.headers.get("content-type") || "";
        let data;
        if (contentType.includes("application/json")) {
            data = await res.json();
        } else if (contentType.includes("text/csv") || contentType.includes("application/pdf")) {
            return await res.blob();
        } else {
            const text = await res.text();
            try {
                data = JSON.parse(text);
            } catch (e) {
                data = { raw: text };
            }
        }

        if (!res.ok) {
            const errorMsg = (data && (data.detail || data.message || data.error)) || `HTTP ${res.status}: ${res.statusText}`;
            const error = new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
            error.status = res.status;
            error.data = data;
            throw error;
        }

        // Inform UI that API is live
        window.dispatchEvent(new CustomEvent("api:online", { detail: { endpoint } }));

        return data;
    } catch (err) {
        // If it's an HTTP response error with status code (like 400 Bad Request, 401, etc.), throw it
        if (err.status) {
            throw err;
        }

        // If backend connection was refused (server offline), activate offline demo simulation
        console.warn(`[StockSense API] Backend (${fullUrl}) unreachable (${err.message}). Using Seamless Offline Simulation Mode.`);
        window.dispatchEvent(new CustomEvent("api:offline", { detail: { endpoint, error: err } }));

        return handleOfflineSimulation(endpoint, method, body);
    }
}

/**
 * Seamless Offline Simulation Router
 * Provides realistic responses when the FastAPI backend on port 8000 is not running.
 */
function handleOfflineSimulation(endpoint, method, body) {
    const cleanPath = endpoint.replace("/api/v1/auth", "").replace("/api/v1", "");

    // 1. AUTH: POST /signup
    if (cleanPath.startsWith("/signup")) {
        const users = getMockStorage("users", []);
        const email = body ? body.email : "user@stocksense.io";
        users.push(body);
        setMockStorage("users", users);
        return {
            message: "Account created successfully! Please log in.",
            user: { email, name: body ? body.name : "User", role: body ? body.role : "staff" }
        };
    }

    // 2. AUTH: POST /login
    if (cleanPath.startsWith("/login")) {
        const email = body ? body.email : "admin@stocksense.io";
        const name = body && body.name ? body.name : email.split("@")[0];
        return {
            access_token: "demo-jwt-token-stocksense-offline-" + Date.now(),
            token_type: "bearer",
            user: {
                id: "usr-" + Date.now().toString().slice(-4),
                name: name,
                email: email,
                role: "Inventory Manager"
            }
        };
    }

    // 3. AUTH: POST /forgot-password
    if (cleanPath.startsWith("/forgot-password")) {
        return {
            message: "Password reset OTP sent to registered email address (OTP: 749210)."
        };
    }

    // 4. DASHBOARD: GET /dashboard/kpis
    if (cleanPath.startsWith("/dashboard/kpis")) {
        return {
            total_products: 248,
            low_stock: 12,
            out_of_stock: 3,
            pending_receipts: 4,
            pending_deliveries: 7,
            pending_transfers: 2
        };
    }

    // 5. DASHBOARD: GET /dashboard/activity
    if (cleanPath.startsWith("/dashboard/activity")) {
        return {
            items: [
                {
                    id: "act-1",
                    product_name: "Steel Rod 12mm",
                    warehouse_name: "Central Hub (WH-01)",
                    qty_delta: 50,
                    source_document_type: "RECEIPT",
                    created_at: new Date(Date.now() - 3600000 * 2).toISOString()
                },
                {
                    id: "act-2",
                    product_name: "Hex Bolt M8x40",
                    warehouse_name: "Central Hub (WH-01)",
                    qty_delta: -10,
                    source_document_type: "DELIVERY",
                    created_at: new Date(Date.now() - 3600000 * 1).toISOString()
                },
                {
                    id: "act-3",
                    product_name: "Aluminum Sheet 2mm",
                    warehouse_name: "North Distribution (WH-02)",
                    qty_delta: 15,
                    source_document_type: "TRANSFER",
                    created_at: new Date(Date.now() - 3600000 * 4).toISOString()
                }
            ],
            total: 3
        };
    }

    // 6. ALERTS: GET /alerts
    if (cleanPath.startsWith("/alerts")) {
        return [
            {
                id: 1,
                product_id: 1,
                location_id: 1,
                current_stock: 4,
                min_stock: 20,
                status: "ACTIVE",
                message: "Critical Low Stock: 10mm Steel Rebar"
            },
            {
                id: 2,
                product_id: 2,
                location_id: 1,
                current_stock: 15,
                min_stock: 50,
                status: "ACTIVE",
                message: "Threshold Warning: Hex Bolts M8"
            }
        ];
    }

    // 7. PRODUCTS: /products
    if (cleanPath.startsWith("/products")) {
        let prods = getMockStorage("products", [
            { id: "p-1", sku: "STL001", name: "Steel Rod 12mm", category_name: "Metal", category_id: "cat-1", qty: 120, unit_of_measure: "pcs", reorder_min: 50, reorder_max: 500 },
            { id: "p-2", sku: "BLT044", name: "Hex Bolt M8x40", category_name: "Hardware", category_id: "cat-2", qty: 450, unit_of_measure: "boxes", reorder_min: 100, reorder_max: 1000 },
            { id: "p-3", sku: "ALM089", name: "Aluminum Sheet 2mm", category_name: "Metal", category_id: "cat-1", qty: 35, unit_of_measure: "sheets", reorder_min: 20, reorder_max: 200 },
            { id: "p-4", sku: "CPR012", name: "Copper Wire Spool 50m", category_name: "Electrical", category_id: "cat-3", qty: 18, unit_of_measure: "spools", reorder_min: 10, reorder_max: 100 },
            { id: "p-5", sku: "VLV102", name: "Brass Ball Valve 1/2\"", category_name: "Hardware", category_id: "cat-2", qty: 85, unit_of_measure: "units", reorder_min: 30, reorder_max: 250 }
        ]);

        if (method === "GET") {
            return prods;
        } else if (method === "POST") {
            const newProd = { id: "p-" + Date.now(), qty: 0, ...body };
            prods.unshift(newProd);
            setMockStorage("products", prods);
            return newProd;
        } else if (method === "PUT") {
            const id = cleanPath.split("/")[2];
            const idx = prods.findIndex(p => p.id === id);
            if (idx !== -1) prods[idx] = { ...prods[idx], ...body };
            setMockStorage("products", prods);
            return prods[idx] || body;
        } else if (method === "DELETE") {
            const id = cleanPath.split("/")[2];
            prods = prods.filter(p => p.id !== id);
            setMockStorage("products", prods);
            return { success: true };
        }
    }

    // 8. CATEGORIES: /categories
    if (cleanPath.startsWith("/categories")) {
        return [
            { id: "cat-1", name: "Metal & Raw Materials" },
            { id: "cat-2", name: "Fasteners & Hardware" },
            { id: "cat-3", name: "Electrical & Wiring" },
            { id: "cat-4", name: "Finished Assemblies" }
        ];
    }

    // 9. WAREHOUSES: /warehouses
    if (cleanPath.startsWith("/warehouses")) {
        return [
            { id: "wh-1", name: "Central Hub (WH-01)" },
            { id: "wh-2", name: "North Distribution (WH-02)" },
            { id: "wh-3", name: "South Yard Depot (WH-03)" }
        ];
    }

    // 10. RECEIPTS: /receipts
    if (cleanPath.startsWith("/receipts")) {
        let receipts = getMockStorage("receipts", [
            { id: "rcpt-001", receipt_number: "RCP-2026-001", supplier: "Apex Steel Global", status: "draft", summary: "50 Steel Rods", created_at: new Date(Date.now() - 7200000).toISOString() },
            { id: "rcpt-002", receipt_number: "RCP-2026-002", supplier: "Precision Metals Corp", status: "waiting", summary: "30 Aluminum Sheets", created_at: new Date(Date.now() - 14400000).toISOString() },
            { id: "rcpt-003", receipt_number: "RCP-2026-003", supplier: "Industrial Fasteners Ltd", status: "done", summary: "400 Hex Bolts", created_at: new Date(Date.now() - 86400000).toISOString() }
        ]);

        if (cleanPath.includes("/validate")) {
            const id = cleanPath.split("/")[2];
            const r = receipts.find(item => item.id === id);
            if (r) r.status = "done";
            setMockStorage("receipts", receipts);
            return r || { success: true, status: "done" };
        }

        if (method === "GET") {
            return receipts;
        } else if (method === "POST") {
            const newR = {
                id: "rcpt-" + Date.now().toString().slice(-4),
                receipt_number: "RCP-2026-" + Math.floor(100 + Math.random() * 900),
                status: "draft",
                created_at: new Date().toISOString(),
                ...body
            };
            receipts.unshift(newR);
            setMockStorage("receipts", receipts);
            return newR;
        }
    }

    // 11. DELIVERIES: /deliveries
    if (cleanPath.startsWith("/deliveries")) {
        let dels = getMockStorage("deliveries", [
            { id: "del-001", delivery_number: "DEL-2026-101", customer: "Matrix Infrastructure Ltd", status: "waiting", summary: "10 Hex Bolts", created_at: new Date(Date.now() - 3600000).toISOString() },
            { id: "del-002", delivery_number: "DEL-2026-102", customer: "Skyline Engineering Corp", status: "draft", summary: "15 Aluminum Sheets", created_at: new Date(Date.now() - 18000000).toISOString() },
            { id: "del-003", delivery_number: "DEL-2026-103", customer: "Vanguard Heavy Industries", status: "done", summary: "100 Hex Bolts", created_at: new Date(Date.now() - 172800000).toISOString() }
        ]);

        if (cleanPath.includes("/validate")) {
            const id = cleanPath.split("/")[2];
            const d = dels.find(item => item.id === id);
            if (d) d.status = "done";
            setMockStorage("deliveries", dels);
            return d || { success: true, status: "done" };
        }

        if (method === "GET") {
            return dels;
        } else if (method === "POST") {
            const newD = {
                id: "del-" + Date.now().toString().slice(-4),
                delivery_number: "DEL-2026-" + Math.floor(100 + Math.random() * 900),
                status: "draft",
                created_at: new Date().toISOString(),
                ...body
            };
            dels.unshift(newD);
            setMockStorage("deliveries", dels);
            return newD;
        }
    }

    // 12. TRANSFERS: /transfers
    if (cleanPath.startsWith("/transfers")) {
        let transfers = getMockStorage("transfers", [
            { id: "tr-001", transfer_number: "TR-2026-001", product_name: "Steel Rod 12mm", from_warehouse_name: "Central Hub (WH-01)", to_warehouse_name: "North Distribution (WH-02)", quantity: 25, status: "draft", created_at: new Date(Date.now() - 10800000).toISOString() },
            { id: "tr-002", transfer_number: "TR-2026-002", product_name: "Hex Bolt M8x40", from_warehouse_name: "South Yard Depot (WH-03)", to_warehouse_name: "Central Hub (WH-01)", quantity: 100, status: "done", created_at: new Date(Date.now() - 64800000).toISOString() }
        ]);

        if (cleanPath.includes("/validate")) {
            const id = cleanPath.split("/")[2];
            const t = transfers.find(item => item.id === id);
            if (t) t.status = "done";
            setMockStorage("transfers", transfers);
            return t || { success: true, status: "done" };
        }

        if (method === "GET") {
            return transfers;
        } else if (method === "POST") {
            const newT = {
                id: "tr-" + Date.now().toString().slice(-4),
                transfer_number: "TR-2026-" + Math.floor(100 + Math.random() * 900),
                status: "draft",
                created_at: new Date().toISOString(),
                ...body
            };
            transfers.unshift(newT);
            setMockStorage("transfers", transfers);
            return newT;
        }
    }

    // 13. ADJUSTMENTS: /adjustments
    if (cleanPath.startsWith("/adjustments")) {
        return {
            id: Date.now(),
            adjustment_number: "ADJ-" + Math.floor(100 + Math.random() * 900),
            counted_qty: body ? body.counted_quantity : 100,
            system_qty: 102,
            delta_qty: -2,
            created_at: new Date().toISOString()
        };
    }

    // 14. LEDGER: /ledger
    if (cleanPath.startsWith("/ledger")) {
        return [
            { date: "26 Sep", product: "Steel Rod (STL001)", type: "Receipt", delta: 50, warehouse: "Central Hub (WH-01)", ref: "RCP-2026-001" },
            { date: "26 Sep", product: "Steel Rod (STL001)", type: "Delivery", delta: -10, warehouse: "Central Hub (WH-01)", ref: "DEL-2026-101" },
            { date: "25 Sep", product: "Hex Bolt (BLT044)", type: "Receipt", delta: 200, warehouse: "Central Hub (WH-01)", ref: "RCP-2026-003" },
            { date: "25 Sep", product: "Aluminum Sheet (ALM089)", type: "Transfer", delta: -15, warehouse: "North Distribution (WH-02)", ref: "TR-2026-001" },
            { date: "24 Sep", product: "Steel Rod (STL001)", type: "Adjustment", delta: -2, warehouse: "Central Hub (WH-01)", ref: "ADJ-2026-001" }
        ];
    }

    // 15. PROFILE: /profile
    if (cleanPath.startsWith("/profile")) {
        if (method === "GET") {
            const user = JSON.parse(localStorage.getItem("user") || "{}");
            return {
                id: user.id || "usr-01",
                name: user.name || "Alex Vance",
                email: user.email || "admin@stocksense.io",
                role: user.role || "Inventory Manager",
                is_active: true,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            };
        } else if (method === "PUT") {
            return {
                ...body,
                role: "Inventory Manager",
                is_active: true
            };
        }
    }

    // 16. AI ASSISTANT: /ai/chat

    if (cleanPath.startsWith("/ai")) {
        const q = (body && body.query) ? body.query.toLowerCase() : "";
        let ans = "Analyzed warehouse telemetry across all bays. Inventory is healthy and operating within safety margins.";
        if (q.includes("steel") || q.includes("rebar")) {
            ans = "Central Hub (WH-01) currently has 82 Steel Rods 12mm on hand across Rack A-1 and Rack B-2. Consumption velocity: 20 units/week.";
        } else if (q.includes("po") || q.includes("receipt") || q.includes("order")) {
            ans = "Purchase Order #PO-8822 drafted for 50 units of Steel Rods from Apex Steel. Expected delivery tomorrow morning.";
        } else if (q.includes("bolt") || q.includes("fastener")) {
            ans = "Hex Bolts M8x40 on hand: 450 boxes in Rack A-2, Bin 14. Stock is healthy and requires no replenishment.";
        } else if (q.includes("low") || q.includes("alert")) {
            ans = "Currently 2 active low stock alerts: Titanium Fasteners (BLT-044) and 10mm Steel Rebar. Automated purchase orders recommended.";
        }
        return { answer: ans, context: { model: "StockSense-AI-v2", timestamp: new Date().toISOString() } };
    }

    // 17. DEMAND FORECASTING: /forecast
    if (cleanPath.startsWith("/forecast")) {
        return {
            items: [
                { product: "Steel Rod 12mm", days_to_stockout: 6, recommended_order: 120, current_stock: 82, daily_consumption_rate: 13.6 },
                { product: "Hex Bolt M8x40", days_to_stockout: 32, recommended_order: 0, current_stock: 450, daily_consumption_rate: 14.0 },
                { product: "Aluminum Sheet 2mm", days_to_stockout: 4, recommended_order: 60, current_stock: 12, daily_consumption_rate: 3.0 },
                { product: "Copper Wire Spool 50m", days_to_stockout: 9, recommended_order: 25, current_stock: 18, daily_consumption_rate: 2.0 }
            ],
            total: 4
        };
    }

    // 18. ANALYTICS & ANOMALY DETECTION: /analytics
    if (cleanPath.startsWith("/analytics/anomalies")) {
        return {
            anomalies: [
                { severity: "High", message: "Outbound delivery spike detected: Hex Bolts volume is 3.2× higher than 30-day average.", anomaly_type: "UNUSUAL_DELIVERY", product_name: "Hex Bolt M8x40" },
                { severity: "Medium", message: "Aluminum Sheet 2mm has 2 repeated damage write-offs in the last 7 days.", anomaly_type: "REPEATED_DAMAGE", product_name: "Aluminum Sheet 2mm" }
            ],
            total_anomalies: 2
        };
    }
    if (cleanPath.startsWith("/analytics/summary")) {
        return {
            total_consumption_30d: 1420,
            total_shrinkage_30d: 18,
            high_velocity_products_count: 5,
            anomalies_count: 2
        };
    }

    // 19. AUDIT TRAIL: /audit
    if (cleanPath.startsWith("/audit")) {
        return [
            { id: "aud-1", user_id: "Monaal", action: "VALIDATE", entity: "Receipt", entity_id: "RCP-2026-001", details: "Intake of 50 Steel Rods approved", timestamp: new Date(Date.now() - 3600000).toISOString() },
            { id: "aud-2", user_id: "Alex", action: "CREATE", entity: "Product", entity_id: "p-5", details: "Added Brass Ball Valve 1/2\"", timestamp: new Date(Date.now() - 7200000).toISOString() },
            { id: "aud-3", user_id: "Rahul", action: "ADJUST", entity: "Stock", entity_id: "ADJ-001", details: "Count reconciliation delta: -2 units", timestamp: new Date(Date.now() - 14400000).toISOString() }
        ];
    }

    // 20. DOCUMENT OCR: /ocr
    if (cleanPath.startsWith("/ocr/scan")) {
        return {
            supplier_name: "Apex Steel Global Ltd",
            document_number: "INV-8821",
            confidence: 0.98,
            items: [
                { product_name: "Steel Rod 12mm", sku: "STL001", quantity: 50, unit_price: 124.0 },
                { product_name: "Hex Bolt M8x40", sku: "BLT044", quantity: 200, unit_price: 24.0 }
            ]
        };
    }
    if (cleanPath.startsWith("/ocr/receipt")) {
        return {
            receipt_id: "rcpt-" + Date.now().toString().slice(-4),
            receipt_number: "RCP-OCR-" + Math.floor(100 + Math.random() * 900),
            supplier: "Apex Steel Global Ltd",
            status: "draft",
            items_count: 2,
            detected_items: [
                { product_name: "Steel Rod 12mm", sku: "STL001", quantity: 50, unit_price: 124.0 },
                { product_name: "Hex Bolt M8x40", sku: "BLT044", quantity: 200, unit_price: 24.0 }
            ]
        };
    }

    // Default fallback
    return { success: true, simulated: true };
}

// Attach to window for standard script access
window.api = api;
window.BASE_URL = BASE_URL;
