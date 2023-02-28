from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import DetailUser, ReferalCode, ReferalUser, UserBonus, FreeBalanceHistory
from .serializers import ReferalCodeModelSerializer


@api_view(['GET'])
def give_bonus(request, ref_code):
    """Даёт бонус за регистрацию пользователю"""
    if request.user.is_authenticated:
        # проверяем, есть ли такой код
        referal_code = get_object_or_404(ReferalCode, ref_code=ref_code)
        # проверка, не активировал ли юзер свой же код
        if referal_code.user == request.user:
            return Response(data='{detail: "Вы активируете свой код"}', status=status.HTTP_403_FORBIDDEN)
        # проверяем, не активировал ли юзер код
        try:
            with transaction.atomic():
                (activation_referal, created) = ReferalUser.objects.get_or_create(invited_user=request.user)
                # если это первая активация
                if created:
                    activation_referal.user_with_bonus = referal_code.user  # != request.user
                    detail_user = get_object_or_404(DetailUser, user=referal_code.user)
                    detail_user.free_balance += activation_referal.bonus_sum
                    request.user.detailuser.balance += activation_referal.bonus_sum
                    # request.user -> user who activating, detail_user -> user who owns code
                    FreeBalanceHistory.objects.create(detail_user=request.user.detailuser,
                                                      is_active=False,
                                                      bonus_sum=activation_referal.bonus_sum,
                                                      activated_by=1)
                    FreeBalanceHistory.objects.create(detail_user=detail_user,
                                                      bonus_sum=activation_referal.bonus_sum)
                    UserBonus.objects.create(detail_user=request.user.detailuser,
                                             _bonus_to_win_back=activation_referal.bonus_sum * 3,
                                             total_bonus=activation_referal.bonus_sum,
                                             is_active=True)
                    UserBonus.objects.create(detail_user=detail_user,
                                             _bonus_to_win_back=activation_referal.bonus_sum * 2,
                                             total_bonus=activation_referal.bonus_sum)
                    activation_referal.save()
                    request.user.detailuser.save()
                    detail_user.save()
                    return Response(data='{detail: "Код активирован"}', status=status.HTTP_200_OK)
                return Response(data='{detail: "Вы уже активировали код"}', status=status.HTTP_403_FORBIDDEN)
        except IntegrityError:
            return Response(data='{detail: "Ошибка, попробуйте ещё раз позже"}', status=status.HTTP_403_FORBIDDEN)
    return Response(data='{detail: "Войдите в аккаунт на сайте"}', status=status.HTTP_401_UNAUTHORIZED)


class ReferalCodeViewSet(ViewSet):
    """Апи для реферального кода"""
    queryset = ReferalCode.objects.all()
    serializer_class = ReferalCodeModelSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=0):
        """
        Возвращает реферальный код
        """
        user_pk = request.user.pk
        if user_pk != int(pk):
            return Response({"detail": "нельзя получить код другого юзера"}, status=status.HTTP_403_FORBIDDEN)
        referal = get_object_or_404(self.queryset, user=user_pk)
        serializer = self.serializer_class(referal)
        return Response(serializer.data)

    def create(self, request):
        """
        Создаёт реферальный код.
        {
            "ref_code": "345678",
            "user": {
                "id": 2
            }
        }
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if request.user != serializer.validated_data['user']:
                return Response({"detail": "нельзя создать код для другого юзера"}, status=status.HTTP_403_FORBIDDEN)

            referal = serializer.save()
            response_serializer = self.serializer_class(referal)
            return Response(response_serializer.data)
        
        return Response({"detail": "неверные данные"}, status=status.HTTP_400_BAD_REQUEST)
