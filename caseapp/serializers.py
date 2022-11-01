from rest_framework import serializers
from .models import Case, Grade


class GradeModelSerializer(serializers.ModelSerializer):
    """Grade serializer for Case serializer"""
    class Meta:
        model = Grade
        fields = ('name', 'min_lvl')


class CaseSerializer(serializers.Serializer):
    """Case serializer"""
    name = serializers.CharField()
    grade = GradeModelSerializer()

    class Meta:
        model = Case
