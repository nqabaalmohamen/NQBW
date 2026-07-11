from django.contrib import admin
from .models import News, NewsImage, CouncilMember, Complaint, FAQ, Service, UserProfile, SiteSettings, LibraryJournal, LibraryLegislation, LibraryBook, LibraryContract

class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_published')
    list_filter = ('is_published', 'date')
    search_fields = ('title', 'content')
    inlines = [NewsImageInline]

@admin.register(CouncilMember)
class CouncilMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'position')
    ordering = ('order',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'name', 'phone', 'message')
    readonly_fields = ('created_at',)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active')
    list_editable = ('order', 'is_active')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'target', 'order', 'is_active')
    list_editable = ('order', 'is_active')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone', 'national_id')
    list_filter = ('user_type',)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slider_speed')

@admin.register(LibraryJournal)
class LibraryJournalAdmin(admin.ModelAdmin):
    list_display = ('title', 'issue_number', 'publish_date', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('title', 'issue_number')

@admin.register(LibraryLegislation)
class LibraryLegislationAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'number', 'year', 'is_active')
    list_filter = ('category', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('title', 'number')

@admin.register(LibraryBook)
class LibraryBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('title', 'author')

@admin.register(LibraryContract)
class LibraryContractAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('title',)
