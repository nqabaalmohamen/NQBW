import os
import django
from dotenv import load_dotenv

load_dotenv('.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
c = Client()

urls = [
    '/library/journals/',
    '/library/legislations/',
    '/library/books/',
    '/library/contracts/',
]

for url in urls:
    print(f"Testing {url}")
    try:
        response = c.get(url)
        print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Exception: {e}")

