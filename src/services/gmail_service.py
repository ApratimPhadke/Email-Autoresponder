"""Gmail API service for email operations."""

import base64
import pickle
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import Settings
from src.models import Email
from src.utils import EmailParser, get_logger

logger = get_logger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


class GmailService:
    """Gmail API service for email operations."""

    def __init__(self, settings: Settings):
        """Initialize Gmail service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.service = None
        self.parser = EmailParser()
        self._initialize_service()

    def _initialize_service(self) -> None:
        """Initialize Gmail API service."""
        creds = None
        token_path = Path("data/token.pickle")

        # Load existing credentials
        if token_path.exists():
            with open(token_path, "rb") as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Create credentials from settings
                creds = self._get_credentials_from_settings()

            # Save credentials
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)

        self.service = build("gmail", "v1", credentials=creds)
        logger.info("Gmail service initialized successfully")

    def _get_credentials_from_settings(self) -> Credentials:
        """Get credentials from settings.

        Returns:
            Gmail API credentials
        """
        if self.settings.gmail_refresh_token:
            # Use existing refresh token
            creds = Credentials(
                token=None,
                refresh_token=self.settings.gmail_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.settings.gmail_client_id,
                client_secret=self.settings.gmail_client_secret,
                scopes=SCOPES,
            )
            creds.refresh(Request())
            return creds
        else:
            # OAuth flow for first-time setup
            credentials_info = {
                "installed": {
                    "client_id": self.settings.gmail_client_id,
                    "client_secret": self.settings.gmail_client_secret,
                    "redirect_uris": ["http://localhost"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            }

            flow = InstalledAppFlow.from_client_config(credentials_info, SCOPES)
            creds = flow.run_local_server(port=0)
            return creds

    def fetch_emails(
        self, max_results: int = 50, query: str = "is:unread"
    ) -> List[Email]:
        """Fetch emails from Gmail.

        Args:
            max_results: Maximum number of emails to fetch
            query: Gmail search query

        Returns:
            List of Email objects
        """
        try:
            logger.info(f"Fetching emails with query: {query}", max_results=max_results)

            results = (
                self.service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])
            emails = []

            for message in messages:
                msg = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=message["id"], format="full")
                    .execute()
                )

                parsed_email = self.parser.parse_gmail_message(msg)
                emails.append(Email(**parsed_email))

            logger.info(f"Fetched {len(emails)} emails successfully")
            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {e}", exc_info=True)
            return []

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        attachment_path: Optional[Path] = None,
        html: bool = False,
    ) -> bool:
        """Send an email via Gmail.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            attachment_path: Optional path to attachment
            html: Whether body is HTML

        Returns:
            True if sent successfully
        """
        try:
            message = MIMEMultipart()
            message["To"] = to
            message["Subject"] = subject

            # Add body
            if html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))

            # Add attachment if provided
            if attachment_path and attachment_path.exists():
                with open(attachment_path, "rb") as f:
                    attachment = MIMEApplication(f.read(), Name=attachment_path.name)
                    attachment["Content-Disposition"] = (
                        f'attachment; filename="{attachment_path.name}"'
                    )
                    message.attach(attachment)

            # Send message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            send_message = {"raw": raw_message}

            self.service.users().messages().send(userId="me", body=send_message).execute()

            logger.info(f"Email sent successfully to {to}", subject=subject)
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            return False

    def mark_as_read(self, email_id: str) -> bool:
        """Mark email as read.

        Args:
            email_id: Email ID

        Returns:
            True if successful
        """
        try:
            self.service.users().messages().modify(
                userId="me", id=email_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
            return False

    def add_label(self, email_id: str, label_id: str) -> bool:
        """Add label to email.

        Args:
            email_id: Email ID
            label_id: Label ID

        Returns:
            True if successful
        """
        try:
            self.service.users().messages().modify(
                userId="me", id=email_id, body={"addLabelIds": [label_id]}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error adding label: {e}")
            return False
