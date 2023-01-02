import redis
from django.contrib import admin
from django.contrib.admin.utils import get_deleted_objects
from django.db.models import QuerySet

from .models import SiteContent, FAQ, BadSlang
from configs.settings import REDIS_URL_STACK
from .models import SiteContent, FAQ, BadSlang, FakeOnline, ShowRound

r = redis.Redis(encoding="utf-8", decode_responses=True, host=REDIS_URL_STACK)
SET_BAD_SLAG = set()

@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    """Контент сайта"""
    list_display = '__str__', 'support_email',
    fieldsets = (
        ('ПРАВИЛО ЧАТА', {
            'classes': ('collapse',),
            'fields': ('chat_rule',)
        }),
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
    list_display = 'name', 'body_description', 'is_active'
    list_editable = 'is_active',
    list_filter = 'is_active',


@admin.register(BadSlang)
class BadSlangAdmin(admin.ModelAdmin):
    """Фильтр нежелательных слов в чате"""
    list_display = 'name',

    def save_model(self, request, obj, form, change):
        if BadSlang.objects.filter(name=obj.name.lower()).exists():
            return
        obj.name = obj.name.lower()
        if r.exists("bad_slang"):
            r.sadd("bad_slang", obj.name)
            obj.save()
        else:
            obj.save()
            if words := BadSlang.objects.all().only("name").values_list("name", flat=True):
                all_words = words
                r.sadd("bad_slang", *set(all_words))

    def get_deleted_objects(self, objs, request):
        if type(objs) is QuerySet:
            objs_words = set(objs.values_list("name", flat=True))
            r.srem("bad_slang", *objs_words)
        else:
            r.srem("bad_slang", objs[0].name)
        return get_deleted_objects(objs, request, self.admin_site)


@admin.register(FakeOnline)
class AdminFakeOnline(admin.ModelAdmin):
    """Фейковый онлайн чата"""
    list_display = "count", "is_active"
    fields = "count", "is_active"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        if obj.is_active is True:
            r.set("fake_online", obj.count)
        else:
            r.delete("fake_online")
        obj.save()


@admin.register(ShowRound)
class ShowRoundAdmin(admin.ModelAdmin):
    """Показывать раунды в транзакциях"""
    list_display = "__str__", "show",
    fields = "show",

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
