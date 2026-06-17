from django.db import models
from members.models import Lawyer

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم التصنيف")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "تصنيفات الأرشيف"

    def __str__(self):
        return self.name

class Document(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان المستند")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="التصنيف")
    file = models.FileField(upload_to='archive/', verbose_name="الملف")
    lawyer = models.ForeignKey(Lawyer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="يخص المحامي (اختياري)")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الرفع")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "مستند"
        verbose_name_plural = "الأرشيف الإلكتروني"
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title
