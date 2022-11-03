from django.contrib import admin
from .models import SiteContent, FAQ, BadSlang


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


@admin.register(BadSlang)
class BadSlangAdmin(admin.ModelAdmin):
    """Помощь"""
    list_display = 'name',

