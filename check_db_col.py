import os
import django

with open('.env.production.real', 'r') as f:
    for line in f:
        if line.startswith('DATABASE_URL='):
            db_url = line.strip().split('=', 1)[1].strip('\"\'')
            os.environ['DATABASE_URL'] = db_url

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT slider_style FROM core_sitesettings;')
        print("Success:", cursor.fetchall())
except Exception as e:
    print("Error:", e)
