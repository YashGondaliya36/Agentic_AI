// ============================================
// InvoiceIQ - JavaScript Application
// Upload, Extract, Review, Save
// ============================================

// Global state
let extractedData = null;
let currentFilePath = null;

// ========== Initialize ========== 
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    console.log('🚀 InvoiceIQ initialized');

    // Load stats
    loadStats();

    // Setup event listeners
    setupNavigation();
    setupUpload();
    setupSaveButton();

    // Load invoices
    loadInvoices();
    loadInventory();
}

// ========== Navigation ==========
function setupNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const viewName = btn.dataset.view;
            switchView(viewName);

            // Update active state
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
}

function switchView(viewName) {
    const views = document.querySelectorAll('.view');
    views.forEach(view => view.classList.remove('active'));

    const targetView = document.getElementById(`view-${viewName}`);
    if (targetView) {
        targetView.classList.add('active');
    }
}

// ========== Stats ==========
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        if (data.success) {
            document.getElementById('stat-invoices').textContent = data.stats.invoices;
            document.getElementById('stat-items').textContent = data.stats.items;
            document.getElementById('stat-suppliers').textContent = data.stats.suppliers;
            document.getElementById('stat-alerts').textContent = data.stats.low_stock_alerts;
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// ========== Upload ==========
function setupUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');

    // Click to browse
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });

    // File selected
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            uploadInvoice(file);
        }
    });

    // Drag & drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = 'var(--primary)';
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.style.borderColor = 'var(--border-color)';
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = 'var(--border-color)';

        const file = e.dataTransfer.files[0];
        if (file) {
            uploadInvoice(file);
        }
    });
}

async function uploadInvoice(file) {
    // Validate file
    const validTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(file.type)) {
        showToast('Please upload PDF, JPG, or PNG file', 'error');
        return;
    }

    // Show processing
    document.getElementById('uploadZone').classList.add('hidden');
    document.getElementById('processingStatus').classList.remove('hidden');
    document.getElementById('reviewSection').classList.add('hidden');

    // Upload
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload-invoice', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // Success!
            extractedData = data.data;
            currentFilePath = data.file_path;

            showToast('Invoice extracted successfully!', 'success');

            // Show review section
            displayReviewData(data.data);

            // Hide processing, show review
            setTimeout(() => {
                document.getElementById('processingStatus').classList.add('hidden');
                document.getElementById('reviewSection').classList.remove('hidden');
            }, 500);

        } else {
            showToast(`Extraction failed: ${data.error}`, 'error');
            resetUploadZone();
        }

    } catch (error) {
        console.error('Upload error:', error);
        showToast('Upload failed. Please try again.', 'error');
        resetUploadZone();
    }
}

function resetUploadZone() {
    document.getElementById('uploadZone').classList.remove('hidden');
    document.getElementById('processingStatus').classList.add('hidden');
    document.getElementById('reviewSection').classList.add('hidden');
    document.getElementById('fileInput').value = '';
}

// ========== Display Review Data ==========
function displayReviewData(data) {
    // Supplier info
    document.getElementById('supplier-name').value = data.supplier_name || '';
    document.getElementById('supplier-gstin').value = data.supplier_gstin || '';
    document.getElementById('supplier-contact').value = data.supplier_contact || '';
    document.getElementById('supplier-email').value = '';
    document.getElementById('supplier-address').value = data.supplier_address || '';

    // Invoice details
    document.getElementById('invoice-number').value = data.invoice_number || '';
    document.getElementById('invoice-date').value = data.invoice_date || '';
    document.getElementById('invoice-due-date').value = data.due_date || '';
    document.getElementById('payment-terms').value = data.payment_terms || 30;

    // Items
    const tbody = document.getElementById('itemsTableBody');
    tbody.innerHTML = '';

    if (data.items && data.items.length > 0) {
        data.items.forEach((item, index) => {
            const row = createItemRow(item, index);
            tbody.appendChild(row);
        });
    }

    // Totals
    document.getElementById('total-subtotal').textContent = `₹${formatNumber(data.subtotal || 0)}`;
    document.getElementById('total-gst').textContent = `₹${formatNumber(data.total_gst || 0)}`;
    document.getElementById('total-amount').textContent = `₹${formatNumber(data.total_amount || 0)}`;
}

function createItemRow(item, index) {
    const tr = document.createElement('tr');
    tr.dataset.index = index;

    // Match badge
    let matchBadge = '';
    if (item.matched_item_id) {
        matchBadge = `<span class="match-badge matched">✓ Matched</span>`;
    } else {
        matchBadge = `<span class="match-badge new">+ New</span>`;
    }

    tr.innerHTML = `
        <td><input type="text" value="${item.name || ''}" data-field="name"></td>
        <td><input type="text" value="${item.hsn_code || ''}" data-field="hsn_code" style="width: 100px;"></td>
        <td><input type="number" value="${item.quantity || 0}" data-field="quantity" step="0.01" style="width: 80px;"></td>
        <td><input type="text" value="${item.unit || 'piece'}" data-field="unit" style="width: 80px;"></td>
        <td><input type="number" value="${item.unit_price || 0}" data-field="unit_price" step="0.01" style="width: 100px;"></td>
        <td><input type="number" value="${item.gst_rate || 18}" data-field="gst_rate" step="0.01" style="width: 70px;"></td>
        <td>₹${formatNumber(item.total || 0)}</td>
        <td>${matchBadge}</td>
    `;

    // Add change listeners to recalculate
    tr.querySelectorAll('input').forEach(input => {
        input.addEventListener('change', () => updateItemCalculations(tr, index));
    });

    return tr;
}

function updateItemCalculations(row, index) {
    // Get values
    const qty = parseFloat(row.querySelector('[data-field="quantity"]').value) || 0;
    const unitPrice = parseFloat(row.querySelector('[data-field="unit_price"]').value) || 0;
    const gstRate = parseFloat(row.querySelector('[data-field="gst_rate"]').value) || 0;

    // Calculate
    const subtotal = qty * unitPrice;
    const gstAmount = subtotal * (gstRate / 100);
    const total = subtotal + gstAmount;

    // Update display
    row.cells[6].textContent = `₹${formatNumber(total)}`;

    // Update extracted data
    if (extractedData && extractedData.items[index]) {
        extractedData.items[index].quantity = qty;
        extractedData.items[index].unit_price = unitPrice;
        extractedData.items[index].gst_rate = gstRate;
        extractedData.items[index].subtotal = subtotal;
        extractedData.items[index].gst_amount = gstAmount;
        extractedData.items[index].total = total;
    }

    // Recalculate totals
    recalculateTotals();
}

function recalculateTotals() {
    if (!extractedData || !extractedData.items) return;

    let subtotal = 0;
    let totalGst = 0;

    extractedData.items.forEach(item => {
        const itemSubtotal = (item.quantity || 0) * (item.unit_price || 0);
        const itemGst = itemSubtotal * ((item.gst_rate || 0) / 100);

        subtotal += itemSubtotal;
        totalGst += itemGst;
    });

    const grandTotal = subtotal + totalGst;

    // Update display
    document.getElementById('total-subtotal').textContent = `₹${formatNumber(subtotal)}`;
    document.getElementById('total-gst').textContent = `₹${formatNumber(totalGst)}`;
    document.getElementById('total-amount').textContent = `₹${formatNumber(grandTotal)}`;

    // Update extracted data
    extractedData.subtotal = subtotal;
    extractedData.total_gst = totalGst;
    extractedData.total_amount = grandTotal;
}

// ========== Save Invoice ==========
function setupSaveButton() {
    const btnSave = document.getElementById('btnSave');
    const btnCancel = document.getElementById('btnCancel');

    btnSave.addEventListener('click', saveInvoice);
    btnCancel.addEventListener('click', () => {
        resetUploadZone();
        switchView('upload');
    });
}

async function saveInvoice() {
    if (!extractedData) {
        showToast('No data to save', 'error');
        return;
    }

    // Collect form data
    const invoiceData = {
        file_path: currentFilePath,

        supplier: {
            name: document.getElementById('supplier-name').value.trim(),
            gstin: document.getElementById('supplier-gstin').value.trim(),
            contact_person: '',
            phone: document.getElementById('supplier-contact').value.trim(),
            email: document.getElementById('supplier-email').value.trim(),
            address: document.getElementById('supplier-address').value.trim(),
            payment_terms_days: parseInt(document.getElementById('payment-terms').value) || 30
        },

        invoice_number: document.getElementById('invoice-number').value.trim(),
        invoice_date: document.getElementById('invoice-date').value,
        due_date: document.getElementById('invoice-due-date').value,

        subtotal: extractedData.subtotal || 0,
        gst_amount: extractedData.total_gst || 0,
        total_amount: extractedData.total_amount || 0,

        raw_text: extractedData.raw_text || '',

        items: []
    };

    // Validate
    if (!invoiceData.supplier.name) {
        showToast('Supplier name is required', 'error');
        return;
    }

    if (!invoiceData.invoice_number) {
        showToast('Invoice number is required', 'error');
        return;
    }

    // Collect items from table
    const rows = document.querySelectorAll('#itemsTableBody tr');
    rows.forEach((row, index) => {
        const item = {
            name: row.querySelector('[data-field="name"]').value.trim(),
            hsn_code: row.querySelector('[data-field="hsn_code"]').value.trim(),
            quantity: parseFloat(row.querySelector('[data-field="quantity"]').value) || 0,
            unit: row.querySelector('[data-field="unit"]').value.trim(),
            unit_price: parseFloat(row.querySelector('[data-field="unit_price"]').value) || 0,
            gst_rate: parseFloat(row.querySelector('[data-field="gst_rate"]').value) || 0
        };

        // Calculate amounts
        const subtotal = item.quantity * item.unit_price;
        const gstAmount = subtotal * (item.gst_rate / 100);
        const total = subtotal + gstAmount;

        item.subtotal = subtotal;
        item.gst_amount = gstAmount;
        item.total = total;

        // Check if matched
        if (extractedData.items[index]?.matched_item_id) {
            item.matched_item_id = extractedData.items[index].matched_item_id;
        }

        invoiceData.items.push(item);
    });

    if (invoiceData.items.length === 0) {
        showToast('At least one item is required', 'error');
        return;
    }

    // Show saving state
    const btnSave = document.getElementById('btnSave');
    const originalHTML = btnSave.innerHTML;
    btnSave.disabled = true;
    btnSave.innerHTML = '<span class="spinner" style="width: 20px; height: 20px; margin-right: 8px;"></span>Saving...';

    try {
        const response = await fetch('/api/save-invoice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(invoiceData)
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Invoice ${invoiceData.invoice_number} saved successfully!`, 'success');

            // Reset and reload
            setTimeout(() => {
                resetUploadZone();
                loadStats();
                loadInvoices();
                loadInventory();
            }, 1000);

        } else {
            showToast(`Save failed: ${data.error}`, 'error');
        }

    } catch (error) {
        console.error('Save error:', error);
        showToast('Save failed. Please try again.', 'error');
    } finally {
        btnSave.disabled = false;
        btnSave.innerHTML = originalHTML;
    }
}

// ========== Load Invoices ==========
async function loadInvoices() {
    try {
        const response = await fetch('/api/invoices?limit=50');
        const data = await response.json();

        if (data.success) {
            displayInvoices(data.invoices);
        }
    } catch (error) {
        console.error('Failed to load invoices:', error);
    }
}

function displayInvoices(invoices) {
    const container = document.getElementById('invoicesList');

    if (!invoices || invoices.length === 0) {
        container.innerHTML = '<p class="placeholder-text">📄 No invoices yet. Upload your first invoice!</p>';
        return;
    }

    container.innerHTML = invoices.map(inv => `
        <div class="review-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h3 class="review-card-title">${inv.invoice_number}</h3>
                    <p style="color: var(--text-secondary); margin-bottom: 0.5rem;">
                        <strong>${inv.supplier_name}</strong>
                    </p>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">
                        📅 ${formatDate(inv.date)} | 📦 ${inv.items_count} items
                    </p>
                </div>
                <div style="text-align: right;">
                    <p style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary);">
                        ₹${formatNumber(inv.total)}
                    </p>
                    <span class="match-badge ${inv.payment_status === 'paid' ? 'matched' : 'new'}">
                        ${inv.payment_status.toUpperCase()}
                    </span>
                </div>
            </div>
        </div>
    `).join('');
}

// ========== Load Inventory ==========
async function loadInventory() {
    try {
        const response = await fetch('/api/items');
        const data = await response.json();

        if (data.success) {
            displayInventory(data.items);
        }
    } catch (error) {
        console.error('Failed to load inventory:', error);
    }
}

function displayInventory(items) {
    const container = document.getElementById('inventoryList');

    if (!items || items.length === 0) {
        container.innerHTML = '<p class="placeholder-text">📦 No items in catalog yet.</p>';
        return;
    }

    container.innerHTML = `
        <div class="table-container">
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Item Name</th>
                        <th>Current Stock</th>
                        <th>Unit</th>
                        <th>Cost Price</th>
                        <th>Selling Price</th>
                        <th>Stock Value</th>
                    </tr>
                </thead>
                <tbody>
                    ${items.map(item => `
                        <tr>
                            <td><strong>${item.name}</strong></td>
                            <td>${formatNumber(item.stock)}</td>
                            <td>${item.unit}</td>
                            <td>₹${formatNumber(item.cost_price)}</td>
                            <td>₹${formatNumber(item.selling_price)}</td>
                            <td>₹${formatNumber(item.stock * item.cost_price)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// ========== Utilities ==========
function formatNumber(num) {
    return parseFloat(num || 0).toFixed(2);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    // Auto remove
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
