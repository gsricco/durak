import json
import time

import requests
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404

from accaunts.models import CustomUser, BonusVKandYoutube, DetailUser
from content_manager.models import SiteContent


@sync_to_async
def vk_api_subscribe(user_pk):
    """ Функция проверяет подписан ли пользователь на группу в VK"""
    vk_id = CustomUser.objects.filter(id=user_pk).first().social_auth.filter(provider="vk-oauth2").first().uid
    print("ID in VK -- ",vk_id)
## Необходимо проставить токен из приложения группы Дурака в VK =
    token = "vk1.a.HAHCn97Rw-ySBtvABHBhCgk2A4foP7eunqdb95ZvvthL2iAk_hozLljuybjRTsxS7E4ANLdmA2uDJXI73TPeKgNzUDkDjMPdyg85PRwNqaS5nUC1IEHWSjwwj8vL0Bs0CtiHZPRXPVHJFusy4YN4SFrkmAZkID7dAyzFMyiDuzTyg8XeKNK8wlStk9ADjCw0ZbA7-B2AaXfGy6XYEHnavw"
## Необходимо проставить id группы Дурака в VK =
    group_id = "club218205130"    # группа Миши
    # group_id = "171518034"
    #user_id = "775388070"
    extended = 0
    version = 5.92
    for _ in range(4):
        time.sleep(15)
        response = requests.get("https://api.vk.com/method/groups.isMember",
                                params={
                                    "access_token": token,
                                    'group_id': group_id,
                                    'user_id': vk_id,
                                    'extended': extended,
                                    'v': version})
        data = response.json()
        print("api ---", response.url)
        print("response ---", data)
        if data['response']:
            give_bonus_vk_youtube(user_pk, "bonus_vk")
            return 1

@sync_to_async
def give_bonus_vk_youtube(user_pk, type_bonus):
    """Даёт бонус за подписку пользователя на канал в YouTube"""
    user_bonus, created = BonusVKandYoutube.objects.get_or_create(user_id=user_pk)
    if type_bonus == "bonus_vk":
        # проверяем, не получал ли юзер бонус за VK
        if not user_bonus.bonus_vk:
            detail_user = DetailUser.objects.get(user_id=user_pk)
            detail_user.free_balance += SiteContent.objects.all().first().bonus_vk
            user_bonus.bonus_vk = True
            detail_user.save()
            user_bonus.save()
            print("Бонус VK в обработке")
            return
    elif type_bonus == "bonus_youtube":
        # проверяем, не получал ли юзер бонус за YouTube
        if not user_bonus.bonus_youtube:
            detail_user = DetailUser.objects.get(user_id=user_pk)
            detail_user.free_balance += SiteContent.objects.all().first().bonus_youtube
            user_bonus.bonus_youtube = True
            detail_user.save()
            user_bonus.save()
            print("Бонус YouTube в обработке")
            return
    print("Вы уже получали бонус")
    return



