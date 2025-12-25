# 🎉 InvoiceIQ - AI Invoice Processor

**Production-Ready Invoice Management System for Hardware Distributors**

A comprehensive AI-powered invoice processing system with purchase/sales tracking, inventory management, profit analytics, and business intelligence.

---

## ✨ **Features**

### **Core Features** ✅
- 📥 **Purchase Invoice Processing** - Upload supplier invoices, AI extracts data
- 📤 **Sales Invoice Processing** - Upload customer invoices, calculate profit
- 🤖 **AI-Powered Extraction** - Gemini Vision AI with text extraction (quota-friendly)
- 📦 **Stock Management** - Auto Stock IN/OUT tracking
- 💰 **Profit Tracking** - Real-time profit calculations per transaction
- 👥 **Customer & Supplier Management** - Auto-create and track partners

### **Analytics & Reports** 📊
- 📈 **Business Dashboard** - Total sales, profit, margins, stock value
- 💸 **Cash Flow Tracking** - Receivables, payables, net position
- 🏆 **Top Performers** - Best-selling items, top suppliers/customers
- ⚠️ **Low Stock Alerts** - Automatic reorder suggestions
- 📉 **Profit & Loss** - Detailed P&L reports by item

### **Technical Features** ⚡
- 🎨 **Beautiful UI** - Glassmorphism design with smooth animations
- 🔄 **Real-time Updates** - Live data synchronization
- 💾 **SQLite Database** - Lightweight, serverless database
- 🔍 **Smart Item Matching** - Fuzzy name matching for catalog items
- 📱 **Responsive** - Works on desktop, tablet, mobile

---

## 🏗️ **Architecture**

```
project_05_invoice_processor/
├── app.py                 # FastAPI backend (main server)
├── ai_extractor.py        # Gemini AI + text extraction
├── analytics.py           # Analytics & reports API
├── models.py              # Database schema (SQLAlchemy)
├── requirements.txt       # Dependencies
├── .gitignore            # Git ignore rules
├── templates/
│   └── index.html        # Main UI
├── static/
│   ├── css/
│   │   └── style.css     # Premium design
│   └── js/
│       └── app.js        # Frontend logic
└── uploads/              # Invoice files (auto-created)
```

---

## 🚀 **Quick Start**

### **1. Prerequisites**
- Python 3.8+
- Virtual environment (recommended)
- Google Gemini API key

### **2. Installation**

```bash
# Navigate to project
cd project_05_invoice_processor

# Activate virtual environment
# Windows:
F:\Data_Science_Project\temp\.venv\Scripts\activate.ps1

# Install dependencies
pip install -r requirements.txt

# Optional: Install OCR for image invoices
pip install pdfplumber pytesseract
```

### **3. Configure API Key**

Create `.env` file in parent directory (`Agentic_ai/.env`):
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### **4. Run Server**

```bash
python app.py
```

Open browser: **http://localhost:8000**

---

## 📖 **Usage Guide**

### **Upload Purchase Invoice** (Stock IN)
1. Select **📥 Purchase Invoice**
2. Upload supplier invoice (PDF/Image)
3. AI extracts supplier, items, prices
4. Review & edit if needed
5. Save → Stock increases

### **Upload Sales Invoice** (Stock OUT)
1. Select **📤 Sales Invoice**
2. Upload customer invoice (PDF/Image)
3. AI extracts customer, items sold
4. See **real-time profit** calculations
5. Save → Stock decreases, profit tracked

### **View Analytics**
- Click **📊 Analytics** tab
- See total profit, margins, cash flow
- Track top items, suppliers, customers
- Monitor low stock alerts

---

## 🔧 **How It Works**

### **AI Extraction (Quota-Friendly)**
```
Old Way (File Upload):
PDF → Send to Gemini → Parse
❌ Low quota: 5 requests/min

New Way (Text Extraction):
PDF → PyPDF extracts text → Send text to Gemini → Parse
✅ High quota: 60 requests/min
```

### **Purchase Flow**
```
Upload Invoice
    ↓
AI extracts: Supplier, Items, Prices
    ↓
Match with existing items OR create new
    ↓
Save to database
    ↓
Stock += Quantity (Stock IN)
```

### **Sales Flow**
```
Upload Invoice
    ↓
AI extracts: Customer, Items, Prices
    ↓
Match with catalog (must exist or auto-create)
    ↓
Calculate profit: (Selling Price - Cost Price) × Qty
    ↓
Save to database
    ↓
Stock -= Quantity (Stock OUT)
    ↓
Track profit
```

---

## 💾 **Database Schema**

### **Tables**
- `suppliers` - Supplier/vendor master
- `customers` - Customer master
- `items` - Item catalog with stock tracking
- `purchase_invoices` - Purchase invoice headers
- `purchase_items` - Purchase line items
- `sales_invoices` - Sales invoice headers (with profit)
- `sales_items` - Sales line items (with profit per item)

### **View Database**

```bash
# Interactive CLI viewer
python view_database.py

# Or use SQLite browser
sqlite3 invoice_data.db
```

---

## 📊 **Analytics API**

### **Endpoints**

```
GET /api/analytics/dashboard
Returns: Overview, cash flow, top items/suppliers/customers

GET /api/analytics/profit-loss
Returns: P&L statement with item-wise breakdown

GET /api/analytics/low-stock
Returns: Items below min stock level

POST /api/invoices/mark-paid/{invoice_id}
Mark invoice as paid
```

---

## 🎨 **UI Highlights**

- **Glassmorphism Design** - Modern, premium look
- **Animated Gradients** - Floating orb background
- **Smooth Transitions** - Every interaction animated
- **Real-time Stats** - Live dashboard updates
- **Invoice Type Selector** - Visual purchase/sales choice
- **Profit Visualization** - Color-coded profit displays
- **Low Stock Alerts** - Red highlights for critical items

---

## 🔐 **Security**

- `.gitignore` protects sensitive files
- API keys via environment variables
- No hardcoded credentials
- Database stored locally (not committed)

---

## 🛠️ **Configuration**

### **Disable Smart Matching (Quota Saving)**
In `app.py`, smart AI matching is already disabled:
```python
# Simple name matching (exact match)
matched_item = next((item for item in catalog_items 
                   if item.name.lower() == item_name), None)
```

### **Auto-Create Items During Sales**
Items not in catalog are auto-created with:
- Stock: 999 (default)
- Cost = Selling price (update via purchase later)

---

## 📚 **Tech Stack**

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI |
| Frontend | Vanilla JS |
| AI | Google Gemini 2.5 Flash |
| Database | SQLite + SQLAlchemy |
| UI | CSS (Glassmorphism) |
| PDF Extraction | pdfplumber |
| OCR | pytesseract (optional) |

---

## 🐛 **Troubleshooting**

### **Quota Exceeded Error**
- **Solution**: Text extraction uses less quota
- Current limit: 60 requests/min (vs 5 with file upload)

### **Item Not Found Error**
- **Solution**: Items auto-created during sales now
- Or upload purchase invoice first

### **Low Stock Error**
- **Solution**: Upload purchase invoice to restock
- Or manually adjust default stock (999)

---

## 🎯 **Roadmap**

- [ ] Export invoices to PDF
- [ ] Multi-user support
- [ ] Role-based access
- [ ] WhatsApp invoice upload
- [ ] Advanced reporting
- [ ] Batch invoice processing

---

## 📄 **License**

This project is for educational purposes.

---

## 🙏 **Credits**

Built with:
- Google Gemini AI
- FastAPI
- SQLAlchemy
- Modern Web Standards

---

## 📧 **Support**

For issues or questions:
1. Check logs in terminal
2. Verify `.env` configuration
3. Ensure database permissions

---

**Made with ❤️ for Hardware Distributors**
