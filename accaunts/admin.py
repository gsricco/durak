from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from social_django.models import UserSocialAuth, Nonce, Association
from .models import CustomUser, Level, UserAgent, DetailUser, ReferalUser, ReferalCode, GameID, Ban, UserIP, LevelRange

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
        ('Дополнительная информация', {'fields': ('avatar', 'vk_url', 'photo')})
    )
    def preview(self, obj):
        return mark_safe(f'<img src="{obj.avatar.url}" width="50" height="50">')

    preview.short_description = 'Аватар'



admin.site.register(LevelRange)


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    """Класс отображения в админке уровней пользователей(модель Level)"""
    list_display = 'level', 'experience_for_lvl', 'image', 'preview'
    list_editable = 'experience_for_lvl', 'image'
    list_filter = 'level',
    search_fields = 'level',
    readonly_fields = 'preview',

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50">')
        else:
            return 'Нет аватара'

    preview.short_description = 'Аватар'

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
