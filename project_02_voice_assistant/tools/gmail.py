"""Gmail tool wrapper"""

import os
import base64
from email.mime.text import MIMEText
from typing import Optional
from dotenv import load_dotenv

# Google Gmail imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# Scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class GmailTool:
    """
    Wrapper for Gmail API
    Handles OAuth authentication and email sending
    """
    
    def __init__(self):
        """Initialize Gmail tool"""
        
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
        
        # Build Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail authenticated!")
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None
    ) -> dict:
        """
        Send an email via Gmail
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email (optional, uses authenticated account)
            
        Returns:
            Dict with success status and message details
        """
        try:
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if from_email:
                message['from'] = from_email
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send email (synchronous)
            import asyncio
            send_result = await asyncio.to_thread(
                self.service.users().messages().send(
                    userId='me',
                    body={'raw': raw_message}
                ).execute
            )
            
            return {
                "success": True,
                "message_id": send_result.get('id'),
                "to": to,
                "subject": subject,
                "body_length": len(body)
            }
            
        except HttpError as error:
            import traceback
            print(f"\n⚠️  Gmail error:")
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(error)
            }
        except Exception as e:
            import traceback
            print(f"\n⚠️  Gmail error:")
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_draft(
        self,
        to: str,
        subject: str,
        body: str
    ) -> dict:
        """
        Create an email draft (doesn't send)
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            
        Returns:
            Dict with success status and draft details
        """
        try:
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Create draft (synchronous)
            import asyncio
            draft_result = await asyncio.to_thread(
                self.service.users().drafts().create(
                    userId='me',
                    body={'message': {'raw': raw_message}}
                ).execute
            )
            
            return {
                "success": True,
                "draft_id": draft_result.get('id'),
                "to": to,
                "subject": subject
            }
            
        except Exception as e:
            import traceback
            print(f"\n⚠️  Gmail draft error:")
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e)
            }
