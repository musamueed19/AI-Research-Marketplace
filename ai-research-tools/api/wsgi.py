"""
Vercel serverless entry point.
Exposes Django WSGI application as `app` (required by Vercel Python runtime).
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()
