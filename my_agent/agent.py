# from google.adk.agents.llm_agent import Agent
#
# root_agent = Agent(
#     model='gemini-2.5-flash',
#     name='root_agent',
#     description='A helpful assistant for user questions.',
#     instruction='Answer user questions to the best of your knowledge',
# )
"""Main email agent implementation using Google ADK framework."""

import asyncio
from pathlib import Path
from typing import List

from config import Settings, get_settings
from src.models import Email, EmailSummary
from src.services import GeminiService, GmailService, RAGService, SlackService
from src.utils import get_logger

logger = get_logger(__name__)


class EmailAgent:
    """Main email agent orchestrator."""

    def __init__(self, settings: Settings | None = None):
        """Initialize email agent.

        Args:
            settings: Application settings (optional)
        """
        self.settings = settings or get_settings()

        # Initialize services
        logger.info("Initializing Email Agent services...")
        self.gmail_service = GmailService(self.settings)
        self.gemini_service = GeminiService(self.settings)
        self.rag_service = RAGService(self.settings)
        self.slack_service = SlackService(self.settings)

        logger.info("Email Agent initialized successfully")

    async def process_emails(self) -> dict:
        """Process new emails with all features.

        Returns:
            Processing statistics
        """
        logger.info("Starting email processing cycle")

        try:
            # Fetch unread emails
            emails = self.gmail_service.fetch_emails(
                max_results=self.settings.max_emails_per_check, query="is:unread"
            )

            if not emails:
                logger.info("No new emails to process")
                return {"status": "success", "emails_processed": 0}

            logger.info(f"Processing {len(emails)} emails")

            # Process emails concurrently
            summaries = []
            duplicates_found = []
            job_responses_sent = 0

            for email in emails:
                # Add to RAG for duplicate detection
                self.rag_service.add_email(email)

                # Check for duplicates
                similar = self.rag_service.find_similar_emails(
                    email, threshold=self.settings.duplicate_similarity_threshold
                )

                if similar:
                    duplicates_found.append((email.id, len(similar)))
                    logger.info(f"Found {len(similar)} similar emails for: {email.subject}")

                # Summarize email
                summary = self.gemini_service.summarize_email(email)
                summaries.append(summary)

                # Auto-respond to job emails
                if self.settings.auto_response_enabled:
                    if self.gemini_service.is_job_related(
                        email, self.settings.job_keywords_list
                    ):
                        logger.info(f"Job-related email detected: {email.subject}")
                        await self._handle_job_email(email)
                        job_responses_sent += 1

                # Mark as read
                self.gmail_service.mark_as_read(email.id)

            # Send summaries to Slack
            if summaries:
                self.slack_service.send_email_summaries(summaries)

            stats = {
                "status": "success",
                "emails_processed": len(emails),
                "duplicates_found": len(duplicates_found),
                "job_responses_sent": job_responses_sent,
                "high_priority": len([s for s in summaries if s.priority.value == "high"]),
                "summaries": [s.dict() for s in summaries],
            }

            logger.info("Email processing completed", **stats)
            return stats

        except Exception as e:
            logger.error(f"Error in email processing: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def _handle_job_email(self, email: Email) -> None:
        """Handle job-related email with auto-response.

        Args:
            email: Job-related email
        """
        try:
            # Generate response
            response_body = self.gemini_service.generate_auto_response(
                email, include_resume=True
            )

            # Get resume path
            resume_path = Path(self.settings.default_resume_path)

            if not resume_path.exists():
                logger.warning(f"Resume not found at {resume_path}")
                resume_path = None

            # Send response
            subject = f"Re: {email.subject}"
            success = self.gmail_service.send_email(
                to=email.sender,
                subject=subject,
                body=response_body,
                attachment_path=resume_path,
            )

            if success:
                logger.info(f"Auto-response sent to {email.sender}")
            else:
                logger.error(f"Failed to send auto-response to {email.sender}")

        except Exception as e:
            logger.error(f"Error handling job email: {e}", exc_info=True)

    def check_duplicates(self, emails: List[Email]) -> dict:
        """Check for duplicate emails in a batch.

        Args:
            emails: List of emails to check

        Returns:
            Duplicate detection results
        """
        try:
            groups = self.rag_service.detect_duplicates(
                emails, threshold=self.settings.duplicate_similarity_threshold
            )

            return {
                "status": "success",
                "total_emails": len(emails),
                "duplicate_groups": len(groups),
                "groups": [g.dict() for g in groups],
            }

        except Exception as e:
            logger.error(f"Error checking duplicates: {e}")
            return {"status": "error", "message": str(e)}

    def summarize_emails(self, emails: List[Email]) -> List[EmailSummary]:
        """Summarize a list of emails.

        Args:
            emails: List of emails to summarize

        Returns:
            List of email summaries
        """
        return self.gemini_service.batch_summarize(emails)

    def get_statistics(self) -> dict:
        """Get agent statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "vector_store_size": self.rag_service.get_email_count(),
            "settings": {
                "auto_response_enabled": self.settings.auto_response_enabled,
                "duplicate_threshold": self.settings.duplicate_similarity_threshold,
                "check_interval": self.settings.email_check_interval,
            },
        }
