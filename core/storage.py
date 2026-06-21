import os
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
import uuid

@deconstructible
class DatabaseStorage(Storage):
    def _save(self, name, content):
        from core.models import DatabaseFile
        file_data = content.read()
        
        # Ensure name is unique and clean
        ext = name.split('.')[-1] if '.' in name else ''
        new_name = f"{uuid.uuid4().hex}.{ext}"
        
        DatabaseFile.objects.create(
            name=new_name,
            data=file_data
        )
        return new_name

    def _open(self, name, mode='rb'):
        from core.models import DatabaseFile
        try:
            db_file = DatabaseFile.objects.get(name=name)
            return ContentFile(db_file.data)
        except DatabaseFile.DoesNotExist:
            return ContentFile(b'')

    def exists(self, name):
        from core.models import DatabaseFile
        return DatabaseFile.objects.filter(name=name).exists()

    def url(self, name):
        return f"/media/db/{name}"

    def size(self, name):
        from core.models import DatabaseFile
        try:
            return len(DatabaseFile.objects.get(name=name).data)
        except DatabaseFile.DoesNotExist:
            return 0
