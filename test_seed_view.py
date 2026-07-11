import os
import django
from dotenv import load_dotenv

load_dotenv('.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
c = Client()

print("Testing seed view...")
response = c.get('/seed-library-secret/')
print(f"Status: {response.status_code}")
print(response.content.decode('utf-8'))
