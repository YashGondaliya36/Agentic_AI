// API Base URL
const API_BASE = '';

// Global state
let currentEmail = null;
let allEmails = [];

// DOM Elements
const elements = {
    emailGrid: document.getElementById('emailGrid'),
    loading: document.getElementById('loading'),
    emptyState: document.getElementById('emptyState'),
    refreshBtn: document.getElementById('refreshBtn'),
    emailCount: document.getElementById('emailCount'),
    processedCount: document.getElementById('processedCount'),

    // Modal
    modal: document.getElementById('emailModal'),
    modalClose: document.getElementById('modalClose'),
    modalTitle: document.getElementById('modalTitle'),
    modalFrom: document.getElementById('modalFrom'),
    modalSubject: document.getElementById('modalSubject'),
    modalCategory: document.getElementById('modalCategory'),
    modalPriority: document.getElementById('modalPriority'),
    modalBody: document.getElementById('modalBody'),

    // Draft
    draftSection: document.getElementById('draftSection'),
    draftTextarea: document.getElementById('draftTextarea'),

    // Buttons
    classifyBtn: document.getElementById('classifyBtn'),
    generateDraftBtn: document.getElementById('generateDraftBtn'),
    sendBtn: document.getElementById('sendBtn'),
    regenerateBtn: document.getElementById('regenerateBtn'),
    archiveBtn: document.getElementById('archiveBtn'),

    toastContainer: document.getElementById('toastContainer')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadEmails();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    elements.refreshBtn.addEventListener('click', loadEmails);
    elements.modalClose.addEventListener('click', closeModal);
    elements.classifyBtn.addEventListener('click', classifyEmail);
    elements.generateDraftBtn.addEventListener('click', generateDraft);
    elements.sendBtn.addEventListener('click', sendEmail);
    elements.regenerateBtn.addEventListener('click', generateDraft);
    elements.archiveBtn.addEventListener('click', archiveEmail);

    // Close modal on outside click
    elements.modal.addEventListener('click', (e) => {
        if (e.target === elements.modal) closeModal();
    });

    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

// Load Emails
async function loadEmails() {
    showLoading(true);

    try {
        const response = await fetch(`${API_BASE}/api/emails`);
        const data = await response.json();

        if (data.success) {
            allEmails = data.emails;
            renderEmails(data.emails);
            updateStats(data.count);
        } else {
            showToast('Failed to load emails: ' + data.error, 'error');
        }
    } catch (error) {
        showToast('Error fetching emails: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Render Emails
function renderEmails(emails) {
    if (!emails || emails.length === 0) {
        elements.emailGrid.innerHTML = '';
        elements.emptyState.style.display = 'block';
        return;
    }

    elements.emptyState.style.display = 'none';

    elements.emailGrid.innerHTML = emails.map(email => `
        <div class="email-card" onclick="openEmail('${email.id}')">
            <div class="email-header">
                <div class="email-from">${escapeHtml(email.from_name)}</div>
                <div class="email-time">${formatTime(email.date)}</div>
            </div>
            <div class="email-subject">${escapeHtml(email.subject)}</div>
            <div class="email-preview">${escapeHtml(email.body)}</div>
        </div>
    `).join('');
}

// Open Email Modal
function openEmail(emailId) {
    currentEmail = allEmails.find(e => e.id === emailId);

    if (!currentEmail) return;

    elements.modalTitle.textContent = 'Email Details';
    elements.modalFrom.textContent = `${currentEmail.from_name} <${currentEmail.from_email}>`;
    elements.modalSubject.textContent = currentEmail.subject;
    elements.modalBody.textContent = currentEmail.full_body || currentEmail.body;
    elements.modalCategory.textContent = '-';
    elements.modalPriority.textContent = '-';

    // Hide draft section
    elements.draftSection.style.display = 'none';
    elements.draftTextarea.value = '';

    // Show modal
    elements.modal.classList.add('active');
}

// Close Modal
function closeModal() {
    elements.modal.classList.remove('active');
    currentEmail = null;
}

// Classify Email
async function classifyEmail() {
    if (!currentEmail) return;

    elements.classifyBtn.disabled = true;
    elements.classifyBtn.innerHTML = '<span class="btn-icon">⏳</span> Classifying...';

    try {
        const response = await fetch(`${API_BASE}/api/classify/${currentEmail.id}`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.success) {
            elements.modalCategory.textContent = data.category.toUpperCase();
            elements.modalCategory.className = `badge badge-${data.category}`;
            elements.modalPriority.textContent = `${data.priority}/5 ${'⭐'.repeat(data.priority)}`;

            showToast('Email classified successfully!', 'success');
        } else {
            showToast('Classification failed: ' + data.error, 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    } finally {
        elements.classifyBtn.disabled = false;
        elements.classifyBtn.innerHTML = '<span class="btn-icon">🏷️</span> Classify Email';
    }
}

// Generate Draft
async function generateDraft() {
    if (!currentEmail) return;

    elements.generateDraftBtn.disabled = true;
    elements.generateDraftBtn.innerHTML = '<span class="btn-icon">⏳</span> Generating...';

    try {
        const response = await fetch(`${API_BASE}/api/generate-draft/${currentEmail.id}`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.success) {
            elements.draftTextarea.value = data.draft;
            elements.draftSection.style.display = 'block';

            // Update classification if included
            if (data.category) {
                elements.modalCategory.textContent = data.category.toUpperCase();
                elements.modalCategory.className = `badge badge-${data.category}`;
                elements.modalPriority.textContent = `${data.priority}/5 ${'⭐'.repeat(data.priority)}`;
            }

            showToast('Draft generated successfully!', 'success');
        } else {
            showToast('Draft generation failed: ' + data.error, 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    } finally {
        elements.generateDraftBtn.disabled = false;
        elements.generateDraftBtn.innerHTML = '<span class="btn-icon">✍️</span> Generate Draft';
    }
}

// Send Email
async function sendEmail() {
    if (!currentEmail || !elements.draftTextarea.value) return;

    // Confirm before sending
    if (!confirm('Are you sure you want to send this email?')) return;

    elements.sendBtn.disabled = true;
    elements.sendBtn.innerHTML = '<span class="btn-icon">⏳</span> Sending...';

    try {
        const response = await fetch(`${API_BASE}/api/send-email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email_id: currentEmail.id,
                to: currentEmail.from_email,
                subject: `Re: ${currentEmail.subject}`,
                body: elements.draftTextarea.value
            })
        });
        const data = await response.json();

        if (data.success) {
            showToast('Email sent successfully!', 'success');
            closeModal();
            loadEmails(); // Refresh list
            updateStats(null, 1); // Increment processed count
        } else {
            showToast('Send failed: ' + data.error, 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    } finally {
        elements.sendBtn.disabled = false;
        elements.sendBtn.innerHTML = '<span class="btn-icon">📤</span> Send Email';
    }
}

// Archive Email
async function archiveEmail() {
    if (!currentEmail) return;

    elements.archiveBtn.disabled = true;
    elements.archiveBtn.innerHTML = '<span class="btn-icon">⏳</span> Archiving...';

    try {
        const response = await fetch(`${API_BASE}/api/archive/${currentEmail.id}`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.success) {
            showToast('Email archived!', 'success');
            closeModal();
            loadEmails(); // Refresh list
        } else {
            showToast('Archive failed: ' + data.error, 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    } finally {
        elements.archiveBtn.disabled = false;
        elements.archiveBtn.innerHTML = '<span class="btn-icon">📥</span> Archive';
    }
}

// Update Stats
function updateStats(emailCount, processedIncrement = 0) {
    if (emailCount !== null) {
        elements.emailCount.textContent = emailCount;
    }

    if (processedIncrement > 0) {
        const current = parseInt(elements.processedCount.textContent) || 0;
        elements.processedCount.textContent = current + processedIncrement;
    }
}

// Show/Hide Loading
function showLoading(show) {
    elements.loading.style.display = show ? 'block' : 'none';
    elements.emailGrid.style.display = show ? 'none' : 'grid';
}

// Show Toast
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return date.toLocaleDateString();
}
