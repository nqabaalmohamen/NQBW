import sqlite3
import re
import os
import urllib.request
import urllib.error
import json as json_module

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


# ============================================================
# Static ngrok tunnel URL (permanent free domain)
# ============================================================
TUNNEL_URL = 'https://goldfish-banked-valley.ngrok-free.dev'


def check_internal_systems(request):
    """
    Public inquiry page — renders the HTML template.
    The actual search is done via the proxy_inquiry_api below (AJAX).
    """
    return render(request, 'inquiry.html', {})


@csrf_exempt
def proxy_inquiry_api(request):
    """
    SERVER-SIDE PROXY — The browser calls this Vercel endpoint,
    and this view forwards the request to the local ngrok tunnel.
    This completely eliminates all browser CORS / ngrok-warning issues.
    """
    query = request.GET.get('q', '').strip()
    sys_type = request.GET.get('sys', '').strip()
    num = request.GET.get('num', '').strip()

    if not query and not num:
        return JsonResponse({'success': False, 'error': 'رقم الاستعلام مطلوب'}, status=400,
                            json_dumps_params={'ensure_ascii': False})

    target_url = (
        f"{TUNNEL_URL}/api/unified-inquiry/"
        f"?q={urllib.parse.quote(query)}&sys={urllib.parse.quote(sys_type)}&num={urllib.parse.quote(num)}"
    )

    try:
        req = urllib.request.Request(
            target_url,
            headers={
                'ngrok-skip-browser-warning': 'true',
                'Bypass-Tunnel-Reminder': 'true',
                'User-Agent': 'NqabaProxy/1.0',
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode('utf-8')
            data = json_module.loads(raw)
            
            # Save successful response to cache
            if data.get('success'):
                from .models import CachedInquiry
                lookup_num = num if num else query
                CachedInquiry.objects.update_or_create(
                    system_type=sys_type,
                    inquiry_number=lookup_num,
                    defaults={'response_data': data}
                )
                
            return JsonResponse(data, status=200, json_dumps_params={'ensure_ascii': False})

    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode('utf-8')
            data = json_module.loads(err_body)
            return JsonResponse(data, status=e.code, json_dumps_params={'ensure_ascii': False})
        except Exception:
            pass # Fall through to cache
    except Exception as e:
        pass # Fall through to cache
        
    # Local system is offline or unreachable - Fallback to Cached Data
    from .models import CachedInquiry
    lookup_num = num if num else query
    
    # 1. Try exact match
    cached = CachedInquiry.objects.filter(system_type=sys_type, inquiry_number=lookup_num).first()
    
    # 2. Try partial match if not found
    if not cached:
        if sys_type == 'archive':
            cached = CachedInquiry.objects.filter(system_type=sys_type, inquiry_number__endswith=f"-{lookup_num}").first()
        elif sys_type == 'certificate':
            cached = CachedInquiry.objects.filter(system_type=sys_type, inquiry_number__startswith=f"{lookup_num}-").first()
        elif sys_type == 'complaint':
            cached = CachedInquiry.objects.filter(system_type=sys_type, inquiry_number__startswith=f"{lookup_num}/").first()
            
    if cached:
        return JsonResponse(cached.response_data, status=200, json_dumps_params={'ensure_ascii': False})
    
    return JsonResponse({'success': False, 'error': 'لم يتم العثور على بيانات بهذا الرقم.'}, status=200, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
def bulk_sync_api(request):
    """
    Receives all local DB data and caches it for offline use.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
        
    try:
        data = json_module.loads(request.body)
        records = data.get('records', [])
        
        from .models import CachedInquiry
        for rec in records:
            CachedInquiry.objects.update_or_create(
                system_type=rec['system_type'],
                inquiry_number=rec['inquiry_number'],
                defaults={'response_data': rec['response_data']}
            )
        return JsonResponse({'success': True, 'synced_count': len(records)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



# ---------------------------------------------------------------------------
# Import needed for URL building
# ---------------------------------------------------------------------------
import urllib.parse


# ============================================================
# Legacy direct-DB helpers (used only when running locally)
# ============================================================

def get_db_path(system_name):
    return getattr(settings, 'INTERNAL_SYSTEMS', {}).get(f'{system_name}_db')


def query_archive(tracking_number):
    db_path = get_db_path('archive')
    if not db_path or not os.path.exists(db_path):
        return None, "نظام الأرشيف غير متصل حالياً."

    if not tracking_number.upper().startswith('TRK-'):
        tracking_number = f"TRK-{tracking_number}"
    tracking_number = tracking_number.upper()

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tracking_number, title, current_status, client_name, missing_info, completion_note, updated_at
            FROM eams_transaction
            WHERE tracking_number = ? OR tracking_number LIKE ?
        """, (tracking_number, f"%{tracking_number}%"))
        row = cursor.fetchone()
        conn.close()

        if row:
            status_map = {
                'received': 'تم تسجيل المعاملة',
                'sent_to_dept': 'تم الإرسال للقسم المختص',
                'under_review': 'تحت المراجعة',
                'in_progress': 'جاري التنفيذ',
                'completed': 'تم الانتهاء'
            }
            return {
                'title': row['title'],
                'number': row['tracking_number'],
                'client': row['client_name'],
                'status': status_map.get(row['current_status'], row['current_status']),
                'is_completed': row['current_status'] == 'completed',
                'missing_info': row['missing_info'],
                'completion_note': row['completion_note'],
                'date': row['updated_at'][:10] if row['updated_at'] else ''
            }, None
        else:
            return None, "لم يتم العثور على معاملة بهذا الرقم."
    except Exception:
        return None, "خطأ في الاتصال بنظام الأرشيف."


def query_certificate(cert_id):
    db_path = get_db_path('certificates')
    if not db_path or not os.path.exists(db_path):
        return None, "نظام الشهادات غير متصل حالياً."

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, serial_number, recipient_name, status, issue_date
            FROM certificates_certificate
            WHERE id = ? OR serial_number = ?
        """, (cert_id, cert_id))
        row = cursor.fetchone()
        conn.close()

        if row:
            if row['status'] != 'published':
                return None, "هذه الشهادة ملغاة أو غير منشورة."
            return {
                'title': f"شهادة برقم {row['serial_number']}",
                'number': row['serial_number'],
                'client': row['recipient_name'],
                'status': 'معتمدة وموثقة',
                'is_completed': True,
                'date': row['issue_date']
            }, None
        else:
            return None, "لم يتم العثور على شهادة بهذا الرقم."
    except Exception:
        return None, "خطأ في الاتصال بنظام الشهادات."


def query_complaint(complaint_id):
    db_path = get_db_path('complaints')
    if not db_path or not os.path.exists(db_path):
        return None, "نظام الشؤون القانونية غير متصل حالياً."

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.complaint_id, c.subject, c.status, c.updated_at,
                   p.name as complainant_name, c.complainant_name as old_name
            FROM complaints_complaint c
            LEFT JOIN complaints_person p ON c.complainant_id = p.id
            WHERE c.complaint_id = ? OR c.complaint_id LIKE ?
        """, (complaint_id, f"%{complaint_id}%"))
        row = cursor.fetchone()
        conn.close()

        if row:
            status_map = {
                'ongoing': 'جارية',
                'archived': 'محفوظة',
                'escalated': 'تم التصعيد',
                'closed': 'منتهية'
            }
            client_name = (
                row['complainant_name'] if row['complainant_name']
                else (row['old_name'] if row['old_name'] else "غير متوفر")
            )
            return {
                'title': row['subject'],
                'number': row['complaint_id'],
                'client': client_name,
                'status': status_map.get(row['status'], row['status']),
                'is_completed': row['status'] in ['closed', 'archived'],
                'date': row['updated_at'][:10] if row['updated_at'] else ''
            }, None
        else:
            return None, "لم يتم العثور على شكوى بهذا الرقم."
    except Exception:
        return None, "خطأ في الاتصال بنظام الشؤون القانونية."
