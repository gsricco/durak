from django.db import models
from django.utils import timezone
from accaunts.models import CustomUser


class Popoln(models.Model):
    user_game = models.ForeignKey(CustomUser, verbose_name='Игрок', on_delete=models.CASCADE, related_name='us_game')
    sum = models.DecimalField(verbose_name="Сумма пополнения", max_digits=8, decimal_places=2)
    date = models.DateTimeField(verbose_name="Дата покупки", default=timezone.now)
    status_pay = models.CharField(verbose_name="Статус оплаты", max_length=200)

    class Meta:
        verbose_name = "Пополнение"
        verbose_name_plural = "Пополнения"
        ordering = 'user_game',

    def __str__(self):
        return f'{self.user_game} - {self.sum}'


    # def save(self, *args, **kwargs):
    #     if sum != None:
    #         user_balans = sum * 80
    #         userbalance
    #

