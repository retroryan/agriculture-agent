"""Claude integration for weather data classification and analysis."""

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
from pathlib import Path
from typing import Dict, List, Any
import json


class ClaudeIntegration:
    """Unified Claude AI integration for query classification and data analysis."""
    
    def __init__(self):
        """Initialize Claude model with LangChain."""
        # Load environment variables
        env_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(env_path)
        
        # Initialize Claude model once
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0
        )
    
    def classify_query(self, query: str, location: Dict[str, float]) -> Dict[str, any]:
        """Classify a user query and extract intent using Claude."""
        prompt = f"""You are a query classifier for an Open-Meteo weather data analysis system.

Analyze this query and return a JSON object with:
1. data_needs: Array of needed data types. Choose from: ["temperature", "precipitation", "soil_moisture", "wind", "solar_radiation", "evapotranspiration"]
2. time_range: Extracted date range as {{start: "YYYY-MM-DD", end: "YYYY-MM-DD"}}
3. location: Extracted location as {{name: "location name"}} or {{latitude: float, longitude: float}}
4. analysis_focus: The main analytical goal (e.g., "crop_health", "irrigation_planning", "frost_risk", "drought_monitoring")

Query: "{query}"
Default location (if none specified): {location}

Return ONLY valid JSON, no other text."""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        try:
            result = json.loads(response.content)
            
            # Parse time range from response
            if 'time_range' in result and isinstance(result['time_range'], dict):
                from datetime import datetime
                try:
                    start = datetime.strptime(result['time_range']['start'], '%Y-%m-%d')
                    end = datetime.strptime(result['time_range']['end'], '%Y-%m-%d')
                    result['time_range'] = (start, end)
                except:
                    # Use default if parsing fails
                    from datetime import datetime, timedelta
                    end = datetime.now()
                    start = end - timedelta(days=30)
                    result['time_range'] = (start, end)
            
            return result
            
        except json.JSONDecodeError:
            return {
                'data_needs': ['temperature'],
                'time_range': None,
                'location': location,
                'analysis_focus': 'general'
            }
    
    def analyze_data(self, analysis_type: str, results: Dict[str, Any]) -> str:
        """Analyze weather data and provide insights based on the type."""
        if analysis_type == 'temperature':
            return self._analyze_temperature_data(results)
        elif analysis_type == 'precipitation':
            return self._analyze_precipitation_data(results)
        elif analysis_type == 'soil_moisture':
            return self._analyze_soil_moisture_data(results)
        else:
            return self._analyze_general_data(results)
    
    def _analyze_temperature_data(self, results: Dict[str, Any]) -> str:
        """Analyze temperature data and provide insights."""
        data = results.get('data', {})
        location = results.get('location', {})
        insights = results.get('insights', [])
        
        prompt = f"""You are an agricultural weather analyst. Analyze this Open-Meteo temperature data and provide practical insights.

Location: {location.get('name', 'Unknown')}
Time Period: {results.get('time_range', {}).get('start')} to {results.get('time_range', {}).get('end')}

Statistics:
{json.dumps(data.get('statistics', {}), indent=2)}

System-Generated Insights:
{json.dumps(insights, indent=2)}

Provide a concise agricultural analysis focusing on:
1. Temperature trends and extremes
2. Impact on crop growth and development
3. Specific risks or opportunities
4. Actionable recommendations

Keep the response under 200 words and use clear, practical language."""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
    
    def _analyze_precipitation_data(self, results: Dict[str, Any]) -> str:
        """Analyze precipitation data for agricultural insights."""
        data = results.get('data', {})
        location = results.get('location', {})
        insights = results.get('insights', [])
        
        prompt = f"""You are an agricultural water management expert. Analyze this Open-Meteo precipitation data.

Location: {location.get('name', 'Unknown')}
Time Period: {results.get('time_range', {}).get('start')} to {results.get('time_range', {}).get('end')}

Precipitation Statistics:
{json.dumps(data.get('statistics', {}), indent=2)}

System Insights:
{json.dumps(insights, indent=2)}

Provide practical analysis covering:
1. Rainfall patterns and distribution
2. Water availability for crops
3. Irrigation recommendations
4. Flood or drought risks

Keep response under 200 words with actionable advice."""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
    
    def _analyze_soil_moisture_data(self, results: Dict[str, Any]) -> str:
        """Analyze soil moisture data for irrigation guidance."""
        data = results.get('data', {})
        location = results.get('location', {})
        insights = results.get('insights', [])
        
        # Extract layer summaries
        layer_summaries = []
        for layer_name, layer_data in data.get('soil_moisture_layers', {}).items():
            layer_summaries.append({
                'layer': layer_data.get('description'),
                'average': layer_data.get('average'),
                'range': f"{layer_data.get('min', 0):.3f} - {layer_data.get('max', 0):.3f}"
            })
        
        prompt = f"""You are an irrigation management specialist. Analyze this Open-Meteo soil moisture data.

Location: {location.get('name', 'Unknown')}
Time Period: {results.get('time_range', {}).get('start')} to {results.get('time_range', {}).get('end')}

Soil Moisture by Layer:
{json.dumps(layer_summaries, indent=2)}

System Insights:
{json.dumps(insights, indent=2)}

Provide irrigation guidance including:
1. Current soil moisture status
2. Irrigation needs by depth
3. Optimal irrigation timing
4. Water conservation strategies

Keep response under 200 words with specific recommendations."""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
    
    def _analyze_general_data(self, results: Dict[str, Any]) -> str:
        """Provide general analysis for unspecified data types."""
        prompt = f"""Analyze this weather data and provide agricultural insights:

Data: {json.dumps(results, indent=2)}

Provide a brief, practical analysis suitable for farmers or agricultural managers."""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content