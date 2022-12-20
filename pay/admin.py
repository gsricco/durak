from django.contrib import admin
from .models import Popoln


@admin.register(Popoln)
class PopolnAdmin(admin.ModelAdmin):
    list_display = 'id', 'user_game', 'sum', 'date', 'status_pay',
    list_filter = 'status_pay', 'date',
    search_fields = 'user_game__username', 'sum'
    search_help_text = 'Поиск по имени игрока или суммы пополнения'
