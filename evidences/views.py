from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from cases.models import Case
from .models import Evidence
from .serializers import EvidenceSerializer
from common.permissions import HasPerm
#
# class EvidenceCreateAPI(generics.CreateAPIView):
#     queryset = Evidence.objects.all()
#     serializer_class = EvidenceSerializer
#     permission_classes = [IsAuthenticated, HasPerm("evidence_create")]
#
#     @extend_schema(summary="Attach evidence to case", tags=["Evidence"])
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)
#
# class CaseEvidenceListAPI(generics.ListAPIView):
#     serializer_class = EvidenceSerializer
#     permission_classes = [IsAuthenticated, HasPerm("evidence_read")]
#
#     @extend_schema(summary="List evidence for a case", tags=["Evidence"])
#     def get_queryset(self):
#         return Evidence.objects.filter(case_id=self.kwargs["case_id"])
#

class EvidenceViewSet(viewsets.ModelViewSet):
    queryset = Evidence.objects.all()
    serializer_class = EvidenceSerializer

    def get_permissions(self):
        if self.action == "create":
            return [HasPerm("evidence_create")]
        if self.action in ("update", "partial_update"):
            return [HasPerm("evidence_edit")]
        if self.action == "destroy":
            return [HasPerm("evidence_delete")]
        return [HasPerm("evidence_read")]

    def get_queryset(self):
        queryset = Evidence.objects.filter(
            case__in=Case.objects.visible_to(self.request.user)
        )
        case_id = self.request.query_params.get("case")
        if case_id:
            queryset = queryset.filter(case_id=case_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())