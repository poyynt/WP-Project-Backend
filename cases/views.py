from datetime import timedelta

from django.db.models import ExpressionWrapper, DurationField, F, Max
from django.db.models.functions import Coalesce, Now
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.response import Response

from suspects.models import Suspect
from .models import Case
from .serializers import CaseSerializer, MostWantedSerializer
from common.permissions import HasPerm, has_perm_helper


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


@extend_schema(
    summary="Get number of solved cases",
    tags=["Stats"]
)
@api_view(["GET"])
@permission_classes([has_perm_helper("base")])
def num_solved(request):
    count = Case.objects.filter(status="solved").count()
    return Response({"count": count})


@extend_schema(
    summary="Get number of active cases",
    tags=["Stats"]
)
@api_view(["GET"])
@permission_classes([has_perm_helper("base")])
def num_active(request):
    count = Case.objects.exclude(status="solved").count()
    return Response({"count": count})

@extend_schema(
    summary="List most wanted suspects",
    description=(
        "Returns all suspects who have been under interrogation "
        "for more than 30 days in at least one open cases."
    ),
    responses={200: MostWantedSerializer(many=True)},
    tags=["Cases"]
)
@api_view(["GET"])
def most_wanted(request):
    suspects = (
        Suspect.objects
        .annotate(case_duration=ExpressionWrapper(
            Coalesce(F("case__closed_at"), Now()) - F("case__created_at"),
            output_field=DurationField()
        ))
        .annotate(
            max_duration=Max("case_duration"),
            max_level=Max("case__level"),
        )
        .filter(max_duration__gt=timedelta(days=30))
    )

    return Response(MostWantedSerializer(suspects, many=True, context={"request": request}).data)
