// Email Agent Chrome Extension Popup Script

const API_BASE = 'http://localhost:8080';

document.getElementById('processBtn').addEventListener('click', async () => {
  const statusDiv = document.getElementById('status');
  statusDiv.textContent = 'Processing emails...';
  statusDiv.className = 'info';

  try {
    const response = await fetch(`${API_BASE}/api/process`, {
      method: 'POST'
    });
    const data = await response.json();

    if (data.status === 'success') {
      statusDiv.textContent = `✅ Processed ${data.emails_processed} emails`;
      statusDiv.className = 'success';
    } else {
      statusDiv.textContent = `❌ Error: ${data.message}`;
      statusDiv.className = 'error';
    }
  } catch (error) {
    statusDiv.textContent = `❌ Connection error. Is the server running?`;
    statusDiv.className = 'error';
  }
});

document.getElementById('dashboardBtn').addEventListener('click', () => {
  chrome.tabs.create({ url: API_BASE });
});
