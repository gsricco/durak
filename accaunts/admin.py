from django import forms
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.db.models import Count, Sum
from django.utils.safestring import mark_safe
from django_celery_beat.models import (ClockedSchedule, CrontabSchedule,
                                       IntervalSchedule, PeriodicTask,
                                       SolarSchedule)
from django_celery_results.models import GroupResult, TaskResult
from rangefilter.filters import DateTimeRangeFilter
from social_django.models import Association, Nonce, UserSocialAuth

from bot_payment.models import RefillRequest, WithdrawalRequest
from caseapp.models import ItemForCase, OwnedCase
from content_manager.admin import AdminBalanceEditor
from pay.models import Popoln

from .forms import LevelForm
from .models import (AvatarProfile, Ban, BonusVKandYoutube, CustomUser,
                     DayHash, DetailUser, GameID, ItemForUser, Level,
                     ReferalCode, ReferalUser, RouletteRound, UserAgent,
                     UserBet, UserIP)

"""Модели которые не нужно отображать в Admin из SocialAuth"""
admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)
admin.site.unregister(Association)

admin.site.unregister(TaskResult)
admin.site.unregister(GroupResult)

admin.site.unregister(SolarSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)


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


class MyChangeListOleg(ChangeList):

    def get_results(self, *args, **kwargs):
        super(MyChangeListOleg, self).get_results(*args, **kwargs)
        q = self.result_list.aggregate(asum=Sum('bonus_sum'))
        self.sum_count = q['asum']


@admin.register(ReferalUser)
class ReferalUserAdmin(admin.ModelAdmin):
    list_display = 'user_with_bonus', 'user_with_bonus_id', 'invited_user', 'invited_user_id', 'bonus_sum', 'date',
    list_filter = 'date', ('date', DateTimeRangeFilter),
    search_fields = 'user_with_bonus__username', 'user_with_bonus__id',
    search_help_text = 'Поиск по имени пользователя который пригласил и его id'
    list_per_page = 100

    def get_changelist(self, request, **kwargs):
        return MyChangeListOleg


class DetailUserInline(admin.TabularInline):
    model = DetailUser
    readonly_fields = "balance", "_reserve",  "free_balance", "frozen_balance",
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False

    # @admin.display(description='Общий Баланс')
    # def total_balance(self, obj):
    #     return obj.total_balance


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


class BonusVKandYoutubeInLine(admin.TabularInline):
    """Подписки на YouTube и VK"""
    model = BonusVKandYoutube
    extra = 0
    classes = ['collapse']
    readonly_fields = ("bonus_vk", "bonus_youtube", "date_created_vk",
                       "date_created_youtube", "vk_disabled", "youtube_disabled")

    def has_delete_permission(self, request, obj=None):
        return False


class CustomUserModelForm(UserChangeForm):
    level = forms.ModelChoiceField(queryset=Level.objects, empty_label=None)

    class Meta:
        model = CustomUser
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(CustomUserModelForm, self).__init__(*args, **kwargs)
    #     self.fields['level'].initial = 0


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Класс отображения в админке пользователей(модель CustomUser)"""
    form = CustomUserModelForm
    list_display = 'usernameinfo', 'id', 'random_id', 'preview', 'user_info', 'level', 'email', 'vk_url', 'note',
    list_editable = 'note',
    search_fields = 'username', 'id', 'vk_url', 'note', 'userip__userip', 'gameid__game_id', 'random_id'
    search_help_text = 'Поиск по имени пользователя, id пользователя, id c дурак онлайн, ссылки на vk, замтеки пользователя, ip пользователя И cгенерированного id'
    inlines = [PopolnInline, DetailUserInline, AdminBalanceEditor, BonusVKandYoutubeInLine, UserAgentInline, UserIPInline, ReferalCodeInline, GameIDInline,
               BanInline, ItemForUserInline, RefillRequestInline, WithdrawalRequestInline]
    readonly_fields = 'preview', 'random_id',
    list_select_related = "level", "avatar_default",
    fieldsets = (
        ('ИНФОРМАЦИЯ', {'fields': ('random_id', 'username', 'password', 'last_login', 'date_joined')}),
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
        if formset.__class__.__name__ == 'BalanceEditorFormFormSet':
            for i, new_form in enumerate(formset.forms):
                if new_form.has_changed():
                    if user_detail := DetailUser.objects.filter(user=new_form.cleaned_data['to_user']).first():
                        if new_form.cleaned_data['to_add'] == 'True':
                            user_detail.balance += new_form.cleaned_data['amount']
                        else:
                            if user_detail.balance < new_form.cleaned_data['amount']:
                                formset.forms.pop(i)
                                break
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
    list_select_related = "case",

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
    list_select_related = "user",


@admin.register(RouletteRound)
class RouletteRoundAdmin(admin.ModelAdmin):
    list_display = 'round_number', 'round_roll', 'rolled', 'round_started', "day_of_round",
    list_editable = 'round_roll',
    search_fields = '=round_number',
    search_help_text = 'Поиск по номеру раунда'
    list_filter = 'round_started', ('round_started', DateTimeRangeFilter), 'rolled', 'round_roll',
    readonly_fields = 'day_hash', 'round_number', 'round_started', 'rolled', 'total_bet_amount', 'winners',
    ordering = '-rolled', '-round_started'
    list_select_related = "day_hash",


@admin.register(DayHash)
class DayHashAdmin(admin.ModelAdmin):
    list_display = 'date_generated', 'private_key', 'public_key', 'show_hash',
    list_filter = 'date_generated', ('date_generated', DateTimeRangeFilter)
    list_editable = 'show_hash',
    readonly_fields = 'private_key', 'public_key', 'private_key_hashed'


@admin.register(UserBet)
class UserBetAdmin(admin.ModelAdmin):
    list_display = 'user', 'user_id', 'round_number', 'sum', 'sum_win', 'date', 'win'
    list_filter = 'win', 'date',  ('date', DateTimeRangeFilter)
    search_fields = 'user__username', 'user__id', 'sum_win'
    search_help_text = 'Поиск по имени пользователя id пользователя и сумме выйгрыша'
    fields = "sum", "sum_win", "win", "round_number", "placed_on", "user"
    readonly_fields = "sum", "sum_win", "win", "round_number", "placed_on", "user"
    list_select_related = "user",


@admin.register(ItemForCase)
class ItemForCase(admin.ModelAdmin):
    list_display = 'item', 'case', 'chance',
    list_editable = 'chance',
    list_filter = 'case', 'item',


class MyChangeList(ChangeList):
    """Предмет пользователя"""

    def get_results(self, *args, **kwargs):
        super(MyChangeList, self).get_results(*args, **kwargs)
        q = self.result_list.filter(is_forwarded=True).aggregate(asum=Count('is_forwarded'))
        self.sum_count = q['asum']


@admin.register(ItemForUser)
class ItemForUser(admin.ModelAdmin):
    list_display = 'user', 'user_item', 'is_used', 'is_forwarded', 'date_modified'
    list_filter = 'date_modified', ('date_modified', DateTimeRangeFilter), 'is_used', 'is_forwarded', 'user_item'
    search_fields = 'user__username',
    search_help_text = 'Поиск по имени пользователя'
    list_per_page = 100

    def get_changelist(self, request):
        return MyChangeList
