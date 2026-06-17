from django.contrib import admin
from .models import Lawyer

@admin.register(Lawyer)
class LawyerAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_number', 'national_id', 'degree', 'status', 'phone')
    list_filter = ('degree', 'status')
    search_fields = ('name', 'registration_number', 'national_id', 'phone')
    ordering = ('-created_at',)
    fieldsets = (
        ('البيانات الأساسية', {
            'fields': ('user', 'name', 'photo', 'registration_number', 'national_id')
        }),
        ('النقابة', {
            'fields': ('degree', 'status')
        }),
        ('التواصل', {
            'fields': ('phone', 'email', 'address')
        }),
    )
