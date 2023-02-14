import datetime
import time

import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from accaunts.models import (BonusVKandYoutube, CustomUser, DetailUser,
                             UserBonus)
from configs.settings import VK_TOKEN, YOUTUBE_API_KEY
from content_manager.models import SiteContent

# YOUTUBE
if YOUTUBE_API_KEY is None:
    YOUTUBE_API_KEY = 'AIzaSyBxKAi_XTdjMX3NLK1AfjwA_017G7v-bc0' # my API_KEY
BASE_URL = 'https://youtube.googleapis.com/youtube/v3/subscriptions?part=snippet%2CcontentDetails'

CHANNEL_ID = '&channelId='
MAX_RESULT = '&maxResults=5'
PAGE_TOKEN = '&pageToken='
API_KEY = '&key='+YOUTUBE_API_KEY

# VK
if VK_TOKEN is None:
    VK_TOKEN = '''vk1.a.HAHCn97Rw-ySBtvABHBhCgk2A4foP7eunqdb95ZvvthL2iAk_h
            ozLljuybjRTsxS7E4ANLdmA2uDJXI73TPeKgNzUDkDjMPdyg85PRwNqa
            S5nUC1IEHWSjwwj8vL0Bs0CtiHZPRXPVHJFusy4YN4SFrkmAZkID7dAy
            zFMyiDuzTyg8XeKNK8wlStk9ADjCw0ZbA7-B2AaXfGy6XYEHnavw'''
#
#

channel_layer = get_channel_layer()


def add_bonus(sub_type, user_obj, user_bonus):
    """Начисляет бонус пользователю
    Args:
        sub_type(str): flag -> youtube|vk
        user_obj(CustomUser): объект пользователя
        user_bonus(BonusVKandYoutube): информация о подписках юзера
    Returns:
        None: only calles channel_layer to send via channels info to user
    """
    message = {
        'type': 'subscriber',
        'sub': 'info',
    }
    bonus = SiteContent.objects.first()
    detail_user = DetailUser.objects.get(user_id=user_obj.id)
    if bonus:

        if sub_type == 'y':
            if bonus.bonus_youtube:
                UserBonus.objects.create(detail_user=user_obj.detailuser,
                                         _bonus_to_win_back=bonus.bonus_youtube * 1000 * 3,
                                         total_bonus=bonus.bonus_youtube * 1000,
                                         is_active=True)
            # detail_user.balance += bonus.bonus_youtube * 1000 if bonus.bonus_youtube else 0
            user_bonus.bonus_youtube = True
            user_bonus.youtube_disabled = False
            user_bonus.date_created_youtube = datetime.datetime.now()
            message['youtube_subscribe'] = 'success'
        elif sub_type == 'v':
            # detail_user.balance += bonus.bonus_vk * 1000 if bonus.bonus_vk else 0
            if bonus.bonus_vk:
                UserBonus.objects.create(detail_user=user_obj.detailuser,
                                         _bonus_to_win_back=bonus.bonus_vk * 1000 * 3,
                                         total_bonus=bonus.bonus_vk * 1000,
                                         is_active=True)
            user_bonus.bonus_vk = True
            user_bonus.vk_disabled = False
            user_bonus.date_created_vk = datetime.datetime.now()
            message['vk_subscribe'] = 'success'
        detail_user.save()
        user_bonus.save()
    balance_message = {
        'type': 'get_balance',
        'balance_update': {
            'current_balance': detail_user.total_balance
        }
    }
    async_to_sync(channel_layer.group_send)(f"{user_obj.id}_room", balance_message)

    async_to_sync(channel_layer.group_send)(f"{user_obj.id}_room", message)


def send_error(user_obj, channel_type):
    """Посылает ошибку о попытке проверить подписку"""
    message = {
        'type': 'subscriber',
        'sub': 'info',
    }
    if channel_type == 'y':
        message['youtube_subscribe'] = 'fail'
    elif channel_type == 'v':
        message['vk_subscribe'] = 'fail'
    async_to_sync(channel_layer.group_send)(f"{user_obj.id}_room", message)


def check_youtube_subscribers(user_channel_id, user_obj):
    """Проверяет подписку на ютуб канал по CHANNEL ID
    Args:
        user_obj(CustomUser): User Object
        user_channel_id(str): Youtube Channel ID
    Returns:
        bool: flag -> True if success, else False
    """
    user_bonus, created = BonusVKandYoutube.objects.get_or_create(user_id=user_obj.id)
    user_bonus.youtube_disabled = True
    user_bonus.save()
    if not user_bonus.bonus_youtube:
        site_channel_id_youtube = SiteContent.objects.first().youtube_channel_id
        if site_channel_id_youtube:
            start_time = time.time()
            page = ''
            n = True
            while n:
                if (time.time() - start_time) > 300:
                    break
                if page:
                    url = BASE_URL+CHANNEL_ID+user_channel_id+MAX_RESULT+PAGE_TOKEN+page+API_KEY
                else:
                    url = BASE_URL+CHANNEL_ID+user_channel_id+MAX_RESULT+API_KEY
                response = requests.get(url, headers={'Content-type': 'application/json'})
                if response.status_code == 200:
                    channels = response.json()
                    if next_page := channels.get('nextPageToken'):
                        page = next_page
                    else:
                        n = False
                    if channels_list := channels.get('items'):
                        for channel in channels_list:
                            try:
                                channel_id = channel.get('snippet')['resourceId']['channelId']
                            except AttributeError:
                                send_error(user_obj, 'y')
                                return False
                            # channel_title = channel.get('snippet')['title']
                            if channel_id == site_channel_id_youtube:
                                add_bonus('y', user_obj, user_bonus)
                                return True
                else:
                    break
    user_bonus.youtube_disabled = False
    user_bonus.save()
    send_error(user_obj, 'y')
    return False


def vk_subscribe(user_obj):
    """ Функция проверяет подписан ли пользователь на группу в VK"""
    vk_auth = user_obj.social_auth.filter(provider='vk-oauth2').first()
    user_bonus, created = BonusVKandYoutube.objects.get_or_create(user_id=user_obj.id)
    user_bonus.vk_disabled = True
    user_bonus.save()
    if vk_auth and not user_bonus.bonus_vk:
        bonus = SiteContent.objects.first()
        if bonus:
            if vk_group_id := bonus.url_vk:
                vk_id = vk_auth.uid
                group_id = SiteContent.objects.first().vk_group_id
                if group_id:
                    extended = 0
                    version = 5.92
                    for _ in range(4):
                        time.sleep(2)
                        response = requests.get("https://api.vk.com/method/groups.isMember",
                                                params={
                                                    "access_token": VK_TOKEN,
                                                    'group_id': group_id,
                                                    'user_id': vk_id,
                                                    'extended': extended,
                                                    'v': version})
                        data = response.json()
                        if data['response']:
                            add_bonus('v', user_obj, user_bonus)
                            return 1
    user_bonus.vk_disabled = False
    user_bonus.save()
    send_error(user_obj, 'v')
    return 0
