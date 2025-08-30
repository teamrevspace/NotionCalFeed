#!/usr/bin/env python3
"""
Example usage of the Notion ICS Calendar Feed Server components

This script demonstrates how to use the individual components
outside of the FastAPI server context.
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.models import ViewConfiguration
from app.notion_client import NotionCalendarClient
from app.ics_generator import ICSGenerator


async def example_usage():
    """Example of how to use the components directly"""
    
    # Example configuration for a calendar view
    view_config = ViewConfiguration(
        database_id="your-database-id-here",
        date_property="Date",
        title_property="Name",
        description_property="Description",
        location_property="Location",
        query_days_back=30,
        query_days_forward=365,
        timezone="America/New_York"
    )
    
    try:
        print("Initializing Notion client...")
        notion_client = NotionCalendarClient(view_config)
        
        print("Fetching calendar events...")
        events = await notion_client.get_calendar_events()
        print(f"Retrieved {len(events)} events")
        
        if events:
            print("\nSample event:")
            sample_event = events[0]
            print(f"  Title: {sample_event.title}")
            print(f"  Start: {sample_event.start_time}")
            print(f"  End: {sample_event.end_time}")
            print(f"  All day: {sample_event.all_day}")
            
        print("\nGenerating ICS calendar...")
        ics_generator = ICSGenerator()
        ics_content = ics_generator.generate_calendar(
            events=events,
            calendar_name="Example Calendar",
            view_config=view_config
        )
        
        print(f"Generated ICS content ({len(ics_content)} characters)")
        
        # Optionally save to file
        with open("example_calendar.ics", "w") as f:
            f.write(ics_content)
        print("Saved to example_calendar.ics")
        
        # Show first few lines of ICS content
        print("\nFirst 10 lines of ICS content:")
        for i, line in enumerate(ics_content.split("\n")[:10]):
            print(f"  {line}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure to:")
        print("1. Set NOTION_TOKEN in your .env file")
        print("2. Replace 'your-database-id-here' with a real database ID")
        print("3. Share the database with your Notion integration")


def main():
    """Run the example"""
    print("Notion ICS Calendar Feed Server - Example Usage")
    print("=" * 50)
    
    # Check if token is set
    if not os.getenv("NOTION_TOKEN"):
        print("Error: NOTION_TOKEN environment variable not set")
        print("Please create a .env file with your Notion token")
        return
    
    # Run async example
    asyncio.run(example_usage())


if __name__ == "__main__":
    main()
