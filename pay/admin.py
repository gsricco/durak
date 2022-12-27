from django.contrib import admin
from .models import Popoln, BalPay


@admin.register(Popoln)
class PopolnAdmin(admin.ModelAdmin):
    list_display = 'id', 'user_game', 'sum', 'date', 'status_pay',
    list_filter = 'status_pay', 'date',
    search_fields = 'user_game__username', 'sum'
    search_help_text = 'Поиск по имени игрока или суммы пополнения'


@admin.register(BalPay)
class BalPayAdmin(admin.ModelAdmin):
    list_display = 'id', 'pay_sum', 'credit_range'
    list_editable = 'pay_sum', 'credit_range'
