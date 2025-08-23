#!/usr/bin/env python3
"""
Configuration Module
Application settings and constants
"""

import os
from pathlib import Path

# Application Information
APP_NAME = "Roblox Community Analyzer"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Community Tools"
APP_DESCRIPTION = "Analyze Roblox communities for wealth and Discord connections"

# GUI Settings
DEFAULT_WINDOW_SIZE = (1200, 800)
MIN_WINDOW_SIZE = (1000, 700)
DEFAULT_THEME = "dark"

# API Settings
ROBLOX_BASE_URL = "https://www.roblox.com"
ROBLOX_API_BASE = "https://api.roblox.com"
ROBLOX_GROUPS_API = "https://groups.roblox.com/v1"
ROBLOX_USERS_API = "https://users.roblox.com/v1"
ROBLOX_INVENTORY_API = "https://inventory.roblox.com/v1"
ROBLOX_ECONOMY_API = "https://economy.roblox.com/v1"

DISCORD_API_BASE = "https://discord.com/api/v9"

# Rate Limiting
DEFAULT_RATE_LIMIT = 0.5  # seconds between requests
MAX_RETRIES = 3
TIMEOUT_SECONDS = 10

# Analysis Limits
MAX_COMMUNITY_MEMBERS = 1000  # Limit for performance
MAX_WEALTHY_USERS_FOR_DISCORD = 20  # Top users to check for Discord
MAX_LIMITEDS_PER_USER = 500  # Limit inventory checks

# File Paths
APP_DATA_DIR = Path.home() / "AppData" / "Local" / "RobloxCommunityAnalyzer"
CACHE_DIR = APP_DATA_DIR / "cache"
LOGS_DIR = APP_DATA_DIR / "logs"
EXPORTS_DIR = APP_DATA_DIR / "exports"

# Create directories if they don't exist
for directory in [APP_DATA_DIR, CACHE_DIR, LOGS_DIR, EXPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Headers for requests
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Discord patterns for finding invite links
DISCORD_INVITE_PATTERNS = [
    r'discord\.gg/([a-zA-Z0-9]+)',
    r'discord\.com/invite/([a-zA-Z0-9]+)',
    r'discordapp\.com/invite/([a-zA-Z0-9]+)',
]

# Common Discord username patterns in Roblox profiles
DISCORD_USERNAME_PATTERNS = [
    r'discord[:\s]*([a-zA-Z0-9_]{2,32}#\d{4})',  # Discord tag with discriminator
    r'discord[:\s]*([a-zA-Z0-9_]{2,32})',        # Discord username
    r'@([a-zA-Z0-9_]{2,32})',                    # @username format
    r'dc[:\s]*([a-zA-Z0-9_]{2,32})',            # dc: username
    r'disc[:\s]*([a-zA-Z0-9_]{2,32})',          # disc: username
]

# Error Messages
ERROR_MESSAGES = {
    'invalid_cookie': 'Invalid Roblox cookie. Please check your .ROBLOSECURITY cookie.',
    'invalid_url': 'Invalid community URL format. Please use the correct Roblox community URL.',
    'community_not_found': 'Community not found. Please check the URL and your access permissions.',
    'rate_limited': 'API rate limit exceeded. Please wait and try again.',
    'network_error': 'Network error. Please check your internet connection.',
    'auth_failed': 'Authentication failed. Please check your Roblox cookie.',
    'permission_denied': 'Permission denied. You may not have access to this community.',
}

# Success Messages
SUCCESS_MESSAGES = {
    'analysis_complete': 'Community analysis completed successfully!',
    'export_complete': 'Results exported successfully!',
    'auth_success': 'Authentication successful!',
}

# UI Colors (for custom themes)
COLORS = {
    'dark': {
        'primary': '#3b82f6',
        'primary_hover': '#2563eb',
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'background': '#1a1a1a',
        'surface': '#2b2b2b',
        'text': '#ffffff',
        'text_secondary': '#9ca3af',
    },
    'light': {
        'primary': '#3b82f6',
        'primary_hover': '#2563eb',
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'background': '#ffffff',
        'surface': '#f8fafc',
        'text': '#1f2937',
        'text_secondary': '#6b7280',
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': str(LOGS_DIR / 'app.log'),
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# Build Configuration (for PyInstaller)
BUILD_CONFIG = {
    'app_name': 'RobloxCommunityAnalyzer',
    'console': False,  # No console window
    'icon': None,  # Add icon file path if available
    'onefile': True,  # Single executable file
    'optimize': 2,  # Python optimization level
    'upx': True,  # UPX compression
}

# Feature Flags
FEATURES = {
    'enable_caching': True,
    'enable_discord_matching': True,
    'enable_export': True,
    'enable_rate_limiting': True,
    'enable_error_reporting': True,
    'enable_progress_tracking': True,
}

# Cache Settings
CACHE_SETTINGS = {
    'enable': FEATURES['enable_caching'],
    'ttl_seconds': 3600,  # 1 hour
    'max_size': 100,  # Maximum cached items
    'cleanup_interval': 1800,  # 30 minutes
}

def get_app_info():
    """Get application information"""
    return {
        'name': APP_NAME,
        'version': APP_VERSION,
        'author': APP_AUTHOR,
        'description': APP_DESCRIPTION,
    }

def get_api_endpoints():
    """Get API endpoint configuration"""
    return {
        'roblox_base': ROBLOX_BASE_URL,
        'roblox_api': ROBLOX_API_BASE,
        'groups': ROBLOX_GROUPS_API,
        'users': ROBLOX_USERS_API,
        'inventory': ROBLOX_INVENTORY_API,
        'economy': ROBLOX_ECONOMY_API,
        'discord': DISCORD_API_BASE,
    }

def get_rate_limits():
    """Get rate limiting configuration"""
    return {
        'default_delay': DEFAULT_RATE_LIMIT,
        'max_retries': MAX_RETRIES,
        'timeout': TIMEOUT_SECONDS,
    }

def get_analysis_limits():
    """Get analysis limitation settings"""
    return {
        'max_members': MAX_COMMUNITY_MEMBERS,
        'max_wealthy_for_discord': MAX_WEALTHY_USERS_FOR_DISCORD,
        'max_limiteds': MAX_LIMITEDS_PER_USER,
    }