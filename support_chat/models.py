from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models
from accaunts.models import CustomUser


def admin():
    return CustomUser.objects.get(username="admin").id


class Message(models.Model):
    """Модель сообщений чата поддержки"""
    user_posted = models.ForeignKey(CustomUser, verbose_name='Пользователь', on_delete=models.CASCADE,
                                    related_name='user_send', null=True)
    chat_room = models.ForeignKey('UserChatRoom',verbose_name='Комната чата', on_delete=models.CASCADE,
                                  related_name='message', null=True)
    message = models.TextField(verbose_name='Сообщение', blank=True, null=True)
    # message = models.TextField(validators=[MaxLengthValidator(50)], blank=True, null=True)
    file_message = models.FileField(verbose_name='Файл', upload_to=f'support_chat/%Y/%m/%d/', blank=True, null=True)
    date = models.DateTimeField(verbose_name='Дата', auto_now_add=True)
    is_read = models.BooleanField(verbose_name='Прочитано', default=False)
    is_sell_item = models.BooleanField(verbose_name='Продажа предмета',default=False)

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ('date',)

    def status_is_read(self):
        """Метод для установки статуса 'Прочитанно' у поля конкретного сообщения"""
        self.is_read = True
        return {"status": "Ok"}

    def clean(self):
        """Метод для проверки длинны сообщения"""
        if len(self.message) > 500:
            raise ValidationError(
                {'message': "message support_chat more 500"},
            )


class UserChatRoom(models.Model):
    user = models.ForeignKey('accaunts.CustomUser',verbose_name='Пользователь', on_delete=models.CASCADE,
                             null=True, blank=True)
    room_id = models.CharField(verbose_name='ID комнаты', max_length=255, unique=True)
    updated = models.DateTimeField(verbose_name='Дата последнего изменения', auto_now=True, null=True, blank=True)
    not_read_owner_counter = models.PositiveIntegerField(verbose_name='Не прочитал пользователь', default=0,
                                                         null=True, blank=True)
    not_read_counter = models.PositiveIntegerField(verbose_name='Не прочитал админ', default=0, null=True, blank=True)

    def __str__(self):
        return f'Комната {self.room_id}'

    def save(self, *args, **kwargs):
        # при изменении пересчитывает количество непрочитанных писем
        self.not_read_owner_counter = Message.objects.filter(chat_room=self, is_read=False).\
            exclude(user_posted=self.user).count()
        self.not_read_counter = Message.objects.filter(chat_room=self, is_read=False). \
            filter(user_posted=self.user).count()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Админ чат'
        verbose_name_plural = "Админ чат"
        ordering = ('-updated',)
