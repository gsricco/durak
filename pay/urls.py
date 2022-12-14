from django.urls import path

from .views import balance

urlpatterns = [
    path('buy/', balance, name='balance'),

]
