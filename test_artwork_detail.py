#!/usr/bin/env python3

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aizasfineart.settings')
django.setup()

from django.test import Client
from django.urls import reverse

client = Client()

try:
    response = client.get('/art/wide-images-2025/')
    print('Status:', response.status_code)
    if response.status_code != 200:
        print('Error content:', response.content.decode()[:1000])
except Exception as e:
    print('Exception:', e)
    import traceback
    traceback.print_exc()