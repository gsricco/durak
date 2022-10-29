from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = 'username', 'experience', 'level', 'balance', 'email', 'ban'
    list_editable = 'ban',
    list_filter = 'ban',
    search_fields = 'username',


