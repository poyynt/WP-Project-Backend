from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Evidence
from .serializers import EvidenceSerializer
from common.permissions import HasPerm

class EvidenceCreateAPI(generics.CreateAPIView):
    queryset = Evidence.objects.all()
    serializer_class = EvidenceSerializer
    permission_classes = [IsAuthenticated, HasPerm("evidence_create")]

    @extend_schema(summary="Attach evidence to case", tags=["Evidence"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class CaseEvidenceListAPI(generics.ListAPIView):
    serializer_class = EvidenceSerializer
    permission_classes = [IsAuthenticated, HasPerm("evidence_read")]

    @extend_schema(summary="List evidence for a case", tags=["Evidence"])
    def get_queryset(self):
        return Evidence.objects.filter(case_id=self.kwargs["case_id"])