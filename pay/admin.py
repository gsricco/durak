from django.contrib import admin
from .models import Popoln, Currency


@admin.register(Popoln)
class PopolnAdmin(admin.ModelAdmin):
    list_display = 'id', 'user_game', 'sum', 'date', 'status_pay',
    list_filter = 'date',
    search_help_text = 'Поиск по имени игрока'
    search_fields = 'user_game',


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = 'name',
