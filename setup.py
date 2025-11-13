#!/usr/bin/env python3
"""Setup script for Email Agent."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a shell command."""
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, cwd=cwd, capture_output=True, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return None


def main():
    """Main setup routine."""
    print("📧 Email Agent Setup")
    print("=" * 50)

    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required")
        sys.exit(1)

    print("✅ Python version OK")

    # Create virtual environment
    print("\n📦 Creating virtual environment...")
    if not Path("venv").exists():
        run_command(f"{sys.executable} -m venv venv")
        print("✅ Virtual environment created")
    else:
        print("ℹ️  Virtual environment already exists")

    # Determine pip path
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"

    # Upgrade pip
    print("\n⬆️  Upgrading pip...")
    run_command(f"{python_path} -m pip install --upgrade pip")

    # Install dependencies
    print("\n📚 Installing dependencies...")
    result = run_command(f"{pip_path} install -r requirements.txt")
    if result is not None:
        print("✅ Dependencies installed successfully")
    else:
        print("❌ Failed to install dependencies")
        sys.exit(1)

    # Create .env file
    if not Path(".env").exists():
        print("\n📝 Creating .env file...")
        shutil.copy(".env.example", ".env")
        print("✅ .env file created")
        print("⚠️  Please edit .env and add your API keys")
    else:
        print("\nℹ️  .env file already exists")

    # Create data directories
    print("\n📁 Creating data directories...")
    Path("data/resumes").mkdir(parents=True, exist_ok=True)
    Path("data/chroma_db").mkdir(parents=True, exist_ok=True)
    print("✅ Data directories created")

    # Final instructions
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Edit .env file and add your API keys:")
    print("   - GOOGLE_API_KEY (Gemini AI)")
    print("   - GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET")
    print("   - SMTP_USERNAME and SMTP_PASSWORD")
    print("   - SLACK_WEBHOOK_URL (optional)")
    print("\n2. Add your resume to data/resumes/default_resume.pdf")
    print("\n3. Run the application:")

    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")

    print("   python main.py web")
    print("\n4. Visit http://localhost:8080")
    print("\n🎉 Happy emailing!")


if __name__ == "__main__":
    main()
