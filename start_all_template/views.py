from django.shortcuts import render

from start_all_template.models import FAQ, SiteContent


def index(request):
    """ГЛАВНАЯ"""
    sitecontent = SiteContent.objects.all()
    context = {
        'sitecontent': sitecontent,
    }
    return render(request, 'index.html', context)


def bonus_currency(request):
    """FREE"""
    sitecontent = SiteContent.objects.all()
    context = {
        'sitecontent': sitecontent,
    }
    return render(request, 'bonus-currency.html', context)


def contact(request):
    """КОНТАКТЫ"""
    sitecontent = SiteContent.objects.all()
    context = {
        'sitecontent': sitecontent,
    }
    return render(request, 'contact.html', context)


def faq(request):
    """ПОМОЩЬ"""
    faq = FAQ.objects.filter(is_active=True)
    sitecontent = SiteContent.objects.all()
    context = {
        'faq': faq,
        'sitecontent': sitecontent,
    }
    return render(request, 'faq.html', context)


def honesty(request):
    """ЧЕСТНОСТЬ"""
    sitecontent = SiteContent.objects.all()
    context = {
        'faq': faq,
        'sitecontent': sitecontent,
    }
    return render(request, 'honesty.html', context)


def profil(request):
    """ПРОФИЛЬ"""
    sitecontent = SiteContent.objects.all()
    context = {
        'sitecontent': sitecontent,
    }
    return render(request, 'profil.html', context)
