# Agricultural Weather Intelligence Demo

This demo showcases how to build AI-powered agricultural intelligence applications using OpenMeteo weather data and Claude AI.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export ANTHROPIC_API_KEY="your-claude-api-key"

# Run from project root directory
# Interactive mode
python 02-domain-applications/main.py

# Demo mode with sample queries
python 02-domain-applications/main.py --demo

# Single query
python 02-domain-applications/main.py --query "Is it too hot for corn in Iowa?"
```

## Architecture

```
02-domain-applications/
├── main.py                 # Entry point with CLI interface
├── api_utils/              # Weather API utilities
│   ├── api_client.py       # OpenMeteo API client
│   ├── collections.py      # Weather parameter definitions
│   ├── temperature_api.py  # Temperature data analyzer
│   ├── precipitation_api.py # Precipitation analyzer
│   └── soil_moisture_api.py # Soil moisture analyzer
└── utils/                  # General utilities
    ├── claude_integration.py # Claude AI for classification & analysis
    └── display.py          # Terminal output formatting
```

## How It Works

1. **User Query**: Accept natural language questions about weather and agriculture
2. **Classification**: Claude AI classifies the query to determine:
   - Data types needed (temperature, precipitation, soil moisture)
   - Location (extracted from query or using defaults)
   - Time range (extracted or default to last 30 days)
   - Analysis focus (crop health, irrigation, frost risk, etc.)
3. **Data Fetching**: Appropriate API helper fetches OpenMeteo data
4. **Analysis**: Claude AI analyzes the data and provides insights
5. **Output**: Formatted results with actionable recommendations

## Example Queries

```
"How much rain did we get in Austin last week?"
"What was the average temperature in Iowa City in May?"
"Tell me about soil moisture in Des Moines for the past 10 days"
"Is it too dry to plant corn in Nebraska?"
"When should I irrigate my fields in California?"
```

## Key Features

- **Natural Language Interface**: Ask questions in plain English
- **Multi-Parameter Analysis**: Temperature, precipitation, soil moisture
- **AI-Powered Insights**: Claude provides agricultural context
- **Location Flexibility**: Specify by name or coordinates
- **Time Range Detection**: Understands various date formats
- **Actionable Recommendations**: Practical advice for farmers

## API Helpers

### Temperature Analyzer
- Tracks daily min/max/mean temperatures
- Identifies heat stress periods (>32°C)
- Detects frost risks (<0°C)
- Provides crop-specific recommendations

### Precipitation Analyzer
- Monitors rainfall totals and patterns
- Identifies drought risks (<10mm over 2 weeks)
- Warns about flood risks (>100mm in a week)
- Tracks dry spell duration

### Soil Moisture Analyzer
- Analyzes moisture at multiple depths
- Surface moisture for germination (0-1cm)
- Root zone moisture for irrigation (9-27cm)
- Deep reserves for drought resilience (27-81cm)

## Claude Integration

The `claude_integration.py` module provides:
- **Query Classification**: Understands user intent
- **Data Analysis**: Interprets weather data in agricultural context
- **Customized Insights**: Tailored to specific crops and conditions

## Environment Variables

Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your-claude-api-key
```

## Dependencies

- `langchain-anthropic`: Claude AI integration
- `requests`: HTTP client for OpenMeteo API
- `python-dotenv`: Environment variable management
- `colorama`: Terminal color support

## Extending the Demo

1. **Add New Analyzers**: Create new modules in `api_utils/`
2. **Custom Parameters**: Extend `collections.py` with new weather parameters
3. **Enhanced Analysis**: Add specialized analysis methods
4. **New Locations**: The geocoding API supports global locations

## Notes

- OpenMeteo API is free and requires no authentication
- Rate limits apply for high-frequency requests
- Historical data available for several years
- Forecast data available up to 16 days