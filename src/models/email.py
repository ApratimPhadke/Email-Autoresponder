"""Email data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class EmailCategory(str, Enum):
    """Email category enumeration."""

    IMPORTANT = "important"
    URGENT = "urgent"
    JOB_RELATED = "job_related"
    PROMOTIONAL = "promotional"
    SOCIAL = "social"
    UPDATES = "updates"
    SPAM = "spam"
    PERSONAL = "personal"
    WORK = "work"
    OTHER = "other"


class EmailPriority(str, Enum):
    """Email priority enumeration."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Email(BaseModel):
    """Email data model."""

    id: str = Field(..., description="Unique email ID")
    message_id: str = Field(..., description="Email message ID")
    thread_id: Optional[str] = Field(None, description="Email thread ID")
    sender: EmailStr = Field(..., description="Sender email address")
    sender_name: Optional[str] = Field(None, description="Sender name")
    recipients: List[EmailStr] = Field(default_factory=list, description="Recipients")
    cc: List[EmailStr] = Field(default_factory=list, description="CC recipients")
    bcc: List[EmailStr] = Field(default_factory=list, description="BCC recipients")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")
    html_body: Optional[str] = Field(None, description="HTML email body")
    date: datetime = Field(..., description="Email date and time")
    labels: List[str] = Field(default_factory=list, description="Email labels")
    attachments: List[str] = Field(default_factory=list, description="Attachment names")
    is_read: bool = Field(default=False, description="Email read status")
    is_starred: bool = Field(default=False, description="Email starred status")


class EmailSummary(BaseModel):
    """Email summary model."""

    email_id: str = Field(..., description="Email ID")
    subject: str = Field(..., description="Email subject")
    sender: EmailStr = Field(..., description="Sender email")
    date: datetime = Field(..., description="Email date")
    summary: str = Field(..., description="AI-generated summary")
    category: EmailCategory = Field(..., description="Email category")
    priority: EmailPriority = Field(..., description="Email priority")
    action_items: List[str] = Field(default_factory=list, description="Action items")
    deadlines: List[str] = Field(default_factory=list, description="Deadlines mentioned")
    key_points: List[str] = Field(default_factory=list, description="Key points")
    requires_response: bool = Field(default=False, description="Requires response")
    sentiment: str = Field(default="neutral", description="Email sentiment")


class DuplicateEmailGroup(BaseModel):
    """Model for grouped duplicate emails."""

    primary_email_id: str = Field(..., description="Primary email ID")
    duplicate_ids: List[str] = Field(default_factory=list, description="Duplicate email IDs")
    similarity_scores: List[float] = Field(
        default_factory=list, description="Similarity scores"
    )
    subject: str = Field(..., description="Email subject")
    count: int = Field(..., description="Number of duplicates")


class AutoResponse(BaseModel):
    """Auto-response configuration model."""

    enabled: bool = Field(default=True, description="Auto-response enabled")
    template: str = Field(..., description="Response template")
    include_resume: bool = Field(default=True, description="Include resume attachment")
    resume_path: Optional[str] = Field(None, description="Resume file path")
    subject_prefix: str = Field(default="Re: ", description="Subject prefix")
