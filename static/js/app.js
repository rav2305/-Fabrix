(function () {
    const statusDot = document.querySelector(".status-dot");
    const statusLabel = document.getElementById("syncStatusLabel");
    const toastContainer = document.getElementById("toastContainer");
    const installButton = document.getElementById("installAppButton");
    let deferredInstallPrompt = null;

    function showToast(message, type = "info") {
        if (!toastContainer) {
            return;
        }

        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        toast.textContent = message;
        toastContainer.appendChild(toast);

        window.setTimeout(() => {
            toast.remove();
        }, 3200);
    }

    function setSyncStatus(online, label) {
        if (statusDot) {
            statusDot.classList.toggle("online", online);
            statusDot.classList.toggle("offline", !online);
        }
        if (statusLabel) {
            statusLabel.textContent = label;
        }
    }

    async function apiRequest(url, options = {}) {
        const headers = {
            Accept: "application/json",
            ...(options.body ? { "Content-Type": "application/json" } : {}),
            ...(options.headers || {}),
        };

        const response = await fetch(url, { ...options, headers });
        const payload = await response.json().catch(() => ({
            success: false,
            message: "Unexpected server response",
        }));

        if (!response.ok || payload.success === false) {
            throw new Error(payload.message || "Request failed");
        }

        return payload;
    }

    const socket = window.io
        ? window.io({
              transports: ["websocket", "polling"],
              reconnection: true,
          })
        : null;

    if (socket) {
        socket.on("connect", () => {
            setSyncStatus(true, "Live sync connected");
        });

        socket.on("disconnect", () => {
            setSyncStatus(false, "Live sync disconnected");
        });

        socket.on("connect_error", () => {
            setSyncStatus(false, "Reconnecting to server...");
        });
    } else {
        setSyncStatus(false, "Socket client unavailable");
    }

    window.Fabrix = {
        apiRequest,
        showToast,
        setSyncStatus,
        socket,
        formatCurrency(value) {
            const number = Number(value || 0);
            return `Rs ${number.toFixed(2)}`;
        },
        escapeHtml(value) {
            return String(value ?? "")
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#39;");
        },
    };

    if ("serviceWorker" in navigator) {
        window.addEventListener("load", () => {
            navigator.serviceWorker
                .register("/service-worker.js")
                .catch(() => showToast("Offline install support failed to register", "error"));
        });
    }

    window.addEventListener("beforeinstallprompt", (event) => {
        event.preventDefault();
        deferredInstallPrompt = event;
        installButton?.classList.remove("hidden");
    });

    installButton?.addEventListener("click", async () => {
        if (!deferredInstallPrompt) {
            showToast("Use your browser menu to install Fabrix on this device", "info");
            return;
        }

        deferredInstallPrompt.prompt();
        const choice = await deferredInstallPrompt.userChoice;
        if (choice.outcome === "accepted") {
            showToast("Fabrix install started", "success");
        }
        deferredInstallPrompt = null;
        installButton.classList.add("hidden");
    });

    window.addEventListener("appinstalled", () => {
        deferredInstallPrompt = null;
        installButton?.classList.add("hidden");
        showToast("Fabrix installed on this device", "success");
    });
})();
