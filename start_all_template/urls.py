from django.urls import path
from .views import index, index123, bonus_currency, contact, faq, honesty, profil

urlpatterns = [
    path('', index, name='index'),
    path('index123', index123, name='index123'),
    path('bonus-currency', bonus_currency, name='bonus-currency'),
    path('contact', contact, name='contact'),
    path('faq', faq, name='faq'),
    path('honesty', honesty, name='honesty'),
    path('profil', profil, name='profil'),
]
