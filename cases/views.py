from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema
from .models import Case
from .serializers import CaseSerializer
from common.permissions import HasPerm

@extend_schema_view(
    list=extend_schema(summary="List cases", tags=["Cases"]),
    retrieve=extend_schema(summary="Get details of case", tags=["Cases"]),
    create=extend_schema(summary="Submit new case", tags=["Cases"]),
    partial_update=extend_schema(summary="Edit case", tags=["Cases"])
)
class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

    def get_permissions(self):
        if self.action == "create":
            return [HasPerm("case_create")]
        if self.action in ("update", "partial_update"):
            return [HasPerm("case_edit")]
        if self.action == "destroy":
            return [HasPerm("case_delete")]
        return [HasPerm("case_read")]
