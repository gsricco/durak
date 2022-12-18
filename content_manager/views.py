from django.shortcuts import render, redirect
from social_django.models import UserSocialAuth
from django.core.paginator import Paginator
from django.utils import timezone

from accaunts.forms import UserEditName
from accaunts.models import DetailUser, Level, CustomUser, UserAgent, UserIP, DayHash
from .models import FAQ, SiteContent


def index(request):
    """ГЛАВНАЯ"""
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        detail_user = DetailUser.objects.get(user_id=request.user.id)
        level_data = Level.objects.get(pk=request.user.level.pk)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            'level_data': level_data,
            'title': 'Рулетка',
        }
    else:
        context = {
            'sitecontent': sitecontent,
            'title': 'Рулетка',
        }
    return render(request, 'new_index.html', context)


def bonus_currency(request):
    """FREE"""
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        detail_user = DetailUser.objects.get(user_id=request.user.id)
        level_data = Level.objects.get(pk=request.user.level.pk)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            'level_data': level_data,
            'title': 'Free',
        }
    else:
        context = {
            'sitecontent': sitecontent,
            'title': 'Free',
        }
    return render(request, 'new_bonus-currency.html', context)


def contact(request):
    """КОНТАКТЫ"""
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        detail_user = DetailUser.objects.get(user_id=request.user.id)
        level_data = Level.objects.get(pk=request.user.level.pk)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            'level_data': level_data,
            'title': 'Контакты',
        }
    else:
        context = {
            'sitecontent': sitecontent,
            'title': 'Контакты',
        }
    return render(request, 'new_contact.html', context)


def faq(request):
    """ПОМОЩЬ"""
    faq = FAQ.objects.filter(is_active=True)
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        detail_user = DetailUser.objects.get(user_id=request.user.id)
        level_data = Level.objects.get(pk=request.user.level.pk)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            'level_data': level_data,
            "faq": faq,
            'title': 'Помощь',
        }
    else:
        context = {
            'sitecontent': sitecontent,
            "faq": faq,
            'title': 'Помощь',
        }
    return render(request, 'new_faq.html', context)


def honesty(request):
    """ЧЕСТНОСТЬ"""
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        detail_user = DetailUser.objects.get(user_id=request.user.id)
        level_data = Level.objects.get(pk=request.user.level.pk)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            'level_data': level_data,
            'title': 'Честность',
        }
    else:
        context = {
            'sitecontent': sitecontent,
            'title': 'Честность',
        }
    # получение хешей для отображения
    day_hashes = DayHash.objects.all()

    paginator = Paginator(day_hashes, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if page_obj.number <= 2:
        page_range = range(1, 6)
    elif page_obj.number >= paginator.num_pages - 1:
        page_range = range(max(paginator.num_pages - 4, 1), paginator.num_pages + 1)
    else: 
        page_range = range(page_obj.number - 2, page_obj.number + 3)

    context['page_obj'] = page_obj
    context['paginator'] = paginator
    context['today'] = timezone.now().date()
    context['page_range'] = page_range

    return render(request, 'new_honesty_fairness.html', context)


def profil(request):
    """ПРОФИЛЬ"""
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        form_user = UserEditName(request.POST)  # Смена имени для пользователя
        user_ed = CustomUser.objects.get(username=request.user)
        if request.method == 'POST' and form_user.is_valid():
            user_ed.username = form_user.cleaned_data['username']
            user_ed.save()
            return redirect('profil')
        agent = (request.META['HTTP_USER_AGENT'])  # Информация пользователя useragent
        ip = (request.META['REMOTE_ADDR'])  # Информация пользователя ip
        us = CustomUser.objects.get(username=request.user)
        user_agent, created = UserAgent.objects.get_or_create(user=us, useragent=agent)
        user_ip, created = UserIP.objects.get_or_create(user=us, userip=ip)
        # print(user_agent, ' - USER AGENT')
        # print(user_ip, ' - IP USER')
        detail_user = DetailUser.objects.get(user_id=request.user.id)
        level_data = Level.objects.get(pk=request.user.level.pk)
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
            'social_google': social_google,
            'social_vk': social_vk,
            'form_user': form_user,
            'user_ed': user_ed,
            'title': 'Профиль',
        }
    else:
        level_data = Level.objects.get(level=1)
        context = {
            'sitecontent': sitecontent,
            'level_data': level_data,
            'title': 'Профиль',
        }
    return render(request, 'new_profil.html', context)
