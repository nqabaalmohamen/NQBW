import os
import django
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import LibraryJournal, LibraryLegislation, LibraryBook, LibraryContract
from datetime import date

def populate():
    print("Clearing old data...")
    LibraryJournal.objects.all().delete()
    LibraryLegislation.objects.all().delete()
    LibraryBook.objects.all().delete()
    LibraryContract.objects.all().delete()

    print("Populating LibraryJournals...")
    LibraryJournal.objects.create(
        title="المجلة القانونية لنقابة المحامين - العدد الأول",
        issue_number="1",
        description="العدد الأول من المجلة القانونية يناقش أهم التعديلات في قانون المرافعات الجديد وتأثيرها على سير الدعاوى.",
        publish_date=date(2025, 1, 15),
        is_active=True
    )
    LibraryJournal.objects.create(
        title="المجلة القانونية لنقابة المحامين - العدد الثاني",
        issue_number="2",
        description="يستعرض هذا العدد أحدث أحكام محكمة النقض في القضايا الجنائية وقضايا الأحوال الشخصية لعام 2025.",
        publish_date=date(2025, 6, 20),
        is_active=True
    )

    print("Populating LibraryLegislations...")
    LibraryLegislation.objects.create(
        title="قانون العقوبات المصري",
        category="law",
        number="58",
        year="1937",
        description="نص قانون العقوبات المصري رقم 58 لسنة 1937 وتعديلاته التي تشمل كافة الجرائم والعقوبات المقررة.",
        is_active=True
    )
    LibraryLegislation.objects.create(
        title="قانون الإجراءات الجنائية",
        category="law",
        number="150",
        year="1950",
        description="قانون الإجراءات الجنائية وتعديلاته الصادرة لتنظيم سير القضايا الجنائية أمام المحاكم المصرية.",
        is_active=True
    )
    LibraryLegislation.objects.create(
        title="حكم محكمة النقض في شأن الشفعة",
        category="ruling",
        number="1025",
        year="2021",
        description="مبدأ هام لمحكمة النقض يوضح شروط وضوابط الأخذ بالشفعة في العقارات المجاورة.",
        is_active=True
    )
    LibraryLegislation.objects.create(
        title="قانون العمل الجديد",
        category="law",
        number="12",
        year="2003",
        description="قانون العمل المصري وتعديلاته التي تنظم العلاقة بين العامل وصاحب العمل.",
        is_active=True
    )

    print("Populating LibraryBooks...")
    LibraryBook.objects.create(
        title="الوسيط في شرح القانون المدني",
        author="د. عبد الرزاق السنهوري",
        description="المرجع الشامل في شرح القانون المدني المصري، ويعتبر أهم موسوعة قانونية في العالم العربي.",
        is_active=True
    )
    LibraryBook.objects.create(
        title="موسوعة القضاء الإداري",
        author="المستشار / محمد طه",
        description="دراسة مفصلة في قضاء مجلس الدولة وإجراءات التقاضي أمام المحاكم الإدارية والتأديبية.",
        is_active=True
    )
    LibraryBook.objects.create(
        title="الدفوع الجنائية",
        author="د. محمود نجيب حسني",
        description="شرح تفصيلي للدفوع الجنائية الشكلية والموضوعية أمام المحاكم الجنائية.",
        is_active=True
    )

    print("Populating LibraryContracts...")
    LibraryContract.objects.create(
        title="نموذج عقد بيع ابتدائي لعقار",
        category="sale",
        description="نموذج صيغة عقد بيع ابتدائي لشقة سكنية أو عقار شامل كافة البنود القانونية للحفاظ على حقوق الطرفين.",
        is_active=True
    )
    LibraryContract.objects.create(
        title="نموذج عقد إيجار شقة قانون جديد",
        category="rent",
        description="صيغة عقد إيجار خاضع لأحكام القانون رقم 4 لسنة 1996 وتعديلاته.",
        is_active=True
    )
    LibraryContract.objects.create(
        title="نموذج عقد تأسيس شركة ذات مسئولية محدودة",
        category="company",
        description="نموذج استرشادي لإنشاء وتأسيس شركة ذات مسئولية محدودة وفقاً لقانون الشركات المصري.",
        is_active=True
    )
    LibraryContract.objects.create(
        title="مذكرة بدفاع في جنحة ضرب",
        category="criminal",
        description="صيغة مذكرة قانونية مقدمة لمحكمة الجنح تتضمن الدفوع القانونية في قضايا الضرب وإحداث العاهة.",
        is_active=True
    )

    print("Done!")

if __name__ == '__main__':
    populate()
