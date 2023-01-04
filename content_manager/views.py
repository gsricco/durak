from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from social_django.models import UserSocialAuth
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Value, F

from accaunts.forms import UserEditName
from accaunts.models import DetailUser, Level, CustomUser, UserAgent, UserIP, DayHash, UserBet, ReferalUser
from pay.models import Popoln, RefillBotSum, WithdrawBotSum
from bot_payment.models import RefillRequest, WithdrawalRequest
from .models import FAQ, SiteContent, ShowRound, DurakNickname


def add_pay_buttons(context):
    """
    Добавляет в контекст данные для создания кнопок для ввода/вывода
    кредитов через бота
    """
    context['refill_buttons'] = RefillBotSum.objects.all()
    context['withdraw_buttons'] = WithdrawBotSum.objects.all()
    context['range_refill'] = [f"{i}:{i+2}" for i in range(0,len(context['refill_buttons']),2)]
    context['range_withdraw'] = [f"{i}:{i+2}" for i in range(0,len(context['withdraw_buttons']),2)]


def index(request):
    """ГЛАВНАЯ (логика при оплатах через freekassa)"""
    sitecontent = SiteContent.objects.all()
    show_modal = False
    if request.user.is_authenticated:
        if MERCHANT_ORDER_ID := request.GET.get('MERCHANT_ORDER_ID'):
            try:
                pay = Popoln.objects.get(pk=MERCHANT_ORDER_ID)
            except ObjectDoesNotExist:
                pass
            else:
                if pay.user_game == request.user and pay.url_ok:
                    show_modal = True
                    pay.url_ok = False
                    pay.save()
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
    context['show_modal'] = show_modal
    add_pay_buttons(context)
    if show_modal:
        context['pay_modal'] = pay
    return render(request, 'new_index.html', context)


def bonus_currency(request):
    """FREE"""
    sitecontent = SiteContent.objects.all()
    sitecontent2 = sitecontent.first()
    if request.user.is_authenticated:
        detail_user = DetailUser.objects.get(user_id=request.user.id)
        level_data = Level.objects.get(pk=request.user.level.pk)
        context = {
            'sitecontent': sitecontent,
            'sitecontent2': sitecontent2,
            'detail_user': detail_user,
            'level_data': level_data,
            'title': 'Free',
        }
    else:
        context = {
            'sitecontent': sitecontent,
            'sitecontent2': sitecontent2,
            'title': 'Free',
        }
    add_pay_buttons(context)
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
    add_pay_buttons(context)
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
    add_pay_buttons(context)
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

    paginator = Paginator(day_hashes, 7)
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

    add_pay_buttons(context)

    return render(request, 'new_honesty_fairness.html', context)


def profil(request):
    """ПРОФИЛЬ"""
    sitecontent = SiteContent.objects.all()
    if request.user.is_authenticated:
        # Смена имени для пользователя
        user_ed = CustomUser.objects.get(username=request.user)
        if request.method == 'POST':
            form_user = UserEditName(request.POST)
            if form_user.is_valid():
                user_ed.username = form_user.cleaned_data['username']
                user_ed.save()
                return redirect('profil')
        else:
            initial_data = {'username': user_ed.username}
            form_user = UserEditName(initial_data)
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
        # логика для отображения транзакций
        popoln = Popoln.objects.filter(user_game=request.user, status_pay=True)\
            .annotate(tr_type=Value('Пополнение деньгами'), tr_plus=Value(True), round_r=Value(0))\
            .values('date', 'pay', 'tr_type', 'tr_plus', 'sum', 'round_r')
        user_bets = UserBet.objects.filter(user=request.user)\
            .annotate(tr_type=Value('Ставка'), tr_plus=F('win'), round_r=F('round_number'))\
            .values('date', 'sum_win', 'tr_type', 'tr_plus', 'sum', 'round_r')
        refill = RefillRequest.objects.filter(user=request.user, status='succ')\
            .annotate(tr_type=Value('Пополнение кредитами из игры'), tr_plus=Value(True), round_r=Value(0))\
            .values('date_closed', 'amount', 'tr_type', 'tr_plus', 'balance', 'round_r')
        withdraw = WithdrawalRequest.objects.filter(user=request.user, status='succ')\
            .annotate(tr_type=Value('Вывод кредитов в игру'), tr_plus=Value(False),  round_r=Value(0))\
            .values('date_closed', 'balance', 'tr_type', 'tr_plus', 'amount', 'round_r')
        referal = ReferalUser.objects.filter(user_with_bonus=request.user)\
            .annotate(tr_type=Value('Активация промокода'), tr_plus=Value(True), round_r=Value(0))\
            .values('date', 'bonus_sum', 'tr_type', 'tr_plus', 'user_with_bonus', 'round_r')
        transactions = popoln.union(user_bets, refill, withdraw, referal).order_by('-date')
        paginator = Paginator(transactions, 8)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        page_paginated = True if page_number else False
        show_round = ShowRound.objects.filter().only("show").first()
        mod_nick = ''
        if mod_nick := DurakNickname.objects.first():
            mod_nick = mod_nick.nickname
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            'level_data': level_data,
            'social_google': social_google,
            'social_vk': social_vk,
            'form_user': form_user,
            'user_ed': user_ed,
            'title': 'Профиль',
            'page_obj': page_obj,
            'page_paginated': page_paginated,
            'modal_nickname': mod_nick,
            'show_round': show_round.show
            # 'paginator': paginator,
        }
    else:
        level_data = Level.objects.get(level=1)
        context = {
            'sitecontent': sitecontent,
            'level_data': level_data,
            'title': 'Профиль',
        }
    add_pay_buttons(context)
    return render(request, 'new_profil.html', context)
