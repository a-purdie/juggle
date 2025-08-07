"""Application configuration and settings."""

import os
import dash_mantine_components as dmc


# External stylesheets
EXTERNAL_STYLESHEETS = [
    "https://fonts.googleapis.com/css2?family=Chonburi&display=swap",
    "assets/bootstrap.css",
    "assets/fontawesome/css/fontawesome.css",
    "assets/fontawesome/css/solid.css",
    "assets/custom.css",
    "assets/table-styles.css",
    "assets/responsive.css",
    dmc.styles.ALL,
    dmc.styles.DATES
]

# App configuration
APP_CONFIG = {
    'suppress_callback_exceptions': True,
    'title': 'indentured.services - Debt Calculator',
    'react_version': '18.2.0'
}

# Security headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.plot.ly https://fonts.googleapis.com https://api.iconify.design https://code.iconify.design; "
        "connect-src 'self' https://api.iconify.design https://api.simplesvg.com https://api.unisvg.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' data: https://fonts.gstatic.com https://fonts.googleapis.com; "
        "img-src 'self' data: https: https://api.iconify.design;"
    )
}

# Runtime configuration
def get_runtime_config():
    """Get runtime configuration based on environment."""
    is_production = (
        os.environ.get('GAE_ENV', '').startswith('standard') or 
        os.environ.get('K_SERVICE') is not None
    )
    
    if is_production:
        return {
            'debug': False,
            'port': int(os.environ.get('PORT', 8080)),
            'host': '0.0.0.0'
        }
    else:
        return {
            'debug': True,
            'port': 8050,
            'host': '0.0.0.0'
        }