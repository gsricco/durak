from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from social_django.models import UserSocialAuth, Nonce, Association
from .models import CustomUser, UserAgent, DetailUser, ReferalUser, ReferalCode, GameID, Ban, UserIP, Level
from .forms import LevelForm
from psycopg2.extras import NumericRange

"""Модели которые не нужно отображать в Admin из SocialAuth"""
admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)
admin.site.unregister(Association)


@admin.register(ReferalUser)
class ReferalUserAdmin(admin.ModelAdmin):
    list_display = 'user_with_bonus', 'invited_user', 'date',


class DetailUserInline(admin.TabularInline):
    model = DetailUser
    extra = 0


class UserAgentInline(admin.TabularInline):
    """Класс отображения в админке агентов с которых заходил пользователь(Модель UserAgent)"""
    model = UserAgent
    extra = 0


class UserIPInline(admin.TabularInline):
    """Класс отображения в админке IP с которых заходил пользователь(модель UserIP)"""
    model = UserIP
    extra = 0


class ReferalCodeInline(admin.TabularInline):
    model = ReferalCode
    extra = 0


class GameIDInline(admin.TabularInline):
    model = GameID
    extra = 0


class BanInline(admin.TabularInline):
    model = Ban
    extra = 0


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Класс отображения в админке пользователей(модель CustomUser)"""
    list_display = ('usernameinfo', 'preview', 'user_info', 'email', 'vk_url',)
    search_fields = 'usernameinfo',
    inlines = [UserAgentInline, UserIPInline, DetailUserInline, ReferalCodeInline, GameIDInline, BanInline]
    readonly_fields = 'preview',
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Данные пользователя', {'fields': ('first_name', 'last_name', 'email')}),
        (None, {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (None, {'fields': ('last_login', 'date_joined')}),
        ('Дополнительная информация', {'fields': ('avatar', 'vk_url', 'photo')}),
        ('Игровые данные', {'fields': ('experience', 'level')})
    )
    def preview(self, obj):
        return mark_safe(f'<img src="{obj.avatar.url}" width="50" height="50">')

    # переопределение сохранения модели для выдачи новых уровней и наград при 
    # изменении опыта пользователя через админку
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.give_level(save_immediately=True)

    preview.short_description = 'Аватар'


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    """Класс отображения в админке уровней пользователей(модель Level)"""
    # actions = 'add_experience',
    form = LevelForm
    list_display = 'level', 'experience_range', 'experience_for_lvl', 'image', 'preview'
    list_editable = 'image',
    list_filter = 'level',
    ordering = 'level',
    readonly_fields = 'preview',
    search_fields = 'level', 'experience_range'

    # @admin.action(description='Добавить опыт для получения уровней')
    # def add_experience(self, request, queryset):
    #     self.message_user(request, f"{queryset}", messages.SUCCESS)

    @admin.display(description='Опыт до следующего уровня')
    def experience_for_lvl(self, obj):
        return obj.experience_range.upper - obj.experience_range.lower

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50">')
        else:
            return 'Нет изображения'

    preview.short_description = 'Картинка уровня'


# admin.site.register(ReferalUser)
# admin.site.unregister(Group)
# admin.site.register(ReferalCode)
# admin.site.register(GameID)
# admin.site.register(Ban)
# @admin.register(UserAgent)
# class UserAgentAdmin(admin.ModelAdmin):
#     list_display = 'user', 'useragent'
#
#
# @admin.register(UserIP)
# class UserIPAdmin(admin.ModelAdmin):
#     list_display = 'user', 'userip'
