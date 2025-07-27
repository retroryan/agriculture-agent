#!/bin/bash
# Stop the unified weather server

echo "Stopping unified weather server..."

# Kill server on port 7074
lsof -ti:7074 | xargs kill -9 2>/dev/null

echo "Server stopped"