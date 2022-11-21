from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from django.core.files import File
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import BigIntegerRangeField, RangeOperators
from django.contrib.postgres.constraints import ExclusionConstraint
from psycopg2.extras import NumericRange


class CustomUser(AbstractUser):
    """Пользователи"""
    avatar = models.FileField(verbose_name='Аватар', upload_to='img/avatar/user/',
                              default='img/avatar/user/avatar.svg')
    vk_url = models.URLField(verbose_name="Ссылка на профиль VK", blank=True, null=True)
    photo = models.URLField(blank=True, null=True)
    experience = models.IntegerField(verbose_name="Опыт", default=0)

    def save(self, *args, **kwargs):
        if self.photo and self.avatar == 'img/avatar/user/avatar.svg':
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(self.photo).read())
            img_temp.flush()
            self.avatar.save(f"image_{self.pk}", File(img_temp))
        super().save(*args, **kwargs)
        if not DetailUser.objects.filter(user=self):
            if not Level.objects.exists():  # создание первого лвл при регистрации первого пользователя
                level_1 = Level(level=1, experience_for_lvl=600)
                level_1.save()
            detail = DetailUser(user=self, level=Level.objects.get(level=1))
            detail.save()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def user_info(self):
        return f'{self.last_name} {self.first_name}'

    user_info.short_description = 'Фамилия имя с аккаунта'

    def usernameinfo(self):
        return f'{self.username}'

    usernameinfo.short_description = 'Никнейм в игре'


class UserAgent(models.Model):
    """Модель UserAgent адресов с которых заходил пользователь"""
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    useragent = models.CharField(verbose_name="UserAgent пользователя", max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'UserAgent пользователя'
        verbose_name_plural = 'UserAgent пользователя'

    def __str__(self):
        return f'{self.user}'


class UserIP(models.Model):
    """Модель UserIP адресов с которых заходил пользователь"""
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    userip = models.CharField(verbose_name="IP пользователя", max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'IP пользователя'
        verbose_name_plural = 'IP пользователя'

    def __str__(self):
        return f'{self.user}'


class LevelRange(models.Model):
    """Модель уровня игрока"""
    level = models.PositiveBigIntegerField(verbose_name='Номер уровня', unique=True, default=1)
    experience_range = BigIntegerRangeField(verbose_name='Диапазон опыта для уровня', default=NumericRange(lower=0, upper=601))
    image = models.ImageField(verbose_name='Картинка уровня', upload_to='img/level/', blank=True, null=True)

    def __str__(self):
        return f"Уровень {self.level}, опыт на уровне: {self.experience_range}"

    class Meta:
        constraints = [
            ExclusionConstraint(
                name='exclude_overlapped_levels',
                expressions=[
                    ('experience_range', RangeOperators.OVERLAPS),
                ],
                violation_error_message='Диапазон опыта для уровня пересекается с другим уровнем.',
            ),
        ]
        verbose_name = 'Уровень в игре'
        verbose_name_plural = 'Уровни в игре'



class Level(models.Model):
    """Модель уровней пользователей"""
    level = models.PositiveIntegerField(verbose_name='Уровень', unique=True)
    experience_for_lvl = models.IntegerField(verbose_name="Опыт", default=0)
    image = models.ImageField(verbose_name='Аватар', upload_to='img/level/', blank=True, null=True)

    class Meta:
        verbose_name = 'Уровни в игре (старые)'
        verbose_name_plural = 'Уровни в игре (старые)'

    def __str__(self):
        return f'{self.level}'


class DetailUser(models.Model):
    """Данные юзера по балансу и опыту"""
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    balance = models.IntegerField(verbose_name="Баланс", default=0)
    level = models.ForeignKey('Level', verbose_name="Уровень", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = 'Данные пользователя'
        verbose_name_plural = 'Данные пользователя'

    def __str__(self):
        return f'{self.user}'


class ReferalCode(models.Model):
    """Модель реферальных ссылок"""
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    ref_code = models.CharField(verbose_name="Реферальный код", unique=True, max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'Реферальный код'
        verbose_name_plural = 'Реферальный код'

    def __str__(self):
        return f'{self.ref_code}'


class ReferalUser(models.Model):
    """Модель пользователей приглашённых на сайт"""
    user_with_bonus = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="users_with_bonus",
                                        verbose_name="Пользователь который пригласил")
    invited_user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name="invited_users",
                                        verbose_name="Приглашенный пользователь")
    date = models.DateTimeField(verbose_name="Дата входа в систему", auto_now_add=True)

    class Meta:
        verbose_name = 'Приглашенный пользователь'
        verbose_name_plural = 'Приглашенный пользователь'

    def __str__(self):
        return f'{self.user_with_bonus}'


class GameID(models.Model):
    """Модель игровых id с дурак онлайн"""
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    game_id = models.IntegerField(verbose_name="Игрвой id дурак онлайн", blank=True, null=True)

    class Meta:
        verbose_name = 'Игровой id'
        verbose_name_plural = 'Игровой id'

    def __str__(self):
        return f'{self.user}'


class Ban(models.Model):
    """Модель банов пользователей (нужна доработка)"""
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    ban = models.BooleanField(verbose_name='Бан', default=False)  # расписать виды банов

    class Meta:
        verbose_name = 'Баны'
        verbose_name_plural = 'Баны'

    def __str__(self):
        return f'{self.user}'
