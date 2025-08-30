"""
Notion ICS Calendar Feed Server

A FastAPI application that serves dynamic ICS calendar feeds
based on data from Notion calendar database views.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import logging
from typing import Dict, Any
from contextlib import asynccontextmanager

from .config import load_config
from .notion_client import NotionCalendarClient
from .ics_generator import ICSGenerator
from .models import ViewConfiguration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle handler replacing deprecated on_event."""
    global config, notion_clients, view_configs
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")

        # Initialize Notion clients for each configured view
        for view_name, view_config_dict in config["calendar_views"].items():
            vc = ViewConfiguration(**view_config_dict)
            view_configs[view_name] = vc
            notion_clients[view_name] = NotionCalendarClient(
                view_config=vc
            )
            logger.info(f"Initialized Notion client for view: {view_name}")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    # Yield control to the application (no special shutdown needed)
    yield

# Initialize FastAPI app using lifespan
app = FastAPI(
    title="Notion ICS Calendar Feed Server",
    description="Serves dynamic ICS calendar feeds from Notion database views",
    version="1.0.0",
    lifespan=lifespan
)

# Global variables for configuration and clients
config: Dict[str, Any] = {}
notion_clients: Dict[str, NotionCalendarClient] = {}
view_configs: Dict[str, ViewConfiguration] = {}
ics_generator = ICSGenerator()


 


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Notion ICS Calendar Feed Server",
        "available_feeds": list(config.get("calendar_views", {}).keys()),
        "endpoints": {
            "calendar_feed": "/calendar/{view_name}.ics",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "views_configured": len(notion_clients)}


@app.get("/calendar/{view_name}.ics")
async def get_calendar_feed(view_name: str):
    """
    Get ICS calendar feed for a specific Notion database view
    
    Args:
        view_name: Name of the configured calendar view
        
    Returns:
        ICS calendar data as plain text
    """
    if view_name not in notion_clients:
        raise HTTPException(
            status_code=404, 
            detail=f"Calendar view '{view_name}' not found"
        )
    
    try:
        # Get calendar events from Notion
        notion_client = notion_clients[view_name]
        events = await notion_client.get_calendar_events()
        
        # Generate ICS calendar
        view_config = view_configs[view_name]
        ics_content = ics_generator.generate_calendar(
            events=events,
            calendar_name=view_name,
            view_config=view_config
        )
        
        logger.info(f"Generated ICS feed for '{view_name}' with {len(events)} events")
        return Response(content=ics_content, media_type="text/calendar")
        
    except Exception as e:
        logger.error(f"Error generating calendar feed for '{view_name}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate calendar feed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
