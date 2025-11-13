"""Slack notification service for sending email summaries."""

from datetime import datetime
from typing import List

import requests

from config import Settings
from src.models import EmailSummary
from src.utils import get_logger

logger = get_logger(__name__)


class SlackService:
    """Slack service for sending notifications."""

    def __init__(self, settings: Settings):
        """Initialize Slack service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.webhook_url = settings.slack_webhook_url

    def send_email_summaries(self, summaries: List[EmailSummary]) -> bool:
        """Send email summaries to Slack.

        Args:
            summaries: List of email summaries

        Returns:
            True if sent successfully
        """
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False

        try:
            # Build message blocks
            blocks = self._build_summary_blocks(summaries)

            payload = {"blocks": blocks}

            response = requests.post(self.webhook_url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info(f"Sent {len(summaries)} email summaries to Slack")
                return True
            else:
                logger.error(f"Slack API error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending to Slack: {e}", exc_info=True)
            return False

    def _build_summary_blocks(self, summaries: List[EmailSummary]) -> List[dict]:
        """Build Slack message blocks from summaries.

        Args:
            summaries: Email summaries

        Returns:
            List of Slack message blocks
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📧 Email Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Total Emails:* {len(summaries)}",
                },
            },
            {"type": "divider"},
        ]

        # Group by priority
        high_priority = [s for s in summaries if s.priority.value == "high"]
        medium_priority = [s for s in summaries if s.priority.value == "medium"]
        low_priority = [s for s in summaries if s.priority.value == "low"]

        if high_priority:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🔴 High Priority ({len(high_priority)})*",
                    },
                }
            )
            for summary in high_priority[:5]:  # Limit to 5
                blocks.extend(self._create_email_block(summary))

        if medium_priority:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🟡 Medium Priority ({len(medium_priority)})*",
                    },
                }
            )
            for summary in medium_priority[:5]:
                blocks.extend(self._create_email_block(summary))

        if low_priority:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🟢 Low Priority ({len(low_priority)})*",
                    },
                }
            )

        # Add statistics
        job_related = len([s for s in summaries if s.category.value == "job_related"])
        requires_response = len([s for s in summaries if s.requires_response])

        blocks.extend(
            [
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Statistics:*\n"
                        f"• Job-related: {job_related}\n"
                        f"• Requires response: {requires_response}",
                    },
                },
            ]
        )

        return blocks

    def _create_email_block(self, summary: EmailSummary) -> List[dict]:
        """Create Slack blocks for a single email summary.

        Args:
            summary: Email summary

        Returns:
            List of Slack blocks
        """
        emoji_map = {
            "important": "⭐",
            "urgent": "🚨",
            "job_related": "💼",
            "promotional": "📢",
            "work": "💻",
        }

        emoji = emoji_map.get(summary.category.value, "📧")

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *{summary.subject}*\n"
                    f"From: {summary.sender}\n"
                    f"_{summary.summary}_",
                },
            }
        ]

        if summary.action_items:
            action_text = "\n".join([f"• {item}" for item in summary.action_items[:3]])
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Action Items:*\n{action_text}"},
                }
            )

        return blocks

    def send_notification(self, message: str, title: str = "Email Agent") -> bool:
        """Send a simple notification to Slack.

        Args:
            message: Notification message
            title: Notification title

        Returns:
            True if sent successfully
        """
        if not self.webhook_url:
            return False

        try:
            payload = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": title},
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": message},
                    },
                ]
            }

            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
