from django.apps import AppConfig


class BotPaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot_payment'
    verbose_name = 'Заявки на ввод-вывод средств из игры Durak Online'
