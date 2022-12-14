from django.contrib import admin
from .models import Popoln


@admin.register(Popoln)
class PopolnAdmin(admin.ModelAdmin):
    list_display = 'user_game', 'sum', 'date', 'status_pay',
    list_filter = 'date',
    search_help_text = 'Поиск по имени игрока'
    search_fields = 'user_game',
