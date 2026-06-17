from django.contrib import admin
from .models import Category, Document

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'lawyer', 'uploaded_at')
    list_filter = ('category', 'uploaded_at')
    search_fields = ('title', 'notes', 'lawyer__name', 'lawyer__registration_number')
    autocomplete_fields = ['lawyer']
