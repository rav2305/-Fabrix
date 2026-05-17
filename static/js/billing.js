document.addEventListener("DOMContentLoaded", () => {
    const productSelect = document.getElementById("productSelect");
    const qtyInput = document.getElementById("qtyInput");
    const billItemsTable = document.getElementById("billItems");
    const customerName = document.getElementById("customerName");
    const customerPhone = document.getElementById("customerPhone");
    const paymentMode = document.getElementById("paymentMode");
    const discountPercent = document.getElementById("discountPercent");
    const gstPercent = document.getElementById("gstPercent");
    const summarySubtotal = document.getElementById("summarySubtotal");
    const summaryTotal = document.getElementById("summaryTotal");
    const addBillItemButton = document.getElementById("addBillItemButton");
    const generateBillButton = document.getElementById("generateBillButton");

    let products = [];
    let billItems = [];

    function renderProductOptions() {
        productSelect.innerHTML = '<option value="">-- Choose Product --</option>';

        products.forEach((product) => {
            const option = document.createElement("option");
            option.value = product.id;
            option.textContent = `${product.name} (Stock: ${product.stock}) - ${window.Fabrix.formatCurrency(product.price)}`;
            option.disabled = product.stock <= 0;
            productSelect.appendChild(option);
        });
    }

    async function loadProducts(silent = false) {
        try {
            const response = await fetch("/inventory", {
                headers: { Accept: "application/json" },
            });
            if (!response.ok) {
                throw new Error("Product request failed");
            }
            products = await response.json();
            renderProductOptions();
            reconcileBillWithLatestStock();
        } catch (error) {
            if (!silent) {
                window.Fabrix.showToast("Failed to load products", "error");
            }
        }
    }

    function reconcileBillWithLatestStock() {
        const stockMap = new Map(products.map((product) => [product.id, product.stock]));
        let changed = false;

        billItems = billItems.filter((item) => {
            const stock = stockMap.get(item.product_id);
            if (stock === undefined || stock <= 0) {
                changed = true;
                return false;
            }

            if (item.quantity > stock) {
                item.quantity = stock;
                changed = true;
            }

            return true;
        });

        if (changed) {
            renderItems();
            window.Fabrix.showToast(
                "Bill items were adjusted to match live stock",
                "info"
            );
        }
    }

    function renderItems() {
        if (!billItems.length) {
            billItemsTable.innerHTML =
                '<tr><td colspan="5" class="empty-row">No items added</td></tr>';
            summarySubtotal.textContent = "0.00";
            updateSummary();
            return;
        }

        let subtotal = 0;
        billItemsTable.innerHTML = billItems
            .map((item, index) => {
                const total = item.price * item.quantity;
                subtotal += total;
                return `
                    <tr>
                        <td class="strong">${window.Fabrix.escapeHtml(item.product_name)}</td>
                        <td>${window.Fabrix.formatCurrency(item.price)}</td>
                        <td>${item.quantity}</td>
                        <td>${window.Fabrix.formatCurrency(total)}</td>
                        <td>
                            <button class="btn btn-danger btn-small" data-remove-index="${index}">
                                <i class="ph ph-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
            })
            .join("");

        summarySubtotal.textContent = subtotal.toFixed(2);
        updateSummary();
    }

    function updateSummary() {
        const subtotal = Number(summarySubtotal.textContent || 0);
        const discount = Number(discountPercent.value || 0);
        const gst = Number(gstPercent.value || 0);
        const afterDiscount = subtotal - subtotal * (discount / 100);
        const total = afterDiscount + afterDiscount * (gst / 100);
        summaryTotal.textContent = total.toFixed(2);
    }

    addBillItemButton.addEventListener("click", () => {
        const productId = Number(productSelect.value);
        const quantity = Number(qtyInput.value);

        if (!productId || Number.isNaN(quantity) || quantity <= 0) {
            window.Fabrix.showToast("Select a product and valid quantity", "error");
            return;
        }

        const product = products.find((item) => item.id === productId);
        if (!product) {
            window.Fabrix.showToast("Selected product was not found", "error");
            return;
        }

        const existingItem = billItems.find((item) => item.product_id === productId);
        const newQuantity = existingItem ? existingItem.quantity + quantity : quantity;

        if (newQuantity > product.stock) {
            window.Fabrix.showToast("Not enough stock available", "error");
            return;
        }

        if (existingItem) {
            existingItem.quantity = newQuantity;
        } else {
            billItems.push({
                product_id: product.id,
                product_name: product.name,
                price: Number(product.price),
                quantity,
            });
        }

        productSelect.value = "";
        qtyInput.value = 1;
        renderItems();
    });

    billItemsTable.addEventListener("click", (event) => {
        const removeButton = event.target.closest("[data-remove-index]");
        if (!removeButton) {
            return;
        }

        const index = Number(removeButton.dataset.removeIndex);
        billItems.splice(index, 1);
        renderItems();
    });

    discountPercent.addEventListener("input", updateSummary);
    gstPercent.addEventListener("input", updateSummary);

    generateBillButton.addEventListener("click", async () => {
        if (!billItems.length) {
            window.Fabrix.showToast("Add at least one item", "error");
            return;
        }

        if (!customerName.value.trim()) {
            window.Fabrix.showToast("Customer name is required", "error");
            return;
        }

        const payload = {
            customer_name: customerName.value.trim(),
            customer_phone: customerPhone.value.trim(),
            payment_mode: paymentMode.value,
            discount_percent: Number(discountPercent.value || 0),
            gst_percent: Number(gstPercent.value || 0),
            items: billItems,
        };

        try {
            const response = await window.Fabrix.apiRequest("/bill/create", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            window.location.href = `/invoice/${response.invoice_id}`;
        } catch (error) {
            window.Fabrix.showToast(error.message, "error");
        }
    });

    const socket = window.Fabrix.socket;
    if (socket) {
        socket.on("inventory:refresh", () => loadProducts(true));
        socket.on("bill:created", () => loadProducts(true));
    }

    loadProducts();
    renderItems();
});
