from django.urls import include, path
from rest_framework import routers

from accaunts.api_views import ReferalCodeViewSet, give_bonus
from bot_payment.api_views import RefillRequestViewSet, WithdrawRequestViewSet
from caseapp import urls as caseappurls
from support_chat.views import MessageViewSet

router = routers.DefaultRouter()

# чат поддержки
router.register(r'message', MessageViewSet, basename='support_chat')
# заявки на ввод средств из игры Durak Online
router.register(r'refill_request', RefillRequestViewSet, basename='bot_refill')
router.register(r'withdraw_request', WithdrawRequestViewSet, basename='bot_withdraw')
router.register(r'referal_code', ReferalCodeViewSet, basename='referal')


urlpatterns = [
    path('api/v1/', include(router.urls + caseappurls.urlpatterns)),
    path('api/v1/get_bonus/<str:ref_code>/', give_bonus),
]
