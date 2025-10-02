"""
WSGI config for savannah_microservice project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'savannah_microservice.settings')

application = get_wsgi_application()
