# from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from hashlib import sha256, md5
# from django.views.decorators.csrf import csrf_exempt
#
#
# # Страница купить
# def buy(request):
#     return render(request, 'pay/sys.html')
#
#
# # Формирование запроса для оплаты
# def popoln(request):
#     mrh_login = "Fotobuka"
#     mrh_pass1 = "uh4ft6593h6tcn"
#     inv_id = '678678'
#     inv_desc = "Товары для животных"
#     out_summ = 100
#     IsTest = 1
#     # Формирование контрольной суммы
#     result_string = "{}:{}:{}:{}".format(mrh_login, out_summ, inv_id, mrh_pass1)
#     SignatureValue = md5(result_string.encode())
#     # crc = sign_hash.hexdigest().upper()
#     url = "https://auth.robokassa.ru/Merchant/Index.aspx?mrh_login={}&out_summ={}&inv_id={}&SignatureValue={}".format(
#         mrh_login, out_summ, inv_id, SignatureValue)
#     # https: // auth.robokassa.ru / Merchant / PaymentForm / FormMS.js?".
#     # "MerchantLogin=$mrh_login&OutSum=$out_summ&InvoiceID=$inv_id"
#
#     if request.method == "POST":
#         # К примеру запись в талицу пополнения
#
#         # Переход на страницу оплаты в робокасса
#         return redirect(url)
#     return render(request, 'popln.html')
#
#
# # Проверка плотежа
# @csrf_exempt
# def res(request):
#     if not request.method == 'POST':
#         return HttpResponse('error')
#     mrh_pass2 = "Ваш пароль 2"
#     # Проверка заголовка авторизации
#     if request.method == 'POST':
#         out_summ = request.POST['OutSum']
#         inv_id = request.POST['InvId']
#         crc = request.POST['SignatureValue']
#         crc = crc.upper()
#         crc = str(crc)
#         # Формирование своей контрольной суммы
#         result_string = "{}:{}:{}".format(out_summ, inv_id, mrh_pass2)
#         sign_hash = sha256(result_string.encode())
#         my_crc = sign_hash.hexdigest().upper()
#         # Проверка сумм
#         if my_crc not in crc:
#             # Ответ ошибки
#             context = "bad sign"
#             return HttpResponse(context)
#         else:
#             # Ответ все верно
#             context = "OK{}".format(inv_id)
#             return HttpResponse(context)
#
#
# # Платеж принят
# @csrf_exempt
# def success(request):
#     if not request.method == 'POST':
#         return HttpResponse('error')
#     mrh_pass1 = "Ваш пароль 1"
#     # Проверка заголовка авторизации
#     if request.method == 'POST':
#         out_summ = request.POST['OutSum']
#         inv_id = request.POST['InvId']
#         crc = request.POST['SignatureValue']
#         crc = crc.upper()
#         crc = str(crc)
#         # Формирование своей контрольной суммы
#         result_string = "{}:{}:{}".format(out_summ, inv_id, mrh_pass1)
#         sign_hash = sha256(result_string.encode())
#         my_crc = sign_hash.hexdigest().upper()
#         # Проверка сумм
#         if my_crc not in crc:
#             # Ошибка
#             context = "bad sign"
#             return HttpResponse(context)
#         else:
#             # Показ страницы успешной оплаты
#             return render(request, 'pay/success.html')
#
#
# # Платеж не принят
# @csrf_exempt
# def fail(request):
#     if request.method == "POST":
#         return render(request, 'pay/fail.html')
import hashlib

from django.shortcuts import redirect
# 3+xJ+XKCLdORi.5
# /xlZ0v8h4Fj_5yp


# # Тут создается форма платежа, она вроде как работает
# def balance(request):
#     merchant_id = '26162' # id магазина
#     secret_word = '3+xJ+XKCLdORi.5' # Секретное слово
#     order_id = '154'
#     order_amount = '10.11'
#     currency = 'RUB'
#     sign = hashlib.md5(f'{merchant_id}:{order_amount}:{secret_word}:{currency}:{order_id}'.encode('utf-8')).hexdigest()
#
#     # context = {
#     #     'm': merchant_id,
#     #     'oa': order_amount,
#     #     'o': order_id,
#     #     's': sign,
#     #     'currency': currency
#     # }
#     # https: // pay.freekassa.ru /?m = & oa = 1000 & i = & currency = RUB & em = & phone = & o = 123 & pay = PAY & s = e723c585cb601241c5bb5727efa16b08
#     return redirect(f'https://pay.freekassa.ru/?m={merchant_id}&oa={order_amount}&currency={currency}&o={order_id}&s={sign}')
#     # return redirect(f'https://pay.freekassa.ru/?m={merchant_id}&oa={order_amount}&i=&currency={currency}&em=&phone=&o={order_id}&pay=PAY&s={sign}')




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
#         'i': 4,
#         'email': 'olegpustovalov220@gmail.com',
#         'ip': '37.214.41.80',
#         'amount': order_amount,
#         'currency': currency,
#     }
#     pa = dict(sorted([(key, val) for key, val in params.items()], key=lambda x:x[0]))
#     api_key = '064d42e30564b0fd0dd93a0005f0fd31'
#     ma = '|'.join(str(val) for val in pa.values())+api_key
#     sign = hashlib.sha256(ma.encode()).hexdigest()
#     print(sign, '**********')
#     params['signature']=sign
#     body = '&'.join(f'{key}={val}' for key, val in params.items())
#     print(body, 'bodybodybodybodybody')
#     return redirect(f'https://api.freekassa.ru/v1/orders/create/?'+body)



# Тут создается форма платежа, она вроде как работает
def balance(request):
    merchant_id = '26162' # id магазина
    secret_word = '3+xJ+XKCLdORi.5' # Секретное слово
    order_id = '154'
    order_amount = '10.11'
    currency = 'RUB'
    params = {
        'shopId': merchant_id,
        'nonce': order_id,
        # 'i': 4,
        # 'email': 'olegpustovalov220@gmail.com',
        # 'ip': '37.214.41.80',
        # 'amount': order_amount,
        # 'currency': currency,
    }
    pa = dict(sorted([(key, val) for key, val in params.items()], key=lambda x:x[0]))
    api_key = '064d42e30564b0fd0dd93a0005f0fd31'
    ma = '|'.join(str(val) for val in pa.values())+api_key
    sign = hashlib.sha256(ma.encode()).hexdigest()
    print(sign, '**********')
    params['signature']=sign
    body = '&'.join(f'{key}={val}' for key, val in params.items())
    print(body, 'bodybodybodybodybody')
    return redirect(f'https://api.freekassa.ru/v1/balance?'+body)


# # Суда приходят данные с URL оповещения. Вот тут и проблема в том что в переменную amount ничего не присваивается.
# def payment_alerts(request):
#     amount = request.GET.get("AMOUNT")
#     current_user = UserProfile.objects.get(pk=request.user.id)
#     current_user.balance = current_user.balance + amount
#     current_user.save()
#
#
# # При успешной оплате
# def payment_success(request):
#     return render(request, 'main/payment/success.html')
#
#
# # При ошибке в оплате
# def payment_error(request):
#     return render(request, 'main/payment/error.html')