from rest_framework import serializers
from .models import Suspect, Investigation

class SuspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suspect
        fields = ["id", "image", "first_name", "last_name", "national_id", "status", "case"]

class InvestigationSerializer(serializers.ModelSerializer):
    suspect = serializers.PrimaryKeyRelatedField(queryset=Suspect.objects.all())

    class Meta:
        model = Investigation
        fields = ["id", "suspect", "investigator", "score", "created_at"]
        read_only_fields = ["id", "investigator", "created_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        return Investigation.objects.create(investigator=user, **validated_data)