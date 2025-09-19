#!/usr/bin/env python
"""Minimal Django test server to identify hanging issues"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aizasfineart.settings_minimal')
    
    # Configure minimal settings
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-key-for-debugging',
            ALLOWED_HOSTS=['*'],
            ROOT_URLCONF='aizasfineart.urls_minimal',
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
            ],
            MIDDLEWARE=[
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            STATIC_URL='/static/',
            USE_TZ=True,
        )
    
    django.setup()
    execute_from_command_line(['manage.py', 'runserver', '8001', '--noreload'])