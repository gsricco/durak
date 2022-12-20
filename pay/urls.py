from django.urls import path

from .views import pay_user, balance

urlpatterns = [
    path('buy/', balance, name='balance'),
    # path('payment_success/', payment_success, name='balance'),
    path('pay_user/', pay_user, name='pay_user')

]
