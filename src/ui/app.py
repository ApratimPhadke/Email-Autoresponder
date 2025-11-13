"""FastAPI web UI for Email Agent configuration and monitoring."""

import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import get_settings
from src.agents import EmailAgent
from src.utils import get_logger, setup_logging

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Email Agent Dashboard",
    description="AI-powered Email Agent with Gmail integration",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
settings = get_settings()
setup_logging(settings.debug)
agent = EmailAgent(settings)

# Background task for periodic email checking
email_check_task = None


@app.on_event("startup")
async def startup_event():
    """Start background tasks on app startup."""
    global email_check_task
    logger.info("Starting Email Agent Dashboard")

    if settings.email_check_interval > 0:
        email_check_task = asyncio.create_task(periodic_email_check())


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    global email_check_task
    if email_check_task:
        email_check_task.cancel()

    logger.info("Email Agent Dashboard shut down")


async def periodic_email_check():
    """Periodically check and process emails."""
    while True:
        try:
            await asyncio.sleep(settings.email_check_interval)
            logger.info("Running periodic email check")
            await agent.process_emails()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in periodic email check: {e}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main dashboard page."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Agent Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .header {
                background: #4285f4;
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            button {
                background: #4285f4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 10px;
            }
            button:hover {
                background: #357ae8;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }
            .stat-box {
                background: #e8f0fe;
                padding: 15px;
                border-radius: 4px;
            }
            .stat-value {
                font-size: 24px;
                font-weight: bold;
                color: #1a73e8;
            }
            #status {
                margin-top: 10px;
                padding: 10px;
                border-radius: 4px;
            }
            .success {
                background: #d4edda;
                color: #155724;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📧 Email Agent Dashboard</h1>
            <p>AI-powered email management with Gemini</p>
        </div>

        <div class="card">
            <h2>Actions</h2>
            <button onclick="processEmails()">Process Emails Now</button>
            <button onclick="getStats()">Refresh Statistics</button>
            <div id="status"></div>
        </div>

        <div class="card">
            <h2>Statistics</h2>
            <div id="stats" class="stats">
                <div class="stat-box">
                    <div class="stat-value" id="vectorStoreSize">-</div>
                    <div>Emails in Vector Store</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="autoResponse">-</div>
                    <div>Auto-Response</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="duplicateThreshold">-</div>
                    <div>Duplicate Threshold</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="checkInterval">-</div>
                    <div>Check Interval (s)</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>Recent Processing Results</h2>
            <div id="results"></div>
        </div>

        <script>
            async function processEmails() {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '⏳ Processing emails...';
                statusDiv.className = '';

                try {
                    const response = await fetch('/api/process');
                    const data = await response.json();

                    if (data.status === 'success') {
                        statusDiv.innerHTML = `✅ Processed ${data.emails_processed} emails. High priority: ${data.high_priority}`;
                        statusDiv.className = 'success';
                    } else {
                        statusDiv.innerHTML = `❌ Error: ${data.message}`;
                        statusDiv.className = 'error';
                    }

                    getStats();
                } catch (error) {
                    statusDiv.innerHTML = `❌ Error: ${error.message}`;
                    statusDiv.className = 'error';
                }
            }

            async function getStats() {
                try {
                    const response = await fetch('/api/stats');
                    const data = await response.json();

                    document.getElementById('vectorStoreSize').textContent = data.vector_store_size;
                    document.getElementById('autoResponse').textContent = data.settings.auto_response_enabled ? 'Enabled' : 'Disabled';
                    document.getElementById('duplicateThreshold').textContent = data.settings.duplicate_threshold;
                    document.getElementById('checkInterval').textContent = data.settings.check_interval;
                } catch (error) {
                    console.error('Error fetching stats:', error);
                }
            }

            // Load stats on page load
            getStats();
            setInterval(getStats, 30000); // Refresh every 30 seconds
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/stats")
async def get_stats():
    """Get agent statistics."""
    try:
        stats = agent.get_statistics()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process")
async def process_emails():
    """Manually trigger email processing."""
    try:
        result = await agent.process_emails()
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error processing emails: {e}")
        return JSONResponse(
            content={"status": "error", "message": str(e)}, status_code=500
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "email-agent"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        log_level="info" if not settings.debug else "debug",
    )
