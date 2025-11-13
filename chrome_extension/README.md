# Email Agent Chrome Extension

Chrome extension for Email Agent Gmail integration.

## Installation

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select this `chrome_extension` folder
5. The Email Agent icon will appear in your toolbar

## Usage

1. Make sure the Email Agent server is running (`python main.py web`)
2. Click the extension icon in Chrome
3. Use the popup to:
   - Process emails immediately
   - Open the main dashboard

## Features

- Quick access to email processing
- Direct link to web dashboard
- Gmail integration ready (can be extended)

## Configuration

The extension connects to `http://localhost:8080` by default.

To change the server URL, edit `popup.js` and update the `API_BASE` constant.

## Icon Note

This extension currently uses placeholder icons. For production use, add proper icons:
- `icons/icon16.png` - 16x16 pixels
- `icons/icon48.png` - 48x48 pixels
- `icons/icon128.png` - 128x128 pixels

You can create simple icons using any image editor or online icon generator.
