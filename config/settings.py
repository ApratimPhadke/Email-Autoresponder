"""Application settings and configuration management."""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Google Gemini API
    google_api_key: str = Field(..., description="Google Gemini API key")

    # Gmail API
    gmail_client_id: str = Field(..., description="Gmail OAuth client ID")
    gmail_client_secret: str = Field(..., description="Gmail OAuth client secret")
    gmail_refresh_token: str = Field(default="", description="Gmail refresh token")

    # SMTP Configuration
    smtp_server: str = Field(default="smtp.gmail.com", description="SMTP server address")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_username: str = Field(..., description="SMTP username (email)")
    smtp_password: str = Field(..., description="SMTP password (app-specific)")

    # Slack Integration
    slack_webhook_url: str = Field(default="", description="Slack webhook URL for notifications")

    # Application Configuration
    app_host: str = Field(default="0.0.0.0", description="Application host")
    app_port: int = Field(default=8080, description="Application port")
    debug: bool = Field(default=False, description="Debug mode")

    # Vector Database Configuration
    chroma_persist_directory: str = Field(
        default="./data/chroma_db", description="ChromaDB persistence directory"
    )

    # Email Processing Configuration
    email_check_interval: int = Field(
        default=300, description="Email check interval in seconds"
    )
    max_emails_per_check: int = Field(
        default=50, description="Maximum emails to process per check"
    )
    duplicate_similarity_threshold: float = Field(
        default=0.85, description="Similarity threshold for duplicate detection (0-1)"
    )

    # Auto-Response Configuration
    auto_response_enabled: bool = Field(
        default=True, description="Enable auto-response feature"
    )
    job_keywords: str = Field(
        default="job,opportunity,position,hiring,career,interview,recruitment",
        description="Comma-separated job-related keywords",
    )
    default_resume_path: str = Field(
        default="./data/resumes/default_resume.pdf", description="Default resume path"
    )

    # MCP Server Configuration
    mcp_server_host: str = Field(default="localhost", description="MCP server host")
    mcp_server_port: int = Field(default=3000, description="MCP server port")

    @property
    def job_keywords_list(self) -> List[str]:
        """Get job keywords as a list."""
        return [kw.strip().lower() for kw in self.job_keywords.split(",")]

    @property
    def base_path(self) -> Path:
        """Get base path of the project."""
        return Path(__file__).parent.parent

    @property
    def data_path(self) -> Path:
        """Get data directory path."""
        return self.base_path / "data"

    @property
    def resume_path(self) -> Path:
        """Get resume directory path."""
        return self.data_path / "resumes"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
