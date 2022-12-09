from django.shortcuts import render, redirect
from django.http import HttpResponse
from hashlib import sha256, md5
from django.views.decorators.csrf import csrf_exempt


# Страница купить
def buy(request):
    return render(request, 'robokassa_pay/sys.html')


# Формирование запроса для оплаты
def popoln(request):
    mrh_login = "Fotobuka"
    mrh_pass1 = "uh4ft6593h6tcn"
    inv_id = '678678'
    inv_desc = "Товары для животных"
    out_summ = 100
    IsTest = 1
    # Формирование контрольной суммы
    result_string = "{}:{}:{}:{}".format(mrh_login, out_summ, inv_id, mrh_pass1)
    SignatureValue = md5(result_string.encode())
    # crc = sign_hash.hexdigest().upper()
    url = "https://auth.robokassa.ru/Merchant/Index.aspx?mrh_login={}&out_summ={}&inv_id={}&SignatureValue={}".format(
        mrh_login, out_summ, inv_id, SignatureValue)
    # https: // auth.robokassa.ru / Merchant / PaymentForm / FormMS.js?".
    # "MerchantLogin=$mrh_login&OutSum=$out_summ&InvoiceID=$inv_id"

    if request.method == "POST":
        # К примеру запись в талицу пополнения

        # Переход на страницу оплаты в робокасса
        return redirect(url)
    return render(request, 'popln.html')


# Проверка плотежа
@csrf_exempt
def res(request):
    if not request.method == 'POST':
        return HttpResponse('error')
    mrh_pass2 = "Ваш пароль 2"
    # Проверка заголовка авторизации
    if request.method == 'POST':
        out_summ = request.POST['OutSum']
        inv_id = request.POST['InvId']
        crc = request.POST['SignatureValue']
        crc = crc.upper()
        crc = str(crc)
        # Формирование своей контрольной суммы
        result_string = "{}:{}:{}".format(out_summ, inv_id, mrh_pass2)
        sign_hash = sha256(result_string.encode())
        my_crc = sign_hash.hexdigest().upper()
        # Проверка сумм
        if my_crc not in crc:
            # Ответ ошибки
            context = "bad sign"
            return HttpResponse(context)
        else:
            # Ответ все верно
            context = "OK{}".format(inv_id)
            return HttpResponse(context)


# Платеж принят
@csrf_exempt
def success(request):
    if not request.method == 'POST':
        return HttpResponse('error')
    mrh_pass1 = "Ваш пароль 1"
    # Проверка заголовка авторизации
    if request.method == 'POST':
        out_summ = request.POST['OutSum']
        inv_id = request.POST['InvId']
        crc = request.POST['SignatureValue']
        crc = crc.upper()
        crc = str(crc)
        # Формирование своей контрольной суммы
        result_string = "{}:{}:{}".format(out_summ, inv_id, mrh_pass1)
        sign_hash = sha256(result_string.encode())
        my_crc = sign_hash.hexdigest().upper()
        # Проверка сумм
        if my_crc not in crc:
            # Ошибка
            context = "bad sign"
            return HttpResponse(context)
        else:
            # Показ страницы успешной оплаты
            return render(request, 'robokassa_pay/success.html')


# Платеж не принят
@csrf_exempt
def fail(request):
    if request.method == "POST":
        return render(request, 'robokassa_pay/fail.html')
