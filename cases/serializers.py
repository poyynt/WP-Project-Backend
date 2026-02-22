from rest_framework import serializers

from suspects.models import Suspect
from .models import Case, Complainant
from accounts.serializers import UserSerializer


class CaseSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Case
        fields = ["id", "title", "level", "status", "created_at", "created_by"]


class ComplainantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Complainant
        fields = ["id", "case", "user", "verified"]
        read_only_fields = ["id"]


class MostWantedSerializer(serializers.ModelSerializer):
    reward_price = serializers.SerializerMethodField()

    class Meta:
        model = Suspect
        fields = ["id", "first_name", "last_name", "image", "reward_price"]

    def get_reward_price(self, obj):
        if not obj.max_duration:
            return 0
        days = obj.max_duration.days
        return days * obj.max_level * 20_000_000
