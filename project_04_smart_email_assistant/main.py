"""Smart Email Assistant - Main Entry Point"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

from graph.state import create_initial_state
from graph.workflow import create_email_workflow, visualize_workflow
from integrations.gmail_client import gmail_client

# Load .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Rich console for pretty output
console = Console()


def print_banner():
    """Print startup banner"""
    banner = """
# 📧 Smart Email Assistant

**Powered by LangGraph + Google Gemini**

Automatically:
- 📊 Classifies your emails
- ✍️  Generates professional responses
- 👤 Asks for your approval
- 📤 Sends emails
- ✅ Marks as read

**Human stays in control!**
"""
    console.print(Panel(Markdown(banner), border_style="cyan"))


def display_email(email_data):
    """Display email in a nice format"""
    email_text = f"""
**From:** {email_data['from_name']} <{email_data['from_email']}>
**Subject:** {email_data['subject']}

**Body:**
{email_data['body'][:500]}{'...' if len(email_data['body']) > 500 else ''}
"""
    console.print(Panel(Markdown(email_text), title="📨 Email", border_style="blue"))


def review_draft(state):
    """
    Human-in-the-loop: Review and approve/edit draft.
    
    Returns:
        tuple: (approved: bool, edited_draft: str or None)
    """
    draft = state["draft_response"]
    
    console.print("\n" + "="*70)
    console.print("[bold yellow]📝 DRAFT RESPONSE (Please Review)[/bold yellow]")
    console.print("="*70)
    console.print(draft)
    console.print("="*70 + "\n")
    
    # Ask for approval
    choice = Prompt.ask(
        "[bold cyan]What would you like to do?[/bold cyan]",
        choices=["approve", "edit", "skip"],
        default="approve"
    )
    
    if choice == "approve":
        console.print("[green]✅ Draft approved![/green]")
        return True, None
    
    elif choice == "edit":
        console.print("\n[yellow]📝 Edit the draft (type your changes, press Enter twice when done):[/yellow]")
        console.print("[dim]Current draft shown above. Type your complete edited version:[/dim]\n")
        
        lines = []
        while True:
            try:
                line = input()
                if line == "":
                    if len(lines) > 0 and lines[-1] == "":
                        break
                lines.append(line)
            except EOFError:
                break
        
        edited = "\n".join(lines[:-1])  # Remove last empty line
        
        if edited.strip():
            console.print("[green]✅ Draft updated![/green]")
            return True, edited
        else:
            console.print("[yellow]⚠️  No changes made, using original[/yellow]")
            return True, None
    
    else:  # skip
        console.print("[red]❌ Email skipped (will not be sent)[/red]")
        return False, None


def process_email(email_data, app):
    """
    Process a single email through the workflow.
    """
    console.print(f"\n[bold]{'='*70}[/bold]")
    console.print(f"[bold cyan]Processing Email {email_data['id'][:10]}...[/bold cyan]")
    console.print(f"[bold]{'='*70}[/bold]\n")
    
    # Display the email
    display_email(email_data)
    
    # Create initial state
    initial_state = create_initial_state(email_data)
    
    # Config for workflow
    config = {"configurable": {"thread_id": email_data['id']}}
    
    # Step 1: Classify
    console.print("\n[bold]Step 1: Classifying email...[/bold]")
    
    # Run ONLY the classification step
    from agents.classifier import classifier_agent
    state = classifier_agent.classify(initial_state)
    
    # Check if we should respond
    if not state.get("action_required", False) or state.get("category") in ["spam", "promotional"]:
        console.print("\n[yellow]📥 No response needed - Archiving email[/yellow]")
        
        # Mark as read
        from integrations.gmail_client import gmail_client
        gmail_client.mark_as_read(email_data['id'])
        console.print("[dim]✅ Marked as read[/dim]")
        return
    
    # Step 2: Generate draft
    console.print("\n[bold]Step 2: Generating draft response...[/bold]")
    
    from agents.draft_writer import draft_writer_agent
    state = draft_writer_agent.write_draft(state)
    
    # Step 3: HUMAN REVIEW (CRITICAL - MUST HAPPEN!)
    console.print("\n[bold]Step 3: 👤 Human Review (Your Approval Required)[/bold]")
    
    approved, edited_draft = review_draft(state)
    
    if not approved:
        console.print("\n[red]❌ Email NOT sent (you chose to skip)[/red]")
        return
    
    # Update state with human decision
    if edited_draft:
        state["draft_edited"] = edited_draft
        state["human_intervention"] = True
    
    state["draft_approved"] = True
    
    # Step 4: Send ONLY if approved
    console.print("\n[bold]Step 4: Sending approved email...[/bold]")
    
    from integrations.gmail_client import gmail_client
    
    # Use edited draft if available, otherwise original
    final_draft = state.get("draft_edited", "") or state["draft_response"]
    
    # Get recipient
    recipient = state["email"]["from_email"]
    subject = f"Re: {state['email']['subject']}"
    
    # Send email
    success = gmail_client.send_email(
        to=recipient,
        subject=subject,
        body=final_draft
    )
    
    if success:
        # Mark original as read
        gmail_client.mark_as_read(state["email"]["id"])
        console.print("\n[green]✅ Email sent successfully and original marked as read![/green]")
    else:
        console.print("\n[red]❌ Failed to send email[/red]")


def main():
    """Main function"""
    
    print_banner()
    visualize_workflow()
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        console.print("[red]❌ Error: GOOGLE_API_KEY not found in .env[/red]")
        return
    
    console.print("\n[bold cyan]Connecting to Gmail...[/bold cyan]")
    
    try:
        # Create workflow
        app = create_email_workflow()
        
        # Fetch recent emails
        console.print("\n[bold]Fetching unread emails from inbox...[/bold]")
        emails = gmail_client.get_recent_emails(max_results=5)
        
        if not emails:
            console.print("\n[green]🎉 Inbox Zero! No unread emails.[/green]")
            return
        
        console.print(f"\n[bold]Found {len(emails)} unread email(s)[/bold]\n")
        
        # Process each email
        for idx, email in enumerate(emails, 1):
            console.print(f"\n[bold magenta]Email {idx}/{len(emails)}[/bold magenta]")
            
            process_email(email, app)
            
            # Ask if user wants to continue
            if idx < len(emails):
                if not Confirm.ask("\n[cyan]Process next email?[/cyan]", default=True):
                    console.print("[yellow]Stopping email processing[/yellow]")
                    break
        
        console.print("\n[bold green]✅ All emails processed![/bold green]")
        
    except FileNotFoundError as e:
        console.print(f"\n[red]❌ {e}[/red]")
        console.print("[yellow]Please set up Gmail API credentials first.[/yellow]")
        console.print("[dim]See project_02_voice_assistant for setup guide.[/dim]")
    
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
