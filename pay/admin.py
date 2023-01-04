import math

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import BaseConstraint
from django.http import HttpResponse
from django.shortcuts import render
from psycopg2._range import NumericRange

from .models import Popoln, BalPay, RefillBotSum, WithdrawBotSum


@admin.register(Popoln)
class PopolnAdmin(admin.ModelAdmin):
    list_display = 'id', 'user_game', 'sum', 'date', 'status_pay',
    list_filter = 'status_pay', 'date',
    search_fields = 'user_game__username', 'sum'
    search_help_text = 'Поиск по имени игрока или сумме пополнения'


@admin.register(BalPay)
class BalPayAdmin(admin.ModelAdmin):
    list_display = "__str__", "range_sum", "range_credits", "conversion_coef"
    fields = "range_sum", "conversion_coef", "range_credits",
    readonly_fields = "range_credits",

    def add_view(self, request, form_url="", extra_context=None):
        if request.POST:
            start = int(request.POST.get('range_sum_0'))
            end = int(request.POST.get('range_sum_1'))
            if BalPay.objects.filter(range_sum__contains=NumericRange(start, end)).exists():
                mess = 'Такой диапазон уже существует, выберите другой'
                context = {"mess": mess}
                return render(request, 'admin/baypal.html', context)
        return super().add_view(request)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if request.POST:
            start = int(request.POST.get('range_sum_0'))
            end = int(request.POST.get('range_sum_1'))
            if BalPay.objects.filter(range_sum__contains=NumericRange(start, end)).exclude(id=object_id).exists():
                mess = 'Такой диапазон уже существует, выберите другой'
                context = {"mess": mess}
                return render(request, 'admin/baypal.html', context)
        return super().change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        start = obj.range_sum.lower
        end = obj.range_sum.upper
        if start and end:
            start_value = math.floor((start * obj.conversion_coef) / 1000) * 1000
            if next_range := BalPay.objects.filter(range_sum__gt=NumericRange(start, end)).first():
                end_value = math.floor((end * next_range.conversion_coef)/1000) * 1000
                obj.range_credits = NumericRange(start_value, end_value)
            else:
                end_value = math.floor((end * obj.conversion_coef)/1000) * 1000
                obj.range_credits = NumericRange(start_value, end_value)
        obj.save()


@admin.register(RefillBotSum)
class RefillBotSumAdmin(admin.ModelAdmin):
    list_display = 'id', 'credits', 'text'
    list_editable = 'credits', 'text'


@admin.register(WithdrawBotSum)
class WithdrawBotSumAdmin(admin.ModelAdmin):
    list_display = 'id', 'credits', 'text'
    list_editable = 'credits', 'text'
