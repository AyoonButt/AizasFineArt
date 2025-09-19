#!/usr/bin/env python3
"""Simple test to see if Django can start without problematic model access"""
import os
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.http import HttpResponse
from django.urls import path

def simple_view(request):
    return HttpResponse("Test server working - no model access")

# Minimal URL patterns
urlpatterns = [
    path('', simple_view),
]

# Configure Django with current project settings but minimal middleware
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aizasfineart.settings')
    django.setup()
    
    # Override URLs to bypass problematic views
    settings.ROOT_URLCONF = __name__
    
    print("Starting test server...")
    execute_from_command_line(['manage.py', 'runserver', '8001', '--noreload'])