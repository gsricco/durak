from django.contrib import admin
from . import models


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


@admin.register(models.RefillRequest)
class RefillRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_id', 'user', 'amount', 'note', 'status')
    list_editable = ('note', 'status')
    list_filter = (RefillStatusListFilter,)


@admin.register(models.WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_id', 'user', 'amount', 'balance', 'note', 'status')
    list_editable = ('note', 'status')
    list_filter = (WithdrawStatusListFilter,)
