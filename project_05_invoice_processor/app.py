"""FastAPI Backend for InvoiceIQ"""

import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Import our modules
from models import (
    init_database, get_session,
    Supplier, Customer, Item,
    PurchaseInvoice, PurchaseItem,
    SalesInvoice, SalesItem,
    PaymentStatus
)
from ai_extractor import extractor

# Initialize FastAPI
app = FastAPI(title="InvoiceIQ - AI Invoice Processor", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize database
engine = init_database()


# ========== HOME PAGE ==========

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main dashboard"""
    return templates.TemplateResponse("index.html", {"request": request})


# ========== INVOICE UPLOAD & EXTRACTION ==========

@app.post("/api/upload-invoice")
async def upload_invoice(file: UploadFile = File(...)):
    """
    Upload and extract purchase invoice.
    
    Flow:
    1. Save uploaded file
    2. AI extracts data using Gemini Vision
    3. Match items with catalog
    4. Return extracted data for review
    """
    try:
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = Path(file.filename).suffix
        safe_filename = f"invoice_{timestamp}{file_ext}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Write file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        print(f"\n📤 Uploaded: {file.filename} → {safe_filename}")
        
        # Extract invoice data using AI
        result = extractor.extract_purchase_invoice(str(file_path))
        
        if not result.get("success"):
            return JSONResponse({
                "success": False,
                "error": result.get("error", "Extraction failed"),
                "file_path": str(file_path)
            })
        
        invoice_data = result["data"]
        
        # Get database session
        session =get_session(engine)
        
        # Try to match/find supplier
        supplier_name = invoice_data.get("supplier_name", "").strip()
        supplier = None
        
        if supplier_name:
            supplier = session.query(Supplier).filter(
                Supplier.name.ilike(f"%{supplier_name}%")
            ).first()
        
        # Match items with catalog
        catalog_items = session.query(Item.id, Item.name, Item.description).all()
        catalog_list = [{"id": item.id, "name": item.name} for item in catalog_items]
        
        for item_data in invoice_data.get("items", []):
            matched = extractor.smart_item_match(item_data["name"], catalog_list)
            if matched:
                item_data["matched_item_id"] = matched["id"]
                item_data["matched_item_name"] = matched["name"]
        
        session.close()
        
        return JSONResponse({
            "success": True,
            "file_path": str(file_path),
            "filename": safe_filename,
            "data": invoice_data,
            "supplier_exists": supplier is not None,
            "supplier_id": supplier.id if supplier else None
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)


@app.post("/api/save-invoice")
async def save_invoice(request: Request):
    """
    Save reviewed/edited invoice to database.
    
    Expects JSON body with:
    - file_path
    - supplier (name, contact, etc.)
    - invoice_number, date, etc.
    - items []
    """
    try:
        data = await request.json()
        session = get_session(engine)
        
        # 1. Get or create supplier
        supplier_data = data.get("supplier", {})
        supplier_name = supplier_data.get("name", "").strip()
        
        if not supplier_name:
            raise HTTPException(400, "Supplier name required")
        
        supplier = session.query(Supplier).filter(Supplier.name == supplier_name).first()
        
        if not supplier:
            # Create new supplier
            supplier = Supplier(
                name=supplier_name,
                contact_person=supplier_data.get("contact_person"),
                phone=supplier_data.get("phone"),
                email=supplier_data.get("email"),
                address=supplier_data.get("address"),
                gstin=supplier_data.get("gstin"),
                payment_terms_days=supplier_data.get("payment_terms_days", 30)
            )
            session.add(supplier)
            session.commit()
            print(f"✅ Created new supplier: {supplier_name}")
        
        # 2. Create purchase invoice
        invoice_number = data.get("invoice_number", "").strip()
        
        # Check if already exists
        existing = session.query(PurchaseInvoice).filter(
            PurchaseInvoice.invoice_number == invoice_number
        ).first()
        
        if existing:
            raise HTTPException(400, f"Invoice {invoice_number} already exists!")
        
        invoice_date_str = data.get("invoice_date")
        invoice_date = datetime.fromisoformat(invoice_date_str) if invoice_date_str else datetime.now()
        
        due_date_str = data.get("due_date")
        due_date = datetime.fromisoformat(due_date_str) if due_date_str else (invoice_date + timedelta(days=30))
        
        purchase_invoice = PurchaseInvoice(
            supplier_id=supplier.id,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            subtotal=data.get("subtotal", 0),
            gst_amount=data.get("gst_amount", 0),
            total_amount=data.get("total_amount", 0),
            original_file_path=data.get("file_path"),
            extracted_text=data.get("raw_text", ""),
            notes=data.get("notes", "")
        )
        
        session.add(purchase_invoice)
        session.commit()
        
        # 3. Add line items
        items_data = data.get("items", [])
        
        for item_data in items_data:
            # Get or create item
            matched_item_id = item_data.get("matched_item_id")
            item_name = item_data.get("name", "").strip()
            
            if matched_item_id:
                item = session.query(Item).get(matched_item_id)
            else:
                # Create new item
                item = Item(
                    name=item_name,
                    description=item_data.get("description"),
                    hsn_code=item_data.get("hsn_code"),
                    unit=item_data.get("unit", "piece"),
                    last_cost_price=item_data.get("unit_price", 0),
                    gst_rate=item_data.get("gst_rate", 18),
                    current_stock=0
                )
                session.add(item)
                session.commit()
                print(f"   ➕ Created new item: {item_name}")
            
            # Create purchase item
            purchase_item = PurchaseItem(
                invoice_id=purchase_invoice.id,
                item_id=item.id,
                item_name=item_name,
                quantity=item_data.get("quantity", 0),
                unit=item_data.get("unit", "piece"),
                unit_price=item_data.get("unit_price", 0),
                subtotal=item_data.get("subtotal", 0),
                gst_rate=item_data.get("gst_rate", 18),
                gst_amount=item_data.get("gst_amount", 0),
                total=item_data.get("total", 0)
            )
            
            session.add(purchase_item)
            
            # Update item cost and stock
            item.last_cost_price = item_data.get("unit_price", 0)
            item.current_stock += item_data.get("quantity", 0)
        
        session.commit()
        
        # Get ID before closing session
        invoice_id = purchase_invoice.id
        
        session.close()
        
        print(f"✅ Saved invoice: {invoice_number} ({len(items_data)} items)")
        
        return JSONResponse({
            "success": True,
            "message": "Invoice saved successfully!",
            "invoice_id": invoice_id,
            "invoice_number": invoice_number
        })
    
    except HTTPException as e:
        raise e
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({
         "success": False,
            "error": str(e)
        }, status_code=500)


# ========== DATA RETRIEVAL ==========

@app.get("/api/invoices")
async def get_invoices(type: str = "purchase", limit: int = 50):
    """Get recent invoices"""
    try:
        session = get_session(engine)
        
        if type == "purchase":
            invoices = session.query(PurchaseInvoice).order_by(
                PurchaseInvoice.invoice_date.desc()
            ).limit(limit).all()
            
            result = [{
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "supplier_name": inv.supplier.name,
                "date": inv.invoice_date.isoformat(),
                "total": inv.total_amount,
                "payment_status": inv.payment_status.value,
                "items_count": len(inv.items)
            } for inv in invoices]
        
        session.close()
        
        return JSONResponse({"success": True, "invoices": result})
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})


@app.get("/api/items")
async def get_items():
    """Get all items in catalog"""
    try:
        session = get_session(engine)
        items = session.query(Item).all()
        
        result = [{
            "id": item.id,
            "name": item.name,
            "stock": item.current_stock,
            "unit": item.unit,
            "cost_price": item.last_cost_price,
            "selling_price": item.default_selling_price
        } for item in items]
        
        session.close()
        
        return JSONResponse({"success": True, "items": result, "count": len(result)})
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})


@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    try:
        session = get_session(engine)
        
        total_invoices = session.query(PurchaseInvoice).count()
        total_items = session.query(Item).count()
        total_suppliers = session.query(Supplier).count()
        
        # Low stock items
        low_stock = session.query(Item).filter(
            Item.current_stock <= Item.min_stock_level
        ).count()
        
        session.close()
        
        return JSONResponse({
            "success": True,
            "stats": {
                "invoices": total_invoices,
                "items": total_items,
                "suppliers": total_suppliers,
                "low_stock_alerts": low_stock
            }
        })
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "InvoiceIQ"}


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting InvoiceIQ Server...")
    print("📍 Open browser: http://localhost:8000\n")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
