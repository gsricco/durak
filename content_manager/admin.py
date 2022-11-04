from django.contrib import admin
from .models import SiteContent, FAQ, BadSlang


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    """Контент сайта"""
    list_display = '__str__', 'support_email',
    fieldsets = (
        ('Страница ЧЕСТНОСТЬ', {
            'classes': ('collapse',),
            'fields': ('honesty_game', 'roll')
        }),
        ('Страница ПОМОЩЬ', {
            'classes': ('collapse',),
            'fields': ('agreement',)
        }),
        ('Страница КОНТАКТЫ', {
            'classes': ('collapse',),
            'fields': ('about_us', 'description', 'support_email', 'url_vk', 'url_youtube')
        }),
        ('Страница FREE', {
            'classes': ('collapse',),
            'fields': ('info2', 'info3', 'bonus_vk', 'bonus_youtube')
        }),
    )

    def has_add_permission(self, request):  # позволяет создать только одну модель
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)


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
