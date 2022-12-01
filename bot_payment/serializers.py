from rest_framework import serializers
from . import models
from accaunts.models import CustomUser


class CustomUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    class Meta:
        model = CustomUser


class RefillRequestModelSerializer(serializers.ModelSerializer):
    user_id = CustomUserSerializer()

    def create(self, validated_data):
        refill_request = models.RefillRequest()
        refill_request.amount = validated_data.get('amount', 0)
        refill_request.balance = validated_data.get('balance', 0)
        user_pk = validated_data.get('user_id').get('id')
        refill_request.user_id = CustomUser.objects.get(pk=user_pk)
        refill_request.game_id = validated_data.get('game_id')
        refill_request.save()

        return refill_request


    class Meta:
        model = models.RefillRequest
        fields = '__all__'        
