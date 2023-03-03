from functools import reduce

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum
from rangefilter.filters import DateTimeRangeFilter

from . import models
from .models import RefillRequest


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
        only_needed = filter(lambda x: x.status == 'succ', list(self.result_list))
        result = 0
        for i in only_needed:
            if hasattr(i, 'amount'):
                result += i.amount
        # q = self.result_list.filter(status='succ').aggregate(asum=Sum('amount'))
        self.sum_count = result
        self.su_prof = self.earnings() - self.get_loss()
        if self.sum_count is None:
            self.sum_count = 0

    def get_loss(self) -> int:
        """Возвращает убыток от обыгрышей бота на пополнение"""
        # заметка заявки на пополнение при убытке начинается с "Убыток". Пример: "Убыток: 23"
        LOSS_REQ_START = "Убыток"
        # получает заявки с убытком
        # loss_requests_notes = self.result_list.filter(note__startswith=LOSS_REQ_START).values_list("note")
        loss_requests_notes = filter(lambda x: x.note.startswith(LOSS_REQ_START) if x.note else False, self.result_list)
        loss_requests_notes = list(map(lambda x: x.note, list(loss_requests_notes)))
        if loss_requests_notes:
            int_loss = 0
            for loss_note in loss_requests_notes:
                try:
                    # парсит строку с заметкой об убытке и получает из неё числовое значение убытка
                    str_loss = loss_note.split()[1]
                    int_loss += abs(int(str_loss))
                except (ValueError, IndexError) as err:
                    # пропускает заметку с неправильным форматом заметки об убытке
                    continue
            return int_loss
        else:
            # Убыток равен нулю, если нет заявок с "Убыток"
            return 0

    def earnings(self) -> int:
        LOSS_REQ_START = "Профит"
        # получает заявки с Профит
        # loss_requests_notes = self.result_list.filter(note__startswith=LOSS_REQ_START).values_list("note")
        loss_requests_notes = filter(lambda x: x.note.startswith(LOSS_REQ_START) if x.note else False, self.result_list)
        loss_requests_notes = list(map(lambda x: x.note, list(loss_requests_notes)))
        if loss_requests_notes:
            int_loss = 0
            for loss_note in loss_requests_notes:
                try:
                    # парсит строку с заметкой об Профит и получает из неё числовое значение Профит
                    str_loss = loss_note.split()[1]
                    int_loss += abs(int(str_loss))
                except (ValueError, IndexError) as err:
                    # пропускает заметку с неправильным форматом заметки об Профит
                    continue
            return int_loss
        else:
            # Убыток равен нулю, если нет заявок с "Профит"
            return 0



@admin.register(models.RefillRequest)
class RefillRequestAdmin(admin.ModelAdmin):
    list_display = 'user', 'user_id', 'request_id', 'amount', 'note', 'status', 'date_closed', 'date_opened'
    list_editable = 'note', 'status'
    search_fields = 'user__username', 'amount', 'note'
    search_help_text = 'Поиск по имени пользователя, сумме пополнения и заметке'
    list_filter = RefillStatusListFilter, 'date_closed', ('date_closed', DateTimeRangeFilter),
    list_per_page = 100

    def get_changelist(self, request):
        return MyChangeListKorney


class MyChangeList(ChangeList):
    """Заявки на вывод"""

    def get_results(self, *args, **kwargs):
        super(MyChangeList, self).get_results(*args, **kwargs)
        only_needed = filter(lambda x: x.status == 'succ', list(self.result_list))
        result = 0
        for i in only_needed:
            if hasattr(i, 'amount'):
                result += i.amount
        # q = self.result_list.filter(status='succ').aggregate(asum=Sum('amount'))
        self.sum_count = result
        if self.sum_count is None:
            self.sum_count = 0


@admin.register(models.WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = 'user', 'user_id', 'request_id', 'amount', 'note', 'status', 'date_closed', 'date_opened'
    list_editable = 'note', 'status'
    search_fields = 'user__username', 'amount', 'note'
    search_help_text = 'Поиск по имени пользователя, сумме пополнения и заметке'
    list_filter = WithdrawStatusListFilter, 'date_closed', ('date_closed', DateTimeRangeFilter),
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
