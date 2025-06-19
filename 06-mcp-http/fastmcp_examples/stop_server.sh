#!/bin/bash
# Stop script for the serializer server

PID_FILE="serializer_server.pid"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "No PID file found. Server may not be running."
    echo "Checking for any running serializer processes..."
    
    # Try to find the process anyway
    PIDS=$(pgrep -f "python servers/serializer.py")
    if [ -n "$PIDS" ]; then
        echo "Found serializer process(es): $PIDS"
        echo "Stopping..."
        kill $PIDS
        echo "Stopped."
    else
        echo "No serializer server process found."
    fi
    exit 0
fi

# Read the PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "Stopping server with PID $PID..."
    kill "$PID"
    
    # Wait for process to stop
    COUNT=0
    while ps -p "$PID" > /dev/null 2>&1 && [ $COUNT -lt 10 ]; do
        sleep 1
        COUNT=$((COUNT + 1))
    done
    
    # Force kill if still running
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Process didn't stop gracefully. Force killing..."
        kill -9 "$PID"
    fi
    
    echo "Server stopped."
else
    echo "Server with PID $PID is not running."
fi

# Remove PID file
rm -f "$PID_FILE"
echo "PID file removed."