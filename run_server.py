#!/usr/bin/env python3
"""
Startup script for Notion ICS Calendar Feed Server
"""

import os
import sys
import uvicorn
from pathlib import Path

from app.config import get_server_config

def main():
    """Run the server with configuration from environment/config"""
    try:
        server_config = get_server_config()
        
        print(f"Starting Notion ICS Calendar Feed Server...")
        print(f"Host: {server_config['host']}")
        print(f"Port: {server_config['port']}")
        print(f"Reload: {server_config['reload']}")
        print()
        print("Available endpoints will be:")
        print(f"  - http://{server_config['host']}:{server_config['port']}/")
        print(f"  - http://{server_config['host']}:{server_config['port']}/health")
        print(f"  - http://{server_config['host']}:{server_config['port']}/calendar/{{view_name}}.ics")
        print()
        
        uvicorn.run(
            "app.main:app",
            host=server_config["host"],
            port=server_config["port"],
            reload=server_config["reload"]
        )
        
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
