"""Google Calendar tool wrapper"""

import os
import datetime
from typing import Optional
from dotenv import load_dotenv

# Google Calendar imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# Scopes for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarTool:
    """
    Wrapper for Google Calendar API
    Handles OAuth authentication and event creation
    """
    
    def __init__(self):
        """Initialize Google Calendar tool"""
        
        self.credentials_file = 'credentials.json'
        self.token_file = 'token.json'
        self.service = None
        
        # Authenticate
        self._authenticate()
    
    def _authenticate(self):
        """Handle OAuth authentication"""
        creds = None
        
        # Check if token file exists
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired token
                creds.refresh(Request())
            else:
                # New authentication flow
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"{self.credentials_file} not found!\n"
                        "Please follow GOOGLE_CALENDAR_SETUP.md to get credentials."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        # Build Calendar service
        self.service = build('calendar', 'v3', credentials=creds)
        print("✅ Google Calendar authenticated!")
    
    async def create_event(
        self,
        title: str,
        start_time: str,
        duration_hours: int = 1,
        description: Optional[str] = None
    ) -> dict:
        """
        Create a calendar event
        
        Args:
            title: Event title
            start_time: Start time (e.g., "tomorrow 3pm", "2024-12-25 10:00")
            duration_hours: Event duration in hours
            description: Optional event description
           
        Returns:
            Dict with success status and event details
        """
        try:
            # Parse start time
            start_dt = self._parse_time(start_time)
            
            # Calculate end time
            end_dt = start_dt + datetime.timedelta(hours=duration_hours)
            
            # Create event object
            event = {
                'summary': title,
                'description': description or f"Event created by Voice Assistant",
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'Asia/Kolkata',  # Change to your timezone
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
            }
            
            # Execute API call (synchronous)
            import asyncio
            event_result = await asyncio.to_thread(
                self.service.events().insert(calendarId='primary', body=event).execute
            )
            
            return {
                "success": True,
                "event_id": event_result.get('id'),
                "title": title,
                "start": start_dt.strftime("%B %d, %Y at %I:%M %p"),
                "end": end_dt.strftime("%I:%M %p"),
                "link": event_result.get('htmlLink')
            }
            
        except Exception as e:
            import traceback
            print(f"\n⚠️  Calendar error:")
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_time(self, time_str: str) -> datetime.datetime:
        """
        Parse human-readable time string to datetime
        
        Args:
            time_str: e.g., "tomorrow 3pm", "next monday 10am", "2024-12-25 14:00"
            
        Returns:
            datetime object
        """
        import re
        from datetime import datetime, timedelta
        
        now = datetime.now()
        time_str = time_str.lower().strip()
        
        # Pattern: "tomorrow 3pm"
        if 'tomorrow' in time_str:
            base_date = now + timedelta(days=1)
            hour = self._extract_hour(time_str)
            return base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # Pattern: "today 3pm"
        if 'today' in time_str:
            hour = self._extract_hour(time_str)
            return now.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # Pattern: "3pm" (assume today)
        if 'pm' in time_str or 'am' in time_str:
            hour = self._extract_hour(time_str)
            return now.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # Pattern: "2024-12-25 14:00" or "2024-12-25T14:00"
        try:
            # Try ISO format
            if 'T' in time_str:
                return datetime.fromisoformat(time_str)
            # Try space-separated
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        except:
            pass
        
        # Default: 1 hour from now
        print(f"⚠️  Could not parse '{time_str}', using 1 hour from now")
        return now + timedelta(hours=1)
    
    def _extract_hour(self, time_str: str) -> int:
        """Extract hour from time string like '3pm', '10am'"""
        import re
        
        # Find number before pm/am
        match = re.search(r'(\d+)\s*(am|pm)', time_str)
        if match:
            hour = int(match.group(1))
            meridiem = match.group(2)
            
            # Convert to 24-hour format
            if meridiem == 'pm' and hour != 12:
                hour += 12
            elif meridiem == 'am' and hour == 12:
                hour = 0
            
            return hour
        
        # Default to noon
        return 12
