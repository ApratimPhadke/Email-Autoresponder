"""Data models module."""

from .email import (
    AutoResponse,
    DuplicateEmailGroup,
    Email,
    EmailCategory,
    EmailPriority,
    EmailSummary,
)

__all__ = [
    "Email",
    "EmailSummary",
    "EmailCategory",
    "EmailPriority",
    "DuplicateEmailGroup",
    "AutoResponse",
]
