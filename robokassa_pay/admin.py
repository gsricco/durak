from django.contrib import admin
from .models import Popoln


@admin.register(Popoln)
class PopolnAdmin(admin.ModelAdmin):
    list_display = 'id', 'sum'
