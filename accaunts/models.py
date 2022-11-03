from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from django.core.files import File
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Пользователи"""
    avatar = models.FileField(verbose_name='Аватар', upload_to='img/avatar/user/',
                               default='img/avatar/user/avatar.svg')
    vk_url = models.URLField(verbose_name="Ссылка на профиль VK", blank=True, null=True)
    photo = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.vk_url and not ("https://vk.com/" in self.vk_url): #добавление ссылки на вк
            self.vk_url = f"https://vk.com/{self.vk_url}"
        if self.photo and self.avatar == 'img/avatar/user/avatar.svg': #сохранение аватарки с внешнего аккаунта
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(self.photo).read())
            img_temp.flush()
            self.avatar.save(f"image_{self.pk}", File(img_temp))
        super().save(*args, **kwargs)
        if not DetailUser.objects.filter(user=self):
            if not Level.objects.exists(): #создание первого лвл при регистрации первого пользователя
                level_1 = Level(level=1, experience_for_lvl=600)
                level_1.save()
            detail = DetailUser(user=self, level=Level.objects.get(level=1))
            detail.save()

    class Meta:
        verbose_name = 'Пользователь'
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


class DetailUser(models.Model):
    """Данные юзера по балансу и опыту"""
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    balance = models.IntegerField(verbose_name="Баланс", default=0)
    experience = models.IntegerField(verbose_name="Опыт", default=0)
    level = models.ForeignKey('Level', verbose_name="Уровень", on_delete=models.CASCADE, blank=True, null=True)

    def lvl_up(self):
        current_level = Level.objects.get(pk=self.level_id)
        next_level = Level.objects.get(level=current_level.level + 1)
        self.experience -= current_level.experience_for_lvl
        self.level = next_level
        self.save()
        if self.experience >= next_level.experience_for_lvl:
            self.lvl_up()

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
