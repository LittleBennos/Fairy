"""
Django-Axes configuration for brute force protection.
Implements 2025 best practices for authentication security.
"""

from datetime import timedelta

# Axes configuration for brute force protection
AXES_ENABLED = True

# Lock out after 3 failed attempts
AXES_FAILURE_LIMIT = 3

# Lock out for 30 minutes
AXES_COOLOFF_TIME = timedelta(minutes=30)

# Lock based on combination of username and IP
AXES_LOCKOUT_PARAMETERS = [
    ["username", "ip_address"],  # Lock specific username from specific IP
    ["ip_address"],  # Also lock IP after too many attempts
]

# Track login attempts by username and IP
AXES_USERNAME_FORM_FIELD = "username"

# Lock out GET requests too (prevent form manipulation)
AXES_LOCK_OUT_AT_FAILURE = True

# Custom lockout response
AXES_LOCKOUT_TEMPLATE = None  # Use JSON response instead
AXES_LOCKOUT_URL = None

# Reset attempts on successful login
AXES_RESET_ON_SUCCESS = True

# Enable logging
AXES_VERBOSE = True

# Whitelist localhost for development (remove in production)
AXES_NEVER_LOCKOUT_WHITELIST = False  # Set to True only in dev
AXES_IP_WHITELIST = []  # Add trusted IPs if needed

# Track all login attempts for audit
AXES_ENABLE_ACCESS_FAILURE_LOG = True

# Additional security settings
AXES_SENSITIVE_PARAMETERS = ["password", "token", "secret"]  # Don't log these

# Cache configuration for better performance
AXES_CACHE = 'default'

# Handler for additional custom logic
AXES_LOCKOUT_CALLABLE = None  # Can add custom function for notifications

# Client IP detection (replaces deprecated settings)
AXES_IPWARE_PROXY_COUNT = 1
AXES_IPWARE_META_PRECEDENCE_ORDER = [
    'HTTP_X_FORWARDED_FOR',
    'REMOTE_ADDR',
]