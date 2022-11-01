from ckeditor.fields import RichTextField
from django.db import models


class SiteContent(models.Model):
    """Контент сайта"""
    # ЧЕСТНОСТЬ
    honesty_game = RichTextField(verbose_name='Как мне убедиться в честности игры?')
    roll = RichTextField(verbose_name='Рулетка')
    # ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ
    agreement = RichTextField(verbose_name='Пользовательское соглашение')
    # КОНТАКТЫ
    about_us = RichTextField(verbose_name='О нас')
    description = RichTextField(verbose_name='Описание снизу')
    support_email = models.EmailField(verbose_name='Почта для связи с поддержкой')
    url_vk = models.URLField(verbose_name="Ссылка на VK")
    url_youtube = models.URLField(verbose_name="Ссылка на Youtube")

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
