#!/bin/bash

# Check if PID file exists
if [ ! -f "server.pid" ]; then
    echo "No server.pid file found. Server may not be running."
    exit 1
fi

# Read PID from file
PID=$(cat server.pid)

# Check if process is running
if ps -p $PID > /dev/null 2>&1; then
    echo "Stopping server with PID $PID..."
    kill $PID
    
    # Wait for process to stop
    sleep 2
    
    # Force kill if still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "Server didn't stop gracefully, forcing..."
        kill -9 $PID
    fi
    
    echo "Server stopped."
else
    echo "Server with PID $PID is not running."
fi

# Clean up PID file
rm -f server.pid
echo "Cleaned up PID file."