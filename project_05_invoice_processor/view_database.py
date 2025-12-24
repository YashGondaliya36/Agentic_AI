"""
Database Viewer - View InvoiceIQ Data
Simple CLI tool to view database contents
"""

from models import get_session, get_engine
from models import Supplier, Customer, Item, PurchaseInvoice, SalesInvoice, PurchaseItem, SalesItem
from rich.console import Console
from rich.table import Table
from rich import box
import sys

console = Console()

def show_menu():
    """Display main menu"""
    console.print("\n[bold cyan]📊 InvoiceIQ Database Viewer[/bold cyan]\n")
    console.print("1. View Suppliers")
    console.print("2. View Customers")
    console.print("3. View Items (Inventory)")
    console.print("4. View Purchase Invoices")
    console.print("5. View Sales Invoices")
    console.print("6. View Purchase Invoice Details")
    console.print("7. View Sales Invoice Details")
    console.print("8. Database Statistics")
    console.print("0. Exit\n")

def view_suppliers():
    """View all suppliers"""
    session = get_session()
    suppliers = session.query(Supplier).all()
    
    table = Table(title="📦 Suppliers", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("GSTIN", style="yellow")
    table.add_column("Phone", style="blue")
    table.add_column("Payment Terms", style="magenta")
    
    for s in suppliers:
        table.add_row(
            str(s.id),
            s.name,
            s.gstin or "-",
            s.phone or "-",
            f"{s.payment_terms_days} days"
        )
    
    console.print(table)
    console.print(f"\n[green]Total Suppliers: {len(suppliers)}[/green]")
    session.close()

def view_customers():
    """View all customers"""
    session = get_session()
    customers = session.query(Customer).all()
    
    table = Table(title="👥 Customers", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("GSTIN", style="yellow")
    table.add_column("Phone", style="blue")
    table.add_column("Credit Limit", style="magenta")
    
    for c in customers:
        table.add_row(
            str(c.id),
            c.name,
            c.gstin or "-",
            c.phone or "-",
            f"₹{c.credit_limit:,.2f}"
        )
    
    console.print(table)
    console.print(f"\n[green]Total Customers: {len(customers)}[/green]")
    session.close()

def view_items():
    """View all inventory items"""
    session = get_session()
    items = session.query(Item).all()
    
    table = Table(title="📦 Inventory", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Stock", style="yellow")
    table.add_column("Unit", style="blue")
    table.add_column("Cost Price", style="magenta")
    table.add_column("Selling Price", style="green")
    table.add_column("Stock Value", style="cyan")
    
    total_value = 0
    for item in items:
        stock_value = item.current_stock * item.last_cost_price
        total_value += stock_value
        
        # Color code stock
        stock_color = "red" if item.current_stock <= item.min_stock_level else "green"
        
        table.add_row(
            str(item.id),
            item.name,
            f"[{stock_color}]{item.current_stock:.2f}[/{stock_color}]",
            item.unit,
            f"₹{item.last_cost_price:,.2f}",
            f"₹{item.default_selling_price:,.2f}",
            f"₹{stock_value:,.2f}"
        )
    
    console.print(table)
    console.print(f"\n[green]Total Items: {len(items)}[/green]")
    console.print(f"[cyan]Total Stock Value: ₹{total_value:,.2f}[/cyan]")
    session.close()

def view_purchase_invoices():
    """View all purchase invoices"""
    session = get_session()
    invoices = session.query(PurchaseInvoice).order_by(PurchaseInvoice.invoice_date.desc()).all()
    
    table = Table(title="📥 Purchase Invoices", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Invoice #", style="green")
    table.add_column("Supplier", style="yellow")
    table.add_column("Date", style="blue")
    table.add_column("Total", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Items", style="cyan")
    
    total_amount = 0
    for inv in invoices:
        total_amount += inv.total_amount
        table.add_row(
            str(inv.id),
            inv.invoice_number,
            inv.supplier.name,
            inv.invoice_date.strftime("%Y-%m-%d"),
            f"₹{inv.total_amount:,.2f}",
            inv.payment_status.value,
            str(len(inv.items))
        )
    
    console.print(table)
    console.print(f"\n[green]Total Invoices: {len(invoices)}[/green]")
    console.print(f"[cyan]Total Amount: ₹{total_amount:,.2f}[/cyan]")
    session.close()

def view_sales_invoices():
    """View all sales invoices"""
    session = get_session()
    invoices = session.query(SalesInvoice).order_by(SalesInvoice.invoice_date.desc()).all()
    
    table = Table(title="📤 Sales Invoices", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Invoice #", style="green")
    table.add_column("Customer", style="yellow")
    table.add_column("Date", style="blue")
    table.add_column("Total", style="magenta")
    table.add_column("Profit", style="green")
    table.add_column("Status", style="cyan")
    table.add_column("Items", style="yellow")
    
    total_amount = 0
    total_profit = 0
    for inv in invoices:
        total_amount += inv.total_amount
        total_profit += inv.total_profit
        
        table.add_row(
            str(inv.id),
            inv.invoice_number,
            inv.customer.name,
            inv.invoice_date.strftime("%Y-%m-%d"),
            f"₹{inv.total_amount:,.2f}",
            f"₹{inv.total_profit:,.2f}",
            inv.payment_status.value,
            str(len(inv.items))
        )
    
    console.print(table)
    console.print(f"\n[green]Total Invoices: {len(invoices)}[/green]")
    console.print(f"[cyan]Total Revenue: ₹{total_amount:,.2f}[/cyan]")
    console.print(f"[green]Total Profit: ₹{total_profit:,.2f}[/green]")
    session.close()

def view_purchase_invoice_details():
    """View detailed purchase invoice"""
    inv_id = console.input("\n[cyan]Enter Purchase Invoice ID: [/cyan]")
    
    try:
        session = get_session()
        invoice = session.query(PurchaseInvoice).get(int(inv_id))
        
        if not invoice:
            console.print("[red]Invoice not found![/red]")
            session.close()
            return
        
        # Invoice header
        console.print(f"\n[bold green]📥 Purchase Invoice #{invoice.invoice_number}[/bold green]")
        console.print(f"Supplier: [cyan]{invoice.supplier.name}[/cyan]")
        console.print(f"Date: {invoice.invoice_date.strftime('%Y-%m-%d')}")
        console.print(f"Status: {invoice.payment_status.value}\n")
        
        # Items table
        table = Table(title="Items", box=box.ROUNDED)
        table.add_column("Item", style="green")
        table.add_column("Qty", style="cyan")
        table.add_column("Unit Price", style="yellow")
        table.add_column("GST", style="blue")
        table.add_column("Total", style="magenta")
        
        for item in invoice.items:
            table.add_row(
                item.item_name,
                f"{item.quantity:.2f} {item.unit}",
                f"₹{item.unit_price:,.2f}",
                f"{item.gst_rate}%",
                f"₹{item.total:,.2f}"
            )
        
        console.print(table)
        console.print(f"\n[yellow]Subtotal: ₹{invoice.subtotal:,.2f}[/yellow]")
        console.print(f"[blue]GST: ₹{invoice.gst_amount:,.2f}[/blue]")
        console.print(f"[bold green]Total: ₹{invoice.total_amount:,.2f}[/bold green]")
        
        session.close()
    except ValueError:
        console.print("[red]Invalid ID![/red]")

def view_sales_invoice_details():
    """View detailed sales invoice"""
    inv_id = console.input("\n[cyan]Enter Sales Invoice ID: [/cyan]")
    
    try:
        session = get_session()
        invoice = session.query(SalesInvoice).get(int(inv_id))
        
        if not invoice:
            console.print("[red]Invoice not found![/red]")
            session.close()
            return
        
        # Invoice header
        console.print(f"\n[bold green]📤 Sales Invoice #{invoice.invoice_number}[/bold green]")
        console.print(f"Customer: [cyan]{invoice.customer.name}[/cyan]")
        console.print(f"Date: {invoice.invoice_date.strftime('%Y-%m-%d')}")
        console.print(f"Status: {invoice.payment_status.value}\n")
        
        # Items table
        table = Table(title="Items", box=box.ROUNDED)
        table.add_column("Item", style="green")
        table.add_column("Qty", style="cyan")
        table.add_column("Cost", style="yellow")
        table.add_column("Unit Price", style="blue")
        table.add_column("Profit/Unit", style="magenta")
        table.add_column("Total Profit", style="green")
        
        for item in invoice.items:
            table.add_row(
                item.item.name,
                f"{item.quantity:.2f}",
                f"₹{item.cost_price:,.2f}",
                f"₹{item.unit_price:,.2f}",
                f"₹{item.profit_per_unit:,.2f}",
                f"₹{item.total_profit:,.2f}"
            )
        
        console.print(table)
        console.print(f"\n[yellow]Subtotal: ₹{invoice.subtotal:,.2f}[/yellow]")
        console.print(f"[blue]GST: ₹{invoice.gst_amount:,.2f}[/blue]")
        console.print(f"[cyan]Total Cost: ₹{invoice.total_cost:,.2f}[/cyan]")
        console.print(f"[bold green]Total: ₹{invoice.total_amount:,.2f}[/bold green]")
        console.print(f"[bold magenta]Profit: ₹{invoice.total_profit:,.2f}[/bold magenta]")
        
        session.close()
    except ValueError:
        console.print("[red]Invalid ID![/red]")

def show_statistics():
    """Show database statistics"""
    session = get_session()
    
    # Count records
    suppliers_count = session.query(Supplier).count()
    customers_count = session.query(Customer).count()
    items_count = session.query(Item).count()
    purchase_count = session.query(PurchaseInvoice).count()
    sales_count = session.query(SalesInvoice).count()
    
    # Calculate totals
    purchases_total = sum([inv.total_amount for inv in session.query(PurchaseInvoice).all()])
    sales_total = sum([inv.total_amount for inv in session.query(SalesInvoice).all()])
    profit_total = sum([inv.total_profit for inv in session.query(SalesInvoice).all()])
    
    # Stock value
    stock_value = sum([item.current_stock * item.last_cost_price for item in session.query(Item).all()])
    
    table = Table(title="📊 Database Statistics", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Suppliers", str(suppliers_count))
    table.add_row("Customers", str(customers_count))
    table.add_row("Items in Catalog", str(items_count))
    table.add_row("Purchase Invoices", str(purchase_count))
    table.add_row("Sales Invoices", str(sales_count))
    table.add_row("", "")  # Separator
    table.add_row("Total Purchases", f"₹{purchases_total:,.2f}")
    table.add_row("Total Sales", f"₹{sales_total:,.2f}")
    table.add_row("Total Profit", f"₹{profit_total:,.2f}")
    table.add_row("Stock Value", f"₹{stock_value:,.2f}")
    
    console.print(table)
    session.close()

def main():
    """Main menu loop"""
    while True:
        show_menu()
        choice = console.input("[cyan]Enter choice: [/cyan]")
        
        try:
            if choice == "1":
                view_suppliers()
            elif choice == "2":
                view_customers()
            elif choice == "3":
                view_items()
            elif choice == "4":
                view_purchase_invoices()
            elif choice == "5":
                view_sales_invoices()
            elif choice == "6":
                view_purchase_invoice_details()
            elif choice == "7":
                view_sales_invoice_details()
            elif choice == "8":
                show_statistics()
            elif choice == "0":
                console.print("\n[green]Goodbye! 👋[/green]\n")
                break
            else:
                console.print("[red]Invalid choice![/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        
        console.input("\n[dim]Press Enter to continue...[/dim]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted! Goodbye! 👋[/yellow]\n")
        sys.exit(0)
