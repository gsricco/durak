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
    list_display = 'user', 'user_id', 'request_id', 'amount', 'note', 'status'
    list_editable = 'note', 'status'
    search_fields = 'user__username', 'amount'
    search_help_text = 'Поиск по имени пользователя и сумме пополнения'
    list_filter = RefillStatusListFilter, 'date_closed'


@admin.register(models.WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = 'user', 'user_id', 'request_id', 'amount', 'note', 'status'
    list_editable = 'note', 'status'
    search_fields = 'user__username', 'amount'
    search_help_text = 'Поиск по имени пользователя и сумме пополнения'
    list_filter = WithdrawStatusListFilter, 'date_closed'


@admin.register(models.BotWork)
class BotWorkAdmin(admin.ModelAdmin):
    list_display = 'id', 'work',
    list_editable = 'work',

    def has_add_permission(self, request):  # позволяет создать только одну модель
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)
