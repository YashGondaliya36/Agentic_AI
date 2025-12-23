"""Email processing workflow using LangGraph"""

from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import EmailWorkflowState
from agents.classifier import classifier_agent
from agents.draft_writer import draft_writer_agent


def create_email_workflow():
    """
    Create the LangGraph workflow for email processing.
    
    Workflow:
    1. Classify email (category, priority)
    2. Decide: Need response?
       - No → Archive/mark as read
       - Yes → Continue
    3. Generate draft response
    4. Human review (INTERRUPT - wait for approval)
    5. Send email
    6. Mark original as read
    """
    
    # Create graph with checkpointing (for human-in-loop)
    workflow = StateGraph(EmailWorkflowState)
    
    # ========= NODES =========
    
    def classify_node(state: EmailWorkflowState) -> EmailWorkflowState:
        """Classify the email"""
        return classifier_agent.classify(state)
    
    def draft_node(state: EmailWorkflowState) -> EmailWorkflowState:
        """Generate draft response"""
        return draft_writer_agent.write_draft(state)
    
    def archive_node(state: EmailWorkflowState) -> EmailWorkflowState:
        """Archive email (no response needed)"""
        print(f"\n📥 Archiving email (no response needed)")
        state["processing_step"] = "complete"
        # In production: mark as read via Gmail API
        return state
    
    def send_node(state: EmailWorkflowState) -> EmailWorkflowState:  
        """Send the approved draft"""
        from integrations.gmail_client import gmail_client
        
        print(f"\n📤 Sending email...")
        
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
            state["processing_step"] = "complete"
            print("   ✅ Email sent and original marked as read")
        else:
            state["error"] = "Failed to send email"
            print("   ❌ Failed to send email")
        
        return state
    
    # Add nodes to graph
    workflow.add_node("classify", classify_node)
    workflow.add_node("draft", draft_node)
    workflow.add_node("archive", archive_node)
    workflow.add_node("send", send_node)
    
    # ========= EDGES =========
    
    # Start with classification
    workflow.set_entry_point("classify")
    
    # After classification, decide next step
    def decide_after_classification(state: EmailWorkflowState) -> Literal["draft", "archive"]:
        """
        Decision: Does this email need a response?
        """
        action_required = state.get("action_required", False)
        category = state.get("category", "normal")
        
        # Don't respond to spam or low-priority promotional
        if category in ["spam", "promotional"]:
            return "archive"
        
        if action_required:
            print("\n🔄 Decision: Response needed → Generating draft")
            return "draft"
        else:
            print("\n🔄 Decision: No response needed → Archiving")
            return "archive"
    
    workflow.add_conditional_edges(
        "classify",
        decide_after_classification,
        {
            "draft": "draft",
            "archive": "archive"
        }
    )
    
    # After draft, wait for human approval (THIS IS THE HUMAN-IN-LOOP!)
    # We'll handle this in the main.py with interrupts
    workflow.add_edge("draft", "send")
    
    # Archive and Send both end the workflow
    workflow.add_edge("archive", END)
    workflow.add_edge("send", END)
    
    # Compile with memory saver (enables interrupts)
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


def visualize_workflow():
    """Print ASCII visualization of the workflow"""
    print("\n" + "="*70)
    print("📊 EMAIL PROCESSING WORKFLOW")
    print("="*70)
    print("""
        START
          ↓
    ┌────────────┐
    │  CLASSIFY  │
    │(Category,  │
    │ Priority)  │
    └────────────┘
          ↓
    [DECISION]
      ↙      ↘
   Need      No
  Reply?   Reply
    │        │
    ↓        ↓
┌─────────┐  ┌────────┐
│  DRAFT  │  │ARCHIVE │
│(Generate│  └────────┘
│Response)│       ↓
└─────────┘      END
    ↓
 ⏸️  PAUSE
[Human Review]
(Approve/Edit)
    ↓
┌─────────┐
│  SEND   │
│(+ Mark  │
│ as Read)│
└─────────┘
    ↓
   END

KEY FEATURES:
✅ Auto-classification
✅ Conditional routing
✅ Human-in-the-loop (review before sending)
✅ Gmail integration
✅ State persistence
    """)
    print("="*70 + "\n")
