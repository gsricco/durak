from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Пользователи"""
    avatar = models.ImageField(verbose_name='Аватар', upload_to='img/avatar/user/',
                               default='img/avatar/user/avatar.svg')
    vk_url = models.URLField(verbose_name="Ссылка на профиль VK", blank=True, null=True)

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class IPUser(models.Model):
    """Модель IP адресов с которых заходил пользователь"""
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    ip = models.CharField(verbose_name="IP пользователя", max_length=200, blank=True, null=True)


class Level(models.Model):
    """Модель уровней пользователей"""
    level = models.PositiveIntegerField(verbose_name='Уровень', unique=True)
    experience_for_lvl = models.IntegerField(verbose_name='Количество опыта до следующего уровня')
    image = models.ImageField(verbose_name='Аватар', upload_to='img/level/', blank=True, null=True)

    def __str__(self):
        return (f"{self.level} уровень")


class DetailUser(models.Model):
    """Данные юзера по балансу и опыту"""
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    balance = models.IntegerField(verbose_name="Баланс", default=0)
    experience = models.IntegerField(verbose_name="Опыт", default=0)
    level = models.ForeignKey('Level', verbose_name="Уровень", to_field='level', on_delete=models.CASCADE, blank=True,
                              null=True)


class ReferalCode(models.Model):
    """Модель реферальных ссылок"""
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    ref_code = models.CharField(verbose_name="Реферальный код", unique=True, max_length=200, blank=True, null=True)


class ReferalUser(models.Model):
    """Модель пользователей приглашённых на сайт"""
    user_with_bonus = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="users_with_bonus",
                                        verbose_name="Пользователь который пригласил")
    invited_user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name="invited_users",
                                        verbose_name="Приглашенный пользователь")
    date = models.DateTimeField(verbose_name="Дата входа в систему", auto_now_add=True)


class GameID(models.Model):
    """Модель игровых id с дурак онлайн"""
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    game_id = models.IntegerField(verbose_name="Игрвой id дурак онлайн", blank=True, null=True)


class Ban(models.Model):
    """Модель банов пользователей (нужна доработка)"""
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    ban = models.BooleanField(verbose_name='Бан', default=False) #расписать виды банов
