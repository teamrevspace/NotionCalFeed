# Notion ICS Calendar Feed Server

A minimalist FastAPI application that serves dynamic ICS calendar feeds based on data from Notion calendar database views.

## Features

- 🔄 **Dynamic ICS Feeds**: Automatically generates ICS calendar files from Notion databases
- 📅 **Multiple Views**: Support for multiple calendar views with separate configurations
- ⚙️ **Flexible Configuration**: YAML-based configuration with environment variable overrides
- 🔗 **Standard Endpoints**: Each calendar view gets its own ICS URL endpoint
- 🕐 **Date Filtering**: Optional date ranges; full calendar by default
- 🌐 **Timezone Support**: Proper timezone handling for events
- 🔍 **Notion Filters**: Support for additional Notion API filters per view
- 📝 **Rich Properties**: Maps Notion properties to ICS event fields (title, description, location, URL)

## Quick Start

### 1. Prerequisites

- Python 3.8+
- A Notion account with API access
- Notion databases with date properties

### 2. Installation

```bash
# Clone or download this project
cd notion_ics_server

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new integration and copy the token
3. Share your calendar databases with the integration

### 4. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Notion token
NOTION_TOKEN=secret_your_actual_token_here
```

Edit `config.yaml` to configure your calendar views:

```yaml
calendar_views:
  personal:
    database_id: "your-notion-database-id"
    date_property: "Date"
    title_property: "Name"
    # ... other settings
```

### 5. Run the Server

```bash
# Development (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m app.main
```

### 6. Access Your Calendars

- View available feeds: `http://localhost:8000/`
- Get ICS feed: `http://localhost:8000/calendar/{view_name}.ics`
- Health check: `http://localhost:8000/health`

## Configuration

### Environment Variables

Required:
- `NOTION_TOKEN`: Your Notion integration token

Optional:
- `NOTION_VERSION`: Notion API version (default: "2022-06-28")
- `SERVER_HOST`: Server host (default: "0.0.0.0")
- `SERVER_PORT`: Server port (default: 8000)
- `SERVER_RELOAD`: Enable auto-reload (default: false)

### YAML Configuration

The `config.yaml` file defines your calendar views. Each view becomes an ICS endpoint.

#### Required Fields per View:
- `database_id`: Notion database UUID
- `date_property`: Name of the date property in your Notion database

#### Optional Fields per View:
- `title_property`: Property for event titles (default: "Name")
- `title_prefix`: String prefixed to every event name (e.g., "[Work] ")
- `description_property`: Property for event descriptions
- `location_property`: Property for event locations
- `url_property`: Property for event URLs
- `query_days_back`: Days to look back for events. If omitted, past is unbounded.
- `query_days_forward`: Days to look forward for events. If omitted, future is unbounded.
- `timezone`: Timezone for the calendar (default: "UTC")
- `filters`: Additional Notion API filters

#### Example Configuration:

```yaml
calendar_views:
  work:
    database_id: "abc123def-4567-890a-bcde-f123456789ab"
    date_property: "Event Date"
    title_property: "Title"
    title_prefix: "[Work] "
    description_property: "Notes"
    location_property: "Meeting Room"
    # Leave both unset for full calendar (no date bounds)
    # query_days_back: 7          # look back 7 days (future unbounded if forward unset)
    # query_days_forward: 180     # look forward 180 days (past unbounded if back unset)
    timezone: "America/New_York"
    filters:
      property: "Status"
      select:
        equals: "Confirmed"
```

## Notion Database Setup

### Required Properties

Your Notion database must have:
1. **Date property**: For event start/end times
2. **Title property**: For event names (usually the database title)

### Optional Properties

- **Rich text**: For descriptions
- **Select/Text**: For locations  
- **URL**: For event links
- **Checkbox**: For filtering (e.g., "Published")
- **Select**: For status filtering

### Database Sharing

Make sure to share your database with your Notion integration:
1. Open your database in Notion
2. Click "Share" → "Invite"
3. Select your integration

## API Endpoints

- `GET /` - List available calendar feeds
- `GET /calendar/{view_name}.ics` - Get ICS calendar for a specific view
- `GET /health` - Health check endpoint

## Usage Examples

### Subscribe in Calendar Apps

Most calendar applications can subscribe to ICS URLs:

**Google Calendar:**
1. In Google Calendar, click "+" next to "Other calendars"
2. Select "From URL"
3. Enter: `http://your-server:8000/calendar/{view_name}.ics`

**Apple Calendar:**
1. File → New Calendar Subscription
2. Enter the ICS URL

**Outlook:**
1. Add calendar → From internet
2. Enter the ICS URL

### Automation

You can automate calendar updates by:
- Running the server as a service
- Setting up webhooks (future feature)
- Using cron jobs to restart/refresh

## Development

### Project Structure

```
notion_ics_server/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration management
│   ├── models.py         # Pydantic models
│   ├── notion_client.py  # Notion API client
│   └── ics_generator.py  # ICS generation
├── config.yaml           # Calendar view configurations
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Adding New Features

1. **Custom Properties**: Extend `notion_client.py` to handle new Notion property types
2. **Filters**: Add more complex filtering logic in `ViewConfiguration`
3. **ICS Features**: Enhance `ics_generator.py` for features like recurrence rules
4. **Authentication**: Add API authentication if needed

### Testing

```bash
# Install development dependencies
pip install pytest pytest-asyncio httpx

# Run tests (add test files as needed)
pytest
```

## Troubleshooting

### Common Issues

1. **"Calendar view not found"**
   - Check view name in URL matches `config.yaml`
   - Verify configuration syntax

2. **"Failed to generate calendar feed"**
   - Check Notion token is valid
   - Verify database is shared with integration
   - Check database ID is correct

3. **Empty calendar**
   - If you set both `query_days_back` and `query_days_forward` very small, you may exclude events
   - Leave them unset to include the full calendar history and future
   - Verify date property name
   - Check additional filters

4. **Invalid dates**
   - Ensure date property contains valid dates
   - Check timezone configuration

### Debug Mode

Set environment variable for more detailed logs:
```bash
export LOG_LEVEL=DEBUG
```

### Notion API Limits

- Rate limit: 3 requests per second
- The server automatically handles pagination
- Large databases may take time to sync

## License

This project is released under the MIT License. Feel free to use and modify as needed.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Notion API documentation
3. Open an issue with configuration details (remove sensitive tokens)

---

**Note**: This is a minimalist implementation focused on core functionality. For production use, consider adding authentication, caching, monitoring, and error handling enhancements.
