from django.contrib.auth.models import User
from django.db import models
from accaunts.models import CustomUser


def admin():
    return CustomUser.objects.get(username="admin").id


class Message(models.Model):
    """Модель сообщений чата поддержки"""
    user_posted = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_send', null=True)
    chat_room = models.ForeignKey('UserChatRoom', on_delete=models.CASCADE, related_name='message', null=True)
    message = models.TextField(blank=True, null=True)
    file_message = models.FileField(upload_to=f'support_chat/%Y/%m/%d/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ('-date',)

    def status_is_read(self):
        """Метод для установки статуса 'Прочитанно' у поля конкретного сообщения"""
        self.is_read = True
        return {"status": "Ok"}


class UserChatRoom(models.Model):
    room_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.room_id

    class Meta:
        verbose_name = 'Room'
        verbose_name_plural = "Rooms"
