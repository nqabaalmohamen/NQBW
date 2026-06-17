from django.db import models
from django.contrib.auth.models import User

class Lawyer(models.Model):
    DEGREE_CHOICES = [
        ('1', 'جدول عام'),
        ('2', 'ابتدائي'),
        ('3', 'استئناف'),
        ('4', 'نقض'),
    ]

    STATUS_CHOICES = [
        ('active', 'مشتغل'),
        ('inactive', 'غير مشتغل'),
        ('suspended', 'موقوف'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="حساب المستخدم")
    name = models.CharField(max_length=255, verbose_name="الاسم الرباعي")
    registration_number = models.CharField(max_length=50, unique=True, verbose_name="رقم القيد")
    national_id = models.CharField(max_length=14, unique=True, verbose_name="الرقم القومي")
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES, verbose_name="درجة القيد")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active', verbose_name="حالة العضوية")
    
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم الهاتف")
    email = models.EmailField(blank=True, null=True, verbose_name="البريد الإلكتروني")
    address = models.TextField(blank=True, null=True, verbose_name="العنوان")
    
    photo = models.ImageField(upload_to='lawyers/', blank=True, null=True, verbose_name="الصورة الشخصية")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "محامي"
        verbose_name_plural = "المحامين"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.registration_number}"
