#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if server is already running
if [ -f "server.pid" ]; then
    OLD_PID=$(cat server.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Server is already running with PID $OLD_PID"
        exit 1
    else
        echo "Removing stale PID file"
        rm server.pid
    fi
fi

# Start the server with logging
echo "Starting FastMCP server..."
nohup python serializer.py > logs/server.log 2>&1 &
PID=$!

# Save PID to file
echo $PID > server.pid

# Wait a moment and check if server started successfully
sleep 2
if ps -p $PID > /dev/null; then
    echo "Server started successfully with PID $PID"
    echo "Logs are being written to logs/server.log"
else
    echo "Failed to start server"
    rm server.pid
    exit 1
fi