from rest_framework import serializers
from .models import Case, Grade, Item


class GradeModelSerializer(serializers.ModelSerializer):
    """Grade serializer for Case serializer"""
    class Meta:
        model = Grade
        fields = ('name', 'image', 'min_lvl')


class CaseSerializer(serializers.Serializer):
    """Case serializer"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    grade = GradeModelSerializer()

    class Meta:
        model = Case


class ItemSerializer(serializers.Serializer):
    """Item serializer"""
    name = serializers.CharField()
    image = serializers.ImageField()
    selling_price = serializers.IntegerField()

    class Meta:
        model = Item
