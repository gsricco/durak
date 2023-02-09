from django.urls import path

from .views import bonus_currency, contact, faq, honesty, index, info, profil

urlpatterns = [
    path('', index, name='index'),
    path('bonus-currency/', bonus_currency, name='bonus-currency'),
    path('contact/', contact, name='contact'),
    path('faq/', faq, name='faq'),
    path('honesty/', honesty, name='honesty'),
    path('profil/', profil, name='profil'),
    path('info/', info, name='info'),
]
