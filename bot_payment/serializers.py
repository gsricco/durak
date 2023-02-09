from rest_framework import serializers

from accaunts.models import CustomUser

from . import models


class CustomUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    class Meta:
        model = CustomUser


class RefillRequestModelSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    def create(self, validated_data):
        refill_request = models.RefillRequest()
        refill_request.amount = validated_data.get('amount', 0)
        refill_request.balance = validated_data.get('balance', 0)
        user_pk = validated_data.get('user').get('id')
        refill_request.note = validated_data.get("note")
        refill_request.user = CustomUser.objects.get(pk=user_pk)
        refill_request.game_id = validated_data.get('game_id')
        refill_request.request_id = validated_data.get('request_id', 0)
        refill_request.save()
        return refill_request

    class Meta:
        model = models.RefillRequest
        fields = '__all__'        


class WithdrawRequestModelSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    def create(self, validated_data):
        withdraw_request = models.WithdrawalRequest()
        withdraw_request.amount = validated_data.get('amount', 0)
        withdraw_request.balance = validated_data.get('balance', 0)
        user_pk = validated_data.get('user').get('id')
        withdraw_request.user = CustomUser.objects.get(pk=user_pk)
        withdraw_request.game_id = validated_data.get('game_id')
        withdraw_request.request_id = validated_data.get('request_id', 0)
        withdraw_request.save()

        return withdraw_request


    class Meta:
        model = models.WithdrawalRequest
        fields = '__all__'        
