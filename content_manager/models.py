from ckeditor.fields import RichTextField
from django.db import models


class SiteContent(models.Model):
    """Контент сайта"""
    # ПРАВИЛО ЧАТА
    chat_rule = RichTextField(verbose_name='Правила чата', null=True)
    # ЧЕСТНОСТЬ
    honesty_game = RichTextField(verbose_name='Как мне убедиться в честности игры?', null=True)
    roll = RichTextField(verbose_name='Рулетка', null=True)
    # ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ
    agreement = RichTextField(verbose_name='Пользовательское соглашение', null=True)
    # КОНТАКТЫ
    about_us = RichTextField(verbose_name='О нас', null=True)
    description = RichTextField(verbose_name='Описание снизу', null=True)
    support_email = models.EmailField(verbose_name='Почта для связи с поддержкой', null=True)
    url_vk = models.URLField(verbose_name="Ссылка на VK", null=True)
    url_youtube = models.URLField(verbose_name="Ссылка на Youtube", null=True)
    # FREE
    info2 = RichTextField(verbose_name='Информация #2', null=True)
    info3 = RichTextField(verbose_name='Информация #3', null=True)
    bonus_vk = models.IntegerField(verbose_name="Бонус за подписку на VK", null=True)
    bonus_youtube = models.IntegerField(verbose_name="Бонус за подписку на YouTube", null=True)
    vk_group_id = models.CharField(verbose_name="ID группы Вконтакте", null=True, max_length=250)
    youtube_channel_id = models.CharField(verbose_name="ID канала на YouTube", null=True, max_length=250)

    class Meta:
        verbose_name = 'Контент сайта'
        verbose_name_plural = 'Контент сайта'

    def __str__(self):
        return f'Контент сайта'


class FAQ(models.Model):
    """Помощь"""
    name = models.CharField(verbose_name='Название вопроса', max_length=250)
    description = RichTextField(verbose_name='Описание вопроса')
    is_active = models.BooleanField(verbose_name='Активный', default=True)

    class Meta:
        verbose_name = 'Часто задаваемые вопросы'
        verbose_name_plural = 'Часто задаваемые вопросы'

    def __str__(self):
        return self.name

    def body_description(self):
        return f"%s..." % (self.description[:200],)

    body_description.short_description = 'Описание вопроса'


class BadSlang(models.Model):
    """Запрещенные слова"""
    name = models.CharField(verbose_name='Запрещенное слово', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Запрещенные слова'
        verbose_name_plural = 'Запрещенные слова'

    def __str__(self):
        return self.name


class FakeOnline(models.Model):
    """Фейковый онлайн чата"""
    count = models.PositiveIntegerField(verbose_name="Фейк онлайн в чате", default=0)
    is_active = models.BooleanField(default=False, verbose_name="Активно")

    class Meta:
        verbose_name = "Фейковый онлайн"
        verbose_name_plural = "Фейковый онлайн"

    def __str__(self):
        return f'Онлайн: {self.count}'


class ShowRound(models.Model):
    """Показывать раунды в транзакциях(профиле пользователя)"""
    show = models.BooleanField(verbose_name="Показывать раунд в транзакциях", default=True)

    def __str__(self):
        return f'Показывать раунды в транзакциях'

    class Meta:
        verbose_name = "Показывать раунд в транзакциях"
        verbose_name_plural = "Показывать раунды в транзакциях"


class DurakNickname(models.Model):
    """Устанавливать Никнейм в модалке(в профиле юзера) при выводе предмета из кейса в игру дурак-онлайн"""
    nickname = models.CharField(max_length=50, verbose_name='Ник для вывода')
    date = models.DateTimeField(auto_now=True, verbose_name='Дата последнего изменения')

    def __str__(self):
        return f'Текущий ник - {self.nickname}'

    class Meta:
        verbose_name = 'Никнейм для вывода'
        verbose_name_plural = 'Никнейм для вывода'


class BalanceEditor(models.Model):
    """Предоставляет возможность изменения баланса юзера для админа"""
    to_user = models.ForeignKey('accaunts.CustomUser', verbose_name="Пользователь", on_delete=models.CASCADE, null=True)
    amount = models.PositiveBigIntegerField(verbose_name="Сумма для изменения")
    to_add = models.BooleanField(verbose_name="Добавить или уменьшить баланс", default=True)
    date = models.DateTimeField(verbose_name="Дата операции", auto_now_add=True)

    def __str__(self):
        return ''

    class Meta:
        verbose_name = "Изменение баланса"
        verbose_name_plural = "Изменение баланса"
        ordering = "-date",
