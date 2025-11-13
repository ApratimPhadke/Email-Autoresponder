#!/usr/bin/env python3
"""Script to create a distributable package of Email Agent."""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path


def create_package():
    """Create a distributable package."""
    print("📦 Creating Email Agent Package")
    print("=" * 50)

    # Package name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"email-agent-{timestamp}"
    package_dir = Path(package_name)

    # Clean up old package if exists
    if package_dir.exists():
        shutil.rmtree(package_dir)

    # Create package directory
    package_dir.mkdir()
    print(f"✅ Created package directory: {package_name}")

    # Files and directories to include
    items_to_copy = [
        "src",
        "config",
        "chrome_extension",
        "data/resumes",  # Empty directory for resumes
        "main.py",
        "setup.py",
        "requirements.txt",
        "pyproject.toml",
        ".env.example",
        "README.md",
    ]

    # Copy files and directories
    print("\n📋 Copying files...")
    for item in items_to_copy:
        src = Path(item)
        if not src.exists():
            continue

        if src.is_dir():
            dest = package_dir / item
            # Create empty directory structure
            if item == "data/resumes":
                dest.mkdir(parents=True, exist_ok=True)
                # Add a placeholder
                (dest / "README.txt").write_text(
                    "Place your default resume here as 'default_resume.pdf'"
                )
            else:
                shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            print(f"   ✓ {item}/")
        else:
            dest = package_dir / item
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            print(f"   ✓ {item}")

    # Create additional README files
    print("\n📝 Creating additional documentation...")

    # Create SETUP_GUIDE.txt
    setup_guide = package_dir / "SETUP_GUIDE.txt"
    setup_guide.write_text("""
EMAIL AGENT - QUICK SETUP GUIDE
================================

1. PREREQUISITES
   - Python 3.10 or higher
   - Gmail account
   - Google Gemini API key

2. INSTALLATION
   Run: python setup.py
   
   This will:
   - Create virtual environment
   - Install all dependencies
   - Create .env file from template

3. CONFIGURATION
   Edit .env file and add:
   
   a) Google Gemini API Key
      - Get from: https://makersuite.google.com/app/apikey
      - Add to: GOOGLE_API_KEY=your_key_here
   
   b) Gmail API Credentials
      - Create project: https://console.cloud.google.com/
      - Enable Gmail API
      - Create OAuth 2.0 credentials
      - Add Client ID and Secret to .env
   
   c) SMTP Settings (for sending emails)
      - Enable 2FA in Gmail
      - Create app password: https://myaccount.google.com/apppasswords
      - Add to SMTP_USERNAME and SMTP_PASSWORD
   
   d) Slack (Optional)
      - Create webhook: https://api.slack.com/messaging/webhooks
      - Add to SLACK_WEBHOOK_URL

4. ADD RESUME
   Copy your resume to: data/resumes/default_resume.pdf

5. RUN APPLICATION
   
   Windows:
   venv\\Scripts\\activate
   python main.py web
   
   Mac/Linux:
   source venv/bin/activate
   python main.py web

6. ACCESS DASHBOARD
   Open browser: http://localhost:8080

7. CHROME EXTENSION (Optional)
   - Open chrome://extensions/
   - Enable Developer mode
   - Click "Load unpacked"
   - Select chrome_extension folder

COMMANDS:
---------
python main.py web        Start web dashboard
python main.py process    Process emails once
python main.py stats      View statistics

For detailed documentation, see README.md

Support: Check README.md troubleshooting section
""")
    print("   ✓ SETUP_GUIDE.txt")

    # Create .gitignore
    gitignore = package_dir / ".gitignore"
    gitignore.write_text("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Environment
.env
.env.local

# Data
data/token.pickle
data/chroma_db/
*.pdf
*.doc
*.docx

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
""")
    print("   ✓ .gitignore")

    # Create zip file
    print(f"\n🗜️  Creating zip archive...")
    zip_filename = f"{package_name}.zip"
    
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)

    # Get zip size
    zip_size = Path(zip_filename).stat().st_size / (1024 * 1024)  # Convert to MB

    print(f"✅ Created: {zip_filename} ({zip_size:.2f} MB)")

    # Clean up temporary directory
    shutil.rmtree(package_dir)
    print(f"🧹 Cleaned up temporary files")

    # Final message
    print("\n" + "=" * 50)
    print("✅ Package created successfully!")
    print(f"\n📦 Package: {zip_filename}")
    print(f"📏 Size: {zip_size:.2f} MB")
    print("\n📤 You can now distribute this zip file.")
    print("Recipients should:")
    print("1. Extract the zip file")
    print("2. Read SETUP_GUIDE.txt")
    print("3. Run: python setup.py")
    print("4. Configure .env file")
    print("5. Run: python main.py web")


if __name__ == "__main__":
    try:
        create_package()
    except Exception as e:
        print(f"\n❌ Error creating package: {e}")
        import traceback
        traceback.print_exc()
