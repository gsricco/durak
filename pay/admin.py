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
    list_display = '__str__', 'range_sum', 'conversion_coef'

    def add_view(self, request, form_url="", extra_context=None):
        if request.POST:
            start = int(request.POST.get('range_sum_0'))
            end = int(request.POST.get('range_sum_1'))
            print(start, end)
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


@admin.register(RefillBotSum)
class RefillBotSumAdmin(admin.ModelAdmin):
    list_display = 'id', 'credits', 'text'
    list_editable = 'credits', 'text'


@admin.register(WithdrawBotSum)
class WithdrawBotSumAdmin(admin.ModelAdmin):
    list_display = 'id', 'credits', 'text'
    list_editable = 'credits', 'text'
