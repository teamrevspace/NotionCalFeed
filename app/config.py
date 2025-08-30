"""
Configuration management for Notion ICS Calendar Feed Server
"""

import os
import yaml
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file and environment variables
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Configuration dictionary
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Load YAML configuration
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"Configuration file '{config_path}' not found")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        raise
    
    # Override with environment variables
    config = _apply_env_overrides(config)
    
    # Validate configuration
    _validate_config(config)
    
    return config


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to configuration"""
    
    # Override Notion API settings
    if os.getenv("NOTION_TOKEN"):
        config["notion"]["api_token"] = os.getenv("NOTION_TOKEN")
    
    if os.getenv("NOTION_VERSION"):
        config["notion"]["api_version"] = os.getenv("NOTION_VERSION")
    
    # Override server settings
    if os.getenv("SERVER_HOST"):
        config.setdefault("server", {})["host"] = os.getenv("SERVER_HOST")
    
    if os.getenv("SERVER_PORT"):
        config.setdefault("server", {})["port"] = int(os.getenv("SERVER_PORT"))
    
    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """Validate required configuration settings"""
    
    # Check required sections
    required_sections = ["notion", "calendar_views"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Required configuration section '{section}' missing")
    
    # Check Notion API token
    if not config["notion"].get("api_token"):
        raise ValueError("Notion API token is required (set NOTION_TOKEN environment variable)")
    
    # Check calendar views
    if not config["calendar_views"]:
        raise ValueError("At least one calendar view must be configured")
    
    # Validate each calendar view
    for view_name, view_config in config["calendar_views"].items():
        _validate_view_config(view_name, view_config)


def _validate_view_config(view_name: str, view_config: Dict[str, Any]) -> None:
    """Validate a single calendar view configuration"""
    
    required_fields = ["database_id", "date_property"]
    for field in required_fields:
        if field not in view_config:
            raise ValueError(f"View '{view_name}': Required field '{field}' missing")
    
    # Validate date range settings (allow None for unbounded)
    days_back = view_config.get("query_days_back", None)
    days_forward = view_config.get("query_days_forward", None)

    if days_back is not None and (not isinstance(days_back, int) or days_back < 0):
        raise ValueError(f"View '{view_name}': 'query_days_back' must be a non-negative integer or omitted")

    if days_forward is not None and (not isinstance(days_forward, int) or days_forward < 0):
        raise ValueError(f"View '{view_name}': 'query_days_forward' must be a non-negative integer or omitted")


def get_notion_token() -> str:
    """Get Notion API token from environment"""
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise ValueError("NOTION_TOKEN environment variable is required")
    return token


def get_server_config() -> Dict[str, Any]:
    """Get server configuration"""
    return {
        "host": os.getenv("SERVER_HOST", "0.0.0.0"),
        "port": int(os.getenv("SERVER_PORT", "8000")),
        "reload": os.getenv("SERVER_RELOAD", "false").lower() == "true"
    }
