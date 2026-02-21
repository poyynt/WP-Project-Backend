from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Suspect, Investigation
from .serializers import SuspectSerializer, InvestigationSerializer
from common.permissions import HasPerm

class SuspectViewSet(viewsets.ModelViewSet):
    queryset = Suspect.objects.all()
    serializer_class = SuspectSerializer
    permission_classes = [IsInvestigator]

    @extend_schema(
        summary="Submit investigation result",
        request=InvestigationSerializer,
        responses={201: InvestigationSerializer},
        tags=["Suspects"]
    )
    @action(detail=True, methods=["post"], url_path="investigate")
    def investigate(self, request, pk=None):
        suspect = self.get_object()
        ser = InvestigationSerializer(data={**request.data, "suspect": suspect.id})
        ser.is_valid(raise_exception=True)
        ser.save(investigator=request.user)
        return Response(ser.data, status=status.HTTP_201_CREATED)