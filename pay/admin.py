import math

from admin_numeric_filter.admin import (NumericFilterModelAdmin,
                                        RangeNumericFilter)
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum
from django.shortcuts import render
from psycopg2._range import NumericRange
from rangefilter.filters import DateTimeRangeFilter

from .models import BalPay, PayOff, Popoln, RefillBotSum, WithdrawBotSum


class MyChangeList(ChangeList):
    """Пополнение"""

    def get_results(self, *args, **kwargs):
        super(MyChangeList, self).get_results(*args, **kwargs)
        q = self.result_list.filter(status_pay=True).aggregate(asum=Sum('sum'))
        self.sum_count = q['asum']


@admin.register(Popoln)
class PopolnAdmin(NumericFilterModelAdmin):
    def ung(self, obj):
        return obj.user_game.usernamegame

    ung.short_description = 'Имя пользователя в игре'

    list_display = 'id', 'ung', 'user_game', 'sum', 'pay', 'status_pay', 'date',
    list_filter = 'date', ('date', DateTimeRangeFilter), 'status_pay', ('pay', RangeNumericFilter), ('sum', RangeNumericFilter),
    search_fields = 'user_game__username', 'sum'
    search_help_text = 'Поиск по имени игрока или сумме пополнения'
    list_per_page = 100

    def get_changelist(self, request):
        return MyChangeList


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


@admin.register(PayOff)
class PayOffAdmin(admin.ModelAdmin):
    list_display = '__str__', 'work',
    list_editable = 'work',

    def has_add_permission(self, request):  # позволяет создать только одну модель
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)
