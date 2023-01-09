from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from social_django.models import UserSocialAuth, Nonce, Association

from bot_payment.models import RefillRequest, WithdrawalRequest
from content_manager.admin import AdminBalanceEditor
from .models import (CustomUser, UserAgent, DetailUser, ReferalUser,
                     ReferalCode, GameID, Ban, UserIP, Level, ItemForUser,
                     DayHash, RouletteRound, AvatarProfile, UserBet)
from .forms import LevelForm
from pay.models import Popoln
from caseapp.models import OwnedCase, ItemForCase
from django_celery_results.models import TaskResult, GroupResult
from django_celery_beat.models import IntervalSchedule, CrontabSchedule, SolarSchedule, ClockedSchedule, PeriodicTask

"""Модели которые не нужно отображать в Admin из SocialAuth"""
admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)
admin.site.unregister(Association)

# admin.site.unregister(TaskResult)
# admin.site.unregister(GroupResult)
#
# admin.site.unregister(SolarSchedule)
# admin.site.unregister(PeriodicTask)
# admin.site.unregister(IntervalSchedule)
# admin.site.unregister(ClockedSchedule)
# admin.site.unregister(CrontabSchedule)


# class OwnedCaseTabularInline(admin.TabularInline):
#     model = OwnedCase
#     extra = 1
#     classes = ['collapse']
#
#     def has_change_permission(self, request, obj=None):
#         return False
#
#     def has_add_permission(self, request, obj=None):
#         return False


class ItemForUserInline(admin.TabularInline):
    model = ItemForUser
    readonly_fields = "user_item", "date_modified", "is_used", "is_forwarded", "is_money"
    extra = 0
    classes = ['collapse']


@admin.register(ReferalUser)
class ReferalUserAdmin(admin.ModelAdmin):
    list_display = 'user_with_bonus', 'user_with_bonus_id', 'invited_user', 'invited_user_id', 'date',
    list_filter = 'date',
    search_fields = 'user_with_bonus__username', 'user_with_bonus__id',
    search_help_text = 'Поиск по имени пользователя который пригласил и его id'


class DetailUserInline(admin.TabularInline):
    model = DetailUser
    readonly_fields = "balance", "free_balance", "frozen_balance"
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False


class UserAgentInline(admin.TabularInline):
    """Класс отображения в админке агентов с которых заходил пользователь(Модель UserAgent)"""
    model = UserAgent
    extra = 0
    classes = ['collapse']


class UserIPInline(admin.TabularInline):
    """Класс отображения в админке IP с которых заходил пользователь(модель UserIP)"""
    model = UserIP
    extra = 0
    classes = ['collapse']


class ReferalCodeInline(admin.TabularInline):
    model = ReferalCode
    extra = 0
    classes = ['collapse']


class GameIDInline(admin.TabularInline):
    model = GameID
    extra = 0
    classes = ['collapse']


class BanInline(admin.TabularInline):
    model = Ban
    extra = 0
    classes = ['collapse']


class PopolnInline(admin.TabularInline):
    model = Popoln
    extra = 0
    classes = ['collapse']


class RefillRequestInline(admin.TabularInline):
    model = RefillRequest
    extra = 0
    classes = ['collapse']


class WithdrawalRequestInline(admin.TabularInline):
    model = WithdrawalRequest
    extra = 0
    classes = ['collapse']


@admin.register(AvatarProfile)
class AvatarProfileAdmin(admin.ModelAdmin):
    """Аватарки профиля (стандартные)"""
    list_display = 'name', 'preview', 'avatar_img',
    readonly_fields = 'preview',
    list_editable = 'avatar_img',

    def preview(self, obj):
        if obj.avatar_img:
            return mark_safe(f'<img src="{obj.avatar_img.url}" width="50" height="50">')
        else:
            return 'Нет изображения'

    preview.short_description = 'Аватарки профиля'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Класс отображения в админке пользователей(модель CustomUser)"""
    list_display = 'usernameinfo', 'id', 'preview', 'user_info', 'level', 'email', 'vk_url', 'note',
    list_editable = 'note',
    search_fields = 'username', 'id', 'vk_url', 'note', 'userip__userip', 'gameid__game_id'
    search_help_text = 'Поиск по имени пользователя, id пользователя, id c дурак онлайн, ссылки на vk, замтеки пользователя и ip пользователя'
    inlines = [PopolnInline, DetailUserInline, UserAgentInline, UserIPInline, ReferalCodeInline, GameIDInline,
               BanInline, ItemForUserInline, RefillRequestInline, WithdrawalRequestInline]
    readonly_fields = 'preview',
    fieldsets = (
        ('ИНФОРМАЦИЯ', {'fields': ('username', 'password', 'last_login', 'date_joined',)}),
        ('ПЕРСОНАЛЬНЫЕ ДАННЫЕ', {'classes': ('collapse',), 'fields': ('first_name', 'last_name', 'email', 'vk_url',)}),
        ('АВАТАРКИ ПОЛЬЗОВАТЕЛЯ',
         {'classes': ('collapse',), 'fields': ('preview', 'avatar', 'use_avatar', 'avatar_default',)}),
        ('ПРАВА ПОЛЬЗОВАТЕЛЯ', {'classes': ('collapse',), 'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',)}),
        ('ИГРОВЫЕ ДАННЫЕ', {'classes': ('collapse',), 'fields': ('experience', 'level',)})
    )

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.avatar.url}" width="50" height="50">')

    # переопределение сохранения модели для выдачи новых уровней и наград при
    # изменении опыта пользователя через админку
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.give_level(save_immediately=True)

    def save_formset(self, request, form, formset, change):
        if formset.has_changed() and formset.__class__.__name__ == 'BalanceEditorFormFormSet':
            for new_form in formset:
                if new_form.has_changed():
                    if user_detail := DetailUser.objects.get(user=new_form.cleaned_data['to_user']):
                        if new_form.cleaned_data['to_add'] == 'True':
                            user_detail.balance += new_form.cleaned_data['amount']
                        else:
                            if user_detail.balance < new_form.cleaned_data['amount']:
                                return
                            user_detail.balance -= new_form.cleaned_data['amount']
                        user_detail.save()
        super().save_formset(request, form, formset, change)

    preview.short_description = 'Аватар'


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    """Класс отображения в админке уровней пользователей(модель Level)"""
    form = LevelForm
    list_display = 'level', 'experience_range', 'experience_for_lvl', 'preview', 'img_name'
    list_editable = 'img_name', 'experience_range'
    list_filter = 'img_name', 'level'
    ordering = 'level',
    readonly_fields = 'preview',

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
            return mark_safe(
                f'<svg style="width: 50px; height: 50px;"><use xlink:href="/static/img/icons/sprite.svg#{obj.img_name}"></use></svg>')
        else:
            return 'Нет изображения'

    preview.short_description = 'Картинка уровня'


@admin.register(Ban)
class BanUserAdmin(admin.ModelAdmin):
    list_display = 'user', 'user_id', 'ban_site', 'ban_chat', 'ban_ip'
    search_fields = 'user__username', 'user__id'
    search_help_text = 'Поиск по имени пользователя и id пользователя'
    list_editable = 'ban_site', 'ban_chat', 'ban_ip'
    list_filter = 'ban_site', 'ban_chat', 'ban_ip'


@admin.register(RouletteRound)
class RouletteRoundAdmin(admin.ModelAdmin):
    list_display = 'round_number', 'round_roll', 'rolled', 'round_started',
    list_editable = 'round_roll',
    search_fields = '=round_number',
    search_help_text = 'Поиск по номеру раунда'
    list_filter = 'rolled', 'round_roll', 'round_started'
    readonly_fields = 'day_hash', 'round_number', 'round_started',  'rolled', 'total_bet_amount', 'winners',
    ordering = '-rolled', '-round_started'


@admin.register(DayHash)
class DayHashAdmin(admin.ModelAdmin):
    list_display = 'date_generated', 'private_key', 'public_key', 'show_hash',
    list_filter = 'date_generated',
    list_editable = 'show_hash',
    readonly_fields = 'private_key', 'public_key', 'private_key_hashed'


@admin.register(UserBet)
class UserBetAdmin(admin.ModelAdmin):
    list_display = 'user', 'user_id', 'round_number', 'sum', 'sum_win', 'date', 'win'
    list_filter = 'win', 'date'
    search_fields = 'user__username', 'user__id', 'sum_win'
    search_help_text = 'Поиск по имени пользователя id пользователя и сумме выйгрыша'
    fields = "sum", "sum_win", "win", "round_number", "placed_on", "user"
    readonly_fields = "sum", "sum_win", "win", "round_number", "placed_on", "user"


@admin.register(ItemForCase)
class ItemForCase(admin.ModelAdmin):
    list_display = 'item', 'case', 'chance',
    list_editable = 'chance',
    list_filter = 'case', 'item',
