"""
Notion API client for retrieving calendar events
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from dateutil import tz
import pytz

from notion_client import AsyncClient
from .models import CalendarEvent, ViewConfiguration
from .config import get_notion_token

logger = logging.getLogger(__name__)


class NotionCalendarClient:
    """Client for fetching calendar events from Notion databases"""
    
    def __init__(self, view_config: ViewConfiguration):
        """
        Initialize Notion client
        
        Args:
            view_config: Configuration for this calendar view
        """
        self.view_config = view_config
        self.notion = AsyncClient(auth=get_notion_token())
        
    async def get_calendar_events(self) -> List[CalendarEvent]:
        """
        Fetch calendar events from Notion database
        
        Returns:
            List of CalendarEvent objects
        """
        try:
            # Calculate date range for query (support unbounded sides)
            now = datetime.now(tz.UTC)
            start_date = (
                now - timedelta(days=self.view_config.query_days_back)
                if self.view_config.query_days_back is not None
                else None
            )
            end_date = (
                now + timedelta(days=self.view_config.query_days_forward)
                if self.view_config.query_days_forward is not None
                else None
            )

            # Build query filters
            filters = self._build_date_filter(start_date, end_date)

            # Add any additional filters from configuration
            if self.view_config.filters:
                additional_filters = self._normalize_filters(self.view_config.filters)
                if filters is None:
                    if len(additional_filters) == 1:
                        filters = additional_filters[0]
                    elif len(additional_filters) > 1:
                        filters = {"and": additional_filters}
                else:
                    if "and" in filters:
                        filters["and"].extend(additional_filters)
                    else:
                        filters = {"and": [filters] + additional_filters}
            
            # Query the database
            logger.info(f"Querying Notion database {self.view_config.database_id}")
            
            results = []
            has_more = True
            start_cursor = None
            
            while has_more:
                query_params = {
                    "database_id": self.view_config.database_id,
                    "page_size": 100
                }
                if filters:
                    query_params["filter"] = filters
                
                if start_cursor:
                    query_params["start_cursor"] = start_cursor
                
                response = await self.notion.databases.query(**query_params)
                
                results.extend(response["results"])
                has_more = response["has_more"]
                start_cursor = response.get("next_cursor")
            
            logger.info(f"Retrieved {len(results)} pages from Notion")
            
            # Convert to CalendarEvent objects
            events = []
            for page in results:
                try:
                    event = self._page_to_event(page)
                    if event:
                        events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to convert page to event: {e}")
                    continue
            
            logger.info(f"Converted {len(events)} pages to calendar events")
            return events
            
        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            raise
    
    def _build_date_filter(self, start_date: Optional[datetime], end_date: Optional[datetime]) -> Optional[Dict[str, Any]]:
        """Build date range filter for Notion query supporting unbounded ranges"""

        date_property = self.view_config.date_property

        if start_date and end_date:
            return {
                "and": [
                    {
                        "property": date_property,
                        "date": {"on_or_after": start_date.isoformat()},
                    },
                    {
                        "property": date_property,
                        "date": {"on_or_before": end_date.isoformat()},
                    },
                ]
            }
        if start_date and not end_date:
            return {
                "property": date_property,
                "date": {"on_or_after": start_date.isoformat()},
            }
        if end_date and not start_date:
            return {
                "property": date_property,
                "date": {"on_or_before": end_date.isoformat()},
            }
        # No bounds -> no date filter
        return None
    
    def _normalize_filters(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize additional filters from configuration"""
        # This is a simplified implementation
        # In a full implementation, you'd handle more complex filter structures
        if isinstance(filters, list):
            return filters
        elif isinstance(filters, dict):
            return [filters]
        else:
            return []
    
    def _page_to_event(self, page: Dict[str, Any]) -> Optional[CalendarEvent]:
        """
        Convert a Notion page to a CalendarEvent
        
        Args:
            page: Notion page object
            
        Returns:
            CalendarEvent or None if conversion fails
        """
        try:
            properties = page["properties"]
            
            # Extract date information
            date_prop = properties.get(self.view_config.date_property)
            if not date_prop or not date_prop.get("date"):
                logger.warning(f"Page {page['id']} missing date property")
                return None
            
            date_info = date_prop["date"]
            start_time = self._parse_notion_date(date_info["start"])
            end_time = None
            all_day = False
            
            if date_info.get("end"):
                end_time = self._parse_notion_date(date_info["end"])
            
            # Check if it's an all-day event (date only, no time)
            if "T" not in date_info["start"]:
                all_day = True
                # For all-day events, set end time to next day if not specified
                if not end_time:
                    end_time = start_time + timedelta(days=1)
            
            # Extract title
            title = self._extract_property_text(
                properties, 
                self.view_config.title_property, 
                "Untitled Event"
            )
            
            # Extract description
            description = None
            if self.view_config.description_property:
                description = self._extract_property_text(
                    properties, 
                    self.view_config.description_property
                )
            
            # Extract location
            location = None
            if self.view_config.location_property:
                location = self._extract_property_text(
                    properties, 
                    self.view_config.location_property
                )
            
            # Extract URL
            url = None
            if self.view_config.url_property:
                url_prop = properties.get(self.view_config.url_property)
                if url_prop and url_prop.get("url"):
                    url = url_prop["url"]
            
            # Create CalendarEvent
            event = CalendarEvent(
                id=page["id"].replace("-", ""),  # Remove hyphens for ICS compatibility
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                all_day=all_day,
                location=location,
                url=url,
                created_time=self._parse_notion_date(page["created_time"]),
                last_modified=self._parse_notion_date(page["last_edited_time"]),
                notion_page_id=page["id"],
                notion_properties=properties
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Error converting page to event: {e}")
            return None
    
    def _parse_notion_date(self, date_str: str) -> datetime:
        """Parse Notion date string to datetime object"""
        try:
            # Handle different date formats from Notion
            if "T" in date_str:
                # Date with time
                if date_str.endswith("Z"):
                    # UTC time
                    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                else:
                    # Parse with timezone info
                    return datetime.fromisoformat(date_str)
            else:
                # Date only - treat as all-day event in configured timezone
                date_obj = datetime.fromisoformat(date_str)
                timezone = pytz.timezone(self.view_config.timezone)
                return timezone.localize(date_obj)
        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {e}")
            # Return current time as fallback
            return datetime.now(tz.UTC)
    
    def _extract_property_text(
        self, 
        properties: Dict[str, Any], 
        property_name: str, 
        default: str = None
    ) -> Optional[str]:
        """Extract text content from a Notion property"""
        
        if not property_name or property_name not in properties:
            return default
        
        prop = properties[property_name]
        prop_type = prop.get("type")
        
        try:
            if prop_type == "title":
                title_array = prop.get("title", [])
                if title_array:
                    return "".join([item["plain_text"] for item in title_array])
            
            elif prop_type == "rich_text":
                rich_text_array = prop.get("rich_text", [])
                if rich_text_array:
                    return "".join([item["plain_text"] for item in rich_text_array])
            
            elif prop_type == "select":
                select_obj = prop.get("select")
                if select_obj:
                    return select_obj.get("name")
            
            elif prop_type == "multi_select":
                multi_select_array = prop.get("multi_select", [])
                if multi_select_array:
                    return ", ".join([item["name"] for item in multi_select_array])
            
            elif prop_type == "url":
                return prop.get("url")
            
            elif prop_type == "email":
                return prop.get("email")
            
            elif prop_type == "phone_number":
                return prop.get("phone_number")
            
            elif prop_type == "number":
                number_val = prop.get("number")
                if number_val is not None:
                    return str(number_val)
            
            elif prop_type == "checkbox":
                checkbox_val = prop.get("checkbox")
                if checkbox_val is not None:
                    return "Yes" if checkbox_val else "No"
            
        except Exception as e:
            logger.warning(f"Error extracting property '{property_name}': {e}")
        
        return default
