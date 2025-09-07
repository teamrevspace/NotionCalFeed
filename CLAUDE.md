# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python FastAPI application that serves dynamic ICS calendar feeds from Notion databases. It acts as a bridge between Notion calendar databases and standard calendar applications that can subscribe to ICS feeds.

## Architecture

The application follows a clean modular architecture:

- **FastAPI Web Server** (`app/main.py`): Main application with endpoints for serving ICS feeds
- **Configuration Management** (`app/config.py`): YAML-based configuration with environment variable overrides
- **Notion API Client** (`app/notion_client.py`): Handles communication with Notion API and event retrieval
- **ICS Generator** (`app/ics_generator.py`): Converts Notion events to ICS calendar format
- **Pydantic Models** (`app/models.py`): Type-safe data models for configuration and calendar events

## Common Development Commands

### Environment Setup
```bash
# Create virtual environment and install dependencies
make setup

# Install dependencies only
make install

# Run the server in development mode (auto-reload)
make dev

# Run in production mode
make run

# Run using convenience script
make run-script
```

### Testing
```bash
# Run tests (when test files are added)
pytest
```

### Development
```bash
# Clean up generated files
make clean

# Show available Make targets
make help
```

## Key Dependencies

- **FastAPI**: Web framework for the API server
- **Uvicorn**: ASGI server for running FastAPI
- **notion-client**: Official Notion API client
- **ics**: ICS calendar file generation library
- **Pydantic**: Data validation and serialization
- **PyYAML**: Configuration file parsing
- **python-dotenv**: Environment variable management

## Configuration

### Required Environment Variables
- `NOTION_TOKEN`: Your Notion integration token (required)

### Optional Environment Variables
- `SERVER_HOST`: Server host (default: "0.0.0.0")
- `SERVER_PORT`: Server port (default: 8000)
- `SERVER_RELOAD`: Enable auto-reload (default: false)
- `NOTION_VERSION`: Notion API version (default: "2022-06-28")

### Configuration File
The application uses `config.yaml` for defining calendar views. Each view becomes an ICS endpoint at `/calendar/{view_name}.ics`. Key configuration sections:

- `notion`: API token and version settings
- `calendar_views`: Dictionary of calendar configurations
- `server`: Server settings (optional, overridden by env vars)

### Calendar View Configuration
Each view requires:
- `database_id`: Notion database UUID
- `date_property`: Name of the date property in the database

Optional view settings:
- `title_property`: Property for event titles (default: "Name")
- `description_property`: Property for event descriptions
- `location_property`: Property for event locations
- `url_property`: Property for event URLs
- `title_prefix`: String prepended to every event title
- `query_days_back`/`query_days_forward`: Date range filtering
- `timezone`: Calendar timezone (default: "UTC")
- `filters`: Additional Notion API filters

## API Endpoints

- `GET /`: Lists available calendar feeds
- `GET /health`: Health check endpoint
- `GET /calendar/{view_name}.ics`: Returns ICS calendar feed for a specific view

## Development Patterns

### Adding New Calendar Views
1. Add configuration to `config.yaml` under `calendar_views`
2. Ensure the Notion database is shared with your integration
3. Test the endpoint at `/calendar/{view_name}.ics`

### Error Handling
- The application uses FastAPI's exception handling
- Configuration errors are caught during startup
- API errors return appropriate HTTP status codes with JSON error responses

### Logging
- Uses Python's standard logging module
- Log level can be controlled via `LOG_LEVEL` environment variable
- Logs include application startup, configuration loading, and request handling

### Date/Time Handling
- All datetime objects use timezone-aware datetime objects
- Supports flexible date range queries (can be bounded or unbounded on either side)
- Timezone conversion is handled for ICS output

## Testing Strategy

The application is designed for easy testing:
- Modular components can be tested in isolation
- Configuration loading has validation
- Notion client can be mocked for unit tests
- ICS generator outputs can be validated

## Deployment

The application can be deployed as:
- Standalone Python process using `run_server.py`
- Containerized application (Dockerfile not included but straightforward to add)
- Background service using systemd or similar

## Security Considerations

- Notion API token is handled securely via environment variables
- No authentication on ICS endpoints (suitable for personal use)
- Consider adding API authentication for production use
- Configuration validation prevents injection attacks