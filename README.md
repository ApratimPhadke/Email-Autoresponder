# 📧 Email Agent - AI-Powered Email Management

An intelligent email management system powered by Google's Gemini AI and ADK framework. Automatically summarize, classify, detect duplicates, and respond to emails with advanced RAG-based duplicate detection and auto-response capabilities.

## 🌟 Features

- **📊 Email Summarization**: AI-powered summaries with key points, action items, and deadlines
- **🏷️ Smart Classification**: Automatic email categorization (Important, Urgent, Job-related, etc.)
- **🔍 Duplicate Detection**: RAG-based vector similarity search to find similar/duplicate emails
- **🤖 Auto-Response**: Intelligent auto-reply to job-related emails with resume attachment
- **📱 Slack Integration**: Send email summaries to Slack channels
- **🌐 Web Dashboard**: Real-time monitoring and control interface
- **🔌 Chrome Extension**: Gmail integration for quick actions
- **⚡ MCP Server**: SMTP operations via Model Context Protocol

## 📁 Project Structure

```
email-agent/
├── src/
│   ├── agents/         # Main email agent logic
│   ├── services/       # Gmail, Gemini, RAG, Slack services
│   ├── models/         # Data models
│   ├── utils/          # Utilities and helpers
│   ├── ui/             # FastAPI web dashboard
│   └── mcp/            # MCP SMTP server
├── chrome_extension/   # Gmail Chrome extension
├── config/             # Configuration settings
├── data/               # Data storage (resumes, vector DB)
├── tests/              # Test files
├── main.py             # Main entry point
├── requirements.txt    # Python dependencies
└── .env.example        # Environment variables template
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- Gmail account with API access
- Google Gemini API key
- (Optional) Slack workspace for notifications

### 2. Installation

```bash
# Clone or extract the project
cd email-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env   # Windows
   cp .env.example .env     # macOS/Linux
   ```

2. Edit `.env` and add your credentials:

   **Google Gemini API:**
   - Get API key from: https://makersuite.google.com/app/apikey
   - Add to `GOOGLE_API_KEY`

   **Gmail API:**
   - Go to: https://console.cloud.google.com/
   - Create a project and enable Gmail API
   - Create OAuth 2.0 credentials
   - Add Client ID and Secret to `.env`

   **SMTP (for sending emails):**
   - Use Gmail app-specific password
   - Enable 2FA in Gmail settings
   - Generate app password: https://myaccount.google.com/apppasswords
   - Add to `SMTP_PASSWORD`

   **Slack (optional):**
   - Create incoming webhook: https://api.slack.com/messaging/webhooks
   - Add webhook URL to `SLACK_WEBHOOK_URL`

3. Add your resume:
   ```bash
   # Place your resume in the data/resumes/ folder
   copy your_resume.pdf data\resumes\default_resume.pdf
   ```

### 4. First Run

```bash
# Start the web dashboard
python main.py web
```

Visit `http://localhost:8080` in your browser.

On first run, you'll be prompted to authenticate with Google. This creates a token for Gmail API access.

## 📖 Usage

### Command Line Interface

```bash
# Start web dashboard
python main.py web

# Process emails once (manual)
python main.py process

# View statistics
python main.py stats

# Enable debug mode
python main.py web --debug
```

### Web Dashboard

1. Start the dashboard: `python main.py web`
2. Open `http://localhost:8080`
3. Click "Process Emails Now" to manually trigger processing
4. View real-time statistics and results

### Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `chrome_extension` folder
5. The extension icon will appear in your toolbar
6. Click it to process emails or open the dashboard

## ⚙️ Configuration Options

Edit `.env` to customize behavior:

| Setting | Description | Default |
|---------|-------------|---------|
| `EMAIL_CHECK_INTERVAL` | Auto-check interval (seconds) | 300 |
| `MAX_EMAILS_PER_CHECK` | Max emails per cycle | 50 |
| `DUPLICATE_SIMILARITY_THRESHOLD` | Duplicate detection threshold (0-1) | 0.85 |
| `AUTO_RESPONSE_ENABLED` | Enable auto-response | true |
| `JOB_KEYWORDS` | Keywords for job detection | job,opportunity,position... |
| `DEFAULT_RESUME_PATH` | Path to resume file | ./data/resumes/default_resume.pdf |

## 🔧 Advanced Features

### RAG-Based Duplicate Detection

The system uses ChromaDB and sentence transformers to create vector embeddings of emails. Similar emails are detected based on semantic similarity, not just exact matches.

### Auto-Response to Job Emails

When a job-related email is detected:
1. Gemini AI confirms it's job-related
2. Generates a professional response
3. Attaches your resume
4. Sends automatically via Gmail

### Slack Integration

Email summaries are automatically sent to Slack with:
- Priority-based organization
- Action items and deadlines
- Statistics and insights

## 📊 API Endpoints

The web dashboard exposes these endpoints:

- `GET /` - Web dashboard
- `GET /api/stats` - Agent statistics
- `POST /api/process` - Trigger email processing
- `GET /api/health` - Health check

## 🐛 Troubleshooting

### Gmail Authentication Issues

1. Ensure Gmail API is enabled in Google Cloud Console
2. Check OAuth redirect URIs include `http://localhost`
3. Delete `data/token.pickle` and re-authenticate

### Gemini API Errors

1. Verify API key is correct
2. Check quota limits at https://makersuite.google.com/
3. Ensure billing is enabled (if required)

### SMTP Send Failures

1. Use app-specific password, not regular Gmail password
2. Enable "Less secure app access" if needed
3. Check firewall/antivirus settings

## 🔒 Security Notes

- Store `.env` securely - never commit to version control
- Use app-specific passwords for SMTP
- Limit Gmail API scopes to minimum required
- Regularly rotate API keys
- Review auto-response emails before enabling in production

## 📝 Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff src/
```

## 🎯 Roadmap

- [ ] Enhanced Gmail UI integration
- [ ] Multi-account support
- [ ] Custom classification rules
- [ ] Email templates library
- [ ] Analytics dashboard
- [ ] Mobile app

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## 📧 Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## 🙏 Acknowledgments

- Google Gemini AI
- Google ADK Framework
- ChromaDB for vector storage
- Sentence Transformers
- FastAPI framework

---

**Made with ❤️ using Google Gemini AI and ADK Framework**
