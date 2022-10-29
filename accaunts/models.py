from django.db import models
from django.contrib.auth.models import AbstractUser


class IPUser(models.Model):
    name = models.CharField(verbose_name="IP пользователя", max_length=200, blank=True, null=True)


class CustomUser(AbstractUser):
    """Пользователи"""
    avatar = models.ImageField(verbose_name='Аватар', upload_to='img/avatar/user/',
                               default='img/avatar/user/avatar.png')
    vk_url = models.URLField(verbose_name="Ссылка на профиль VK", blank=True, null=True)
    balance = models.IntegerField(verbose_name="Баланс", default=0)
    experience = models.IntegerField(verbose_name="Опыт", default=0)
    level = models.IntegerField(verbose_name="Уровень", default=1)
    ip_user = models.ForeignKey('IPUser', verbose_name="IP пользовтаеля", on_delete=models.CASCADE, blank=True,
                                null=True)
    ref_code = models.CharField(verbose_name="Реферальный код", max_length=200, blank=True, null=True)
    ref_id_user = models.ForeignKey('CustomUser', verbose_name="id пользователя который пригласил", blank=True,
                                    null=True, on_delete=models.CASCADE, to_field='id')
    game_id = models.IntegerField(verbose_name="Игрвой id дурак онлайн", blank=True, null=True)
    ban = models.BooleanField(verbose_name='Бан', default=False)

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


