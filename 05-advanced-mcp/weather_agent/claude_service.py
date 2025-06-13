"""Claude service for query classification."""

import os
from typing import Optional
from anthropic import Anthropic
import json
from datetime import date, timedelta
from .models import QueryClassification, DateRange


class ClaudeService:
    """Service for query classification using Claude."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
    
    async def classify_query(self, query: str) -> QueryClassification:
        """Classify user query and extract key information using Claude."""
        classification_prompt = f"""Analyze this weather query and extract key information:
Query: "{query}"

Determine:
1. Query type:
   - forecast: Future weather (today to 16 days ahead)
   - historical: Past weather (5+ days ago)
   - agricultural: Farming/crop conditions
   - general: Unclear or needs more info

2. Location references:
   - Extract specific locations mentioned
   - Note if location is ambiguous (e.g., "Iowa" - which city?)
   - Empty if no location specified

3. Time references:
   - Extract specific dates or relative times
   - For agricultural queries, note planting/harvest seasons
   - Empty if no time specified

4. Weather parameters:
   - Temperature (min/max/average)
   - Precipitation (rain/snow)
   - For agricultural: soil moisture, frost risk, growing degree days
   - Wind, humidity, UV index if mentioned

5. Clarification needs:
   - Missing location
   - Ambiguous location (state vs city)
   - Missing time period
   - Vague agricultural needs

Respond in this exact JSON format:
{{
    "query_type": "forecast|historical|agricultural|general",
    "locations": ["Fresno, California", "latitude,longitude"],
    "time_references": ["tomorrow", "next 7 days", "March 2024"],
    "parameters": ["temperature_2m_max", "precipitation_sum", "soil_moisture_0_to_10cm"],
    "requires_clarification": true/false,
    "clarification_message": "Specific helpful message about what's needed"
}}

Be specific with parameters using actual parameter names when possible.
For clarification messages, be helpful and specific about what information is missing."""
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            temperature=0,
            messages=[
                {"role": "user", "content": classification_prompt}
            ]
        )
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            content = response.content[0].text if response.content else ""
            # Find JSON in the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                data = json.loads(json_str)
                return QueryClassification(**data)
            else:
                # Fallback if no JSON found
                return QueryClassification(
                    query_type="general",
                    requires_clarification=True,
                    clarification_message="I couldn't understand your query. Could you please rephrase?"
                )
        except (json.JSONDecodeError, ValueError) as e:
            # Return a default classification on error
            return QueryClassification(
                query_type="general",
                requires_clarification=True,
                clarification_message="I had trouble understanding your query. Could you please be more specific?"
            )
    
    def extract_location_from_query(self, query: str, classification: QueryClassification) -> Optional[str]:
        """Extract location from query using classification results."""
        if classification.locations:
            return classification.locations[0]
        return None
    
    def extract_date_range_from_query(
        self,
        query: str,
        classification: QueryClassification
    ) -> Optional[DateRange]:
        """Extract date range from query using classification results."""
        if not classification.time_references:
            # Default ranges based on query type
            today = date.today()
            if classification.query_type == "forecast":
                return DateRange(start_date=today, end_date=today + timedelta(days=7))
            elif classification.query_type == "historical":
                return DateRange(start_date=today - timedelta(days=30), end_date=today - timedelta(days=1))
            return None
        
        # Enhanced date extraction logic
        today = date.today()
        time_ref = classification.time_references[0].lower()
        
        # Single day references
        if "today" in time_ref:
            return DateRange(start_date=today, end_date=today)
        elif "tomorrow" in time_ref:
            tomorrow = today + timedelta(days=1)
            return DateRange(start_date=tomorrow, end_date=tomorrow)
        elif "yesterday" in time_ref:
            yesterday = today - timedelta(days=1)
            return DateRange(start_date=yesterday, end_date=yesterday)
        
        # Period references
        elif "next week" in time_ref or "this week" in time_ref:
            return DateRange(start_date=today, end_date=today + timedelta(days=7))
        elif "next month" in time_ref:
            return DateRange(start_date=today, end_date=today + timedelta(days=30))
        elif "last week" in time_ref:
            return DateRange(start_date=today - timedelta(days=7), end_date=today)
        elif "last month" in time_ref:
            return DateRange(start_date=today - timedelta(days=30), end_date=today - timedelta(days=1))
        
        # Specific counts
        elif "next" in time_ref and "days" in time_ref:
            # Extract number of days
            import re
            match = re.search(r'next (\d+) days?', time_ref)
            if match:
                days = int(match.group(1))
                return DateRange(start_date=today, end_date=today + timedelta(days=days))
        
        # Agricultural seasons
        elif "planting season" in time_ref:
            # Typical spring planting season
            if today.month <= 6:
                return DateRange(start_date=today, end_date=today + timedelta(days=60))
            else:
                # Next year's planting season
                next_spring = today.replace(year=today.year + 1, month=4, day=1)
                return DateRange(start_date=next_spring, end_date=next_spring + timedelta(days=60))
        
        # Default to next 7 days for forecast
        if classification.query_type == "forecast":
            return DateRange(start_date=today, end_date=today + timedelta(days=7))
        
        return None