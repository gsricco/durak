from django.shortcuts import render

from accaunts.models import DetailUser, Level
from .models import FAQ, SiteContent


def index(request):
    """ГЛАВНАЯ"""
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        detail_user = DetailUser.objects.get(pk=request.user.id)
        level_data = Level.objects.get(pk=detail_user.level_id)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            'level_data': level_data,
        }
    else:
        context = {
            'sitecontent': sitecontent,
        }
    return render(request, 'index.html', context)


def bonus_currency(request):
    """FREE"""
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        detail_user = DetailUser.objects.get(pk=request.user.id)
        level_data = Level.objects.get(pk=detail_user.level_id)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            'level_data': level_data,
        }
    else:
        context = {
            'sitecontent': sitecontent,
        }
    return render(request, 'bonus-currency.html', context)


def contact(request):
    """КОНТАКТЫ"""
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        detail_user = DetailUser.objects.get(pk=request.user.id)
        level_data = Level.objects.get(pk=detail_user.level_id)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            'level_data': level_data,
        }
    else:
        context = {
            'sitecontent': sitecontent,
        }
    return render(request, 'contact.html', context)


def faq(request):
    """ПОМОЩЬ"""
    faq = FAQ.objects.filter(is_active=True)
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        detail_user = DetailUser.objects.get(pk=request.user.id)
        level_data = Level.objects.get(pk=detail_user.level_id)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            'level_data': level_data,
            "faq": faq,
        }
    else:
        context = {
            'sitecontent': sitecontent,
            "faq": faq,
        }
    return render(request, 'faq.html', context)


def honesty(request):
    """ЧЕСТНОСТЬ"""
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        detail_user = DetailUser.objects.get(pk=request.user.id)
        level_data = Level.objects.get(pk=detail_user.level_id)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            'level_data': level_data,
            "faq": faq,
        }
    else:
        context = {
            'sitecontent': sitecontent,
            "faq": faq,
        }
    return render(request, 'honesty.html', context)


def profil(request):
    """ПРОФИЛЬ"""
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        detail_user = DetailUser.objects.get(pk=request.user.id)
        level_data = Level.objects.get(pk=detail_user.level_id)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            'level_data': level_data,
            "faq": faq,
        }
    else:
        context = {
            'sitecontent': sitecontent,
            "faq": faq,
        }
    return render(request, 'profil.html', context)

