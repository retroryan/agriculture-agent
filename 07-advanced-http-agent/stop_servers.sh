#!/bin/bash

# FastMCP Server Shutdown Script
# This script stops all running FastMCP servers

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping FastMCP servers...${NC}"
echo ""

# Function to stop a server
stop_server() {
    local name=$1
    local pid_file="logs/${name}.pid"
    
    if [ ! -f "$pid_file" ]; then
        echo -e "${YELLOW}⚠️  ${name} server is not running (no PID file found)${NC}"
        return
    fi
    
    local pid=$(cat "$pid_file")
    
    # Check if process exists
    if ps -p $pid > /dev/null 2>&1; then
        echo -e "Stopping ${name} server (PID: $pid)..."
        kill $pid 2>/dev/null
        
        # Wait for process to terminate
        local count=0
        while ps -p $pid > /dev/null 2>&1 && [ $count -lt 10 ]; do
            sleep 0.5
            count=$((count + 1))
        done
        
        # Force kill if still running
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}Force stopping ${name} server...${NC}"
            kill -9 $pid 2>/dev/null
        fi
        
        echo -e "${GREEN}✅ ${name} server stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  ${name} server was not running (PID: $pid not found)${NC}"
    fi
    
    # Remove PID file
    rm -f "$pid_file"
}

# Check if logs directory exists
if [ ! -d "logs" ]; then
    echo -e "${YELLOW}No logs directory found. No servers to stop.${NC}"
    exit 0
fi

# Stop all servers
stop_server "forecast"
stop_server "historical"
stop_server "agricultural"

echo ""
echo -e "${GREEN}All servers have been stopped.${NC}"

# Optional: Clean up old log files
echo ""
read -p "Do you want to remove log files? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f logs/*.log
    echo -e "${GREEN}Log files removed.${NC}"
fi