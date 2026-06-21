import os, django
with open('.env.production.real', 'r') as f:
    for line in f:
        if line.startswith('DATABASE_URL='):
            os.environ['DATABASE_URL'] = line.strip().split('=', 1)[1].strip('\"\'')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT count(*) FROM core_databasefile;')
        print(cursor.fetchone())
except Exception as e:
    print('Exception:', e)
