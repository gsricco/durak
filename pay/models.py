from django.db import models
from django.utils import timezone
from accaunts.models import CustomUser


class Popoln(models.Model):
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
