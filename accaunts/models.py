import random
import string
import sys
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from asgiref.sync import sync_to_async
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import BigIntegerRangeField, RangeOperators
from django.core.files import File
from django.db import models
from django.db.models import Sum
from PIL import Image

from caseapp.models import OwnedCase
from content_manager.models import SiteContent

from .pix_list_rgb import list_rgb
from .validators import validate_referal


def is_migrate():
    """Проверяет - выполняются ли миграции"""
    return 'makemigrations' in sys.argv or 'migrate' in sys.argv


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
    case = models.ForeignKey('caseapp.Case', verbose_name='Кейс в награду за уровень', on_delete=models.PROTECT,
                             null=True, blank=True)
    amount = models.PositiveIntegerField(verbose_name='Количество кейсов', default=0)

    def __str__(self):
        return f"{self.level}"

    @classmethod
    def get_default_lvl(cls):
        if is_migrate():
            return
        if cls.objects.all().exists():
            return cls.objects.first().pk

    class Meta:
        ordering = ['level']
        verbose_name = 'Уровень в игре'
        verbose_name_plural = 'Уровни в игре'


def random_number():
    """Создание сгенерированного id пользователя из 3 букв и 2 чисел"""
    random_id_user = str(''.join(random.choices(string.ascii_lowercase, k=3))+''.join(random.choices(string.digits, k=2)))
    return random_id_user


class CustomUser(AbstractUser):
    """Пользователи"""
    avatar = models.FileField(verbose_name='Аватар', upload_to='img/avatar/user/',
                              default='img/avatar/user/ava_S.png',)
                              # validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    use_avatar = models.BooleanField(verbose_name='Рандомная аватарка профиля', default=False,
                                     help_text='Рандомная аватарка с галочкой, а стандартная без')
    avatar_default = models.ForeignKey('AvatarProfile', verbose_name='Рандомные автарки профиля',
                                       on_delete=models.CASCADE, null=True, blank=True)
    vk_url = models.URLField(verbose_name="Ссылка на профиль VK", blank=True, null=True)
    photo = models.URLField(blank=True, null=True)
    level = models.ForeignKey('Level', verbose_name="Уровень", on_delete=models.PROTECT, default=Level.get_default_lvl,
                              blank=True, null=True)
    experience = models.IntegerField(verbose_name="Опыт", default=0)
    note = models.CharField(verbose_name='Заметка', max_length=100, blank=True, null=True)
    random_id = models.CharField(verbose_name='Сгенерированный id', max_length=5, null=True)#unique=True, default=random_number, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Проверяем на уникальность Сгенерированный id для пользователя в момент его регистрации
        if self.random_id is None:
            while CustomUser.objects.filter(random_id=self.random_id).exists():
                self.random_id = random_number()
        if self.photo and (self.avatar == 'img/avatar/user/ava_S.png'):
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(self.photo).read())
            img_temp.flush()
            self.avatar.save(f"image_{self.pk}", File(img_temp))
            im = Image.open(self.avatar)
            x = 4
            y = 4
            pix = im.load()
            pix_list = list_rgb
            if pix[x, y] in pix_list:
                img_ava = list(AvatarProfile.objects.all())
                img_ra = random.choice(img_ava)
                self.avatar = img_ra.avatar_img
            self.avatar.save(self.avatar.name, self.avatar)
        super().save(*args, **kwargs)
        if not DetailUser.objects.filter(user=self).exists():
            detail = DetailUser(user=self)
            detail.save()
        if not Ban.objects.filter(user=self).exists():
            ban = Ban(user=self)
            ban.save()
        if not BonusVKandYoutube.objects.filter(user=self).exists():
            BonusVKandYoutube.objects.create(user=self)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def give_level(self, save_immediately: bool = False) -> list:
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
            # если есть доступные уровни
            if new_levels:
                # связывает новый уровень с пользователем (не сохраняет в БД)
                new_level = new_levels.first()
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


class DetailUser(models.Model):
    """Данные юзера по балансу и опыту"""
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    balance = models.PositiveBigIntegerField(verbose_name="Баланс Который Можно Снять", default=0)
    free_balance = models.PositiveBigIntegerField(verbose_name="Бонусный счёт", default=0)
    frozen_balance = models.PositiveBigIntegerField(verbose_name='Замороженные средства', default=0)
    # subscribe_balance = models.PositiveBigIntegerField(verbose_name="Бонус за подписку", default=0)
    # bonus_balance = models.PositiveBigIntegerField(verbose_name="Общий бонусный счёт", default=0)
    _reserve = models.PositiveBigIntegerField(verbose_name="Резерв - сумма пополнений реальными деньгами",
                                              default=0)

    class Meta:
        verbose_name = 'Баланс пользователя в игре'
        verbose_name_plural = 'Баланс пользователя в игре'

    def __str__(self):
        return f'{self.user}, total:{self.total_balance}, reserve:{self._reserve}'

    @property
    def reserve(self):
        return self._reserve

    @reserve.setter
    def reserve(self, value):
        """
        Изменения резерва - той части которую точно можно вывести
        """
        assert value >= self._reserve
        diff = value - self._reserve
        self.balance += diff
        self._reserve = value

    async def do_withdraw(self, value):
        """
        Вывод денег
        Args:
            value(int) : сумма, которую хочет вывести пользователь, должна быть > 0;
        Returns:
            int: code 0 если вывод не удался, 1 при удачном списании средств
        """
        if value > 0:
            if withdaw_amount := await self.check_withdraw():
                if withdaw_amount >= value:
                    # если то что возможно снять > чем резерв
                    if withdaw_amount > self._reserve:
                        diff = withdaw_amount - self._reserve
                        if value > diff:
                            # self.balance -= value
                            reserve_to_subtract = value - diff
                            self._reserve -= reserve_to_subtract
                        else:
                            return 1
                            # self.balance -= value
                    else:
                        # self.balance -= value
                        self._reserve -= value
                    return 1
        return 0

    async def check_withdraw(self):
        """Сколько можно снять"""
        bonus = await sync_to_async(self.check_bonus_amount)()
        if self.reserve > 0:
            if self.total_balance > self.reserve:
                diff = self.total_balance - self.reserve
                if diff > bonus:
                    withdraw_sum = self.total_balance - bonus
                else:
                    withdraw_sum = self.reserve
            else:
                withdraw_sum = self.total_balance
            return withdraw_sum
        else:
            if self.total_balance > bonus:
                withdraw_sum = self.total_balance - bonus
                return withdraw_sum
            else:
                return 0

    def check_bonus_amount_to_win_back(self):
        bonus_to_win_back = UserBonus.objects.filter(detail_user=self,
                                                     is_active=True,)\
                                             .aggregate(total_win_back=Sum('_bonus_to_win_back'))\
                                             .get('total_win_back')
        return bonus_to_win_back if bonus_to_win_back is not None else 0

    def check_bonus_amount(self):
        """Просчитывает все бонусные кредиты юзера"""
        bonus = UserBonus.objects.filter(detail_user=self,
                                         is_active=True,)\
                                 .aggregate(user_total_bonus=Sum('total_bonus'))\
                                 .get('user_total_bonus')
        return bonus if bonus is not None else 0

    @property
    def total_balance(self):
        """ВЕСЬ БАЛАНС С УЧЁТОМ БОНУСОВ"""
        return self.balance

    @total_balance.setter
    def total_balance(self, value):
        # setting to ZERO
        if value == 0:
            # if value is 0... here should be some function call
            all_bonus = UserBonus.objects.filter(detail_user=self,
                                                 is_active=True)\
                                         .update(is_active=False)
            self._reserve = 0
            self.balance = 0
        # decrease total_balance
        elif self.balance > value:
            diff = self.balance - value
            balance = self.calculate_balance_after_bet(diff)
            self.balance = value
        # increase total_balance
        elif self.balance < value:
            # total_bonus = self.check_bonus_amount()
            self.balance = value

    def calculate_balance_after_bet(self, value):
        list_of_bonuses = []
        if all_active_bonuses := UserBonus.objects.filter(detail_user=self, is_active=True):
            for bonus in all_active_bonuses:
                if value >= bonus.bonus_to_win_back:
                    value -= bonus.bonus_to_win_back
                    bonus.bonus_to_win_back = 0
                else:
                    diff = bonus.bonus_to_win_back - value
                    bonus.bonus_to_win_back = diff
                    value = 0
                list_of_bonuses.append(bonus)
                if value == 0:
                    break
            UserBonus.objects.bulk_update(list_of_bonuses, ['_bonus_to_win_back', 'is_active',])
            return value
        else:
            return value


class UserBonus(models.Model):
    """Хранит все бонусные начисления кредитов для каждого юзера"""
    _bonus_to_win_back = models.IntegerField(verbose_name="Кол-во кредитов которые нужно отыграть", db_index=True)
    total_bonus = models.IntegerField(verbose_name="Кол-во кредитов бонусом которые ещё актуальны")
    # initial_bonus = models.IntegerField(verbose_name="Стартовый зачисленный бонус", null=True)
    # in_process = models.BooleanField(verbose_name="В процессе списания", default=False, db_index=True)
    is_active = models.BooleanField(verbose_name="Активен", default=False, db_index=True)
    is_from_referal_activated = models.BooleanField(verbose_name="Бонус с рефералок который надо дополнительно забрать",
                                                    db_index=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(auto_now=True)
    detail_user = models.ForeignKey('DetailUser', on_delete=models.CASCADE, null=True, related_name='bonuses')

    @property
    def bonus_to_win_back(self):
        return self._bonus_to_win_back

    @bonus_to_win_back.setter
    def bonus_to_win_back(self, value):
        """Если отыгрывать больше нечего -> _bonus_to_win_back=0
        ставит флаги:
        is_active=False,
        """
        self._bonus_to_win_back = value
        if value == 0:
            self.is_active = False

    def save(self, *args, **kwargs):
        if self.id is None and self.is_from_referal_activated is not None:
            self.detail_user.balance += self.total_bonus
            self.detail_user.save()
        if self.is_from_referal_activated and self.is_active and self.id:
            self.detail_user.balance += self.total_bonus
            self.detail_user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.total_bonus}/{self._bonus_to_win_back}, {self.detail_user}'

    class Meta:
        ordering = "date_created", "-_bonus_to_win_back",


class ReferalCode(models.Model):
    """Модель реферальных ссылок"""
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    ref_code = models.CharField(
        verbose_name="Реферальный код",
        unique=True,
        max_length=200,
        validators=[validate_referal],
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Реферальный код'
        verbose_name_plural = 'Реферальный код'

    def __str__(self):
        return f'{self.ref_code}'


class ReferalUser(models.Model):
    """Модель пользователей приглашённых на сайт"""
    user_with_bonus = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="users_with_bonus",
                                        verbose_name="Пользователь который пригласил", null=True, blank=True)
    invited_user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name="invited_users",
                                        verbose_name="Приглашенный пользователь", null=True, blank=True)
    bonus_sum = models.PositiveBigIntegerField(verbose_name='Сумма бонуса', default=25000)
    date = models.DateTimeField(verbose_name="Дата получения бонуса", auto_now_add=True)

    class Meta:
        verbose_name = 'Приглашенный пользователь'
        verbose_name_plural = 'Приглашенный пользователь'

    def __str__(self):
        return f'{self.user_with_bonus}'


class GameID(models.Model):
    """Модель игровых id из игры дурак онлайн"""
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
    private_key_hashed = models.CharField(verbose_name='Захешированный приватный ключ', max_length=64, null=True,
                                          blank=True)
    date_generated = models.DateField(verbose_name='Дата генерации', unique=True)
    show_hash = models.BooleanField(verbose_name='Показывать в честности (текущий день)', default=True)

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
    round_number = models.PositiveBigIntegerField(verbose_name='Номер раунда', default=0, unique=True)
    round_started = models.DateTimeField(verbose_name='Время начала раунда', blank=True, null=True)
    round_roll = models.CharField(verbose_name='Результат раунда', max_length=6, choices=ROUND_RESULT_CHOISES,
                                  default='hearts')
    rolled = models.BooleanField(verbose_name='Раунд был сыгран', default=False)
    day_hash = models.ForeignKey('DayHash', verbose_name='Хеши раунда', on_delete=models.PROTECT, blank=True, null=True)
    # show_round = models.BooleanField(verbose_name='Отображение раунда в честности', default=True)
    total_bet_amount = models.PositiveBigIntegerField(verbose_name='Общая сумма ставок', default=0)
    winners = models.ManyToManyField('CustomUser', verbose_name='Победители раунда', blank=True)
    day_of_round = models.DateField(verbose_name="Дата когда должен быть сыгран раунд", auto_now_add=True)
    time_rolled = models.DateTimeField(verbose_name="Время когда был сыгран", auto_now=True)

    def __str__(self):
        return f"Раунд номер {self.round_number}: {self.total_bet_amount} кредитов. {self.round_roll}"

    class Meta:
        verbose_name = 'Раунд рулетки'
        verbose_name_plural = 'Раунды рулетки'
        ordering = ('round_number',)


class ItemForUser(models.Model):
    """Предметы пользователя"""
    user_item = models.ForeignKey('caseapp.Item', verbose_name='Предмет', null=True, blank=True,
                                  on_delete=models.CASCADE)
    user = models.ForeignKey('CustomUser', verbose_name='Пользователь', null=True, blank=True, on_delete=models.CASCADE)
    is_used = models.BooleanField(verbose_name='Использован', default=False)
    # date = models.DateTimeField(verbose_name="Дата получения", null=True, auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name="Дата изменения", null=True, auto_now=True)
    is_money = models.BooleanField(verbose_name="Деньги", default=False)
    is_forwarded = models.BooleanField(verbose_name="Выведен", default=False)

    class Meta:
        verbose_name = 'Предмет пользователя'
        verbose_name_plural = 'Предметы пользователя'
        ordering = "-date_modified",

    def __str__(self):
        return self.user_item.name


class AvatarProfile(models.Model):
    """Модель Аватарки профиля"""
    name = models.CharField(verbose_name='Название аватарки профиля', max_length=50, blank=True, null=True)
    avatar_img = models.ImageField(verbose_name='Аватарки профиля', help_text='Аватарки профиля',
                                   upload_to='img/avatar/default/')

    class Meta:
        verbose_name = 'Стандартные аватарки'
        verbose_name_plural = 'Стандартные аватарки'
        ordering = 'id',

    def __str__(self):
        return f'{self.name}'


class UserBet(models.Model):
    """Модель для сохранения транзакций связанных со ставками в рулетке"""
    COIN = 'coin'
    HEART = 'hearts'
    SPADES = 'spades'
    # список состояний заявки
    SUIT_CHOICE_LIST = [
        (COIN, 'монетка'),
        (HEART, 'червы'),
        (SPADES, 'пики'),
    ]
    sum = models.PositiveIntegerField(verbose_name='Сумма ставки', default=0)
    sum_win = models.PositiveIntegerField(verbose_name='Сумма выигрыша', default=0)
    win = models.BooleanField(verbose_name='Ставка выиграла', default=False)
    date = models.DateTimeField(verbose_name='Дата совершения ставки', auto_now_add=True)
    round_number = models.PositiveBigIntegerField(verbose_name='Номер раунда', default=0)
    placed_on = models.CharField(verbose_name='Поставлено на', max_length=6, choices=SUIT_CHOICE_LIST, default='c')
    user = models.ForeignKey('CustomUser', verbose_name='Пользователь', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"Ставка {self.sum}, {self.date}, выиграла: {self.win}"

    class Meta:
        verbose_name = 'Ставка пользователя'
        verbose_name_plural = 'Ставки пользователей'


class BonusVKandYoutube(models.Model):
    """Модель полученных бонусов за подписки на vk и youtube"""
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='vk_youtube')
    bonus_vk = models.BooleanField(verbose_name="Получен бонус за vk", default=False)
    bonus_youtube = models.BooleanField(verbose_name="Получен бонус за youtube", default=False)
    date_created_vk = models.DateTimeField(null=True, verbose_name='Когда создана подписка ВК')
    date_created_youtube = models.DateTimeField(null=True, verbose_name='Когда создана подписка YouTube')
    vk_disabled = models.BooleanField(default=False, verbose_name="Неактивно на время проверки подписки")
    youtube_disabled = models.BooleanField(default=False, verbose_name="Неактивно на время проверки подписки")

    class Meta:
        verbose_name = 'Бонус за подписку'
        verbose_name_plural = 'Бонусы за подписки'

    def __str__(self):
        return ''
