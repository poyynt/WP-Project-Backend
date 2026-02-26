from datetime import timedelta

from django.db.models import ExpressionWrapper, DurationField, F, Max
from django.db.models.functions import Coalesce, Now
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.response import Response

from suspects.models import Suspect
from .models import Case, CaseStatus, WorkflowHistory
from .serializers import CaseSerializer, MostWantedSerializer
from common.permissions import HasPerm, has_perm_helper

import logging


@extend_schema_view(
    list=extend_schema(summary="List cases", tags=["Cases"]),
    retrieve=extend_schema(summary="Get details of case", tags=["Cases"]),
    create=extend_schema(summary="Submit new case", tags=["Cases"]),
    partial_update=extend_schema(summary="Edit case", tags=["Cases"])
)
class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.visible_to(self.request.user)

    def get_permissions(self):
        if self.action == "create":
            return [HasPerm("case_create")]
        if self.action in ("update", "partial_update"):
            return [HasPerm("case_edit")]
        if self.action == "destroy":
            return [HasPerm("case_delete")]
        return [HasPerm("case_read")]

    def update(self, request, *args, **kwargs):
        case = self.get_object()
        verdict = request.data.get("verdict", None)

        if case.status == CaseStatus.CREATED:
            if case.created_by.roles.filter(name__in=("base", "complainant", "cadet")).exists():
                case.send_to_cadet()
            elif case.created_by.roles.filter(name__in=("chief_police",)).exists():
                case.open_case()
            else:
                case.send_to_officer(case.created_by)
            return Response(status=status.HTTP_200_OK)

        elif case.status == CaseStatus.PENDING_APPROVAL:
            if not request.user.roles.filter(permissions__codename="case_approve").exists():
                return Response(status=status.HTTP_403_FORBIDDEN)
            if verdict == "pass":
                case.send_to_officer(request.user)
                return Response(status=status.HTTP_200_OK)
            elif verdict == "fail":
                if case.workflow_history.filter(recipient=case.created_by).count() >= 2:
                    case.cancel_case()
                    return Response({"message": "Case got rejected 3 times, case cancelled"},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
                case.reject_case_to_creator(request.data.get("message"))
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        elif case.status == CaseStatus.PENDING_VERIFICATION:
            if not request.user.roles.filter(permissions__codename="case_verify").exists():
                return Response(status=status.HTTP_403_FORBIDDEN)
            if verdict == "pass":
                case.open_case()
                return Response(status=status.HTTP_200_OK)
            elif verdict == "fail":
                if case.created_by.roles.filter(name__in=("base", "complainant", "cadet")).exists():
                    case.reject_case_to_cadet(request.data.get("message"))
                else:
                    case.reject_case_to_creator(request.data.get("message"))
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        elif case.status in (CaseStatus.CANCELLED, CaseStatus.CLOSED):
            return Response({"error": "Case is cancelled and cannot be updated"}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)  # Default update for other cases


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
