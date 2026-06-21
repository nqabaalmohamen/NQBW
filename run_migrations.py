import os
with open('.env.production.real', 'r') as f:
    for line in f:
        if line.startswith('DATABASE_URL='):
            db_url = line.strip().split('=', 1)[1].strip('\"\'')
            os.environ['DATABASE_URL'] = db_url

os.system('python manage.py migrate')
