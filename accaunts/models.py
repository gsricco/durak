from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from caseapp.models import Item
from django.core.files import File
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import BigIntegerRangeField, RangeOperators
from django.contrib.postgres.constraints import ExclusionConstraint
from psycopg2.extras import NumericRange
from caseapp.models import OwnedCase


class CustomUser(AbstractUser):
    """Пользователи"""
    avatar = models.FileField(verbose_name='Аватар', upload_to='img/avatar/user/',
                              default='img/avatar/user/avatar.svg')
    vk_url = models.URLField(verbose_name="Ссылка на профиль VK", blank=True, null=True)
    photo = models.URLField(blank=True, null=True)
    level = models.ForeignKey('Level', verbose_name="Уровень", on_delete=models.PROTECT, blank=True, null=True)
    experience = models.IntegerField(verbose_name="Опыт", default=0)

    def save(self, *args, **kwargs):
        if self.photo and self.avatar == 'img/avatar/user/avatar.svg':
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(self.photo).read())
            img_temp.flush()
            self.avatar.save(f"image_{self.pk}", File(img_temp))
        if not Level.objects.all().exists():  # создание первого лвл при регистрации первого пользователя
                level_1 = Level(level=1, experience_range=NumericRange(0, 600))
                level_1.save()
                self.level = level_1
        if self.level is None:
            print(self.experience)
            self.level = Level.objects.get(level=1)
        super().save(*args, **kwargs)
        if not DetailUser.objects.filter(user=self):
            detail = DetailUser(user=self)
            detail.save()
        # if not Ban.objects.filter(user=self):    # создание бана при регистрации пользователя
        #     ban = Ban(user=self)
        #     Ban.objects.get_or_create()
        #     ban.save()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def give_level(self, save_immediately: bool=False) -> list:
        """Проверяет, можно ли выдать пользователю уровень и выдаёт его, начисляя награды.

        Args:
            save_immediately (bool)=False: сохранять изменения в пользователе в этом методе или нет

        Returns:
            list: список с выданными за уровень наградами (если выданы)
        """
        rewards = []
        level_changed = False
        # give available level
        while self.experience >= self.level.experience_range.upper:
            new_levels = Level.objects.filter(level__gt=self.level.level).order_by('level')
            print(f"Available levels {new_levels}")
            # если есть доступные уровни
            if new_levels:
                # связывает новый уровень с пользователем (не сохраняет в БД)
                new_level = new_levels.first()
                print(f"New level {new_level}")
                self.level = new_level
                level_changed = True

                # выдаёт награду за уровень 
                # если за уровень выдаётся кейс
                if self.level.case:
                    # создаются экземпляры OwnedCase для хранения начисленных кейсов
                    for _ in range(self.level.amount):
                        new_reward = OwnedCase(case=self.level.case, owner=self)
                        rewards.append(new_reward)
            else:
                break
        
        if level_changed and save_immediately:
            self.save()
            if rewards:
                OwnedCase.objects.bulk_create(rewards)
        return rewards

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


class Level(models.Model):
    """Модель уровня игрока"""
    RUBIN_CHOICES = (
        ('amber_case', 'Amber'),
        ('pearl_case', 'Pearl'),
        ('rubin_blue', 'Sapphire'),
        ('rubin_green', 'Emerald'),
        ('rubin_purple', 'Amethist'),
        ('rubin_red', 'Rubin'),
        ('rubin_turquoise', 'Diamond'),
    )
    level = models.PositiveBigIntegerField(verbose_name='Номер уровня', unique=True)
    experience_range = BigIntegerRangeField(verbose_name='Диапазон опыта для уровня', null=True)
    img_name = models.CharField('Камень для уровня', max_length=50, default='amber_case', choices=RUBIN_CHOICES)
    case = models.ForeignKey('caseapp.Case', verbose_name='Кейс в награду за уровень', on_delete=models.PROTECT, null=True, blank=True)
    amount = models.PositiveIntegerField(verbose_name='Количество кейсов', default=0)

    def __str__(self):
        return f"Уровень {self.level}, опыт на уровне: {self.experience_range}"

    class Meta:
        # constraints = [
        #     ExclusionConstraint(
        #         name='exclude_overlapped_levels',
        #         expressions=[
        #             ('experience_range', RangeOperators.OVERLAPS),
        #         ],
        #         violation_error_message='Диапазон опыта для уровня пересекается с другим уровнем.',
        #     ),
        # ]
        ordering = ['level']
        verbose_name = 'Уровень в игре'
        verbose_name_plural = 'Уровни в игре'


class DetailUser(models.Model):
    """Данные юзера по балансу и опыту"""
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    balance = models.IntegerField(verbose_name="Баланс", default=0)

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
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, null=True)
    ban_site = models.BooleanField(verbose_name='Бан пользователя на сайте', default=False)
    ban_chat = models.BooleanField(verbose_name='Бан пользователя в общем чате', default=False)
    ban_ip = models.BooleanField(verbose_name='Бан пользователя по ip', default=False)         #Надоли по IP????

    class Meta:
        verbose_name = 'Бан'
        verbose_name_plural = 'Баны'

    def __str__(self):
        return f'{self.user}'


class DayHash(models.Model):
    """Модель для хранения сгенерированных public_key и private_key"""
    public_key = models.CharField(verbose_name='Публичный ключ', max_length=16, null=True, blank=True)
    private_key = models.CharField(verbose_name='Приватный ключ', max_length=64, null=True, blank=True)
    private_key_hashed = models.CharField(verbose_name='Захешированный приватный ключ', max_length=64, null=True, blank=True)
    date_generated = models.DateField(verbose_name='Дата генерации', auto_now_add=True, unique=True)

    def __str__(self):
        return f"{self.date_generated}: {self.private_key}-{self.public_key}"

    class Meta:
        verbose_name = 'Хеш'
        verbose_name_plural = 'Хеши'
        ordering = ['-date_generated']


class RouletteRound(models.Model):
    """Модель для сохранения раунда рулетки"""
    ROUND_RESULT_CHOISES = [
        ('spades', 'Пики'),
        ('hearts', 'Червы'),
        ('coin', 'Монетка'),
    ]

    round_number = models.PositiveBigIntegerField(verbose_name='Номер раунда', default=0)
    round_started = models.DateTimeField(verbose_name='Время начала раунда', blank=True, null=True)
    round_roll = models.CharField(verbose_name='Результат раунда', max_length=6, choices=ROUND_RESULT_CHOISES, default='hearts')
    rolled = models.BooleanField(verbose_name='Раунд был сыгран', default=False)
    day_hash = models.ForeignKey('DayHash', verbose_name='Хеши раунда', on_delete=models.PROTECT, blank=True, null=True)
    show_round = models.BooleanField(verbose_name='Отображение раунда в честности', default=True)

    total_bet_amount = models.PositiveBigIntegerField(verbose_name='Общая сумма ставок', default=0)
    winners = models.ManyToManyField('CustomUser', verbose_name='Победители раунда', blank=True)

    def __str__(self):
        return f"Раунд номер {self.round_number}: {self.total_bet_amount} кредитов. {self.round_roll}"

    class Meta:
        verbose_name = 'Раунд рулетки'
        verbose_name_plural = 'Раунды рулетки'
        ordering = ['round_number']


class ItemForUser(models.Model):

    user_item = models.ForeignKey('caseapp.Item', verbose_name='Предмет', null=True, blank=True, on_delete=models.CASCADE )
    user = models.ForeignKey('CustomUser', verbose_name='Пользователь',null=True, blank=True, on_delete=models.CASCADE)
    is_used = models.BooleanField(verbose_name='Использован',default=False)