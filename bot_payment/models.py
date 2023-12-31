from django.db import models


class RefillRequest(models.Model):
    """
    Модель для хранения заявок пользователей на ввод средств из игры Durak Online
    """

    # константы для choice
    OPEN = 'open'
    SUCCESS = 'succ'
    FAIL = 'fail'
    # список состояний заявки
    STATUS_CHOICE_LIST = [
        (OPEN, 'открыта'),
        (SUCCESS, 'закрыта (успешно)'),
        (FAIL, 'закрыта (не успешно)'),
    ]
    
    # переопределяет первичный ключ для задания verbose_name
    id = models.BigAutoField(verbose_name='ID заявки', primary_key=True)
    request_id = models.BigIntegerField(verbose_name='Номер заявки', default=0)

    status = models.CharField(verbose_name='Статус заявки', max_length=4, choices=STATUS_CHOICE_LIST, default=OPEN)
    amount = models.PositiveBigIntegerField(verbose_name='Сумма пополнения', default=0)
    balance = models.PositiveBigIntegerField(verbose_name='Баланс пользователя в игре', default=100)

    date_opened = models.DateTimeField(verbose_name='Дата открытия заявки', auto_now_add=True)
    date_closed = models.DateTimeField(verbose_name='Дата закрытия заявки', null=True, blank=True)

    note = models.CharField(verbose_name='Заметка заявки', max_length=255, null=True, blank=True)
    close_reason = models.CharField(verbose_name='Причина закрытия заявки', max_length=50, null=True, blank=True)

    user = models.ForeignKey(to='accaunts.CustomUser', verbose_name='пользователь на сайте', on_delete=models.SET_NULL, null=True)
    game_id = models.BigIntegerField(verbose_name='id пользователя в игре', null=True, blank=True)
    bot_name = models.CharField(verbose_name='Имя бота', max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Заявка {self.request_id} <статус:{self.status}> сумма: {self.amount}"
    
    class Meta:
        verbose_name = "Заявка на пополнение"
        verbose_name_plural = "Заявки на пополнение"


class WithdrawalRequest(models.Model):
    """
    Заявка на вывод средств в игру Durak Online
    """

    # константы для choice
    OPEN = 'open'
    SUCCESS = 'succ'
    FAIL = 'fail'
    # список состояний заявки
    STATUS_CHOICE_LIST = [
        (OPEN, 'открыта'),
        (SUCCESS, 'закрыта (успешно)'),
        (FAIL, 'закрыта (не успешно)'),
    ]

    # переопределяет первичный ключ для задания verbose_name
    id = models.BigAutoField(verbose_name='ID заявки', primary_key=True)
    request_id = models.BigIntegerField(verbose_name='Номер заявки', default=0)

    status = models.CharField(verbose_name='Статус заявки', max_length=4, choices=STATUS_CHOICE_LIST, default=OPEN)
    amount = models.PositiveBigIntegerField(verbose_name='Сумма вывода', default=0)
    balance = models.PositiveBigIntegerField(verbose_name='Баланс пользователя в игре', default=100)

    date_opened = models.DateTimeField(verbose_name='Дата открытия заявки', auto_now_add=True)
    date_closed = models.DateTimeField(verbose_name='Дата закрытия заявки', null=True, blank=True)

    note = models.CharField(verbose_name='Заметка заявки', max_length=255, null=True, blank=True)
    close_reason = models.CharField(verbose_name='Причина закрытия заявки', max_length=50, null=True, blank=True)

    user = models.ForeignKey(to='accaunts.CustomUser', verbose_name='пользователь на сайте', on_delete=models.SET_NULL, null=True)
    game_id = models.BigIntegerField(verbose_name='id пользователя в игре', null=True, blank=True)
    bot_name = models.CharField(verbose_name='Имя бота', max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Заявка {self.request_id} <статус:{self.status}> сумма: {self.amount}"

    class Meta:
        verbose_name = "Заявка на вывод"
        verbose_name_plural = "Заявки на вывод"


class BotWork(models.Model):
    work = models.BooleanField(verbose_name='Отключить работу бота на пополнение', default=False)
    work_t = models.BooleanField(verbose_name='Отключить работу бота на вывод', default=False)

    class Meta:
        verbose_name = "Отключение бота"
        verbose_name_plural = "Отключение бота"

    def __str__(self):
        return f"Отключение бота"


class BanTime(models.Model):
    hours = models.PositiveIntegerField(verbose_name="Количество часов бана пользователя", default=4)

    class Meta:
        verbose_name = "Время бана более 3-х попыток"
        verbose_name_plural = "Время бана более 3-х попыток"

    def __str__(self):
        return f"Время бана пользователя"