"""
Analytics & Reports API Endpoints
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from models import (
    get_session, get_engine,
    PurchaseInvoice, SalesInvoice, Item, Supplier, Customer,
    PurchaseItem, SalesItem
)

router = APIRouter()


@router.get("/api/analytics/dashboard")
async def get_dashboard_analytics():
    """Get comprehensive dashboard analytics"""
    try:
        session = get_session(get_engine())
        
        # Time periods
        today = datetime.now().date()
        month_start = today.replace(day=1)
        last_month = (month_start - timedelta(days=1)).replace(day=1)
        
        # Purchase stats
        total_purchases = session.query(func.sum(PurchaseInvoice.total_amount)).scalar() or 0
        purchases_this_month = session.query(func.sum(PurchaseInvoice.total_amount)).filter(
            PurchaseInvoice.invoice_date >= month_start
        ).scalar() or 0
        
        # Sales stats
        total_sales = session.query(func.sum(SalesInvoice.total_amount)).scalar() or 0
        total_profit = session.query(func.sum(SalesInvoice.total_profit)).scalar() or 0
        sales_this_month = session.query(func.sum(SalesInvoice.total_amount)).filter(
            SalesInvoice.invoice_date >= month_start
        ).scalar() or 0
        profit_this_month = session.query(func.sum(SalesInvoice.total_profit)).filter(
            SalesInvoice.invoice_date >= month_start
        ).scalar() or 0
        
        # Stock value
        items = session.query(Item).all()
        total_stock_value = sum(item.current_stock * item.last_cost_price for item in items)
        low_stock_count = sum(1 for item in items if item.current_stock <= item.min_stock_level)
        
        # Top suppliers (by purchase amount)
        top_suppliers = session.query(
            Supplier.name,
            func.sum(PurchaseInvoice.total_amount).label('total')
        ).join(PurchaseInvoice).group_by(Supplier.id).order_by(desc('total')).limit(5).all()
        
        # Top customers (by sales amount)
        top_customers = session.query(
            Customer.name,
            func.sum(SalesInvoice.total_amount).label('total')
        ).join(SalesInvoice).group_by(Customer.id).order_by(desc('total')).limit(5).all()
        
        # Top selling items
        top_items = session.query(
            Item.name,
            func.sum(SalesItem.quantity).label('qty_sold'),
            func.sum(SalesItem.total_profit).label('profit')
        ).join(SalesItem).group_by(Item.id).order_by(desc('profit')).limit(5).all()
        
        # Payment status
        pending_receivables = session.query(func.sum(SalesInvoice.total_amount)).filter(
            SalesInvoice.payment_status == 'pending'
        ).scalar() or 0
        
        pending_payables = session.query(func.sum(PurchaseInvoice.total_amount)).filter(
            PurchaseInvoice.payment_status == 'pending'
        ).scalar() or 0
        
        session.close()
        
        return JSONResponse({
            "success": True,
            "analytics": {
                "overview": {
                    "total_purchases": float(total_purchases),
                    "total_sales": float(total_sales),
                    "total_profit": float(total_profit),
                    "profit_margin": (float(total_profit) / float(total_sales) * 100) if total_sales > 0 else 0,
                    "stock_value": float(total_stock_value),
                    "low_stock_alerts": low_stock_count
                },
                "this_month": {
                    "purchases": float(purchases_this_month),
                    "sales": float(sales_this_month),
                    "profit": float(profit_this_month),
                },
                "cash_flow": {
                    "pending_receivables": float(pending_receivables),
                    "pending_payables": float(pending_payables),
                    "net_cash": float(pending_receivables - pending_payables)
                },
                "top_suppliers": [{"name": s[0], "total": float(s[1])} for s in top_suppliers],
                "top_customers": [{"name": c[0], "total": float(c[1])} for c in top_customers],
                "top_items": [{"name": i[0], "qty_sold": float(i[1]), "profit": float(i[2])} for i in top_items]
            }
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.get("/api/analytics/profit-loss")
async def get_profit_loss():
    """Get profit & loss statement"""
    try:
        session = get_session(get_engine())
        
        # Revenue (Sales)
        total_revenue = session.query(func.sum(SalesInvoice.total_amount)).scalar() or 0
        
        # Cost of Goods Sold
        total_cogs = session.query(func.sum(SalesInvoice.total_cost)).scalar() or 0
        
        # Gross Profit
        gross_profit = total_revenue - total_cogs
        
        # Get detailed breakdown by item
        item_profits = session.query(
            Item.name,
            func.sum(SalesItem.quantity).label('qty_sold'),
            func.sum(SalesItem.subtotal).label('revenue'),
            func.sum(SalesItem.quantity * SalesItem.cost_price).label('cost'),
            func.sum(SalesItem.total_profit).label('profit')
        ).join(SalesItem).group_by(Item.id).all()
        
        session.close()
        
        return JSONResponse({
            "success": True,
            "profit_loss": {
                "summary": {
                    "total_revenue": float(total_revenue),
                    "cost_of_goods": float(total_cogs),
                    "gross_profit": float(gross_profit),
                    "gross_margin": (float(gross_profit) / float(total_revenue) * 100) if total_revenue > 0 else 0
                },
                "by_item": [{
                    "name": item[0],
                    "qty_sold": float(item[1]),
                    "revenue": float(item[2]),
                    "cost": float(item[3]),
                    "profit": float(item[4]),
                    "margin": (float(item[4]) / float(item[2]) * 100) if item[2] > 0 else 0
                } for item in item_profits]
            }
        })
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.get("/api/analytics/low-stock")
async def get_low_stock_items():
    """Get items with low stock"""
    try:
        session = get_session(get_engine())
        
        low_stock_items = session.query(Item).filter(
            Item.current_stock <= Item.min_stock_level
        ).all()
        
        result = [{
            "id": item.id,
            "name": item.name,
            "current_stock": item.current_stock,
            "min_level": item.min_stock_level,
            "unit": item.unit,
            "shortage": item.min_stock_level - item.current_stock,
            "last_cost": item.last_cost_price,
            "reorder_value": (item.min_stock_level - item.current_stock) * item.last_cost_price
        } for item in low_stock_items]
        
        session.close()
        
        return JSONResponse({
            "success": True,
            "low_stock_items": result,
            "count": len(result),
            "total_reorder_value": sum(i["reorder_value"] for i in result)
        })
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.post("/api/invoices/mark-paid/{invoice_id}")
async def mark_invoice_paid(invoice_id: int, invoice_type: str = "purchase"):
    """Mark invoice as paid"""
    try:
        session = get_session(get_engine())
        
        if invoice_type == "purchase":
            invoice = session.query(PurchaseInvoice).get(invoice_id)
        else:
            invoice = session.query(SalesInvoice).get(invoice_id)
        
        if not invoice:
            return JSONResponse({"success": False, "error": "Invoice not found"}, status_code=404)
        
        invoice.payment_status = "paid"
        session.commit()
        session.close()
        
        return JSONResponse({
            "success": True,
            "message": f"Invoice marked as paid"
        })
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
