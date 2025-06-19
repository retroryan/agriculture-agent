#!/bin/bash
# Start script for the serializer server

PID_FILE="serializer_server.pid"
LOG_FILE="serializer_server.log"

# Check if server is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Server is already running with PID $PID"
        exit 1
    else
        echo "Removing stale PID file"
        rm "$PID_FILE"
    fi
fi

# Start the server in the background
echo "Starting serializer server..."
python servers/serializer.py > "$LOG_FILE" 2>&1 &
PID=$!

# Save the PID
echo $PID > "$PID_FILE"

# Wait a moment to check if it started successfully
sleep 2

if ps -p "$PID" > /dev/null; then
    echo "Server started successfully with PID $PID"
    echo "Log file: $LOG_FILE"
    echo "To stop the server, run: ./stop_server.sh"
else
    echo "Failed to start server. Check $LOG_FILE for errors."
    rm "$PID_FILE"
    exit 1
fi