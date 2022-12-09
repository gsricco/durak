from django.urls import path

from .views import buy, popoln, success, fail

urlpatterns = [
    path('buy/', buy, name='buy'),
    path('popoln/', popoln, name='popoln'),
    path('success/', success, name='success'),
    path('fail/', fail, name='fail'),
]
