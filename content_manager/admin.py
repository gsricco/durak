import redis
from django import forms
from django.contrib import admin
from django.contrib.admin.utils import get_deleted_objects
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.forms import RadioSelect

from configs.settings import REDIS_PASSWORD, REDIS_URL_STACK

from .models import (FAQ, BadSlang, BalanceEditor, DurakNickname, FakeOnline,
                     ShowRound, SiteContent)

r = redis.Redis(encoding="utf-8", decode_responses=True, host=REDIS_URL_STACK, password=REDIS_PASSWORD)


# class SiteContentAdminModelForm(forms.ModelForm):
#     class Meta:
#         model = SiteContent
#         fields = '__all__'
#
#     def clean(self):
#         if self.changed_data:
#             if 'url_vk' in self.changed_data:
#                 self.data._mutable = True
#                 group_id = get_vk_group_id(self.cleaned_data['url_vk'])
#                 if group_id:
#                     self.cleaned_data['vk_group_id'] = str(group_id)
#                 else:
#                     raise ValidationError('Неправильная ссылка на группу VK')
#             if 'url_youtube' in self.changed_data:
#                 youtube_id = get_youtube_id(self.cleaned_data['url_youtube'])
#                 if youtube_id:
#                     self.cleaned_data['youtube_channel_id'] = str(youtube_id)
#                 else:
#                     raise ValidationError('Неправильная ссылка на YouTube канал')
#         return self.cleaned_data
#
#     def save(self, commit=False):
#         obj = super(SiteContentAdminModelForm, self).save(commit=False)
#         if new_vk_id := self.cleaned_data.get('vk_group_id'):
#             obj.vk_group_id = new_vk_id
#         if new_youtube_id := self.cleaned_data.get('youtube_channel_id'):
#             obj.youtube_channel_id = new_youtube_id
#         obj.save()
#         return obj


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    """Контент сайта"""
    # form = SiteContentAdminModelForm
    list_display = '__str__', 'support_email',
    # readonly_fields = 'vk_group_id', 'youtube_channel_id',
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
            'fields': ('about_us', 'description', 'support_email',
                       'url_vk', 'vk_group_id',
                       'url_youtube', 'youtube_channel_id')
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


@admin.register(DurakNickname)
class DurakNicknameAdmin(admin.ModelAdmin):
    list_display = 'nickname',
    # def has_add_permission(self, request):
    #     return False
    # def has_delete_permission(self, request, obj=None):
    #     return False


class AdminBalanceEditorForm(forms.ModelForm):
    SELECT_CHOICES = (
        (True, "Добавить"),
        (False, "Отнять"),
    )
    to_add = forms.ChoiceField(label="Опции", choices=SELECT_CHOICES, initial=True, widget=RadioSelect)

    class Meta:
        model = BalanceEditor
        fields = '__all__'


class AdminBalanceEditor(admin.TabularInline):
    model = BalanceEditor
    readonly_fields = "date",
    form = AdminBalanceEditorForm
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False
