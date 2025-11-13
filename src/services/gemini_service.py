"""Gemini AI service for email processing and classification."""

import json
from typing import List

import google.generativeai as genai

from config import Settings
from src.models import Email, EmailCategory, EmailPriority, EmailSummary
from src.utils import get_logger

logger = get_logger(__name__)


class GeminiService:
    """Gemini AI service for email intelligence."""

    def __init__(self, settings: Settings):
        """Initialize Gemini service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        genai.configure(api_key=settings.google_api_key)

        # Initialize model
        self.model = genai.GenerativeModel("gemini-1.5-flash")

        logger.info("Gemini service initialized successfully")

    def summarize_email(self, email: Email) -> EmailSummary:
        """Generate comprehensive summary of an email.

        Args:
            email: Email to summarize

        Returns:
            EmailSummary object
        """
        try:
            prompt = f"""Analyze the following email and provide a structured summary in JSON format.

Email Subject: {email.subject}
From: {email.sender}
Date: {email.date}
Body:
{email.body[:2000]}

Provide a JSON response with the following structure:
{{
    "summary": "A concise 2-3 sentence summary of the email",
    "category": "One of: important, urgent, job_related, promotional, social, updates, spam, personal, work, other",
    "priority": "One of: high, medium, low",
    "action_items": ["List of action items mentioned"],
    "deadlines": ["List of deadlines or time-sensitive information"],
    "key_points": ["3-5 key points from the email"],
    "requires_response": true/false,
    "sentiment": "positive, neutral, or negative"
}}

Respond ONLY with valid JSON, no other text."""

            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
                result_text = result_text.strip()

            result = json.loads(result_text)

            return EmailSummary(
                email_id=email.id,
                subject=email.subject,
                sender=email.sender,
                date=email.date,
                summary=result.get("summary", ""),
                category=EmailCategory(result.get("category", "other")),
                priority=EmailPriority(result.get("priority", "medium")),
                action_items=result.get("action_items", []),
                deadlines=result.get("deadlines", []),
                key_points=result.get("key_points", []),
                requires_response=result.get("requires_response", False),
                sentiment=result.get("sentiment", "neutral"),
            )

        except Exception as e:
            logger.error(f"Error summarizing email: {e}", exc_info=True)
            # Return default summary on error
            return EmailSummary(
                email_id=email.id,
                subject=email.subject,
                sender=email.sender,
                date=email.date,
                summary="Unable to generate summary",
                category=EmailCategory.OTHER,
                priority=EmailPriority.MEDIUM,
            )

    def classify_email(self, email: Email) -> EmailCategory:
        """Classify email into a category.

        Args:
            email: Email to classify

        Returns:
            EmailCategory
        """
        try:
            prompt = f"""Classify the following email into ONE category.

Subject: {email.subject}
From: {email.sender}
Body: {email.body[:1000]}

Categories:
- important: Critical business or personal matters
- urgent: Time-sensitive matters requiring immediate attention
- job_related: Job opportunities, applications, interviews
- promotional: Marketing, advertisements, offers
- social: Social media notifications
- updates: Product updates, newsletters
- spam: Unwanted or suspicious emails
- personal: Personal communications
- work: Work-related communications
- other: Everything else

Respond with ONLY the category name, nothing else."""

            response = self.model.generate_content(prompt)
            category_str = response.text.strip().lower()

            try:
                return EmailCategory(category_str)
            except ValueError:
                return EmailCategory.OTHER

        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            return EmailCategory.OTHER

    def is_job_related(self, email: Email, job_keywords: List[str]) -> bool:
        """Determine if email is job-related using AI.

        Args:
            email: Email to check
            job_keywords: List of job-related keywords

        Returns:
            True if job-related
        """
        try:
            # Quick keyword check first
            text = f"{email.subject} {email.body}".lower()
            if any(keyword in text for keyword in job_keywords):
                # Use AI for confirmation
                prompt = f"""Is the following email related to a job opportunity, application, or interview?

Subject: {email.subject}
From: {email.sender}
Body: {email.body[:1000]}

Respond with ONLY "yes" or "no"."""

                response = self.model.generate_content(prompt)
                answer = response.text.strip().lower()

                return "yes" in answer

            return False

        except Exception as e:
            logger.error(f"Error checking if job-related: {e}")
            return False

    def generate_auto_response(self, email: Email, include_resume: bool = True) -> str:
        """Generate an auto-response for job-related emails.

        Args:
            email: Original email
            include_resume: Whether resume will be attached

        Returns:
            Response email body
        """
        try:
            prompt = f"""Generate a professional auto-response to the following job-related email.

Original Email Subject: {email.subject}
From: {email.sender}

The response should:
1. Be professional and courteous
2. Express interest in the opportunity
3. Mention that a resume is attached (if {include_resume})
4. Indicate availability for further discussion
5. Be concise (3-4 paragraphs)

Generate ONLY the email body, no subject line."""

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating auto-response: {e}")
            return """Thank you for your email regarding the opportunity.

I am very interested in learning more about this position. I have attached my resume for your review.

I would be happy to discuss this further at your convenience. Please feel free to contact me.

Best regards"""

    def batch_summarize(self, emails: List[Email]) -> List[EmailSummary]:
        """Summarize multiple emails efficiently.

        Args:
            emails: List of emails to summarize

        Returns:
            List of EmailSummary objects
        """
        summaries = []
        for email in emails:
            summary = self.summarize_email(email)
            summaries.append(summary)

        return summaries
