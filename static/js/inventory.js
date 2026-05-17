document.addEventListener("DOMContentLoaded", () => {
    const inventoryTable = document.getElementById("inventoryTable");
    const searchInput = document.getElementById("searchInput");
    const addProductForm = document.getElementById("addProductForm");
    const editProductForm = document.getElementById("editProductForm");
    const previewButton = document.getElementById("previewUploadButton");
    const resetUploadButton = document.getElementById("resetUploadButton");
    const confirmUploadButton = document.getElementById("confirmUploadButton");
    const uploadFormArea = document.getElementById("uploadFormArea");
    const previewArea = document.getElementById("previewArea");
    const previewTableBody = document.getElementById("previewTableBody");
    const excelFileInput = document.getElementById("excelFileInput");

    let products = [];
    let validUploadData = [];

    function openModal(id) {
        document.getElementById(id)?.classList.add("active");
    }

    function closeModal(id) {
        document.getElementById(id)?.classList.remove("active");
    }

    document.querySelectorAll("[data-modal-open]").forEach((button) => {
        button.addEventListener("click", () => openModal(button.dataset.modalOpen));
    });

    document.querySelectorAll("[data-modal-close]").forEach((button) => {
        button.addEventListener("click", () => closeModal(button.dataset.modalClose));
    });

    document.querySelectorAll(".modal").forEach((modal) => {
        modal.addEventListener("click", (event) => {
            if (event.target === modal) {
                modal.classList.remove("active");
            }
        });
    });

    function renderProducts() {
        const query = searchInput.value.trim().toLowerCase();
        const filtered = products.filter((product) =>
            product.name.toLowerCase().includes(query)
        );

        if (!filtered.length) {
            inventoryTable.innerHTML =
                '<tr><td colspan="6" class="empty-row">No products found.</td></tr>';
            return;
        }

        inventoryTable.innerHTML = filtered
            .map((product) => {
                const stockClass = product.stock > 10 ? "ok" : "low";
                return `
                    <tr>
                        <td>#${product.id}</td>
                        <td class="strong">${window.Fabrix.escapeHtml(product.name)}</td>
                        <td>${window.Fabrix.formatCurrency(product.purchase_price)}</td>
                        <td>${window.Fabrix.formatCurrency(product.price)}</td>
                        <td><span class="stock-pill ${stockClass}">${product.stock}</span></td>
                        <td class="action-row">
                            <button class="btn btn-secondary btn-small" data-edit-id="${product.id}">
                                <i class="ph ph-pencil-simple"></i>
                            </button>
                            <button class="btn btn-danger btn-small" data-delete-id="${product.id}">
                                <i class="ph ph-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
            })
            .join("");
    }

    async function loadInventory(silent = false) {
        try {
            const response = await fetch("/inventory", {
                headers: { Accept: "application/json" },
            });
            if (!response.ok) {
                throw new Error("Inventory request failed");
            }
            products = await response.json();
            renderProducts();
        } catch (error) {
            if (!silent) {
                window.Fabrix.showToast("Failed to load inventory", "error");
            }
        }
    }

    addProductForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = {
            name: document.getElementById("add_name").value,
            purchase_price: document.getElementById("add_purchase_price").value,
            price: document.getElementById("add_price").value,
            stock: document.getElementById("add_stock").value,
        };

        try {
            await window.Fabrix.apiRequest("/inventory/add", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            addProductForm.reset();
            closeModal("addModal");
            window.Fabrix.showToast("Product added successfully", "success");
            loadInventory(true);
        } catch (error) {
            window.Fabrix.showToast(error.message, "error");
        }
    });

    editProductForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const productId = document.getElementById("edit_id").value;
        const payload = {
            name: document.getElementById("edit_name").value,
            purchase_price: document.getElementById("edit_purchase_price").value,
            price: document.getElementById("edit_price").value,
            stock: document.getElementById("edit_stock").value,
        };

        try {
            await window.Fabrix.apiRequest(`/inventory/update/${productId}`, {
                method: "PUT",
                body: JSON.stringify(payload),
            });
            closeModal("editModal");
            window.Fabrix.showToast("Product updated successfully", "success");
            loadInventory(true);
        } catch (error) {
            window.Fabrix.showToast(error.message, "error");
        }
    });

    inventoryTable.addEventListener("click", async (event) => {
        const editButton = event.target.closest("[data-edit-id]");
        const deleteButton = event.target.closest("[data-delete-id]");

        if (editButton) {
            const productId = Number(editButton.dataset.editId);
            const product = products.find((item) => item.id === productId);
            if (!product) {
                return;
            }

            document.getElementById("edit_id").value = product.id;
            document.getElementById("edit_name").value = product.name;
            document.getElementById("edit_purchase_price").value = product.purchase_price;
            document.getElementById("edit_price").value = product.price;
            document.getElementById("edit_stock").value = product.stock;
            openModal("editModal");
            return;
        }

        if (deleteButton) {
            const productId = Number(deleteButton.dataset.deleteId);
            const confirmed = window.confirm(
                "Are you sure you want to delete this product?"
            );
            if (!confirmed) {
                return;
            }

            try {
                await window.Fabrix.apiRequest(`/inventory/delete/${productId}`, {
                    method: "DELETE",
                });
                window.Fabrix.showToast("Product deleted successfully", "success");
                loadInventory(true);
            } catch (error) {
                window.Fabrix.showToast(error.message, "error");
            }
        }
    });

    searchInput.addEventListener("input", renderProducts);

    previewButton.addEventListener("click", () => {
        if (!excelFileInput.files.length) {
            window.Fabrix.showToast("Please select an Excel file", "error");
            return;
        }

        const file = excelFileInput.files[0];
        const reader = new FileReader();
        reader.onload = (loadEvent) => {
            const data = new Uint8Array(loadEvent.target.result);
            const workbook = XLSX.read(data, { type: "array" });
            const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
            const rows = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });

            validUploadData = [];
            previewTableBody.innerHTML = "";

            for (let index = 1; index < rows.length; index += 1) {
                const row = rows[index];
                if (!row || row.length < 4) {
                    continue;
                }

                const name = String(row[0] ?? "").trim();
                const qty = String(row[1] ?? "").trim();
                const price = String(row[2] ?? "").trim();
                const purchasePrice = String(row[3] ?? "").trim();

                if (!name || !qty || !price || !purchasePrice) {
                    continue;
                }

                const parsedRow = {
                    name,
                    qty: Number(qty),
                    price: Number(price),
                    purchase_price: Number(purchasePrice),
                };

                if (
                    Number.isNaN(parsedRow.qty) ||
                    Number.isNaN(parsedRow.price) ||
                    Number.isNaN(parsedRow.purchase_price)
                ) {
                    continue;
                }

                validUploadData.push(parsedRow);
            }

            if (!validUploadData.length) {
                window.Fabrix.showToast(
                    "No valid rows found in the selected Excel file",
                    "error"
                );
                return;
            }

            previewTableBody.innerHTML = validUploadData
                .map(
                    (row) => `
                        <tr>
                            <td>${window.Fabrix.escapeHtml(row.name)}</td>
                            <td>${row.qty}</td>
                            <td>${window.Fabrix.formatCurrency(row.price)}</td>
                            <td>${window.Fabrix.formatCurrency(row.purchase_price)}</td>
                        </tr>
                    `
                )
                .join("");

            uploadFormArea.classList.add("hidden");
            previewArea.classList.remove("hidden");
        };

        reader.readAsArrayBuffer(file);
    });

    resetUploadButton.addEventListener("click", resetUpload);

    function resetUpload() {
        validUploadData = [];
        previewTableBody.innerHTML = "";
        excelFileInput.value = "";
        uploadFormArea.classList.remove("hidden");
        previewArea.classList.add("hidden");
    }

    confirmUploadButton.addEventListener("click", async () => {
        if (!validUploadData.length) {
            return;
        }

        try {
            const response = await window.Fabrix.apiRequest("/inventory/bulk-add", {
                method: "POST",
                body: JSON.stringify(validUploadData),
            });
            window.Fabrix.showToast(
                `Successfully added ${response.count} products`,
                "success"
            );
            resetUpload();
            closeModal("uploadModal");
            loadInventory(true);
        } catch (error) {
            window.Fabrix.showToast(error.message, "error");
        }
    });

    const socket = window.Fabrix.socket;
    if (socket) {
        socket.on("inventory:refresh", () => {
            loadInventory(true);
        });
    }

    loadInventory();
});
