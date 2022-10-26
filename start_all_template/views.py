from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def index123(request):
    return render(request, 'index123.html')


def bonus_currency(request):
    return render(request, 'bonus-currency.html')


def contact(request):
    return render(request, 'contact.html')


def faq(request):
    return render(request, 'faq.html')


def honesty(request):
    return render(request, 'honesty.html')


def profil(request):
    return render(request, 'profil.html')
