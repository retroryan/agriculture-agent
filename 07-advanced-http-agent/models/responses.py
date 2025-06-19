"""
Tool response models for MCP structured output.

These models define the response format for MCP tools, supporting both
human-readable text and structured data preservation.
"""

from typing import Any, Optional, Dict, List, Literal, Union, Callable
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ResponseStatus(str, Enum):
    """Status of a tool response."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    CACHED = "cached"


class DataQualityAssessment(BaseModel):
    """Assessment of data quality and completeness."""
    completeness: float = Field(..., ge=0.0, le=1.0, description="Data completeness score")
    missing_fields: List[str] = Field(default_factory=list, description="List of missing data fields")
    quality_issues: List[str] = Field(default_factory=list, description="Identified quality issues")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in data")
    
    def is_high_quality(self) -> bool:
        """Check if data meets high quality threshold."""
        return self.completeness >= 0.9 and self.confidence >= 0.8 and len(self.quality_issues) == 0


class ResponseMetadata(BaseModel):
    """Metadata about a tool response."""
    source: str = Field(..., description="Data source (e.g., 'open-meteo', 'cache')")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response generation time")
    cache_hit: bool = Field(default=False, description="Whether response was from cache")
    cache_ttl: Optional[int] = Field(None, description="Cache TTL in seconds if cached")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    api_calls_made: int = Field(default=1, description="Number of API calls made")
    data_quality: Optional[DataQualityAssessment] = None
    warnings: List[str] = Field(default_factory=list, description="Any warnings about the data")
    
    def add_warning(self, warning: str):
        """Add a warning to the metadata."""
        if warning not in self.warnings:
            self.warnings.append(warning)


class ToolResponse(BaseModel):
    """
    Standard response format for MCP tools supporting structured data.
    
    This dual-format approach maintains LLM compatibility while preserving
    data structure for downstream tools and analysis.
    """
    type: Literal["structured"] = Field(default="structured", description="Response type marker")
    text: str = Field(..., description="Human-readable summary for LLM understanding")
    data: Any = Field(..., description="Structured Pydantic model instance")
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    metadata: Optional[ResponseMetadata] = None
    
    def to_mcp_format(self) -> List[Dict[str, Any]]:
        """Convert to MCP protocol format."""
        response = [{"type": "text", "text": self.text}]
        
        # Optionally include structured data as JSON in metadata
        if self.data is not None:
            response.append({
                "type": "metadata",
                "data": self.data.model_dump() if hasattr(self.data, 'model_dump') else self.data
            })
        
        return response
    
    def to_legacy_format(self) -> List[Dict[str, str]]:
        """Convert to legacy text-only format for compatibility."""
        return [{"type": "text", "text": self.text}]


class ComposableToolResponse(ToolResponse):
    """
    Extended tool response supporting composition and chaining.
    
    Enables tools to suggest next steps and provide data transformers
    for seamless tool chaining.
    """
    next_tools: Optional[List[str]] = Field(
        None, 
        description="Suggested tools to call next"
    )
    data_transformers: Optional[Dict[str, Callable]] = Field(
        None,
        description="Functions to transform data for specific next tools"
    )
    chain_context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Context to pass to next tool in chain"
    )
    
    def pipe_to(self, next_tool: str) -> Any:
        """
        Transform data for piping to next tool.
        
        Args:
            next_tool: Name of the tool to pipe data to
            
        Returns:
            Transformed data ready for next tool
        """
        if self.data_transformers and next_tool in self.data_transformers:
            transformer = self.data_transformers[next_tool]
            return transformer(self.data)
        return self.data
    
    def suggest_next_action(self) -> Optional[str]:
        """Get suggestion for next action based on current data."""
        if not self.next_tools:
            return None
        
        # Could implement smart logic here based on data analysis
        # For now, return first suggestion
        return f"Consider calling: {self.next_tools[0]}"
    
    class Config:
        arbitrary_types_allowed = True  # Allow Callable types


class ErrorResponse(BaseModel):
    """Structured error response for tool failures."""
    error_type: str = Field(..., description="Type of error (e.g., 'ValidationError', 'APIError')")
    error_message: str = Field(..., description="Human-readable error message")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    retry_possible: bool = Field(default=False, description="Whether retry might succeed")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retry")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for resolution")
    
    def to_tool_response(self) -> ToolResponse:
        """Convert error to standard tool response."""
        text = f"Error: {self.error_message}"
        if self.suggestions:
            text += f"\nSuggestions: {', '.join(self.suggestions)}"
        
        return ToolResponse(
            type="structured",
            text=text,
            data=self,
            status=ResponseStatus.ERROR,
            metadata=ResponseMetadata(
                source="error",
                warnings=[self.error_message]
            )
        )


class StreamingResponse(BaseModel):
    """Support for streaming responses (future enhancement)."""
    chunk_id: int = Field(..., description="Sequence number of this chunk")
    total_chunks: Optional[int] = Field(None, description="Total expected chunks if known")
    data_chunk: Any = Field(..., description="Partial data for this chunk")
    is_final: bool = Field(default=False, description="Whether this is the final chunk")
    
    def merge_with(self, other: 'StreamingResponse') -> 'StreamingResponse':
        """Merge two streaming chunks."""
        # Implementation depends on data structure
        raise NotImplementedError("Streaming merge not yet implemented")