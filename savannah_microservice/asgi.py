"""
ASGI config for savannah_microservice project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'savannah_microservice.settings')

application = get_asgi_application()
