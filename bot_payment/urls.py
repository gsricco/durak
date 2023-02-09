from django.urls import path

from . import views

urlpatterns = [
    path("go/", views.chat, name="pay_chat"),
    path("go_withdraw/", views.withdraw, name="withdraw_chat"),
]
