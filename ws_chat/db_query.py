import base64
import datetime
import os

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError

from accaunts.models import CustomUser
from support_chat.models import UserChatRoom, Message


# запросы в БД
@sync_to_async
def create_or_get_support_chat_room(self, user):  # получает или создает чат рум
    chat_room, created = UserChatRoom.objects.get_or_create(room_id=user)
    return chat_room

@sync_to_async()
def base64_to_image(self, file):
    '''преобразование байт строки в файл и сохранение его'''
    file_type = file.split(';')[0].split('/')[1]
    string_file = file.split(';')[1][7:]
    save_date = datetime.datetime.now()
    byte_file = string_file.encode(encoding='ascii')
    new_file = base64.decodebytes(byte_file)
    user = str(self.scope['user'])
    save_name = f'media/support_chat/{user}/{save_date}.{file_type}'
    try:
        os.mkdir(f'media/support_chat/{user}')
        with open(save_name, 'wb') as f:
            f.write(new_file)
    except:
        with open(save_name, 'wb') as f:
            f.write(new_file)

    return save_name

@sync_to_async
def save_user_message(self, room, user, message, file_path=''):  # сохраняет сообщение в бд
    """Cохраняет сообщения из чата поддержки в БД"""
    if user:
        try:
            user = CustomUser.objects.get(username=user).pk
            user_mess = Message(user_posted_id=user, message=message)
            user_mess.full_clean()
            user_mess.save()
            room.message.add(user_mess, bulk=False)
            return user_mess
        except ValidationError:
            print("Message support_chat more 500")