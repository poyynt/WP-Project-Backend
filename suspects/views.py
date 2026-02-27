from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Suspect, Investigation, SuspectStatus
from .serializers import SuspectSerializer, InvestigationSerializer
from common.permissions import HasPerm, has_perm_helper


@extend_schema_view(
    list=extend_schema(summary="List suspects", tags=["suspects"]),
    retrieve=extend_schema(summary="List suspects", tags=["suspects"]),
    create=extend_schema(summary="List suspects", tags=["suspects"]),
    partial_update=extend_schema(summary="List suspects", tags=["suspects"]),
    update=extend_schema(exclude=True),
    destroy=extend_schema(exclude=True)
)
class SuspectViewSet(viewsets.ModelViewSet):
    queryset = Suspect.objects.all()
    serializer_class = SuspectSerializer

    def get_permissions(self):
        if self.action == "create":
            return [HasPerm("suspect_create")]
        if self.action == "partial_update":
            return [HasPerm("suspect_edit")]
        return [HasPerm("base")]

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def perform_create(self, serializer):
        serializer.save(status=SuspectStatus.SUSPECT_CREATED)

    @extend_schema(
        summary="Submit investigation result",
        request=InvestigationSerializer,
        responses={201: InvestigationSerializer},
        tags=["suspects"]
    )
    @action(detail=True, methods=["POST"], url_path="investigate")
    def investigate(self, request, pk=None):
        suspect = self.get_object()
        ser = InvestigationSerializer(data={**request.data, "suspect": suspect.id})
        ser.is_valid(raise_exception=True)
        ser.save(investigator=request.user)
        return Response(ser.data, status=status.HTTP_201_CREATED)