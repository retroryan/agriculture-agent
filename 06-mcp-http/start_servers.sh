#!/bin/bash
# Start all FastMCP servers in the background and pipe outputs to logs directory

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="$SCRIPT_DIR/logs"
mkdir -p "$LOGDIR"

# Change to the script directory to ensure relative paths work
cd "$SCRIPT_DIR"

# Start forecast server on port 8000
nohup python mcp_servers/forecast_server.py --port 8000 > "$LOGDIR/forecast_server.log" 2>&1 &
echo $! > "$LOGDIR/forecast_server.pid"

# Start historical server on port 8001
nohup python mcp_servers/historical_server.py --port 8001 > "$LOGDIR/historical_server.log" 2>&1 &
echo $! > "$LOGDIR/historical_server.pid"

# Start agricultural server on port 8002
nohup python mcp_servers/agricultural_server.py --port 8002 > "$LOGDIR/agricultural_server.log" 2>&1 &
echo $! > "$LOGDIR/agricultural_server.pid"

sleep 1
echo "Servers started. Logs in $LOGDIR. Use 'kill $(cat $LOGDIR/*.pid)' to stop."
