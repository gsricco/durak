from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from .serializers import ReferalCodeModelSerializer
from .models import ReferalCode, ReferalUser, DetailUser


@api_view(['GET'])
def give_bonus(request, ref_code):
    """Даёт бонус за регистрацию пользователю"""
    if request.user.is_authenticated:
        # проверяем, есть ли такой код
        referal = get_object_or_404(ReferalCode, ref_code=ref_code)
        # проверка, не активировал ли юзер свой же код
        if referal.user == request.user:
            return Response(data='{detail: "Вы активируете свой код"}', status=status.HTTP_403_FORBIDDEN)
        # проверяем, не активировал ли юзер код 
        (referal_user, created) = ReferalUser.objects.get_or_create(invited_user=request.user)
        # если это первая активация
        if created:
            referal_user.user_with_bonus = referal.user
            detail_user = get_object_or_404(DetailUser, user=referal.user)
            detail_user.free_balance += referal_user.bonus_sum
            referal_user.save()
            detail_user.save()
            return Response(data='{detail: "Код активирован"}', status=status.HTTP_200_OK)
        return Response(data='{detail: "Вы уже активировали код"}', status=status.HTTP_403_FORBIDDEN)
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
