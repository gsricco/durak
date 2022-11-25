from rest_framework import routers
from django.urls import path, include

from support_chat.views import MessageViewSet
from caseapp import urls as caseappurls


router = routers.DefaultRouter()

# чат поддержки
router.register(r'message', MessageViewSet, basename='support_chat')


urlpatterns = [
    path('api/v1/', include(router.urls + caseappurls.urlpatterns)),
]
