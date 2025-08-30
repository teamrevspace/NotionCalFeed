"""
Pydantic models for Notion ICS Calendar Feed Server
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CalendarEvent(BaseModel):
    """Represents a calendar event from Notion"""
    
    id: str = Field(description="Unique identifier for the event")
    title: str = Field(description="Event title/summary")
    description: Optional[str] = Field(default=None, description="Event description")
    start_time: datetime = Field(description="Event start date/time")
    end_time: Optional[datetime] = Field(default=None, description="Event end date/time")
    all_day: bool = Field(default=False, description="Whether event is all-day")
    location: Optional[str] = Field(default=None, description="Event location")
    url: Optional[str] = Field(default=None, description="Event URL")
    created_time: Optional[datetime] = Field(default=None, description="When event was created")
    last_modified: Optional[datetime] = Field(default=None, description="When event was last modified")
    
    # Additional Notion-specific properties
    notion_page_id: str = Field(description="Notion page ID")
    notion_properties: Dict[str, Any] = Field(default_factory=dict, description="Raw Notion properties")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ViewConfiguration(BaseModel):
    """Configuration for a Notion calendar view"""
    
    database_id: str = Field(description="Notion database ID")
    date_property: str = Field(description="Name of the date property to use")
    title_property: Optional[str] = Field(default="Name", description="Property to use for event title")
    description_property: Optional[str] = Field(default=None, description="Property to use for event description")
    location_property: Optional[str] = Field(default=None, description="Property to use for event location")
    url_property: Optional[str] = Field(default=None, description="Property to use for event URL")
    
    # Query settings
    query_days_back: Optional[int] = Field(
        default=None, 
        description="How many days back to query; None means unbounded"
    )
    query_days_forward: Optional[int] = Field(
        default=None, 
        description="How many days forward to query; None means unbounded"
    )
    
    # Filters (optional)
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Additional Notion filters to apply")
    
    # Calendar settings
    calendar_name: Optional[str] = Field(default=None, description="Custom calendar name")
    calendar_description: Optional[str] = Field(default=None, description="Calendar description")
    timezone: str = Field(default="UTC", description="Timezone for the calendar")
    title_prefix: Optional[str] = Field(default=None, description="String to prepend to every event title")


class NotionConfiguration(BaseModel):
    """Notion API configuration"""
    
    api_token: str = Field(description="Notion API integration token")
    api_version: str = Field(default="2022-06-28", description="Notion API version")
    timeout: int = Field(default=30, description="Request timeout in seconds")


class ServerConfiguration(BaseModel):
    """Server configuration"""
    
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Enable auto-reload in development")


class ApplicationConfiguration(BaseModel):
    """Complete application configuration"""
    
    notion: NotionConfiguration
    calendar_views: Dict[str, ViewConfiguration]
    server: Optional[ServerConfiguration] = Field(default_factory=ServerConfiguration)
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # ICS settings
    ics_prodid: str = Field(
        default="notion-ics-server//EN", 
        description="ICS PRODID identifier"
    )


class ErrorResponse(BaseModel):
    """Standard error response model"""
    
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response model"""
    
    status: str = Field(description="Health status")
    views_configured: int = Field(description="Number of configured calendar views")
    uptime: Optional[float] = Field(default=None, description="Server uptime in seconds")


class CalendarFeedInfo(BaseModel):
    """Information about available calendar feeds"""
    
    message: str = Field(description="Welcome message")
    available_feeds: List[str] = Field(description="List of available calendar feed names")
    endpoints: Dict[str, str] = Field(description="Available API endpoints")
