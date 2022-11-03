from rest_framework import serializers
from .models import Case, Grade, Item, OwnedCase
import datetime

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


class OwnedCaseSerializer(serializers.Serializer):
    case = CaseSerializer()
    owner = serializers.PKOnlyObject('auth.User')
    date_owned = serializers.DateTimeField()
    date_opened = serializers.DateTimeField()
    item = ItemSerializer()

    class Meta:
        model = OwnedCase


class OwnedCaseTimeSerializer(serializers.Serializer):
    """Serializer for getting time before next case can be opened"""
    date_opened = serializers.DateTimeField()
    seconds_since_prev_open = serializers.SerializerMethodField()
    can_be_opened = serializers.SerializerMethodField()

    def get_seconds_since_prev_open(self, obj):
        """Returns time since prev_open"""
        if obj.date_opened is None:
            return 0

        delta_time = datetime.datetime.now(datetime.timezone.utc) - obj.date_opened
        return delta_time.seconds

    def get_can_be_opened(self, obj):
        """Returns whether case can be opened or not"""
        if obj.date_opened is None:
            return True

        delta_time = datetime.datetime.now(datetime.timezone.utc) - obj.date_opened
        can_be = delta_time >= datetime.timedelta(hours=1)

        return can_be

    class Meta:
        model = OwnedCase
