"""Query classification service using LLM with structured output."""

import os
from typing import Optional, Dict, Any
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
import logging

from .models import EnhancedQueryClassification, LocationInfo, Coordinates

# Import unified model configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import get_model

class QueryClassifier:
    """LLM-based query understanding and classification service."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the query classifier with LangChain components."""
        self.llm = get_model(
            temperature=0,
            max_tokens=1000
        )
        self.parser = PydanticOutputParser(pydantic_object=EnhancedQueryClassification)
        self.logger = logging.getLogger(__name__)
        
        # Create the prompt template
        self.prompt_template = PromptTemplate(
            template="""Analyze this weather query and extract structured information.

Query: "{query}"

Instructions:
1. Identify the query type: forecast (future), historical (past), agricultural (farming), or general
2. Extract locations with coordinates when possible:
   - For well-known major cities, provide exact latitude and longitude coordinates
   - For colloquial names like "Big Apple" or "Windy City", translate to proper city names with coordinates
   - For agricultural regions like "Corn Belt" or "Wine Country", map to representative locations with coordinates
   - If you cannot determine coordinates, provide a normalized_name for geocoding and set coordinates to null

3. Extract time references (today, tomorrow, next week, March 2024, etc.)
4. Identify weather parameters mentioned (temperature, precipitation, humidity, wind, etc.)
5. Determine if clarification is needed for ambiguous queries

Location Guidelines:
- Major US Agricultural Centers: Des Moines Iowa (41.5868, -93.6250), Ames Iowa (42.0308, -93.6319), Grand Island Nebraska (40.9264, -98.3420), Fresno California (36.7378, -119.7871), Salinas California (36.6777, -121.6555), Lubbock Texas (33.5779, -101.8552), Amarillo Texas (35.2220, -101.8313), Scottsbluff Nebraska (41.8666, -103.6672), Cedar Rapids Iowa (41.9778, -91.6656), Bakersfield California (35.3733, -119.0187), Fargo North Dakota (46.8772, -96.7898), Bismarck North Dakota (46.8083, -100.7837), Peoria Illinois (40.6936, -89.5890), Springfield Illinois (39.7817, -89.6501), Topeka Kansas (39.0473, -95.6890), Wichita Kansas (37.6872, -97.3301), Lincoln Nebraska (40.8136, -96.7026), Omaha Nebraska (41.2565, -95.9345)
- Major US Cities: New York (40.7128, -74.0060), Los Angeles (34.0522, -118.2437), Chicago (41.8781, -87.6298), Houston (29.7604, -95.3698), Phoenix (33.4484, -112.0740), Philadelphia (39.9526, -75.1652), San Antonio (29.4241, -98.4936), San Diego (32.7157, -117.1611), Dallas (32.7767, -96.7970), San Jose (37.3382, -121.8863), Austin (30.2672, -97.7431), Jacksonville (30.3322, -81.6557), Fort Worth (32.7555, -97.3308), Columbus (39.9612, -82.9988), Indianapolis (39.7684, -86.1581), Charlotte (35.2271, -80.8431), San Francisco (37.7749, -122.4194), Seattle (47.6062, -122.3321), Denver (39.7392, -104.9903), Washington DC (38.9072, -77.0369), Boston (42.3601, -71.0589)

Examples of Colloquial Names:
- "Big Apple" = New York City
- "Windy City" = Chicago
- "City of Angels" = Los Angeles
- "Motor City" = Detroit
- "Space City" = Houston
- "The Big Easy" = New Orleans
- "Bean Town" = Boston
- "Emerald City" = Seattle
- "Mile High City" = Denver
- "Music City" = Nashville

Agricultural Regions (Map to specific representative locations):
- "Corn Belt" = Des Moines, Iowa (41.5868, -93.6250)
- "Wine Country" = Napa Valley, California (38.5025, -122.2654)
- "Wheat Belt" = Wichita, Kansas (37.6872, -97.3301)
- "Cotton Belt" = Lubbock, Texas (33.5779, -101.8552)
- "Dairy Belt" = Milwaukee, Wisconsin (43.0389, -87.9065)

Default Location Clarifications:
- "Fresno" → Fresno, California (agricultural center)
- "Grand Island" → Grand Island, Nebraska (agricultural region)
- "Ames" → Ames, Iowa (agricultural research center)
- "Lincoln" → Lincoln, Nebraska (agricultural region)
- "Peoria" → Peoria, Illinois (agricultural region)

Time Period Guidelines:
- If no time period specified for forecast → assume next 7 days
- "last month" → previous 30 days from today
- Agricultural/planting queries → next 14 days (critical planting window)
- Historical comparisons → same period last year
- Seasonal queries → 90 day period

{format_instructions}

Important: 
- Provide exact coordinates (latitude, longitude) for any location you recognize
- Set confidence to 1.0 if you're certain about the coordinates
- Set confidence to 0.7-0.9 if you're reasonably sure
- Set confidence below 0.7 if unsure
- If you cannot determine coordinates, leave them null and provide a normalized_name""",
            input_variables=["query"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
    
    async def classify_query(self, query: str) -> EnhancedQueryClassification:
        """
        Classify user query and extract key information including location coordinates.
        
        This method relies entirely on the LLM for query classification and location
        resolution. No preprocessing or postprocessing is performed.
        
        Args:
            query: The user's weather query
            
        Returns:
            EnhancedQueryClassification with locations resolved to coordinates when possible
            
        Raises:
            ValueError: If no location could be determined from the query
        """
        try:
            # Format the prompt
            prompt = self.prompt_template.format(query=query)
            
            # Get structured response from LLM
            response = await self.llm.ainvoke(prompt)
            
            # Parse the response using PydanticOutputParser
            classification = self.parser.parse(response.content)
            
            # Validate that we have at least one location if not a general query
            if classification.query_type != "general" and not classification.locations:
                raise ValueError("No location could be determined from the query. Please specify a location.")
            
            # Check if locations have coordinates or normalized names
            for location in classification.locations:
                if not location.coordinates and not location.normalized_name:
                    raise ValueError(
                        f"Location '{location.name}' could not be resolved. "
                        "Please use a well-known city name or provide more specific location details."
                    )
            
            return classification
            
        except ValueError:
            # Re-raise ValueError for location issues
            raise
        except Exception as e:
            self.logger.error(f"Error classifying query: {e}")
            # Return a default classification on error
            return EnhancedQueryClassification(
                query_type="general",
                requires_clarification=True,
                clarification_message="I had trouble understanding your query. Could you please be more specific?"
            )
    
    def extract_location_from_query(
        self, 
        query: str, 
        classification: EnhancedQueryClassification
    ) -> Optional[LocationInfo]:
        """
        Extract primary location from query using classification results.
        
        Args:
            query: Original query (for compatibility)
            classification: The classification result
            
        Returns:
            Primary LocationInfo if available
        """
        return classification.get_primary_location()
    
    def extract_date_range_from_query(
        self,
        query: str,
        classification: EnhancedQueryClassification
    ) -> Optional[Dict[str, Any]]:
        """
        Extract date range from query using classification results.
        
        This is kept for backward compatibility.
        """
        from datetime import date, timedelta
        
        if not classification.time_references:
            # Default ranges based on query type
            today = date.today()
            if classification.query_type == "forecast":
                return {
                    "start_date": today,
                    "end_date": today + timedelta(days=7)
                }
            elif classification.query_type == "historical":
                return {
                    "start_date": today - timedelta(days=30),
                    "end_date": today - timedelta(days=1)
                }
            return None
        
        # Parse time references (simplified for this example)
        today = date.today()
        time_ref = classification.time_references[0].lower()
        
        if "today" in time_ref:
            return {"start_date": today, "end_date": today}
        elif "tomorrow" in time_ref:
            tomorrow = today + timedelta(days=1)
            return {"start_date": tomorrow, "end_date": tomorrow}
        elif "week" in time_ref or "7 day" in time_ref:
            return {"start_date": today, "end_date": today + timedelta(days=7)}
        elif "month" in time_ref or "30 day" in time_ref:
            return {"start_date": today, "end_date": today + timedelta(days=30)}
        
        # Default for forecast
        return {"start_date": today, "end_date": today + timedelta(days=7)}


# Backward compatibility alias
ClaudeService = QueryClassifier