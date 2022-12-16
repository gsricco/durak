from django.db import models
from django.utils import timezone
from accaunts.models import CustomUser


class Popoln(models.Model):
    user_game = models.ForeignKey(CustomUser, verbose_name='Пользователь', on_delete=models.CASCADE,
                                  related_name='us_game')
    sum = models.IntegerField(verbose_name="Сумма пополнения")
    currency = models.ForeignKey('Currency', verbose_name='Валюта пополнения', on_delete=models.CASCADE)
    # currency = models.IntegerField(verbose_name="Валюта пополнения", blank=True, null=True)
    pay = models.IntegerField(verbose_name="Сумма купленных кредитов", blank=True, null=True)
    date = models.DateTimeField(verbose_name="Дата покупки", default=timezone.now)
    status_pay = models.BooleanField(verbose_name="Оплачено", default=False)
    url_pay = models.URLField(verbose_name='Страница для редиректа', blank=True, null=True)

    class Meta:
        verbose_name = "Пополнение"
        verbose_name_plural = "Пополнения"
        ordering = 'user_game',

    def __str__(self):
        return f'{self.user_game} - {self.sum}'


class Currency(models.Model):
    name = models.CharField(verbose_name='Валюта пополнения', max_length=200, unique=True)

    class Meta:
        verbose_name = "Валюта пополнения"
        verbose_name_plural = "Валюта пополнения"

    def __str__(self):
        return f'{self.name}'
