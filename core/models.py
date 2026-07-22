from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPE = [
        ('citizen', 'مواطن'),
        ('lawyer', 'محامٍ'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE, default='citizen')
    phone = models.CharField(max_length=20, blank=True)
    national_id = models.CharField(max_length=14, blank=True)
    syndicate_id = models.CharField(max_length=10, blank=True, null=True, verbose_name="رقم القيد")
    plain_password = models.CharField(max_length=255, blank=True, verbose_name="كلمة المرور")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_user_type_display()}"


class MedicalExam(models.Model):
    title = models.CharField(max_length=500, verbose_name="عنوان الكشف")
    exam_date = models.DateField(verbose_name="تاريخ الكشف")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "كشف طبي"
        verbose_name_plural = "الكشوفات الطبية"
        ordering = ['-exam_date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.exam_date}"


class MedicalExamImage(models.Model):
    exam = models.ForeignKey(MedicalExam, on_delete=models.CASCADE, related_name='images', verbose_name="الكشف")
    image = models.ImageField(upload_to='medical_exams/', verbose_name="صورة الكشف")
    order = models.IntegerField(default=0, verbose_name="الترتيب")

    class Meta:
        verbose_name = "صورة كشف"
        verbose_name_plural = "صور الكشوفات"
        ordering = ['order']

    def __str__(self):
        return f"صورة - {self.exam.title}"


class InstituteLecture(models.Model):
    title = models.CharField(max_length=500, verbose_name="عنوان الخبر")
    description = models.TextField(verbose_name="نص الخبر", blank=True)
    image = models.ImageField(upload_to='institute_news/', verbose_name="صورة الخبر", blank=True, null=True)
    lecture_date = models.DateField(verbose_name="تاريخ الخبر", blank=True, null=True)
    video_link = models.URLField(verbose_name="رابط إضافي", blank=True)
    file = models.FileField(upload_to='institute_files/', verbose_name="ملف مرفق", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "محاضرة معهد"
        verbose_name_plural = "محاضرات المعهد"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class News(models.Model):
    CATEGORY_CHOICES = [
        ('news', 'خبر'),
        ('decision', 'قرار'),
        ('announcement', 'إعلان'),
        ('event', 'فعالية'),
    ]
    title = models.CharField(max_length=255, verbose_name="العنوان")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='news', verbose_name="التصنيف")
    content = models.TextField(verbose_name="المحتوى")
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="صورة الخبر")
    is_published = models.BooleanField(default=True, verbose_name="منشور")
    in_slider = models.BooleanField(default=True, verbose_name="عرض في السلايدر الرئيسي")
    date = models.DateField(auto_now_add=True, verbose_name="تاريخ النشر")
    views_count = models.PositiveIntegerField(default=0, verbose_name="عدد المشاهدات")

    class Meta:
        verbose_name = "خبر"
        verbose_name_plural = "الأخبار والقرارات"
        ordering = ['-date']

    def __str__(self):
        return self.title


class NewsImage(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='images', verbose_name="الخبر")
    image = models.ImageField(upload_to='news_gallery/', verbose_name="صورة إضافية")
    order = models.IntegerField(default=0, verbose_name="الترتيب")

    class Meta:
        verbose_name = "صورة إضافية للخبر"
        verbose_name_plural = "صور الخبر الإضافية"
        ordering = ['order']

    def __str__(self):
        return f"صورة - {self.news.title}"


class CouncilMember(models.Model):
    ROLE_CHOICES = [
        ('president', 'نقيب المحامين'),
        ('vice', 'وكلاء النقابة'),
        ('general_sec', 'الأمانة العامة'),
        ('treasurer', 'أمانة الصندوق'),
        ('youth', 'عضو الشباب'),
        ('member', 'أعضاء المجلس'),
    ]
    name = models.CharField(max_length=255, verbose_name="الاسم")
    position = models.CharField(max_length=100, verbose_name="المنصب (اللقب الظاهر)")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name="التصنيف / المجموعة")
    image = models.ImageField(upload_to='council/', blank=True, null=True, verbose_name="الصورة")
    order = models.IntegerField(default=0, verbose_name="الترتيب")

    class Meta:
        verbose_name = "عضو مجلس"
        verbose_name_plural = "مجلس النقابة"
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - {self.position}"


class Service(models.Model):
    TARGET_CHOICES = [
        ('all', 'الجميع'),
        ('lawyer', 'المحامون فقط'),
        ('citizen', 'المواطنون فقط'),
    ]
    title = models.CharField(max_length=200, verbose_name="اسم الخدمة")
    description = models.TextField(verbose_name="وصف الخدمة")
    icon = models.CharField(max_length=100, default='fa-solid fa-circle-check', verbose_name="أيقونة FontAwesome")
    url = models.CharField(max_length=200, blank=True, verbose_name="رابط الخدمة")
    target = models.CharField(max_length=20, choices=TARGET_CHOICES, default='all', verbose_name="الفئة المستهدفة")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "خدمة"
        verbose_name_plural = "الخدمات الإلكترونية"
        ordering = ['order']

    def __str__(self):
        return self.title


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('new', 'جديدة'),
        ('in_progress', 'قيد المراجعة'),
        ('resolved', 'تم الحل'),
    ]
    TYPE_CHOICES = [
        ('inquiry', 'استفسار'),
        ('suggestion', 'مقترح تطوير'),
    ]
    complaint_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='inquiry', verbose_name="نوع الطلب")
    name = models.CharField(max_length=255, verbose_name="الاسم")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")
    subject = models.CharField(max_length=255, verbose_name="الموضوع")
    message = models.TextField(verbose_name="التفاصيل")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="الحالة")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "استفسار/مقترح"
        verbose_name_plural = "الاستفسارات ومقترحات التطوير"
        ordering = ['-created_at']

    def __str__(self):
        return self.subject


class FAQ(models.Model):
    question = models.CharField(max_length=500, verbose_name="السؤال")
    answer = models.TextField(verbose_name="الإجابة")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "سؤال شائع"
        verbose_name_plural = "الأسئلة الشائعة"
        ordering = ['order']

    def __str__(self):
        return self.question

class SiteSettings(models.Model):
    slider_speed = models.IntegerField(default=4000, verbose_name="سرعة السليدر (بالميلي ثانية)")
    institute_registration_link = models.URLField(verbose_name="رابط التقديم في معهد المحاماة (مثل Google Form)", blank=True, null=True)
    is_institute_open = models.BooleanField(default=False, verbose_name="فتح التسجيل لمعهد المحاماة")
    
    # Inquiry Settings
    is_inquiry_open = models.BooleanField(default=True, verbose_name="تفعيل قسم الاستعلام في الموقع")
    
    is_under_maintenance = models.BooleanField(default=False, verbose_name="وضع الصيانة (قيد التطوير)")
    maintenance_end_date = models.DateTimeField(blank=True, null=True, verbose_name="موعد انتهاء التطوير (للعد التنازلي)")
    total_visits = models.PositiveIntegerField(default=0, verbose_name="إجمالي زيارات الموقع")
    
    class Meta:
        verbose_name = "إعدادات الموقع"
        verbose_name_plural = "إعدادات الموقع"

    def __str__(self):
        return "إعدادات الموقع العامة"

    @classmethod
    def get_settings(cls):
        try:
            settings, created = cls.objects.get_or_create(pk=1)
            return settings
        except Exception:
            # Fallback: return unsaved default instance (migration may not be applied yet)
            return cls()

    @classmethod
    def get_settings_safe(cls):
        """Returns settings with is_inquiry_open=True if field doesn't exist yet."""
        try:
            obj = cls.objects.filter(pk=1).values().first()
            if obj:
                s = cls()
                for k, v in obj.items():
                    setattr(s, k, v)
                return s
            return cls()
        except Exception:
            return cls()

class DatabaseFile(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="اسم الملف")
    data = models.BinaryField(verbose_name="بيانات الملف")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ملف قاعدة بيانات"
        verbose_name_plural = "ملفات قاعدة البيانات"

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────
#  Live Chat System
# ─────────────────────────────────────────────
class ChatSession(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'في الانتظار'),
        ('active',  'نشطة'),
        ('ended',   'منتهية'),
    ]
    session_key  = models.CharField(max_length=64, unique=True, verbose_name="مفتاح الجلسة")
    user_name    = models.CharField(max_length=100, verbose_name="اسم المستخدم")
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting', verbose_name="الحالة")
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "جلسة محادثة"
        verbose_name_plural = "جلسات المحادثة"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_name} — {self.get_status_display()}"


class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user',  'مستخدم'),
        ('admin', 'مسئول'),
        ('system','نظام'),
    ]
    session    = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender     = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message    = models.TextField(verbose_name="الرسالة")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "رسالة محادثة"
        verbose_name_plural = "رسائل المحادثة"
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.sender}] {self.message[:50]}"


# ══════════════════════════════════════════
#  DIGITAL LIBRARY
# ══════════════════════════════════════════



class LibraryBook(models.Model):
    """الكتب القانونية"""
    title       = models.CharField(max_length=300, verbose_name="عنوان الكتاب")
    author      = models.CharField(max_length=200, blank=True, verbose_name="اسم المؤلف")
    description = models.TextField(blank=True, verbose_name="نبذة عن الكتاب")
    cover_image = models.ImageField(upload_to='library/books/', blank=True, null=True, verbose_name="صورة الغلاف")
    file        = models.FileField(upload_to='library/books/files/', blank=True, null=True, verbose_name="ملف PDF")
    external_url= models.URLField(blank=True, max_length=800, verbose_name="رابط خارجي")
    is_active   = models.BooleanField(default=True, verbose_name="منشور")
    views_count = models.PositiveIntegerField(default=0, verbose_name="عدد المشاهدات")
    downloads_count = models.PositiveIntegerField(default=0, verbose_name="عدد التنزيلات")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "كتاب قانوني"
        verbose_name_plural = "الكتب القانونية"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class LibraryContract(models.Model):
    """نماذج العقود"""
    CATEGORY_CHOICES = [
        ('sale',      'عقود البيع والشراء'),
        ('rent',      'عقود الإيجار'),
        ('work',      'عقود العمل'),
        ('company',   'عقود الشركات'),
        ('proxy',     'توكيلات'),
        ('divorce',   'أحوال شخصية'),
        ('criminal',  'مذكرات جنائية'),
        ('civil',     'مذكرات مدنية'),
        ('other',     'أخرى'),
    ]
    title       = models.CharField(max_length=300, verbose_name="اسم النموذج")
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="التصنيف")
    description = models.TextField(blank=True, verbose_name="وصف النموذج")
    cover_image = models.ImageField(upload_to='library/contracts/covers/', blank=True, null=True, verbose_name="صورة الغلاف")
    file        = models.FileField(upload_to='library/contracts/', blank=True, null=True, verbose_name="ملف النموذج (PDF / Word)")
    external_url= models.URLField(blank=True, max_length=800, verbose_name="رابط خارجي")
    is_active   = models.BooleanField(default=True, verbose_name="منشور")
    views_count = models.PositiveIntegerField(default=0, verbose_name="عدد المشاهدات")
    downloads_count = models.PositiveIntegerField(default=0, verbose_name="عدد التنزيلات")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "نموذج عقد"
        verbose_name_plural = "نماذج العقود"
        ordering = ['category', '-created_at']

    def __str__(self):
        return self.title

