#!/bin/bash

# Chilean E-commerce Sales Toolkit Launcher
echo "🚀 Starting Chilean E-commerce Sales Toolkit..."
echo "================================================"

# Kill any existing Streamlit processes on port 8501
lsof -ti:8501 | xargs kill -9 2>/dev/null

# Clear any cached sessions
rm -rf ~/.streamlit/cache 2>/dev/null

# Set working directory
cd "$(dirname "$0")"

# Launch Streamlit
echo "📊 Launching web interface..."
echo "➡️  Opening in browser: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================"

streamlit run app.py \
    --server.port 8501 \
    --server.address localhost \
    --browser.serverAddress localhost \
    --browser.serverPort 8501