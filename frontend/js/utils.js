/**
 * StockSense IMS — UI Utilities & Shared Layout (utils.js)
 * Developer 3 — Frontend Integration Layer
 */

// Format numbers with commas
function formatNumber(num) {
    if (num === null || num === undefined || isNaN(num)) return "0";
    return Number(num).toLocaleString();
}

// Format date into human readable string (e.g., "26 Sep 2026")
function formatDate(dateStr) {
    if (!dateStr) return "—";
    try {
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        return d.toLocaleDateString("en-US", {
            day: "numeric",
            month: "short",
            year: "numeric"
        });
    } catch {
        return dateStr;
    }
}

// Format time (e.g., "10:20")
function formatTime(dateStr) {
    if (!dateStr) return "—";
    try {
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        return d.toLocaleTimeString("en-US", {
            hour: "2-digit",
            minute: "2-digit",
            hour12: false
        });
    } catch {
        return dateStr;
    }
}

// Status Badges (Draft: Gray, Waiting: Orange, Done: Green)
function renderStatusBadge(status) {
    const s = (status || "draft").toLowerCase();
    let badgeClass = "badge-draft";
    let label = "Draft";

    if (s === "waiting" || s === "pending" || s === "in_transit") {
        badgeClass = "badge-waiting";
        label = "Waiting";
    } else if (s === "done" || s === "completed" || s === "validated") {
        badgeClass = "badge-done";
        label = "Done";
    } else if (s === "cancelled" || s === "rejected") {
        badgeClass = "badge-danger";
        label = "Cancelled";
    }

    return `<span class="status-badge ${badgeClass}">${label}</span>`;
}

// Toast notification helper
function showToast(message, type = "info", duration = 4000) {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type} animate-slide-in`;
    
    const icons = {
        success: `<svg class="toast-icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>`,
        warning: `<svg class="toast-icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>`,
        danger: `<svg class="toast-icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>`,
        info: `<svg class="toast-icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>`
    };

    toast.innerHTML = `
        <div class="toast-content">
            ${icons[type] || icons.info}
            <span class="toast-msg">${message}</span>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.add("animate-fade-out");
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

// Check authentication
function checkAuth() {
    const token = localStorage.getItem("token");
    if (!token) {
        // If not logged in and not on login page, redirect
        const path = window.location.pathname;
        if (!path.endsWith("index.html") && !path.endsWith("/") && path !== "") {
            window.location.href = "index.html";
            return false;
        }
    }
    return true;
}

// Get stored user or default
function getCurrentUser() {
    try {
        const stored = localStorage.getItem("user");
        if (stored) return JSON.parse(stored);
    } catch (e) {
        console.error(e);
    }
    return {
        name: "Warehouse Manager",
        email: "manager@stocksense.io",
        role: "Inventory Manager"
    };
}

// Render dynamic shared Sidebar
function renderSidebar(activeKey) {
    const sidebarEl = document.getElementById("sidebar-container");
    if (!sidebarEl) return;

    const navItems = [
        { key: "dashboard", href: "dashboard.html", icon: "📊", label: "Dashboard" },
        { key: "products", href: "products.html", icon: "📦", label: "Products" },
        { key: "receipts", href: "receipts.html", icon: "📥", label: "Receipts" },
        { key: "deliveries", href: "deliveries.html", icon: "📤", label: "Deliveries" },
        { key: "transfers", href: "transfers.html", icon: "🔄", label: "Transfers" },
        { key: "adjustments", href: "adjustments.html", icon: "⚖", label: "Adjustments" },
        { key: "ledger", href: "ledger.html", icon: "📜", label: "Stock Ledger" },
        { key: "reports", href: "reports.html", icon: "📈", label: "Reports" },
        { key: "profile", href: "profile.html", icon: "👤", label: "Profile" }
    ];

    const user = getCurrentUser();

    sidebarEl.innerHTML = `
        <div class="sidebar-wrapper">
            <div class="sidebar-brand">
                <a href="dashboard.html" class="brand-link">
                    <img src="assets/logo/logo.svg" alt="StockSense IMS" class="brand-logo-img" onerror="this.src='assets/icons/favicon.svg'">
                </a>
                <button class="sidebar-close-btn" id="mobile-sidebar-close" aria-label="Close Sidebar">&times;</button>
            </div>

            <div class="warehouse-pill">
                <span class="wh-dot"></span>
                <div class="wh-meta">
                    <span class="wh-label">Active Warehouse</span>
                    <span class="wh-name">Central Hub (WH-01)</span>
                </div>
            </div>

            <nav class="sidebar-nav">
                <ul class="nav-list">
                    ${navItems.map(item => `
                        <li class="nav-item">
                            <a href="${item.href}" class="nav-link ${item.key === activeKey ? 'active' : ''}">
                                <span class="nav-icon">${item.icon}</span>
                                <span class="nav-label">${item.label}</span>
                                ${item.key === 'alerts' ? '<span class="nav-pill danger">3</span>' : ''}
                            </a>
                        </li>
                    `).join('')}
                </ul>
            </nav>

            <div class="sidebar-footer">
                <a href="profile.html" class="user-profile-badge">
                    <div class="user-avatar-circle">
                        ${user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                    </div>
                    <div class="user-info">
                        <span class="user-name">${user.name || 'User'}</span>
                        <span class="user-role">${user.role || 'Staff'}</span>
                    </div>
                </a>
                <button class="logout-btn" id="logout-btn" title="Sign Out">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                        <polyline points="16 17 21 12 16 7"></polyline>
                        <line x1="21" y1="12" x2="9" y2="12"></line>
                    </svg>
                </button>
            </div>
        </div>
    `;

    // Logout listener
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            if (confirm("Are you sure you want to sign out?")) {
                localStorage.removeItem("token");
                localStorage.removeItem("user");
                window.location.href = "index.html";
            }
        });
    }

    // Mobile close listener
    const closeBtn = document.getElementById("mobile-sidebar-close");
    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            document.body.classList.remove("sidebar-open");
        });
    }
}

// Render dynamic Mobile Bottom Navigation
function renderMobileBottomNav(activeKey) {
    let bottomNav = document.getElementById("mobile-bottom-nav");
    if (!bottomNav) {
        bottomNav = document.createElement("nav");
        bottomNav.id = "mobile-bottom-nav";
        bottomNav.className = "mobile-bottom-nav";
        document.body.appendChild(bottomNav);
    }

    const items = [
        { key: "dashboard", href: "dashboard.html", icon: "📊", label: "Dashboard" },
        { key: "products", href: "products.html", icon: "📦", label: "Products" },
        { key: "receipts", href: "receipts.html", icon: "📥", label: "Receipts" },
        { key: "deliveries", href: "deliveries.html", icon: "📤", label: "Deliveries" },
        { key: "ledger", href: "ledger.html", icon: "📜", label: "Ledger" }
    ];

    bottomNav.innerHTML = items.map(item => `
        <a href="${item.href}" class="mobile-nav-link ${item.key === activeKey ? 'active' : ''}">
            <span class="mobile-nav-icon">${item.icon}</span>
            <span class="mobile-nav-label">${item.label}</span>
        </a>
    `).join('');
}

// Render Top Navbar Header
function renderTopbar(title = "Dashboard", breadcrumb = "StockSense") {
    const topbarEl = document.getElementById("topbar-container");
    if (!topbarEl) return;

    const user = getCurrentUser();

    topbarEl.innerHTML = `
        <div class="topbar-left">
            <button class="mobile-menu-btn" id="mobile-menu-toggle" aria-label="Toggle Menu">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="3" y1="12" x2="21" y2="12"></line>
                    <line x1="3" y1="6" x2="21" y2="6"></line>
                    <line x1="3" y1="18" x2="21" y2="18"></line>
                </svg>
            </button>
            <div class="page-title-block">
                <div class="breadcrumbs"><span class="bc-root">${breadcrumb}</span> / <span class="bc-current">${title}</span></div>
                <h1 class="page-title">${title}</h1>
            </div>
        </div>

        <div class="topbar-right">
            <div class="sync-status" id="backend-status-indicator">
                <span class="sync-dot live"></span>
                <span class="sync-label">API Connected</span>
            </div>

            <div class="quick-user">
                <a href="profile.html" class="quick-user-btn">
                    <span class="quick-user-avatar">${user.name ? user.name.charAt(0).toUpperCase() : 'U'}</span>
                    <span class="quick-user-name">${user.name || 'Account'}</span>
                </a>
            </div>
        </div>
    `;

    const menuToggle = document.getElementById("mobile-menu-toggle");
    if (menuToggle) {
        menuToggle.addEventListener("click", () => {
            document.body.classList.toggle("sidebar-open");
        });
    }

    // Listen to global API errors to reflect backend status
    window.addEventListener("api:error", () => {
        const ind = document.getElementById("backend-status-indicator");
        if (ind) {
            ind.innerHTML = `<span class="sync-dot offline"></span><span class="sync-label">Offline (Demo)</span>`;
            ind.classList.add("offline");
        }
    });
}

// Modal opening/closing helpers
function openModal(id) {
    const m = document.getElementById(id);
    if (m) {
        m.classList.add("show");
        document.body.style.overflow = "hidden";
    }
}

function closeModal(id) {
    const m = document.getElementById(id);
    if (m) {
        m.classList.remove("show");
        document.body.style.overflow = "";
    }
}

// Setup common modal close handlers
function setupModalHandlers() {
    document.querySelectorAll(".modal-overlay").forEach(modal => {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                modal.classList.remove("show");
                document.body.style.overflow = "";
            }
        });
    });

    document.querySelectorAll("[data-close-modal]").forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-close-modal");
            closeModal(targetId);
        });
    });
}

// Window exports
window.formatNumber = formatNumber;
window.formatDate = formatDate;
window.formatTime = formatTime;
window.renderStatusBadge = renderStatusBadge;
window.showToast = showToast;
window.checkAuth = checkAuth;
window.getCurrentUser = getCurrentUser;
window.renderSidebar = renderSidebar;
window.renderTopbar = renderTopbar;
window.renderMobileBottomNav = renderMobileBottomNav;
window.openModal = openModal;
window.closeModal = closeModal;
window.setupModalHandlers = setupModalHandlers;
