"""Tests for Email Agent."""

import pytest
from unittest.mock import Mock, patch

from src.agents import EmailAgent
from src.models import Email, EmailCategory, EmailPriority


@pytest.fixture
def sample_email():
    """Create a sample email for testing."""
    return Email(
        id="test123",
        message_id="msg123",
        sender="test@example.com",
        subject="Test Email",
        body="This is a test email body.",
        date="2024-01-01T12:00:00Z",
    )


def test_email_agent_initialization():
    """Test email agent can be initialized."""
    # This is a placeholder test
    # In real usage, you would need proper API keys
    pass


def test_email_model():
    """Test email data model."""
    email = Email(
        id="test123",
        message_id="msg123",
        sender="test@example.com",
        subject="Test Subject",
        body="Test body",
        date="2024-01-01T12:00:00Z",
    )
    
    assert email.id == "test123"
    assert email.sender == "test@example.com"
    assert email.subject == "Test Subject"


# Add more tests as needed
# Note: Most tests would require mocking external services
# (Gmail API, Gemini API, etc.) for proper unit testing
