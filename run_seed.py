import os
import django
from dotenv import load_dotenv

load_dotenv('.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.views import seed_library_view
from django.http import HttpRequest

request = HttpRequest()
response = seed_library_view(request)
with open('seed_result.txt', 'wb') as f:
    f.write(response.content)
