"""
ICS calendar generator using the ics.py library
"""

from datetime import datetime
from typing import List, Dict, Any
import logging
from ics import Calendar, Event
import pytz

from .models import CalendarEvent, ViewConfiguration

logger = logging.getLogger(__name__)


class ICSGenerator:
    """Generator for ICS calendar files from CalendarEvent objects"""
    
    def __init__(self, prodid: str = "notion-ics-server//EN"):
        """
        Initialize ICS generator
        
        Args:
            prodid: Product identifier for the ICS calendar
        """
        self.prodid = prodid
    
    def generate_calendar(
        self, 
        events: List[CalendarEvent], 
        calendar_name: str,
        view_config: ViewConfiguration
    ) -> str:
        """
        Generate ICS calendar string from events
        
        Args:
            events: List of CalendarEvent objects
            calendar_name: Name for the calendar
            view_config: View configuration for additional settings
            
        Returns:
            ICS calendar content as string
        """
        try:
            # Create new ICS calendar
            calendar = Calendar()
            
            # Set calendar properties
            calendar.prodid = self.prodid
            calendar.version = "2.0"
            calendar.scale = "GREGORIAN"
            calendar.method = "PUBLISH"
            
            # Add events to calendar
            for event_data in events:
                try:
                    ics_event = self._create_ics_event(event_data, view_config)
                    if ics_event:
                        calendar.events.add(ics_event)
                except Exception as e:
                    logger.warning(f"Failed to create ICS event for {event_data.id}: {e}")
                    continue
            
            logger.info(f"Generated ICS calendar with {len(calendar.events)} events")
            
            # Return serialized calendar
            return str(calendar)
            
        except Exception as e:
            logger.error(f"Error generating ICS calendar: {e}")
            raise
    
    def _create_ics_event(
        self, 
        event_data: CalendarEvent, 
        view_config: ViewConfiguration
    ) -> Event:
        """
        Create an ICS Event from a CalendarEvent
        
        Args:
            event_data: CalendarEvent object
            view_config: View configuration
            
        Returns:
            ICS Event object
        """
        try:
            # Create new ICS event
            event = Event()
            
            # Set basic properties
            event.uid = f"{event_data.id}@notion-ics-server"
            # ics.py uses `name` for the event summary/title
            if view_config.title_prefix:
                event.name = f"{view_config.title_prefix}{event_data.title}"
            else:
                event.name = event_data.title
            
            # Set description
            if event_data.description:
                event.description = self._clean_description(event_data.description)
            
            # Set location
            if event_data.location:
                event.location = event_data.location
            
            # Set URL
            if event_data.url:
                event.url = event_data.url

            # Ensure Notion page link is present in description (and URL if absent)
            if event_data.notion_page_id:
                notion_link = f"https://www.notion.so/{event_data.notion_page_id.replace('-', '')}"
                link_line = f"Notion: {notion_link}"
                if getattr(event, "description", None):
                    event.description = f"{event.description}\n\n{link_line}"
                else:
                    event.description = link_line
                if not getattr(event, "url", None):
                    event.url = notion_link
            
            # Set timestamps
            if event_data.created_time:
                event.created = event_data.created_time
            
            if event_data.last_modified:
                event.last_modified = event_data.last_modified
            
            # Always set dtstamp to current time (required by ICS spec)
            event.dtstamp = datetime.now(pytz.UTC)
            
            # Set start and end times
            self._set_event_times(event, event_data, view_config)
            
            return event
            
        except Exception as e:
            logger.error(f"Error creating ICS event: {e}")
            raise
    
    def _set_event_times(
        self, 
        event: Event, 
        event_data: CalendarEvent, 
        view_config: ViewConfiguration
    ) -> None:
        """Set start and end times for the ICS event"""
        
        try:
            # Configure timezone
            timezone = pytz.timezone(view_config.timezone)
            
            if event_data.all_day:
                # All-day event - use date only
                start_date = event_data.start_time.date()
                event.begin = start_date
                
                if event_data.end_time:
                    end_date = event_data.end_time.date()
                    event.end = end_date
                else:
                    # Default to single day event
                    event.end = start_date
                
                # Mark as all-day
                event.make_all_day()
                
            else:
                # Timed event
                start_time = event_data.start_time
                
                # Ensure timezone is set
                if start_time.tzinfo is None:
                    start_time = timezone.localize(start_time)
                
                event.begin = start_time
                
                if event_data.end_time:
                    end_time = event_data.end_time
                    if end_time.tzinfo is None:
                        end_time = timezone.localize(end_time)
                    event.end = end_time
                else:
                    # Default to 1 hour duration
                    event.duration = {"hours": 1}
                    
        except Exception as e:
            logger.error(f"Error setting event times: {e}")
            # Set fallback times
            event.begin = event_data.start_time
            if event_data.end_time:
                event.end = event_data.end_time
    
    def _clean_description(self, description: str) -> str:
        """
        Clean and format description text for ICS
        
        Args:
            description: Raw description text
            
        Returns:
            Cleaned description text
        """
        if not description:
            return ""
        
        # Remove any problematic characters and normalize line endings
        cleaned = description.replace("\n", "\n").replace("\r", "")
        
        # Truncate if too long (some calendar clients have limits)
        max_length = 2000
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
        
        return cleaned
    
    def generate_calendar_with_metadata(
        self, 
        events: List[CalendarEvent], 
        calendar_name: str,
        view_config: ViewConfiguration,
        additional_metadata: Dict[str, Any] = None
    ) -> str:
        """
        Generate ICS calendar with additional metadata in description
        
        Args:
            events: List of CalendarEvent objects
            calendar_name: Name for the calendar
            view_config: View configuration
            additional_metadata: Additional metadata to include
            
        Returns:
            ICS calendar content as string
        """
        # Generate basic calendar
        calendar_content = self.generate_calendar(events, calendar_name, view_config)
        
        # Add metadata comment at the beginning
        metadata_lines = [
            f"# Calendar: {calendar_name}",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Events: {len(events)}",
            f"# Source: Notion Database {view_config.database_id}",
        ]
        
        if additional_metadata:
            for key, value in additional_metadata.items():
                metadata_lines.append(f"# {key}: {value}")
        
        metadata_comment = "\n".join(metadata_lines) + "\n"
        
        # Insert metadata after the BEGIN:VCALENDAR line
        lines = calendar_content.split("\n")
        if lines and lines[0].startswith("BEGIN:VCALENDAR"):
            lines.insert(1, metadata_comment)
            calendar_content = "\n".join(lines)
        
        return calendar_content
