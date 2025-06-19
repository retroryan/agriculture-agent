#!/bin/bash

# Script to stop MCP servers

echo "Stopping MCP servers..."

# Find and kill processes running the MCP servers
pkill -f "forecast_server.py"
pkill -f "historical_server.py"
pkill -f "agricultural_server.py"

# Give processes time to terminate
sleep 1

# Check if any servers are still running
remaining=$(ps aux | grep -E "(forecast|historical|agricultural)_server\.py" | grep -v grep | wc -l)

if [ $remaining -eq 0 ]; then
    echo "✅ All MCP servers stopped successfully"
else
    echo "⚠️  Some servers may still be running. Checking..."
    ps aux | grep -E "(forecast|historical|agricultural)_server\.py" | grep -v grep
    echo ""
    echo "To force stop, use: pkill -9 -f '_server.py'"
fi

# Clean up log files if requested
if [ "$1" = "--clean-logs" ]; then
    echo "Cleaning up log files..."
    rm -f logs/*.log
    echo "✅ Log files cleaned"
fi