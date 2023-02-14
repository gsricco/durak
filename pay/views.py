import hashlib
import math

from django.shortcuts import get_object_or_404, redirect
from psycopg2.extras import NumericRange
from rest_framework import response, status
from rest_framework.decorators import api_view

from accaunts.models import DetailUser
from configs.settings import MERCHANT_ID, SECRET_WORD
from pay.models import BalPay, PayOff, Popoln


# Создается форма платежа
def rub_to_pay(rub):
    """Креды, полученные за реальные деньги"""
    try:
        c_r = BalPay.objects.get(range_sum__contains=NumericRange(rub, rub + 1))
    except BalPay.DoesNotExist or BalPay.MultipleObjectsReturned:
        return 0
    return math.floor((rub * c_r.conversion_coef) / 1000) * 1000


def virtual_money_to_rub(virtual_money):
    """Расчёт денег за кредиты"""
    try:
        creds = BalPay.objects.get(range_credits__contains=NumericRange(virtual_money, virtual_money+1))
    except (BalPay.DoesNotExist or BalPay.MultipleObjectsReturned) as error:
        return 0
    return math.ceil(virtual_money / creds.conversion_coef)


def balance(request):
    if not request.user.is_authenticated:
        return redirect('/')
    merchant_id = MERCHANT_ID  # ID Вашего магазина
    secret_word = SECRET_WORD  # Секретное слово
    order_amount = request.GET.get('sum_rub', '0')
    pay = rub_to_pay(int(order_amount))
    currency = 'RUB'  # RUB,USD,EUR,UAH,KZT
    if PayOff.objects.filter(work=False):
        i = request.GET.get('paymentSystem')
    else:
        i = 1
    user_pay = Popoln(sum=order_amount, pay=pay, user_game=request.user)
    user_pay.url_pay = request.META.get('HTTP_REFERER')
    user_pay.save()
    order_id = user_pay.pk
    sign = hashlib.md5(f'{merchant_id}:{order_amount}:{secret_word}:{currency}:{order_id}'.encode('utf-8')).hexdigest()
    return redirect(
        f'https://pay.freekassa.ru/?m={merchant_id}&oa={order_amount}&currency={currency}&o={order_id}&pay=PAY&s={sign}&i={i}')


@api_view(['GET'])
def pay_user(request):
    """Логика оплаты"""
    merchant_id = MERCHANT_ID  # ID Вашего магазина
    secret_word = SECRET_WORD  # Секретное слово
    ip = (request.META['REMOTE_ADDR'])
    order_amount = request.GET.get('AMOUNT', '')
    order_id = request.GET.get('MERCHANT_ORDER_ID', '')
    intid = request.GET.get('intid', '')
    sign = hashlib.md5(f'{merchant_id}:{order_amount}:{secret_word}:{order_id}'.encode('utf-8')).hexdigest()
    po = request.GET.get('SIGN')
    if sign != po:
        return response.Response(status=status.HTTP_400_BAD_REQUEST)
    if ip in ['168.119.157.136', '168.119.60.227', '138.201.88.124', '178.154.197.79']:  # проверка ip
        return response.Response(status=status.HTTP_403_FORBIDDEN)
    # r = requests.post(f'https://api.freekassa.ru/v1/orders', json={})
    order = get_object_or_404(Popoln, pk=order_id)
    if order.status_pay:
        return response.Response(status=status.HTTP_412_PRECONDITION_FAILED, data={})
    order.status_pay = True
    order.url_ok = True
    order.intid = intid
    order.save()
    det_user = DetailUser.objects.get(user=order.user_game)
    det_user._reserve += order.pay
    det_user.balance += order.pay
    det_user.save()
    return response.Response(status=status.HTTP_200_OK, data={})
