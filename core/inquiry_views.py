import sqlite3
import re
from django.shortcuts import render
from django.conf import settings
import os

def check_internal_systems(request):
    """
    Public page to query status from the 3 internal systems.
    It reads directly from their SQLite databases.
    """
    query = request.GET.get('q', '').strip()
    result = None
    error = None
    system_type = None

    if query:
        # Detect which system to query based on format
        
        # 1. Archive: TRK-YYYY-N or YYYY-N (e.g. TRK-2026-1 or 2026-1)
        if re.match(r'^(TRK-)?\d{4}-\d+$', query, re.IGNORECASE):
            system_type = 'archive'
            result, error = query_archive(query)
            
        # 2. Certificate: UUID or Y-YYYY (e.g. 1-2026)
        elif re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', query, re.IGNORECASE) or re.match(r'^\d+-\d{4}$', query):
            system_type = 'certificate'
            result, error = query_certificate(query)
            
        # 3. Complaint: YYYY-NNN or just a number (e.g. 2026-001)
        elif re.match(r'^\d{4}-\d+$', query) or query.isdigit():
            system_type = 'complaint'
            result, error = query_complaint(query)
            
        else:
            error = "صيغة رقم الاستعلام غير معروفة. تأكد من الرقم وأعد المحاولة."

    return render(request, 'inquiry.html', {
        'query': query,
        'result': result,
        'error': error,
        'system_type': system_type
    })

def get_db_path(system_name):
    return getattr(settings, 'INTERNAL_SYSTEMS', {}).get(f'{system_name}_db')

def query_archive(tracking_number):
    db_path = get_db_path('archive')
    if not db_path or not os.path.exists(db_path):
        return None, "نظام الأرشيف غير متصل حالياً."
        
    # Format tracking number to TRK-YYYY-N if it's just YYYY-N
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
    except Exception as e:
        return None, f"خطأ في الاتصال بنظام الأرشيف."


def query_certificate(cert_id):
    db_path = get_db_path('certificates')
    if not db_path or not os.path.exists(db_path):
        return None, "نظام الشهادات غير متصل حالياً."
        
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check by UUID or serial_number
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
    except Exception as e:
        return None, f"خطأ في الاتصال بنظام الشهادات."


def query_complaint(complaint_id):
    db_path = get_db_path('complaints')
    if not db_path or not os.path.exists(db_path):
        return None, "نظام الشؤون القانونية غير متصل حالياً."
        
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check by complaint_id
        cursor.execute("""
            SELECT c.complaint_id, c.subject, c.status, c.updated_at, p.name as complainant_name, c.complainant_name as old_name
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
            
            # Fallback for old complaint structure if needed
            client_name = row['complainant_name'] if ('complainant_name' in row.keys() and row['complainant_name']) else (row['old_name'] if 'old_name' in row.keys() and row['old_name'] else "غير متوفر")

            
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
    except Exception as e:
        return None, f"خطأ في الاتصال بنظام الشؤون القانونية."
