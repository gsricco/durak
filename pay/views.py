import hashlib

import requests
from django.shortcuts import redirect, get_object_or_404
from rest_framework import response, status
from rest_framework.decorators import api_view
from accaunts.models import DetailUser
from configs.settings import MERCHANT_ID, SECRET_WORD
from pay.models import Popoln


# Cоздается форма платежа
def rub_to_pay(rub):
    """Креды, полученные за реальные деньг"""
    if 0 <= rub <= 109:
        return rub * 725
    if 110 <= rub <= 179:
        return rub * 910
    if 180 <= rub <= 239:
        return rub * 1389
    if 240 <= rub <= 459:
        return rub * 2084
    if 460 <= rub <= 1274:
        return rub * 2174
    if 1275 <= rub:
        return rub * 2353


def balance(request):
    if not request.user.is_authenticated:
        return redirect('/')
    merchant_id = MERCHANT_ID  # ID Вашего магазина
    secret_word = SECRET_WORD  # Секретное слово
    order_amount = request.GET.get('sum_rub', '0')
    pay = rub_to_pay(int(order_amount))
    currency = 'RUB'  # RUB,USD,EUR,UAH,KZT
    user_pay = Popoln(sum=order_amount, pay=pay, user_game=request.user)
    user_pay.url_pay = request.META.get('HTTP_REFERER')
    user_pay.save()
    order_id = user_pay.pk
    sign = hashlib.md5(f'{merchant_id}:{order_amount}:{secret_word}:{currency}:{order_id}'.encode('utf-8')).hexdigest()
    return redirect(
        f'https://pay.freekassa.ru/?m={merchant_id}&oa={order_amount}&currency={currency}&o={order_id}&pay=PAY&s={sign}')
    # return redirect(f'https://pay.freekassa.ru/?m={merchant_id}&oa={order_amount}&i=&currency={currency}&em=&phone=&o={order_id}&pay=PAY&s={sign}')


# MERCHANT_ID=26363&AMOUNT=100&intid=2022&MERCHANT_ORDER_ID=202220&P_EMAIL=olegpustovalov220@gmail.com&P_PHONE=71231231212&CUR_ID=4&payer_account=123456xxxxxx1234&us_field1=123&us_field2=321&SIGN=f1e7d50ae605effd7cd782e4f2e8fc42
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
    print(sign, 'signsignsignsign')
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
    order.intid = intid
    order.save()
    det_user = DetailUser.objects.get(user=order.user_game)
    det_user.balance += order.pay
    print(det_user)
    det_user.save()
    return response.Response(status=status.HTTP_200_OK, data={})



# # Тут создается форма платежа
# def balance(request):
#     merchant_id = MERCHANT_ID  # ID Вашего магазина
#     secret_word = SECRET_WORD  # Секретное слово
#     order_id = '154'
#     order_amount = '100.01'
#     currency = 'RUB'
#     params = {
#         'shopId': merchant_id,
#         'nonce': order_id,
#         'i': 4,
#         'email': 'olegpustovalov220@gmail.com',
#         'ip': '37.214.41.80',
#         'amount': order_amount,
#         'currency': currency,
#     }
#     pa = dict(sorted([(key, val) for key, val in params.items()], key=lambda x: x[0]))
#     api_key = '93cbd088d165c7da268bff505f77acf0'
#     ma = '|'.join(str(val) for val in pa.values()) + api_key
#     sign = hashlib.sha256(ma.encode()).hexdigest()
#     print(sign, '**********')
#     params['signature'] = sign
#     body = '&'.join(f'{key}={val}' for key, val in params.items())
#     print(body, 'bodybodybodybodybody')
#     return redirect(f'https://api.freekassa.ru/v1/orders/create/?' + body)


# # Тут создается форма платежа, она вроде как работает
# def balance(request):
#     merchant_id = '26162' # id магазина
#     secret_word = '3+xJ+XKCLdORi.5' # Секретное слово
#     order_id = '154'
#     order_amount = '10.11'
#     currency = 'RUB'
#     params = {
#         'shopId': merchant_id,
#         'nonce': order_id,
#         # 'i': 4,
#         # 'email': 'olegpustovalov220@gmail.com',
#         # 'ip': '37.214.41.80',
#         # 'amount': order_amount,
#         # 'currency': currency,
#     }
#     pa = dict(sorted([(key, val) for key, val in params.items()], key=lambda x:x[0]))
#     api_key = '064d42e30564b0fd0dd93a0005f0fd31'
#     ma = '|'.join(str(val) for val in pa.values())+api_key
#     sign = hashlib.sha256(ma.encode()).hexdigest()
#     print(sign, '**********')
#     params['signature']=sign
#     body = '&'.join(f'{key}={val}' for key, val in params.items())
#     print(body, 'bodybodybodybodybody')
#     return redirect(f'https://api.freekassa.ru/v1/balance?'+body)


# # Тут создается форма платежа, она вроде как работает
# def balance(request):
#     merchant_id = '26363'  # id магазина
#     secret_word = 'Oleg1988'  # Секретное слово
#     order_id = '154'
#     order_amount = '10.11'
#     currency = 'RUB'
#     # ip = '37.214.41.80'
#     # email = 'olegpustovalov220@gmail.com'
#     params = {
#         'shopId': merchant_id,
#         'nonce': order_id,
#         'i': 4,
#         'email': 'olegpustovalov220@gmail.com',
#         'ip': '37.214.41.80',
#         'amount': order_amount,
#         'currency': currency,
#     }
#     pa = dict(sorted([(key, val) for key, val in params.items()], key=lambda x: x[0]))
#     api_key = '9097f84c55ec99807ed1138b1bc94f91'
#     ma = '|'.join(str(val) for val in pa.values()) + api_key
#     sign = hashlib.sha256(ma.encode()).hexdigest()
#     params['signature'] = sign
#     req = requests.post(f'https://api.freekassa.ru/v1/orders/create', json=params)
#     print(req.json(), '*****************')

# body = '&'.join(f'{key}={val}' for key, val in params.items())
# print(body, 'bodybodybodybodybody')
# return redirect(f'https://api.freekassa.ru/v1/balance?' + body)


# # Суда приходят данные с URL оповещения.
# def payment_alerts(request):
#     amount = request.GET.get("AMOUNT")
#     current_user = Popoln.objects.get(pk=request.user.id)
#     current_user.balance = current_user.balance + amount
#     current_user.save()


# # При успешной оплате
# def payment_success(request):
#     user_pay = Popoln.objects.filter(status_pay=True)
#     cotext = {
#         'user_pay': user_pay,
#     }
#     return render(request, 'new_profil.html', cotext)
#
#
# # При ошибке в оплате
# def payment_error(request):
#     user_pay = Popoln.objects.filter(status_pay=False)
#     cotext = {
#         'user_pay': user_pay,
#     }
#     return render(request, 'new_profil.html', cotext)

# MERCHANT_ID=123&
# AMOUNT=100&intid=123456&
# MERCHANT_ORDER_ID=test_order&
# P_EMAIL=test_user@test_site.ru&
# P_PHONE=71231231212&CUR_ID=4&
# payer_account=123456xxxxxx1234&
# us_field1=123&
# us_field2=321&
# SIGN=68GH247bb77e0ab49f6e429b86bc3e2f
