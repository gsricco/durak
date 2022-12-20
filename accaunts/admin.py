from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from social_django.models import UserSocialAuth, Nonce, Association
from .models import CustomUser, UserAgent, DetailUser, ReferalUser, ReferalCode, GameID, Ban, UserIP, Level, ItemForUser, DayHash, RouletteRound
from .forms import LevelForm
from psycopg2.extras import NumericRange
from caseapp.models import OwnedCase

"""Модели которые не нужно отображать в Admin из SocialAuth"""
admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)
admin.site.unregister(Association)


class OwnedCaseTabularInline(admin.TabularInline):
    model = OwnedCase
    extra = 1

class ItemForUserInline(admin.TabularInline):
    model = ItemForUser
    extra = 0


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
    inlines = [UserAgentInline, UserIPInline, DetailUserInline,
               ReferalCodeInline, GameIDInline, BanInline,OwnedCaseTabularInline,ItemForUserInline]
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
    list_display = 'level', 'experience_range', 'experience_for_lvl', 'preview', 'img_name'
    list_editable = 'img_name',
    list_filter = 'level',
    ordering = 'level',
    readonly_fields = 'preview',
    search_fields = 'level', 'experience_range'

    # @admin.action(description='Добавить опыт для получения уровней')
    # def add_experience(self, request, queryset):
    #     self.message_user(request, f"{queryset}", messages.SUCCESS)

    @admin.display(description='Опыт до следующего уровня')
    def experience_for_lvl(self, obj):
        # проверка на непустые значения диапазона опыта
        if obj and obj.experience_range:
            upper = obj.experience_range.upper if obj.experience_range.upper else 0
            lower = obj.experience_range.lower if obj.experience_range.lower else 0
        
            difference = upper - lower

            return difference
        return None

    def preview(self, obj):
        if obj.img_name:
            return mark_safe(f'<svg style="width: 50px; height: 50px;"><use xlink:href="/static/img/icons/sprite.svg#{obj.img_name}"></use></svg>')
        else:
            return 'Нет изображения'

    preview.short_description = 'Картинка уровня'

@admin.register(Ban)
class BanUserAdmin(admin.ModelAdmin):
    list_display = 'user','ban_site', 'ban_chat',  'ban_ip'
    search_fields = 'user__id', 'user__username',


@admin.register(RouletteRound)
class RouletteRoundAdmin(admin.ModelAdmin):
    list_display = 'round_number', 'round_roll', 'rolled',
    list_editable = 'round_roll',
    search_fields = '=round_number',


@admin.register(DayHash)
class DayHashAdmin(admin.ModelAdmin):
    list_display = 'date_generated', 'private_key', 'public_key', 'show_hash',
    list_editable = 'show_hash',
    readonly_fields = 'private_key', 'public_key', 'private_key_hashed'


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
