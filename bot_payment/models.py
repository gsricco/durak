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

    user = models.ForeignKey(to='accaunts.CustomUser', verbose_name='пользователь на сайте', on_delete=models.DO_NOTHING)
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

    user = models.ForeignKey(to='accaunts.CustomUser', verbose_name='пользователь на сайте', on_delete=models.PROTECT)
    game_id = models.BigIntegerField(verbose_name='id пользователя в игре', null=True, blank=True)
    bot_name = models.CharField(verbose_name='Имя бота', max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Заявка {self.request_id} <статус:{self.status}> сумма: {self.amount}"

    class Meta:
        verbose_name = "Заявка на вывод"
        verbose_name_plural = "Заявки на вывод"
