import os
import django
from dotenv import load_dotenv

load_dotenv('.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
c = Client()

urls = [
    '/',
    '/archive/',
    '/certificates/',
    '/legal/',
]

for url in urls:
    print(f"Testing {url}")
    try:
        response = c.get(url)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Content snippet: {response.content[:200]}")
    except Exception as e:
        print(f"Exception: {e}")
