from rest_framework import serializers
from .models import ReferalCode


class ReferalCodeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferalCode
        fields = '__all__'
