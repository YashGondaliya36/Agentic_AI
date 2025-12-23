"""Email workflow state definition"""

from typing import TypedDict, List, Dict, Optional, Annotated
from operator import add
from datetime import datetime


class EmailData(TypedDict):
    """Structure for a single email"""
    id: str
    thread_id: str
    from_email: str
    from_name: str
    subject: str
    body: str
    date: datetime
    labels: List[str]


class EmailWorkflowState(TypedDict):
    """
    State that flows through the entire email processing workflow.
    
    This is the "brain" that remembers everything about processing an email.
    """
    
    # Input
    email: EmailData  # The email being processed
    
    # Classification
    category: str  # urgent/important/normal/promotional/spam
    priority: int  # 1-5 (5 = highest priority)
    action_required: bool  # Does this need a response?
    
    # Context gathering
    context: Annotated[List[str], add]  # Additional context from search
    past_emails: List[EmailData]  # Related emails from history
    
    # Draft generation
    draft_response: str  # AI-generated response
    draft_approved: bool  # Has human approved?
    draft_edited: str  # Human-edited version (if any)
    
    # Scheduling
    suggested_meeting_time: Optional[str]  # If meeting needed
    calendar_event_created: bool
    
    # Follow-up
    needs_follow_up: bool
    follow_up_date: Optional[datetime]
    follow_up_scheduled: bool
    
    # Metadata
    processing_step: str  # Current step in workflow
    error: Optional[str]  # Any errors encountered
    human_intervention: bool  # Did human intervene?


def create_initial_state(email_data: EmailData) -> EmailWorkflowState:
    """Create initial state for processing an email"""
    return {
        "email": email_data,
        "category": "",
        "priority": 3,
        "action_required": False,
        "context": [],
        "past_emails": [],
        "draft_response": "",
        "draft_approved": False,
        "draft_edited": "",
        "suggested_meeting_time": None,
        "calendar_event_created": False,
        "needs_follow_up": False,
        "follow_up_date": None,
        "follow_up_scheduled": False,
        "processing_step": "classification",
        "error": None,
        "human_intervention": False
    }
