from django.shortcuts import render, redirect
from social_django.models import UserSocialAuth

from accaunts.forms import UserEditName
from accaunts.models import DetailUser, Level, CustomUser, UserAgent
from .models import FAQ, SiteContent


def index(request):
    """ГЛАВНАЯ"""
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        detail_user = DetailUser.objects.get(user_id=request.user.id)
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
        detail_user = DetailUser.objects.get(user_id=request.user.id)
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
        detail_user = DetailUser.objects.get(user_id=request.user.id)
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
        detail_user = DetailUser.objects.get(user_id=request.user.id)
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
        detail_user = DetailUser.objects.get(user_id=request.user.id)
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
    # form_user = UserEditName(request.POST or None)
    # print(request.method, 'methodsa')
    # if request.method == 'POST':
    #     print(request.POST, '123123')
    #     if form_user.is_valid():
    #         print(form_user.data, 'штаффыв')
    #         form_user.save()
    #         return render(request, 'profil.html')
    # else:
    #     print('OK')
    if request.user.is_authenticated:
        agent = (request.META['HTTP_USER_AGENT'])
        us = CustomUser.objects.get(username=request.user)
        user_agent, created = UserAgent.objects.get_or_create(user=us, useragent=agent)
        print(user_agent)
        detail_user = DetailUser.objects.get(user_id=request.user.id)
        level_data = Level.objects.get(pk=detail_user.level_id)
        if UserSocialAuth.objects.filter(user_id=request.user.id, provider='google-oauth2'):
            social_google = True
        else:
            social_google = False
        if UserSocialAuth.objects.filter(user_id=request.user.id, provider='vk-oauth2'):
            social_vk = True
        else:
            social_vk = False
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            'level_data': level_data,
            "faq": faq,
            'social_google': social_google,
            'social_vk': social_vk,
            # 'form_user': form_user,
        }
    else:
        level_data = Level.objects.get(level=1)
        context = {
            'sitecontent': sitecontent,
            "faq": faq,
            'level_data': level_data,
            # 'form_user': form_user,
        }
    return render(request, 'profil.html', context)


def update_profil(request):
    form_user = UserEditName(request.POST or None)
    print(form_user.data, 'methodsa')
    if request.method == 'POST':
        print(form_user, '++++')
        if form_user.is_valid():
            form_user.save()
            return render(request, 'test.html')
    else:
        print('OK')
    context = {
        'form_user': form_user,
    }
    return render(request, 'test.html', context)
