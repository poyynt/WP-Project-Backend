from rest_framework import serializers
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