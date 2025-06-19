"""
Enhanced coordinate handling for MCP servers.
Improves upon the basic implementation with better location resolution.
"""

from typing import Dict, Optional, Union, List
from api_utils import OpenMeteoClient


async def get_coordinates_enhanced(location: str) -> Optional[Dict[str, Union[str, float]]]:
    """
    Enhanced coordinate resolution with better location info.
    
    Returns dict with:
    - latitude: float
    - longitude: float  
    - name: Resolved location name from API
    - display_name: Full display name with country/state
    - country: Country name
    - confidence: High/Medium/Low based on match quality
    """
    if not location or not location.strip():
        return None
        
    client = OpenMeteoClient()
    try:
        # Extract city name for geocoding
        city = location.split(',')[0].strip()
        
        # Get multiple results for better matching
        results = await client.geocode(city, count=5)
        
        if not results:
            return None
            
        # Try to find best match based on full location string
        best_match = results[0]
        confidence = "Medium"
        
        # If user provided state/country info, try to match it
        if ',' in location:
            location_parts = [part.strip().lower() for part in location.split(',')]
            
            for result in results:
                result_parts = []
                if result.get('name'):
                    result_parts.append(result['name'].lower())
                if result.get('admin1'):  # State/province
                    result_parts.append(result['admin1'].lower())
                if result.get('country'):
                    result_parts.append(result['country'].lower())
                
                # Check if all user-provided parts match
                if all(any(part in result_part for result_part in result_parts) 
                       for part in location_parts):
                    best_match = result
                    confidence = "High"
                    break
        
        # Build display name
        display_parts = [best_match.get('name', '')]
        if best_match.get('admin1'):
            display_parts.append(best_match['admin1'])
        if best_match.get('country'):
            display_parts.append(best_match['country'])
        display_name = ', '.join(filter(None, display_parts))
        
        return {
            "latitude": best_match["latitude"],
            "longitude": best_match["longitude"],
            "name": best_match.get("name", city),
            "display_name": display_name,
            "country": best_match.get("country", ""),
            "confidence": confidence
        }
        
    except Exception:
        return None


async def get_coordinates_with_alternatives(location: str) -> Dict[str, any]:
    """
    Get coordinates with alternative suggestions for ambiguous locations.
    
    Returns dict with:
    - primary: The best match location info
    - alternatives: List of alternative locations if ambiguous
    - query: Original query
    """
    if not location or not location.strip():
        return {
            "error": "Empty location provided",
            "query": location
        }
    
    client = OpenMeteoClient()
    try:
        city = location.split(',')[0].strip()
        results = await client.geocode(city, count=5)
        
        if not results:
            return {
                "error": f"No locations found matching '{location}'",
                "query": location
            }
        
        # Process all results
        processed_results = []
        for result in results:
            display_parts = [result.get('name', '')]
            if result.get('admin1'):
                display_parts.append(result['admin1'])
            if result.get('country'):
                display_parts.append(result['country'])
            
            processed_results.append({
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "name": result.get("name", city),
                "display_name": ', '.join(filter(None, display_parts)),
                "country": result.get("country", ""),
                "population": result.get("population", 0)
            })
        
        # Sort by population (if available) to get most likely match
        processed_results.sort(key=lambda x: x.get('population', 0), reverse=True)
        
        return {
            "primary": processed_results[0],
            "alternatives": processed_results[1:] if len(processed_results) > 1 else [],
            "query": location,
            "ambiguous": len(processed_results) > 1
        }
        
    except Exception as e:
        return {
            "error": f"Error resolving location: {str(e)}",
            "query": location
        }