# Weather Agent Chatbot

A multi-agent weather information system that provides forecasts, historical data, and agricultural insights for various locations.

## Features

- **Weather Forecasts**: Current conditions and 7-day forecasts
- **Historical Analysis**: Past weather patterns and trends
- **Agricultural Insights**: Soil conditions and crop-specific recommendations
- **Multi-Agent Architecture**: Specialized agents for different types of queries

## Available Locations

- **Nebraska**: Grand Island, Scottsbluff
- **Iowa**: Ames, Cedar Rapids
- **California**: Fresno, Salinas
- **Texas**: Lubbock, Amarillo

## Usage

### Interactive Mode (Default)
```bash
python 05-advanced-mcp/weather_agent/chatbot.py
```

This starts an interactive chat session where you can ask questions about weather, historical data, or agricultural conditions.

### Demo Mode
```bash
python 05-advanced-mcp/weather_agent/chatbot.py --demo
```

This runs a set of predefined queries to demonstrate the system's capabilities.

## Example Queries

- "What's the weather forecast for Ames, Iowa?"
- "How did last year's rainfall compare to normal in Nebraska?"
- "What are the soil conditions for corn planting in Grand Island?"
- "I need both current weather and historical trends for Fresno agriculture"

## Architecture

The system uses three specialized agents:
1. **Forecast Agent**: Handles current weather and future predictions
2. **Historical Agent**: Analyzes past weather patterns and trends
3. **Agricultural Agent**: Provides farming-specific insights and recommendations

The system uses MCP (Model Context Protocol) to coordinate between specialized agents running as separate processes to provide comprehensive responses.