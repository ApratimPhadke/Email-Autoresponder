"""Email parsing and processing utilities."""

import base64
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import parseaddr
from typing import Dict, List, Optional

import html2text
from bs4 import BeautifulSoup


class EmailParser:
    """Email parser for processing Gmail API responses."""

    def __init__(self):
        """Initialize email parser."""
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True

    def parse_gmail_message(self, message: Dict) -> Dict:
        """Parse Gmail API message into structured format.

        Args:
            message: Gmail API message object

        Returns:
            Parsed email dictionary
        """
        headers = self._parse_headers(message.get("payload", {}).get("headers", []))
        body_data = self._extract_body(message.get("payload", {}))

        return {
            "id": message.get("id"),
            "message_id": headers.get("message-id", ""),
            "thread_id": message.get("threadId"),
            "sender": self._parse_email_address(headers.get("from", "")),
            "sender_name": self._parse_sender_name(headers.get("from", "")),
            "recipients": self._parse_email_list(headers.get("to", "")),
            "cc": self._parse_email_list(headers.get("cc", "")),
            "bcc": self._parse_email_list(headers.get("bcc", "")),
            "subject": headers.get("subject", "(No Subject)"),
            "body": body_data["plain"],
            "html_body": body_data["html"],
            "date": self._parse_date(headers.get("date", "")),
            "labels": message.get("labelIds", []),
            "attachments": self._extract_attachments(message.get("payload", {})),
            "is_read": "UNREAD" not in message.get("labelIds", []),
            "is_starred": "STARRED" in message.get("labelIds", []),
        }

    def _parse_headers(self, headers: List[Dict]) -> Dict[str, str]:
        """Parse email headers.

        Args:
            headers: List of header dictionaries

        Returns:
            Dictionary of header name to value
        """
        return {h["name"].lower(): h["value"] for h in headers}

    def _extract_body(self, payload: Dict) -> Dict[str, str]:
        """Extract email body content.

        Args:
            payload: Email payload

        Returns:
            Dictionary with 'plain' and 'html' body content
        """
        plain_body = ""
        html_body = ""

        if "body" in payload and payload["body"].get("data"):
            data = payload["body"]["data"]
            decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            plain_body = decoded

        if "parts" in payload:
            for part in payload["parts"]:
                mime_type = part.get("mimeType", "")
                if mime_type == "text/plain" and part.get("body", {}).get("data"):
                    data = part["body"]["data"]
                    plain_body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                elif mime_type == "text/html" and part.get("body", {}).get("data"):
                    data = part["body"]["data"]
                    html_body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                elif "parts" in part:
                    # Recursive for nested parts
                    nested = self._extract_body(part)
                    if nested["plain"]:
                        plain_body = nested["plain"]
                    if nested["html"]:
                        html_body = nested["html"]

        # Convert HTML to plain text if needed
        if not plain_body and html_body:
            plain_body = self._html_to_text(html_body)

        return {"plain": plain_body, "html": html_body}

    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text.

        Args:
            html: HTML content

        Returns:
            Plain text content
        """
        try:
            return self.html_converter.handle(html)
        except Exception:
            # Fallback to BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text(separator="\n", strip=True)

    def _extract_attachments(self, payload: Dict) -> List[str]:
        """Extract attachment filenames.

        Args:
            payload: Email payload

        Returns:
            List of attachment filenames
        """
        attachments = []

        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("filename"):
                    attachments.append(part["filename"])
                elif "parts" in part:
                    # Recursive for nested parts
                    attachments.extend(self._extract_attachments(part))

        return attachments

    def _parse_email_address(self, email_str: str) -> str:
        """Parse email address from string.

        Args:
            email_str: Email string (may include name)

        Returns:
            Email address only
        """
        _, email = parseaddr(email_str)
        return email.lower() if email else ""

    def _parse_sender_name(self, email_str: str) -> Optional[str]:
        """Parse sender name from email string.

        Args:
            email_str: Email string

        Returns:
            Sender name or None
        """
        name, _ = parseaddr(email_str)
        return name if name else None

    def _parse_email_list(self, email_str: str) -> List[str]:
        """Parse comma-separated email addresses.

        Args:
            email_str: Comma-separated email string

        Returns:
            List of email addresses
        """
        if not email_str:
            return []

        emails = []
        for part in email_str.split(","):
            _, email = parseaddr(part.strip())
            if email:
                emails.append(email.lower())

        return emails

    def _parse_date(self, date_str: str) -> datetime:
        """Parse email date string.

        Args:
            date_str: Date string from email header

        Returns:
            Datetime object
        """
        try:
            from email.utils import parsedate_to_datetime

            return parsedate_to_datetime(date_str)
        except Exception:
            return datetime.now()

    def clean_email_body(self, body: str) -> str:
        """Clean and normalize email body text.

        Args:
            body: Raw email body

        Returns:
            Cleaned email body
        """
        # Remove excessive whitespace
        body = re.sub(r"\n\s*\n\s*\n+", "\n\n", body)

        # Remove email signatures (common patterns)
        body = re.sub(
            r"--+\s*\n.*?(?:\n--+|$)", "", body, flags=re.DOTALL | re.MULTILINE
        )

        # Remove quoted replies (lines starting with >)
        lines = body.split("\n")
        cleaned_lines = [line for line in lines if not line.strip().startswith(">")]
        body = "\n".join(cleaned_lines)

        return body.strip()
