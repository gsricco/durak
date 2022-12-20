from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Модель пополнения
class Popoln(models.Model):
    # user_game = models.ForeignKey(User, verbose_name='Игрок', on_delete=models.CASCADE)
    sum = models.FloatField("Сумма", default=50.00)
    date = models.DateTimeField("Дата покупки", default=timezone.now)
    odobren = models.BooleanField("Успех пополнения", default=False)

    class Meta:
        verbose_name = "Пополнение"
        verbose_name_plural = "Пополнения"

    # def __str__(self):
    #     return self.user.username
