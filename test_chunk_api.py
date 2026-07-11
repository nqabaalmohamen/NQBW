import os
import django
from dotenv import load_dotenv

load_dotenv('.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
c = Client()

print("Testing chunk upload API...")

# Chunk 1
with open('test_chunk1.txt', 'wb') as f:
    f.write(b'hello '*1000)

with open('test_chunk1.txt', 'rb') as f:
    r = c.post('/api/upload-chunk/', {
        'chunk_index': 0,
        'total_chunks': 2,
        'file_name': 'test.txt',
        'chunk': f
    })
    
print(r.json())
upload_id = r.json()['upload_id']

# Chunk 2
with open('test_chunk2.txt', 'wb') as f:
    f.write(b'world '*1000)

with open('test_chunk2.txt', 'rb') as f:
    r2 = c.post('/api/upload-chunk/', {
        'upload_id': upload_id,
        'chunk_index': 1,
        'total_chunks': 2,
        'file_name': 'test.txt',
        'chunk': f
    })
    
print(r2.json())

from core.models import DatabaseFile
db_file = DatabaseFile.objects.get(name=upload_id)
print("Total size:", len(db_file.data))
