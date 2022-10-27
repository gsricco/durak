from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    avatar = models.ImageField(verbose_name='Аватар', upload_to='img/avatar/user/', default='img/avatar/user/avatar.png')
    vk_url = models.URLField(verbose_name="Ссылка на профиль VK", blank=True, null=True)
    balance = models.IntegerField(verbose_name="Баланс", default=0)
    experience = models.IntegerField(verbose_name="Опыт", default=0)
    level = models.IntegerField(verbose_name="Уровень", default=1)
    # game_id = models.IntegerField()
    # пока не ясно к чему должен быть привязан game_id, но по описанию будет. Возможно это будет отдельная модель,
    # которая по ForeignKey будет ссылаться на пользователя, так как game_id может быт много для одного пользователя
