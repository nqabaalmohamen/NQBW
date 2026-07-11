from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.models import DatabaseFile
import uuid

@csrf_exempt
def upload_chunk_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    upload_id = request.POST.get('upload_id', '')
    chunk_index = int(request.POST.get('chunk_index', 0))
    total_chunks = int(request.POST.get('total_chunks', 1))
    file_name = request.POST.get('file_name', 'file.pdf')
    chunk = request.FILES.get('chunk')
    
    if not chunk:
        return JsonResponse({'error': 'No chunk provided'}, status=400)
    
    chunk_data = chunk.read()
    
    if chunk_index == 0 or not upload_id:
        # First chunk
        ext = file_name.split('.')[-1] if '.' in file_name else 'pdf'
        upload_id = f"{uuid.uuid4().hex}.{ext}"
        DatabaseFile.objects.create(name=upload_id, data=chunk_data)
    else:
        # Subsequent chunks: append data
        try:
            db_file = DatabaseFile.objects.get(name=upload_id)
            db_file.data = bytes(db_file.data) + chunk_data
            db_file.save()
        except DatabaseFile.DoesNotExist:
            return JsonResponse({'error': 'Upload ID not found'}, status=404)
            
    if chunk_index == total_chunks - 1:
        return JsonResponse({'status': 'done', 'upload_id': upload_id, 'url': f"/media/db/{upload_id}"})
        
    return JsonResponse({'status': 'ok', 'upload_id': upload_id})
