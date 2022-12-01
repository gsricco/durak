from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from . import serializers
from . import models


class RefillRequestViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Возвращает все заявки пользователя
        """
        user_pk = request.user.pk
        queryset = models.RefillRequest.objects.filter(user_id=user_pk)
        serializer = serializers.RefillRequestModelSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Возвращает заявку пользователя с заданным pk
        """
        user_pk = request.user.pk
        refill_request = get_object_or_404(models.RefillRequest, pk=pk, user_id=user_pk)
        serializer = serializers.RefillRequestModelSerializer(refill_request)
        return Response(serializer.data)
    
    def create(self, request):
        """
        Создаёт заявку пользователя.
        Пример json (минимальный):
        {
            "user_id": {
                "id": 1
            },
            "amount": 1000,
            "balance": 120
        }
        """
        serializer = serializers.RefillRequestModelSerializer(data=request.data)
        if serializer.is_valid():
            if request.user.pk != serializer.validated_data['user_id']['id']:
                return Response({"detail": "can't create request for other user"}, status=status.HTTP_403_FORBIDDEN)

            refill_request = serializer.save()
            response_serializer = serializers.RefillRequestModelSerializer(refill_request)
            return Response(response_serializer.data)
        
        return Response({"detail": "data validation failed"}, status=status.HTTP_400_BAD_REQUEST)
