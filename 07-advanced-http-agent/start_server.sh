#!/bin/bash
# Start the unified weather server for Stage 7 - Advanced HTTP Agent

echo "Starting unified weather server (HTTP transport)..."

# Kill any existing server on port 7074
lsof -ti:7074 | xargs kill -9 2>/dev/null

# Start the unified server
python -m mcp_servers.weather_server &

echo "Unified weather server started on http://127.0.0.1:7074/mcp"
echo "HTTP transport enabled for distributed deployment"
echo ""
echo "To stop the server, run: ./stop_server.sh"