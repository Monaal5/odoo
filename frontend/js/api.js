/**
 * StockSense IMS — Shared Fetch Wrapper (api.js)
 * Developer 3 — Frontend Integration Layer
 */

const BASE_URL = window.STOCKSENSE_BASE_URL || "http://localhost:8000";

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

        // Handle unauthorized session expiration
        if (res.status === 401) {
            const isAuthPage = window.location.pathname.endsWith("index.html") || 
                               window.location.pathname.endsWith("/") ||
                               window.location.pathname === "";
            if (!isAuthPage) {
                console.warn("[StockSense] Session expired or invalid token. Redirecting to login...");
                localStorage.removeItem("token");
                localStorage.removeItem("user");
                window.location.href = "index.html";
                return null;
            }
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

        return data;
    } catch (err) {
        console.error(`[API Error] ${method} ${fullUrl}:`, err);
        // Dispatch custom event for UI banners or toast notifications
        window.dispatchEvent(new CustomEvent("api:error", { detail: { endpoint, error: err } }));
        throw err;
    }
}

// Attach to window for standard script access
window.api = api;
window.BASE_URL = BASE_URL;
