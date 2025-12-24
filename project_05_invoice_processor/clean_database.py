"""
Clean Database - Reset InvoiceIQ Database
WARNING: This will delete ALL data!
"""

from models import get_session, get_engine, Base
from models import Supplier, Customer, Item, PurchaseInvoice, SalesInvoice, PurchaseItem, SalesItem
from rich.console import Console
from rich.panel import Panel
import os

console = Console()

def show_warning():
    """Show warning message"""
    warning_text = """
[bold red]⚠️  WARNING ⚠️[/bold red]

This will [bold red]DELETE ALL DATA[/bold red] from the database:

• All Suppliers
• All Customers  
• All Items (Inventory)
• All Purchase Invoices
• All Sales Invoices
• All transactions

[yellow]This action CANNOT be undone![/yellow]
    """
    
    panel = Panel(warning_text, title="[bold red]DANGER ZONE[/bold red]", border_style="red")
    console.print(panel)

def clean_database():
    """Delete all data from all tables"""
    console.print("\n[cyan]Starting database cleanup...[/cyan]\n")
    
    session = get_session()
    
    try:
        # Delete in correct order (respect foreign keys)
        
        # 1. Delete line items first
        sales_items_count = session.query(SalesItem).count()
        session.query(SalesItem).delete()
        console.print(f"[green]✓[/green] Deleted {sales_items_count} sales items")
        
        purchase_items_count = session.query(PurchaseItem).count()
        session.query(PurchaseItem).delete()
        console.print(f"[green]✓[/green] Deleted {purchase_items_count} purchase items")
        
        # 2. Delete invoices
        sales_inv_count = session.query(SalesInvoice).count()
        session.query(SalesInvoice).delete()
        console.print(f"[green]✓[/green] Deleted {sales_inv_count} sales invoices")
        
        purchase_inv_count = session.query(PurchaseInvoice).count()
        session.query(PurchaseInvoice).delete()
        console.print(f"[green]✓[/green] Deleted {purchase_inv_count} purchase invoices")
        
        # 3. Delete master data
        items_count = session.query(Item).count()
        session.query(Item).delete()
        console.print(f"[green]✓[/green] Deleted {items_count} items")
        
        customers_count = session.query(Customer).count()
        session.query(Customer).delete()
        console.print(f"[green]✓[/green] Deleted {customers_count} customers")
        
        suppliers_count = session.query(Supplier).count()
        session.query(Supplier).delete()
        console.print(f"[green]✓[/green] Deleted {suppliers_count} suppliers")
        
        # Commit changes
        session.commit()
        console.print("\n[bold green]✅ Database cleaned successfully![/bold green]")
        
        # Show summary
        total = (sales_items_count + purchase_items_count + sales_inv_count + 
                purchase_inv_count + items_count + customers_count + suppliers_count)
        console.print(f"\n[cyan]Total records deleted: {total}[/cyan]")
        
    except Exception as e:
        session.rollback()
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
    finally:
        session.close()

def recreate_database():
    """Drop and recreate entire database"""
    console.print("\n[cyan]Recreating database schema...[/cyan]\n")
    
    try:
        # Delete database file
        db_file = "invoice_data.db"
        if os.path.exists(db_file):
            os.remove(db_file)
            console.print(f"[green]✓[/green] Deleted {db_file}")
        
        # Recreate tables
        engine = get_engine()
        Base.metadata.create_all(engine)
        console.print(f"[green]✓[/green] Created fresh database")
        
        console.print("\n[bold green]✅ Database recreated successfully![/bold green]")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")

def main():
    """Main menu"""
    console.clear()
    console.print("\n[bold cyan]🧹 Database Cleanup Tool[/bold cyan]\n")
    
    show_warning()
    
    console.print("\n[bold]Choose an option:[/bold]\n")
    console.print("1. Clean all data (keep structure)")
    console.print("2. Recreate database (drop & recreate)")
    console.print("0. Cancel\n")
    
    choice = console.input("[cyan]Enter choice: [/cyan]")
    
    if choice == "0":
        console.print("\n[yellow]Cancelled. No changes made.[/yellow]\n")
        return
    
    # Final confirmation
    console.print("\n[bold red]FINAL CONFIRMATION[/bold red]")
    confirm = console.input("Type 'DELETE' to confirm: ")
    
    if confirm != "DELETE":
        console.print("\n[yellow]Cancelled. No changes made.[/yellow]\n")
        return
    
    if choice == "1":
        clean_database()
    elif choice == "2":
        recreate_database()
    else:
        console.print("\n[red]Invalid choice![/red]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Cancelled by user.[/yellow]\n")
