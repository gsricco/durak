import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import CharField, Count, F, IntegerField, Sum, Value
from django.shortcuts import redirect, render
from django.utils import timezone
from social_django.models import UserSocialAuth

from accaunts.forms import UserEditName
from accaunts.models import (BonusVKandYoutube, CustomUser, DayHash,
                             DetailUser, FreeBalanceHistory, ItemForUser,
                             Level, ReferalUser, UserAgent, UserBet, UserIP)
from bot_payment.models import RefillRequest, WithdrawalRequest
from pay.models import Popoln, RefillBotSum, WithdrawBotSum

from .models import FAQ, BalanceEditor, DurakNickname, ShowRound, SiteContent


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
        # level_data = Level.objects.get(pk=request.user.level.pk)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            # 'level_data': level_data,
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
        if UserSocialAuth.objects.filter(user_id=request.user.id, provider='google-oauth2'):
            social_google = True
        else:
            social_google = False
        if UserSocialAuth.objects.filter(user_id=request.user.id, provider='vk-oauth2'):
            social_vk = True
        else:
            social_vk = False
        # level_data = Level.objects.get(pk=request.user.level.pk)
        context = {
            'sitecontent': sitecontent,
            'sitecontent2': sitecontent2,
            'detail_user': detail_user,
            "social_google": social_google,
            "social_vk": social_vk,
            # 'level_data': level_data,
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
        # level_data = Level.objects.get(pk=request.user.level.pk)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            # 'level_data': level_data,
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
        # level_data = Level.objects.get(pk=request.user.level.pk)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            # 'level_data': level_data,
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
        # level_data = Level.objects.get(pk=request.user.level.pk)
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            # 'level_data': level_data,
            'title': 'Честность',
        }
    else:
        context = {
            'sitecontent': sitecontent,
            'title': 'Честность',
        }
    # получение хешей для отображения
    day_hashes = DayHash.objects.all().prefetch_related("rouletteround_set")

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
    context['today'] = datetime.datetime.now().date()
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
        # agent = (request.META['HTTP_USER_AGENT'])  # Информация пользователя useragent
        # ip = (request.META['REMOTE_ADDR'])  # Информация пользователя ip
        # us = CustomUser.objects.get(username=request.user)
        # user_agent, created = UserAgent.objects.get_or_create(user=us, useragent=agent)
        # user_ip, created = UserIP.objects.get_or_create(user=us, userip=ip)
        detail_user = DetailUser.objects.get(user_id=request.user.id)
        # level_data = Level.objects.get(pk=request.user.level.pk)
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
            .annotate(tr_type=Value('Пополнение деньгами'), tr_plus=Value(True), round_r=Value(0), name=Value(""))\
            .values('date', 'pay', 'tr_type', 'tr_plus', 'sum', 'round_r', 'name')
        user_bets = UserBet.objects.filter(user=request.user)\
            .annotate(tr_type=Value('Ставка'), tr_plus=F('win'), round_r=F('round_number'), name=Value(""))\
            .values('date', 'sum_win', 'tr_type', 'tr_plus', 'sum', 'round_r', 'name')
        refill = RefillRequest.objects.filter(user=request.user, status='succ')\
            .annotate(tr_type=Value('Пополнение кредитами из игры'), tr_plus=Value(True), round_r=Value(0), name=Value(""))\
            .values('date_closed', 'amount', 'tr_type', 'tr_plus', 'balance', 'round_r', 'name')
        withdraw = WithdrawalRequest.objects.filter(user=request.user, status='succ')\
            .annotate(tr_type=Value('Вывод кредитов в игру'), tr_plus=Value(False),  round_r=Value(0), name=Value(""))\
            .values('date_closed', 'balance', 'tr_type', 'tr_plus', 'amount', 'round_r', 'name')
        referal = FreeBalanceHistory.objects.filter(detail_user_id=request.user.id,
                                                    is_active=False,
                                                    activated_by=0)\
            .annotate(tr_type=Value('Активация вашего промокода'), tr_plus=Value(True), round_r=Value(0), name=Value(""))\
            .values('created', 'bonus_sum', 'tr_type', 'tr_plus', 'detail_user', 'round_r', 'name')
        referal_invited = FreeBalanceHistory.objects.filter(detail_user_id=request.user.id,
                                                            is_active=False,
                                                            activated_by=1) \
            .annotate(tr_type=Value('Активация промокода'), tr_plus=Value(True), round_r=Value(0), name=Value("")) \
            .values('created', 'bonus_sum', 'tr_type', 'tr_plus', 'detail_user', 'round_r', 'name')
        items_for_user = ItemForUser.objects.filter(user=request.user)\
            .annotate(sum=F("user_item__selling_price"), amount=Value(0), tr_type=Value("Бонусный кейс"), tr_plus=F("is_used"), round_r=Value(0),
                      name=F("user_item__name"), )\
            .values("date_modified", "sum", "tr_type", "tr_plus", "amount", "round_r", "name")
        balance_from_admin = BalanceEditor.objects.filter(to_user=request.user)\
            .annotate(sum=F("amount"), amount_to=F("amount"), tr_type=Value("От Админа"), tr_plus=F("to_add"), round_r=Value(0),
                      name=Value(""))\
            .values("date", "sum", "tr_type", "tr_plus", "amount_to", "round_r", "name")
        y_bonus = int(sitecontent.first().bonus_youtube) * 1000
        vk_bonus = int(sitecontent.first().bonus_vk) * 1000
        if vk_sub := BonusVKandYoutube.objects.filter(user=request.user, bonus_vk=True):
            bonus_sub_vk = BonusVKandYoutube.objects.filter(user=request.user)\
                .annotate(sum=Value(vk_bonus), amount_to=Value(0),
                          tr_type=Value("Подписка VK"), tr_plus=Value(True),
                          round_r=Value(0), name=Value(""))\
                .values('date_created_vk', 'sum', 'tr_type', 'tr_plus', 'amount_to', 'round_r', 'name')
        if youtube_sub := BonusVKandYoutube.objects.filter(user=request.user, bonus_youtube=True):
            bonus_sub_youtube = BonusVKandYoutube.objects.filter(user=request.user)\
                .annotate(sum=Value(y_bonus), amount_to=Value(0),
                          tr_type=Value("Подписка Youtube"), tr_plus=Value(True),
                          round_r=Value(0), name=Value(""))\
                .values('date_created_youtube', 'sum', 'tr_type', 'tr_plus', 'amount_to', 'round_r', 'name')
        if vk_sub and youtube_sub:
            transactions = popoln.union(user_bets, refill, withdraw, referal, referal_invited,
                                        items_for_user, balance_from_admin,
                                        bonus_sub_vk, bonus_sub_youtube)\
                                 .order_by('-date')
        elif vk_sub:
            transactions = popoln.union(user_bets, refill, withdraw, referal, referal_invited,
                                        items_for_user, balance_from_admin,
                                        bonus_sub_vk) \
                                 .order_by('-date')
        elif youtube_sub:
            transactions = popoln.union(user_bets, refill, withdraw, referal, referal_invited,
                                        items_for_user, balance_from_admin,
                                        bonus_sub_youtube) \
                                 .order_by('-date')
        else:
            transactions = popoln.union(user_bets, refill, withdraw, referal, referal_invited,
                                        items_for_user, balance_from_admin) \
                                 .order_by('-date')
        paginator = Paginator(transactions, 8)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        page_paginated = True if page_number else False
        show_round = ShowRound.objects.filter().only("show").first()
        mod_nick = ''

        item_user = ItemForUser.objects.filter(user=request.user, is_used=False).exists()
        if mod_nick := DurakNickname.objects.first():
            mod_nick = mod_nick.nickname
        context = {
            'sitecontent': sitecontent,
            'detail_user': detail_user,
            # 'level_data': level_data,
            'social_google': social_google,
            'social_vk': social_vk,
            'form_user': form_user,
            'user_ed': user_ed,
            'title': 'Профиль',
            'page_obj': page_obj,
            'page_paginated': page_paginated,
            'modal_nickname': mod_nick,
            'show_round': show_round.show,
            # 'paginator': paginator,
            'item_user': item_user,
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


def get_loss() -> int:
    """Возвращает убыток от обыгрышей бота на пополнение"""
    # заметка заявки на пополнение при убытке начинается с "Убыток". Пример: "Убыток: 23"
    LOSS_REQ_START = "Убыток"
    # получает заявки с убытком
    loss_requests_notes = RefillRequest.objects.filter(note__startswith=LOSS_REQ_START).values_list("note")
    if loss_requests_notes:
        int_loss = 0
        for loss_note in loss_requests_notes:
            try:
                # парсит строку с заметкой об убытке и получает из неё числовое значение убытка
                str_loss = loss_note[0].split()[1]
                int_loss += abs(int(str_loss))
            except (ValueError, IndexError) as err:
                # пропускает заметку с неправильным форматом заметки об убытке
                continue
        return int_loss
    else:
        # УБыток равен нулю, если нет заявок с убытком
        return 0


def earnings() -> int:
    LOSS_REQ_START = "Профит"
    # получает заявки с Профит
    loss_requests_notes = RefillRequest.objects.filter(note__startswith=LOSS_REQ_START).values_list("note")
    if loss_requests_notes:
        int_loss = 0
        for loss_note in loss_requests_notes:
            try:
                # парсит строку с заметкой об Профит и получает из неё числовое значение Профит
                str_loss = loss_note[0].split()[1]
                int_loss += abs(int(str_loss))
            except (ValueError, IndexError) as err:
                # пропускает заметку с неправильным форматом заметки об Профит
                continue
        return int_loss
    else:
        # УБыток равен нулю, если нет заявок с Профит
        return 0


def info(request):
    """Ставка пользователя"""
    if not request.user.is_authenticated: # Если пользователь не зарегестрирован.
        return index(request)
    if not request.user.is_superuser: # Если пользователь не superuser.
        return index(request)
    loss_requests_notes = get_loss()  # Кредитов, полученных с игроков, которые хотели обыграть бота для пополнения
    sum_of_all_bets = UserBet.objects.aggregate(Sum('sum'))["sum__sum"]
    if sum_of_all_bets is None:
        sum_of_all_bets = 0
    sum_of_all_winner_bets = UserBet.objects.aggregate(Sum('sum_win'))["sum_win__sum"]
    if sum_of_all_winner_bets is None:
        sum_of_all_winner_bets = 0
    difference_all_vs_winners_bets = sum_of_all_bets - sum_of_all_winner_bets
    # sum_amount_req_1 = RefillRequest.objects.filter(status='fail')\
    #                                         .aggregate(Sum('amount'))["amount__sum"]
    sum_gain = earnings()-get_loss()  # “Заработок с нарушителей”
    if sum_gain is None:
        sum_gain = 0
    sum_items_user_sold = ItemForUser.objects.filter(is_forwarded=True)\
                                             .aggregate(Count('is_forwarded'))["is_forwarded__count"]  # 2 Коллекционных предметов (медведь, робот, покерная и т.д.), выведенных с сайта. Отобразить их количество
    sum_referal_bonus = ReferalUser.objects.aggregate(Sum('bonus_sum'))["bonus_sum__sum"]  # 3 Кредитов, полученных игроками за активацию кода
    if sum_referal_bonus is None:
        sum_referal_bonus = 0
    sum_all_payments_rubs = Popoln.objects.filter(status_pay=True)\
                                          .aggregate(Sum('sum'))["sum__sum"]
    if sum_all_payments_rubs is None:
        sum_all_payments_rubs = 0
    sum_to_withdraw_all = WithdrawalRequest.objects.filter(status='succ')\
                                                   .aggregate(Sum('amount'))["amount__sum"]
    if sum_to_withdraw_all is None:
        sum_to_withdraw_all = 0
    sum_to_refill_all = RefillRequest.objects.filter(status='succ')\
                                             .aggregate(Sum('amount'))["amount__sum"]
    if sum_to_refill_all is None:
        sum_to_refill_all = 0
    # ss3 = sum_amount - sum_amount_req_1  # 1 Кредитов, полученных с игроков, которые хотели обыграть бота для пополнения
    full_profit_with_credits_exclude_items = sum_to_refill_all - sum_to_withdraw_all + sum_gain - sum_referal_bonus  # Чистого профита в кредитах без учета смайлов

    context = {
        'sum_bets1': sum_of_all_bets,
        'sum_bets2': sum_of_all_winner_bets,
        'sum_bonus': sum_referal_bonus,
        'sum_item_user': sum_items_user_sold,
        'sum_amount': sum_to_withdraw_all,
        'sum_amount_req': sum_to_refill_all,
        'sum_money': sum_all_payments_rubs,
        "ss": difference_all_vs_winners_bets,
        "ss2": full_profit_with_credits_exclude_items,
        "loss_requests_notes": loss_requests_notes,
        "sum_gain": sum_gain
    }
    return render(request, 'admin/info.html', context)
