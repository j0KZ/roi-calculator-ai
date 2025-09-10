#!/bin/bash

# Chilean E-commerce Sales Toolkit - Web App Launcher

echo "=================================================="
echo "🚀 Chilean E-commerce Sales Toolkit"
echo "   Professional Web Dashboard"
echo "=================================================="
echo ""

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "⚠️  Streamlit not found. Installing dependencies..."
    pip3 install -r requirements.txt
    echo "✅ Dependencies installed"
    echo ""
fi

# Launch the web app
echo "🌐 Starting web application..."
echo "   The app will open in your browser automatically"
echo "   If not, navigate to: http://localhost:8501"
echo ""
echo "📌 Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

# Run Streamlit
streamlit run app.py --server.port 8501 --server.address localhost