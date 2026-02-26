from rest_framework import serializers
from .models import Evidence, EvidenceFile
from cases.models import Case
from accounts.models import User


class EvidenceFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceFile
        fields = ["id", "file", "uploaded_at"]


class EvidenceSerializer(serializers.ModelSerializer):
    files = EvidenceFileSerializer(many=True, read_only=True)
    case = serializers.PrimaryKeyRelatedField(queryset=Case.objects.all())
    # recorded_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    metadata = serializers.JSONField()

    class Meta:
        model = Evidence
        fields = [
            "id",
            "case",
            "type",
            "title",
            "description",
            "metadata",
            # "recorded_by",
            "recorded_at",
            "files",
        ]
        read_only_fields = ["recorded_at"]

    def create(self, validated_data):
        """
        Handle file creation and association with evidence
        """
        request = self.context["request"]
        evidence = Evidence.objects.create(**validated_data)

        for file in request.FILES.getlist("files"):
            EvidenceFile.objects.create(
                evidence=evidence,
                file=file
            )

        return evidence