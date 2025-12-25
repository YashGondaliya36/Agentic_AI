// ============================================
// InvoiceIQ - JavaScript Application  
// COMPLETE: Purchase + Sales Support
// ============================================

// Global state
let extractedData = null;
let currentFilePath = null;
let selectedInvoiceType = 'purchase'; // 'purchase' or 'sales'
let currentInvoiceFilter = 'purchase'; // For invoices view filter

// ========== Initialize ========== 
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    console.log('🚀 InvoiceIQ initialized - Purchase + Sales');

    // Load stats
    loadStats();

    // Setup event listeners
    setupNavigation();
    setupInvoiceTypeSelector();
    setupUpload();
    setupSaveButton();
    setupInvoiceFilter();

    // Load invoices
    loadInvoices(currentInvoiceFilter);
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

            // Reload data for specific views
            if (viewName === 'invoices') {
                loadInvoices(currentInvoiceFilter);
            } else if (viewName === 'inventory') {
                loadInventory();
            } else if (viewName === 'analytics') {
                loadAnalytics();
            }
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

// ========== Invoice Type Selector ==========
function setupInvoiceTypeSelector() {
    const typeBtns = document.querySelectorAll('.type-btn');

    typeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const type = btn.dataset.type;
            selectedInvoiceType = type;

            // Update active state
            typeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update label
            const label = type === 'purchase' ? 'Purchase Invoice' : 'Sales Invoice';
            document.getElementById('selectedTypeLabel').textContent = label;

            console.log(`Invoice type selected: ${type}`);
        });
    });
}

// ========== Invoice Filter ==========
function setupInvoiceFilter() {
    const filterBtns = document.querySelectorAll('.filter-btn');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const filter = btn.dataset.filter;
            currentInvoiceFilter = filter;

            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Load invoices
            loadInvoices(filter);
        });
    });
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

    // Upload to correct endpoint based on type
    const formData = new FormData();
    formData.append('file', file);

    const endpoint = selectedInvoiceType === 'purchase'
        ? '/api/upload-invoice'
        : '/api/upload-sales-invoice';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // Success!
            extractedData = data.data;
            currentFilePath = data.file_path;

            const typeLabel = selectedInvoiceType === 'purchase' ? 'Purchase' : 'Sales';
            showToast(`${typeLabel} invoice extracted successfully!`, 'success');

            // Show review section
            displayReviewData(data.data, selectedInvoiceType);

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
function displayReviewData(data, invoiceType) {
    // Update labels based on type
    if (invoiceType === 'purchase') {
        document.getElementById('partnerCardTitle').textContent = 'Supplier Information';
        document.getElementById('partnerNameLabel').textContent = 'Supplier Name';
        document.getElementById('partner-name').value = data.supplier_name || '';
    } else {
        document.getElementById('partnerCardTitle').textContent = 'Customer Information';
        document.getElementById('partnerNameLabel').textContent = 'Customer Name';
        document.getElementById('partner-name').value = data.customer_name || '';
    }

    // Partner info
    document.getElementById('partner-gstin').value = data.supplier_gstin || data.customer_gstin || '';
    document.getElementById('partner-contact').value = data.supplier_contact || data.customer_contact || '';
    document.getElementById('partner-email').value = '';
    document.getElementById('partner-address').value = data.supplier_address || data.customer_address || '';

    // Invoice details
    document.getElementById('invoice-number').value = data.invoice_number || '';
    document.getElementById('invoice-date').value = data.invoice_date || '';
    document.getElementById('invoice-due-date').value = data.due_date || '';
    document.getElementById('payment-terms').value = data.payment_terms || 30;

    // Show/hide profit columns for sales
    const costCols = document.querySelectorAll('.cost-col');
    const profitCols = document.querySelectorAll('.profit-col');
    const profitRow = document.querySelector('.profit-row');

    if (invoiceType === 'sales') {
        costCols.forEach(col => col.classList.remove('hidden'));
        profitCols.forEach(col => col.classList.remove('hidden'));
        if (profitRow) profitRow.classList.remove('hidden');
    } else {
        costCols.forEach(col => col.classList.add('hidden'));
        profitCols.forEach(col => col.classList.add('hidden'));
        if (profitRow) profitRow.classList.add('hidden');
    }

    // Items
    const tbody = document.getElementById('itemsTableBody');
    tbody.innerHTML = '';

    if (data.items && data.items.length > 0) {
        data.items.forEach((item, index) => {
            const row = createItemRow(item, index, invoiceType);
            tbody.appendChild(row);
        });
    }

    // Totals
    document.getElementById('total-subtotal').textContent = `₹${formatNumber(data.subtotal || 0)}`;
    document.getElementById('total-gst').textContent = `₹${formatNumber(data.total_gst || 0)}`;
    document.getElementById('total-amount').textContent = `₹${formatNumber(data.total_amount || 0)}`;

    if (invoiceType === 'sales') {
        const totalProfit = data.total_potential_profit || 0;
        document.getElementById('total-profit').textContent = `₹${formatNumber(totalProfit)}`;
    }
}

function createItemRow(item, index, invoiceType) {
    const tr = document.createElement('tr');
    tr.dataset.index = index;

    // Match badge
    let matchBadge = '';
    if (item.matched_item_id) {
        matchBadge = `<span class="match-badge matched">✓ Matched</span>`;
    } else {
        matchBadge = `<span class="match-badge new">+ New</span>`;
    }

    // Stock warning for sales
    let stockWarning = '';
    if (invoiceType === 'sales' && item.matched_item_id) {
        const stock = item.current_stock || 0;
        const qty = item.quantity || 0;
        if (stock < qty) {
            stockWarning = `<br><small style="color: var(--error);">⚠ Insufficient stock (${stock} available)</small>`;
        }
    }

    // Base columns (same for both)
    let html = `
        <td><input type="text" value="${item.name || ''}" data-field="name">${stockWarning}</td>
        <td><input type="text" value="${item.hsn_code || ''}" data-field="hsn_code" style="width: 100px;"></td>
        <td><input type="number" value="${item.quantity || 0}" data-field="quantity" step="0.01" style="width: 80px;"></td>
        <td><input type="text" value="${item.unit || 'piece'}" data-field="unit" style="width: 80px;"></td>
    `;

    // Sales-specific: Cost column
    if (invoiceType === 'sales') {
        html += `<td class="cost-col">₹${formatNumber(item.cost_price || 0)}</td>`;
    }

    // Unit price
    html += `<td><input type="number" value="${item.unit_price || 0}" data-field="unit_price" step="0.01" style="width: 100px;"></td>`;

    // GST
    html += `<td><input type="number" value="${item.gst_rate || 18}" data-field="gst_rate" step="0.01" style="width: 70px;"></td>`;

    // Total
    html += `<td>₹${formatNumber(item.total || 0)}</td>`;

    // Sales-specific: Profit column
    if (invoiceType === 'sales') {
        const profit = item.total_profit || 0;
        const profitColor = profit >= 0 ? 'var(--success)' : 'var(--error)';
        html += `<td class="profit-col" style="color: ${profitColor}; font-weight: 600;">₹${formatNumber(profit)}</td>`;
    }

    // Match badge
    html += `<td>${matchBadge}</td>`;

    tr.innerHTML = html;

    // Add change listeners to recalculate
    tr.querySelectorAll('input').forEach(input => {
        input.addEventListener('change', () => updateItemCalculations(tr, index, invoiceType));
    });

    return tr;
}

function updateItemCalculations(row, index, invoiceType) {
    // Get values
    const qty = parseFloat(row.querySelector('[data-field="quantity"]').value) || 0;
    const unitPrice = parseFloat(row.querySelector('[data-field="unit_price"]').value) || 0;
    const gstRate = parseFloat(row.querySelector('[data-field="gst_rate"]').value) || 0;

    // Calculate
    const subtotal = qty * unitPrice;
    const gstAmount = subtotal * (gstRate / 100);
    const total = subtotal + gstAmount;

    // Update display
    const cells = row.cells;
    let totalCellIndex = invoiceType === 'sales' ? 8 : 7;
    cells[totalCellIndex].textContent = `₹${formatNumber(total)}`;

    // Update profit for sales
    if (invoiceType === 'sales' && extractedData.items[index]) {
        const costPrice = extractedData.items[index].cost_price || 0;
        const profit = (unitPrice - costPrice) * qty;
        cells[9].textContent = `₹${formatNumber(profit)}`;
        cells[9].style.color = profit >= 0 ? 'var(--success)' : 'var(--error)';
        extractedData.items[index].total_profit = profit;
    }

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
    recalculateTotals(invoiceType);
}

function recalculateTotals(invoiceType) {
    if (!extractedData || !extractedData.items) return;

    let subtotal = 0;
    let totalGst = 0;
    let totalProfit = 0;

    extractedData.items.forEach(item => {
        const itemSubtotal = (item.quantity || 0) * (item.unit_price || 0);
        const itemGst = itemSubtotal * ((item.gst_rate || 0) / 100);

        subtotal += itemSubtotal;
        totalGst += itemGst;

        if (invoiceType === 'sales') {
            totalProfit += item.total_profit || 0;
        }
    });

    const grandTotal = subtotal + totalGst;

    // Update display
    document.getElementById('total-subtotal').textContent = `₹${formatNumber(subtotal)}`;
    document.getElementById('total-gst').textContent = `₹${formatNumber(totalGst)}`;
    document.getElementById('total-amount').textContent = `₹${formatNumber(grandTotal)}`;

    if (invoiceType === 'sales') {
        document.getElementById('total-profit').textContent = `₹${formatNumber(totalProfit)}`;
    }

    // Update extracted data
    extractedData.subtotal = subtotal;
    extractedData.total_gst = totalGst;
    extractedData.total_amount = grandTotal;
    if (invoiceType === 'sales') {
        extractedData.total_potential_profit = totalProfit;
    }
}

// ========== Save Invoice ==========
function setupSaveButton() {
    const btnSave = document.getElementById('btnSave');
    const btnCancel = document.getElementById('btnCancel');

    btnSave.addEventListener('click', () => saveInvoice(selectedInvoiceType));
    btnCancel.addEventListener('click', () => {
        resetUploadZone();
        switchView('upload');
    });
}

async function saveInvoice(invoiceType) {
    if (!extractedData) {
        showToast('No data to save', 'error');
        return;
    }

    // Collect form data
    const partnerName = document.getElementById('partner-name').value.trim();

    const invoiceData = {
        file_path: currentFilePath,

        // Partner (supplier or customer)
        [invoiceType === 'purchase' ? 'supplier' : 'customer']: {
            name: partnerName,
            gstin: document.getElementById('partner-gstin').value.trim(),
            contact_person: '',
            phone: document.getElementById('partner-contact').value.trim(),
            email: document.getElementById('partner-email').value.trim(),
            address: document.getElementById('partner-address').value.trim(),
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
    if (!partnerName) {
        const label = invoiceType === 'purchase' ? 'Supplier' : 'Customer';
        showToast(`${label} name is required`, 'error');
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

    const endpoint = invoiceType === 'purchase'
        ? '/api/save-invoice'
        : '/api/save-sales-invoice';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(invoiceData)
        });

        const data = await response.json();

        if (response.ok && data.success) {
            const typeLabel = invoiceType === 'purchase' ? 'Purchase' : 'Sales';
            let msg = `${typeLabel} invoice ${invoiceData.invoice_number} saved successfully!`;
            if (invoiceType === 'sales' && data.profit) {
                msg += ` Profit: ₹${formatNumber(data.profit)}`;
            }
            showToast(msg, 'success');

            // Reset and reload
            setTimeout(() => {
                resetUploadZone();
                loadStats();
                loadInvoices(currentInvoiceFilter);
                loadInventory();
            }, 1500);

        } else {
            // Show actual error from backend
            const errorMsg = data.error || data.message || response.statusText || 'Unknown error';
            showToast(`Save failed: ${errorMsg}`, 'error');
            console.error('Save error details:', data);
        }

    } catch (error) {
        console.error('Save error:', error);
        showToast(`Save failed: ${error.message}`, 'error');
    } finally {
        btnSave.disabled = false;
        btnSave.innerHTML = originalHTML;
    }
}

// ========== Load Invoices ==========
async function loadInvoices(type = 'purchase') {
    try {
        const response = await fetch(`/api/invoices?type=${type}&limit=50`);
        const data = await response.json();

        if (data.success) {
            displayInvoices(data.invoices, type);
        }
    } catch (error) {
        console.error('Failed to load invoices:', error);
    }
}

function displayInvoices(invoices, type) {
    const container = document.getElementById('invoicesList');

    if (!invoices || invoices.length === 0) {
        const typeLabel = type === 'purchase' ? 'purchase' : 'sales';
        container.innerHTML = `<p class="placeholder-text">📄 No ${typeLabel} invoices yet.</p>`;
        return;
    }

    container.innerHTML = invoices.map(inv => {
        const partnerLabel = type === 'purchase' ? 'Supplier' : 'Customer';
        const icon = type === 'purchase' ? '📥' : '📤';

        let profitHTML = '';
        if (type === 'sales' && inv.profit !== undefined) {
            profitHTML = `<p style="color: var(--success); font-size: 1rem; margin-top: 0.5rem;">
                💰 Profit: ₹${formatNumber(inv.profit)}
            </p>`;
        }

        return `
        <div class="review-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h3 class="review-card-title">${icon} ${inv.invoice_number}</h3>
                    <p style="color: var(--text-secondary); margin-bottom: 0.5rem;">
                        <strong>${inv.partner_name}</strong> (${partnerLabel})
                    </p>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">
                        📅 ${formatDate(inv.date)} | 📦 ${inv.items_count} items
                    </p>
                    ${profitHTML}
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
    `;
    }).join('');
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
                    ${items.map(item => {
        const stockColor = item.stock <= 0 ? 'var(--error)' : 'var(--text-primary)';
        return `
                        <tr>
                            <td><strong>${item.name}</strong></td>
                            <td style="color: ${stockColor};">${formatNumber(item.stock)}</td>
                            <td>${item.unit}</td>
                            <td>₹${formatNumber(item.cost_price)}</td>
                            <td>₹${formatNumber(item.selling_price)}</td>
                            <td>₹${formatNumber(item.stock * item.cost_price)}</td>
                        </tr>
                    `;
    }).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// ========== Analytics ==========
async function loadAnalytics() {
    try {
        // Load comprehensive analytics
        const response = await fetch('/api/analytics/dashboard');
        const data = await response.json();

        if (data.success) {
            displayAnalytics(data.analytics);
        }

        // Load low stock separately
        loadLowStock();
    } catch (error) {
        console.error('Failed to load analytics:', error);
    }
}

function displayAnalytics(analytics) {
    // Overview stats
    document.getElementById('analytics-total-sales').textContent = `₹${formatNumber(analytics.overview.total_sales)}`;
    document.getElementById('analytics-total-profit').textContent = `₹${formatNumber(analytics.overview.total_profit)}`;
    document.getElementById('analytics-margin').textContent = `${formatNumber(analytics.overview.profit_margin)}%`;
    document.getElementById('analytics-stock-value').textContent = `₹${formatNumber(analytics.overview.stock_value)}`;

    // Cash flow
    document.getElementById('analytics-receivables').textContent = `₹${formatNumber(analytics.cash_flow.pending_receivables)}`;
    document.getElementById('analytics-payables').textContent = `₹${formatNumber(analytics.cash_flow.pending_payables)}`;
    const netCash = analytics.cash_flow.net_cash;
    const netCashEl = document.getElementById('analytics-net-cash');
    netCashEl.textContent = `₹${formatNumber(netCash)}`;
    netCashEl.style.color = netCash >= 0 ? 'var(--success)' : 'var(--error)';

    // Top items
    const topItemsBody = document.getElementById('analytics-top-items');
    if (analytics.top_items.length > 0) {
        topItemsBody.innerHTML = analytics.top_items.map(item => `
            <tr>
                <td><strong>${item.name}</strong></td>
                <td>${formatNumber(item.qty_sold)}</td>
                <td style="color: var(--success);">₹${formatNumber(item.profit)}</td>
            </tr>
        `).join('');
    } else {
        topItemsBody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">No sales data yet</td></tr>';
    }

    // Top suppliers
    const suppliersDiv = document.getElementById('analytics-top-suppliers');
    if (analytics.top_suppliers.length > 0) {
        suppliersDiv.innerHTML = analytics.top_suppliers.map((s, i) => `
            <div style="padding: 0.75rem; border-bottom: 1px solid var(--border-color);">
                <div style="display: flex; justify-content: space-between;">
                    <span><strong>${i + 1}. ${s.name}</strong></span>
                    <span style="color: var(--primary);">₹${formatNumber(s.total)}</span>
                </div>
            </div>
        `).join('');
    } else {
        suppliersDiv.innerHTML = '<p style="text-align: center; color: var(--text-muted);">No suppliers yet</p>';
    }

    // Top customers
    const customersDiv = document.getElementById('analytics-top-customers');
    if (analytics.top_customers.length > 0) {
        customersDiv.innerHTML = analytics.top_customers.map((c, i) => `
            <div style="padding: 0.75rem; border-bottom: 1px solid var(--border-color);">
                <div style="display: flex; justify-content: space-between;">
                    <span><strong>${i + 1}. ${c.name}</strong></span>
                    <span style="color: var(--success);">₹${formatNumber(c.total)}</span>
                </div>
            </div>
        `).join('');
    } else {
        customersDiv.innerHTML = '<p style="text-align: center; color: var(--text-muted);">No customers yet</p>';
    }
}

async function loadLowStock() {
    try {
        const response = await fetch('/api/analytics/low-stock');
        const data = await response.json();

        if (data.success) {
            const tbody = document.getElementById('analytics-low-stock');

            if (data.low_stock_items.length > 0) {
                tbody.innerHTML = data.low_stock_items.map(item => `
                    <tr>
                        <td><strong>${item.name}</strong></td>
                        <td style="color: var(--error);">${formatNumber(item.current_stock)}</td>
                        <td>${formatNumber(item.min_level)}</td>
                        <td style="color: var(--error);">${formatNumber(item.shortage)}</td>
                        <td>₹${formatNumber(item.reorder_value)}</td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--success);">✅ All items have sufficient stock!</td></tr>';
            }
        }
    } catch (error) {
        console.error('Failed to load low stock:', error);
    }
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
    }, 5000);
}
