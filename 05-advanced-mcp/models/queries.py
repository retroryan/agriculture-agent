"""
Query classification models for intelligent weather request processing.

This module provides models for parsing and classifying user queries about weather,
with support for location resolution and parameter extraction.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from .weather import LocationInfo


class EnhancedQueryClassification(BaseModel):
    """Query classification with intelligent location resolution."""
    query_type: Literal["forecast", "historical", "agricultural", "general"] = Field(
        ...,
        description="Type of weather query"
    )
    locations: List[LocationInfo] = Field(
        default_factory=list,
        description="Extracted locations with coordinates when possible"
    )
    time_references: List[str] = Field(
        default_factory=list,
        description="Extracted time references"
    )
    parameters: List[str] = Field(
        default_factory=list,
        description="Weather parameters mentioned or implied"
    )
    requires_clarification: bool = Field(
        False,
        description="Whether the query needs clarification"
    )
    clarification_message: Optional[str] = Field(
        None,
        description="Message to show user if clarification needed"
    )
    
    def get_primary_location(self) -> Optional[LocationInfo]:
        """Get the primary (first) location if available."""
        return self.locations[0] if self.locations else None
    
    def has_resolved_location(self) -> bool:
        """Check if at least one location has coordinates."""
        return any(loc.has_coordinates() for loc in self.locations)