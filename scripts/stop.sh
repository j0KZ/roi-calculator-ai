#!/bin/bash
# Stop script for ROI Calculator

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping ROI Calculator...${NC}"

# Stop using process manager
if [ -f "scripts/process_manager.py" ]; then
    python3 scripts/process_manager.py stop
fi

# Ensure all processes are killed
pkill -f streamlit 2>/dev/null || true

# Clean up PID file
rm -f .streamlit_pid

echo -e "${GREEN}✅ ROI Calculator stopped${NC}"