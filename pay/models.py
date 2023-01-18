from django.contrib.postgres.fields import BigIntegerRangeField
from django.db import models
from django.utils import timezone
from accaunts.models import CustomUser


class Popoln(models.Model):
    """История транзакций"""
    user_game = models.ForeignKey(CustomUser, verbose_name='Пользователь', on_delete=models.CASCADE,
                                  related_name='us_game')
    sum = models.IntegerField(verbose_name="Сумма пополнения в деньгах")
    currency = models.IntegerField(verbose_name="Валюта пополнения", default=1)
    pay = models.IntegerField(verbose_name="Сумма купленных кредитов", blank=True, null=True)
    date = models.DateTimeField(verbose_name="Дата покупки", default=timezone.now)
    status_pay = models.BooleanField(verbose_name="Оплачено", default=False)
    url_ok = models.BooleanField(verbose_name='Показывать модалку', default=True)
    intid = models.IntegerField(verbose_name='Номер операции Free-Kassa', blank=True, null=True)

    class Meta:
        verbose_name = "Пополнение"
        verbose_name_plural = "Пополнения"
        ordering = 'user_game',

    def __str__(self):
        return f''


class BalPay(models.Model):
    """Кредиты за реальные деньги"""
    conversion_coef = models.PositiveIntegerField(verbose_name='Коэффициент конверсии рубль/игровая валюта',
                                                  help_text="В х раз", default=1)
    range_sum = BigIntegerRangeField(verbose_name='Диапазон в рублях - на который применяется данный коэффициент',
                                     null=True)
    range_credits = BigIntegerRangeField(verbose_name="Диапазон в кредитах", null=True)

    class Meta:
        verbose_name = "Коэффициент конверсии рубль/игровая валюта"
        verbose_name_plural = "Коэффициенты конверсии рубль/игровая валюта"
        ordering = 'range_sum',

    def __str__(self):
        return f'Сумма в рублях - от {self.range_sum.lower} до {self.range_sum.upper}'


class RefillBotSum(models.Model):
    """Кнопки с суммами для пополнения кредитов через бота"""
    credits = models.PositiveBigIntegerField(verbose_name="Сумма кредитов", default=0)
    text = models.CharField(verbose_name="Текст на кнопке", max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.text}, сумма: {self.credits}"

    class Meta:
        verbose_name = "Сумма для пополнения через бота"
        verbose_name_plural = "Суммы для пополнения через бота"
        ordering = ['credits']


class WithdrawBotSum(models.Model):
    """Кнопки с суммами для вывода кредитов через бота"""
    credits = models.PositiveBigIntegerField(verbose_name="Сумма кредитов", default=0)
    text = models.CharField(verbose_name="Текст на кнопке", max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.text}, сумма: {self.credits}"

    class Meta:
        verbose_name = "Сумма для вывода через бота"
        verbose_name_plural = "Суммы для вывода через бота"
        ordering = ['credits']


class PayOff(models.Model):
    work = models.BooleanField(verbose_name='Оплаты только через FKWallet', default=False)

    def __str__(self):
        return f"{self.work}"

    class Meta:
        verbose_name = "Оплаты только через FKWallet"
        verbose_name_plural = "Оплаты только через FKWallet"
