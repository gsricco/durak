from django.contrib import admin
from start_all_template.models import SiteContent, FAQ


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    """Контент сайта"""
    list_display = '__str__', 'support_email',


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """Помощь"""
    list_display = 'name', 'description', 'is_active'
    list_editable = 'is_active',
    list_filter = 'is_active',
