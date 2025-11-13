#!/usr/bin/env python3
"""Main entry point for Email Agent application."""

import asyncio
import sys

from config import get_settings
from src.utils import setup_logging

# Initialize settings and logging
settings = get_settings()
setup_logging(settings.debug)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Email Agent - AI-powered email management")
    parser.add_argument(
        "command",
        choices=["web", "process", "stats"],
        help="Command to run: web (start web UI), process (process emails once), stats (show statistics)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    if args.debug:
        settings.debug = True
        setup_logging(True)

    if args.command == "web":
        # Start web UI
        from src.ui.app import app
        import uvicorn

        print("🚀 Starting Email Agent Dashboard...")
        print(f"📍 Dashboard URL: http://{settings.app_host}:{settings.app_port}")
        print(f"📧 Email check interval: {settings.email_check_interval}s")
        print(f"🤖 Auto-response: {'Enabled' if settings.auto_response_enabled else 'Disabled'}")
        print("\nPress Ctrl+C to stop\n")

        uvicorn.run(
            app,
            host=settings.app_host,
            port=settings.app_port,
            log_level="info" if not settings.debug else "debug",
        )

    elif args.command == "process":
        # Process emails once
        from src.agents import EmailAgent

        print("🔍 Processing emails...")
        agent = EmailAgent(settings)
        result = asyncio.run(agent.process_emails())

        print(f"\n✅ Processing completed:")
        print(f"   Emails processed: {result.get('emails_processed', 0)}")
        print(f"   Duplicates found: {result.get('duplicates_found', 0)}")
        print(f"   Job responses sent: {result.get('job_responses_sent', 0)}")
        print(f"   High priority: {result.get('high_priority', 0)}")

    elif args.command == "stats":
        # Show statistics
        from src.agents import EmailAgent

        agent = EmailAgent(settings)
        stats = agent.get_statistics()

        print("\n📊 Email Agent Statistics:")
        print(f"   Vector store size: {stats['vector_store_size']} emails")
        print(f"   Auto-response: {'Enabled' if stats['settings']['auto_response_enabled'] else 'Disabled'}")
        print(f"   Duplicate threshold: {stats['settings']['duplicate_threshold']}")
        print(f"   Check interval: {stats['settings']['check_interval']}s")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Email Agent stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
