from django.urls import path

from . import views


urlpatterns = [
    path("go/", views.chat, name="pay_chat"),
]
