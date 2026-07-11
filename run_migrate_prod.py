import os
import django
from dotenv import load_dotenv
import subprocess

load_dotenv('.env')

env = os.environ.copy()
subprocess.run(['python', 'manage.py', 'migrate'], env=env)
