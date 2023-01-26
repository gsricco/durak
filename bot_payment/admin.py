from django.contrib import admin

from . import models
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum
from rangefilter.filters import DateTimeRangeFilter


class StatusListFilter(admin.SimpleListFilter):
    title = 'Статус заявки'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        
        return (
            ('open', 'Открытые заявки'),
            ('succfail', 'Закрытые заявки (все)'),
            ('succ', 'Закрытые заявки (успешно)'),
            ('fail', 'Закрытые заявки (не успешно)'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'succfail':
            return self.model.objects.filter(status__in=('succ', 'fail'))
        if val in ('succ', 'open', 'fail'):
            return self.model.objects.filter(status=val)
        return self.model.objects.all()


class RefillStatusListFilter(StatusListFilter):
    model = models.RefillRequest


class WithdrawStatusListFilter(StatusListFilter):
    model = models.WithdrawalRequest


class MyChangeListKorney(ChangeList):
    """Заявки на пополнение"""

    def get_results(self, *args, **kwargs):
        super(MyChangeListKorney, self).get_results(*args, **kwargs)
        q = self.result_list.filter(status='succ').aggregate(asum=Sum('amount'))
        self.sum_count = q['asum']


@admin.register(models.RefillRequest)
class RefillRequestAdmin(admin.ModelAdmin):
    list_display = 'user', 'user_id', 'request_id', 'amount', 'note', 'status', 'date_closed'
    list_editable = 'note', 'status'
    search_fields = 'user__username', 'amount'
    search_help_text = 'Поиск по имени пользователя и сумме пополнения'
    list_filter = 'date_closed', ('date_closed', DateTimeRangeFilter), RefillStatusListFilter,
    list_per_page = 100

    def get_changelist(self, request):
        return MyChangeListKorney


class MyChangeList(ChangeList):
    """Заявки на вывод"""

    def get_results(self, *args, **kwargs):
        super(MyChangeList, self).get_results(*args, **kwargs)
        q = self.result_list.filter(status='succ').aggregate(asum=Sum('amount'))
        self.sum_count = q['asum']


@admin.register(models.WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = 'user', 'user_id', 'request_id', 'amount', 'note', 'status', 'date_closed'
    list_editable = 'note', 'status'
    search_fields = 'user__username', 'amount'
    search_help_text = 'Поиск по имени пользователя и сумме пополнения'
    list_filter = 'date_closed', ('date_closed', DateTimeRangeFilter), WithdrawStatusListFilter,
    list_per_page = 100

    def get_changelist(self, request):
        return MyChangeList


@admin.register(models.BotWork)
class BotWorkAdmin(admin.ModelAdmin):
    list_display = '__str__', 'work', 'work_t'
    list_editable = 'work', 'work_t'

    def has_add_permission(self, request):  # позволяет создать только одну модель
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)


@admin.register(models.BanTime)
class BanTimeAdmin(admin.ModelAdmin):
    list_display = '__str__', 'hours',
    list_editable = 'hours',

    def has_add_permission(self, request):  # позволяет создать только одну модель
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False
