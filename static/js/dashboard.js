document.addEventListener("DOMContentLoaded", () => {
    const productNode = document.getElementById("totalProducts");
    const stockNode = document.getElementById("totalStock");
    const salesNode = document.getElementById("todaySales");
    const profitNode = document.getElementById("todayProfit");

    async function loadStats(silent = false) {
        try {
            const response = await window.Fabrix.apiRequest("/dashboard/stats");
            renderStats(response.stats);
        } catch (error) {
            if (!silent) {
                window.Fabrix.showToast(error.message, "error");
            }
        }
    }

    function renderStats(stats) {
        productNode.textContent = stats.total_products;
        stockNode.textContent = stats.total_stock;
        salesNode.textContent = window.Fabrix.formatCurrency(stats.today_sales);
        profitNode.textContent = window.Fabrix.formatCurrency(stats.today_profit);
    }

    const socket = window.Fabrix.socket;
    if (socket) {
        socket.on("dashboard:refresh", (payload) => {
            if (payload?.stats) {
                renderStats(payload.stats);
                return;
            }
            loadStats(true);
        });

        socket.on("bill:created", () => loadStats(true));
        socket.on("inventory:refresh", () => loadStats(true));
    }

    loadStats(true);
});
