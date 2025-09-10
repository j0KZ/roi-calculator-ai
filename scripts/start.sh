#!/bin/bash
# Start script for ROI Calculator

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting ROI Calculator...${NC}"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo -e "${RED}❌ Python $required_version or higher is required. Found: $python_version${NC}"
    exit 1
fi

# Create necessary directories
mkdir -p logs data/history cache

# Check and install dependencies
echo -e "${YELLOW}📦 Checking dependencies...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
pip install -q --upgrade pip
pip install -q -r requirements.txt 2>/dev/null || {
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install streamlit pandas plotly python-dotenv psutil
}

# Kill any existing Streamlit processes
echo -e "${YELLOW}🔧 Cleaning up old processes...${NC}"
pkill -f streamlit 2>/dev/null || true
sleep 1

# Start with process manager
echo -e "${GREEN}✅ Starting application with process manager...${NC}"
python3 scripts/process_manager.py start

# Check if started successfully
sleep 2
if python3 scripts/process_manager.py status | grep -q '"status": "running"'; then
    echo -e "${GREEN}✅ ROI Calculator is running at http://localhost:8501${NC}"
    echo -e "${YELLOW}📊 To monitor: python3 scripts/process_manager.py monitor${NC}"
    echo -e "${YELLOW}🛑 To stop: python3 scripts/process_manager.py stop${NC}"
else
    echo -e "${RED}❌ Failed to start application${NC}"
    exit 1
fi