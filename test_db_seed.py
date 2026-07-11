import os
import django
from dotenv import load_dotenv

load_dotenv('.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.views import seed_library_view
from core.models import LibraryJournal, LibraryLegislation, LibraryBook, LibraryContract
from datetime import date
from django.db import connection

print("Check external_url type in DB:")
with connection.cursor() as cursor:
    cursor.execute("SELECT character_maximum_length FROM information_schema.columns WHERE table_name = 'core_libraryjournal' AND column_name = 'external_url'")
    row = cursor.fetchone()
    print("LibraryJournal:", row)
    
try:
    EL = 'https://egyls.com/'
    print("Trying Journal...")
    LibraryJournal.objects.create(title="مجلة المحاماة الإلكترونية - الإصدار الرابع عشر", issue_number="14",
        description="أصدر المركز الإعلامي لنقابة المحامين العدد الرابع عشر من مجلة المحاماة الإلكترونية - مارس 2024.",
        publish_date=date(2024, 4, 6), is_active=True,
        external_url=EL+'%d8%b7%d8%a7%d9%84%d8%b9-%d8%a7%d9%84%d8%a5%d8%b5%d8%af%d8%a7%d8%b1-%d8%a7%d9%84%d8%b1%d8%a7%d8%a8%d8%b9-%d8%b9%d8%b4%d8%b1-%d9%85%d9%86-%d9%85%d8%ac%d9%84%d8%a9-%d8%a7%d9%84%d9%85%d8%ad%d8%a7%d9%85/')
    print("Journal OK")
except Exception as e:
    print("Journal failed:", e)

try:
    print("Trying Legislation...")
    LibraryLegislation.objects.create(title="بوابة التشريعات والأحكام المصرية", category="law", number="", year="2021",
        description="بوابة شاملة تتيح الاطلاع على القوانين والأحكام الصادرة عن المحاكم المصرية والمحكمة الدستورية العليا.",
        external_url=EL+'%d8%a8%d9%88%d8%a7%d8%a8%d8%a9-%d8%a7%d9%84%d8%aa%d8%b4%d8%b1%d9%8a%d8%b9%d8%a7%d8%aa-%d9%88%d8%a7%d9%84%d8%a3%d8%ad%d9%83%d8%a7%d9%85-%d8%a7%d9%84%d9%85%d8%b5%d8%b1%d9%8a%d8%a9/', is_active=True)
    print("Legislation OK")
except Exception as e:
    print("Legislation failed:", e)

try:
    print("Trying Book...")
    LibraryBook.objects.create(title="المبادئ القانونية في الجرائم الاقتصادية - محكمة النقض",
        author="المكتب الفني لمحكمة النقض",
        description="كتاب يتضمن أهم المبادئ القانونية الصادرة عن محكمة النقض الدوائر الجنائية في الجرائم الاقتصادية.",
        external_url=EL+'%d8%b7%d8%a7%d9%84%d8%b9-%d9%83%d8%aa%d8%a8-%d8%a7%d9%84%d9%85%d8%a8%d8%a7%d8%af%d8%a6-%d8%a7%d9%84%d9%82%d8%a7%d9%86%d9%88%d9%86%d9%8a%d8%a9-%d8%a7%d9%84%d8%b5%d8%a7%d8%af%d8%b1%d8%a9-%d8%b9/', is_active=True)
    print("Book OK")
except Exception as e:
    print("Book failed:", e)

try:
    print("Trying Contract...")
    LibraryContract.objects.create(title="إدارة التصديق على العقود - نقابة المحامين", category="other",
        description="خدمة التصديق على العقود المقدمة من نقابة المحامين لإضفاء الشرعية القانونية على العقود.",
        external_url=EL+'service/%d8%a7%d9%84%d8%a5%d8%af%d8%a7%d8%b1%d8%a9-%d8%a7%d9%84%d8%b9%d8%a7%d9%85%d8%a9-%d9%84%d9%84%d8%aa%d8%b5%d8%af%d9%8a%d9%82-%d8%b9%d9%84%d9%89-%d8%a7%d9%84%d8%b9%d9%82%d9%88%d8%af-2/', is_active=True)
    print("Contract OK")
except Exception as e:
    print("Contract failed:", e)
