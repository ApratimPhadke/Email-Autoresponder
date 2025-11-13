"""MCP server for SMTP email operations."""

import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List

from config import Settings, get_settings
from src.utils import get_logger

logger = get_logger(__name__)


class MCPSMTPServer:
    """MCP server for SMTP operations."""

    def __init__(self, settings: Settings):
        """Initialize MCP SMTP server.

        Args:
            settings: Application settings
        """
        self.settings = settings

    async def send_email(self, to: str, subject: str, body: str, html: bool = False) -> Dict:
        """Send email via SMTP.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            html: Whether body is HTML

        Returns:
            Result dictionary
        """
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.settings.smtp_username
            message["To"] = to
            message["Subject"] = subject

            if html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port) as server:
                server.starttls()
                server.login(self.settings.smtp_username, self.settings.smtp_password)
                server.send_message(message)

            logger.info(f"Email sent successfully via MCP to {to}")
            return {"status": "success", "recipient": to}

        except Exception as e:
            logger.error(f"Error sending email via MCP: {e}")
            return {"status": "error", "message": str(e)}

    async def check_connection(self) -> Dict:
        """Check SMTP connection.

        Returns:
            Connection status
        """
        try:
            with smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port) as server:
                server.starttls()
                server.login(self.settings.smtp_username, self.settings.smtp_password)

            return {"status": "connected", "server": self.settings.smtp_server}

        except Exception as e:
            logger.error(f"SMTP connection error: {e}")
            return {"status": "disconnected", "error": str(e)}
