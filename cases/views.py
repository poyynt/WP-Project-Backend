from datetime import timedelta

from django.db.models import ExpressionWrapper, DurationField, F, Max, Q, OuterRef, Exists
from django.db.models.functions import Coalesce, Now
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.response import Response

from accounts.models import Role, User
from suspects.models import Suspect
from .models import Case, CaseStatus, WorkflowHistory
from .serializers import CaseSerializer, MostWantedSerializer, UserWorkflowCaseSerializer
from common.permissions import HasPerm, has_perm_helper

import logging


@extend_schema_view(
    list=extend_schema(summary="List cases", tags=["cases"]),
    retrieve=extend_schema(summary="Get details of case", tags=["cases"]),
    create=extend_schema(summary="Submit new case", tags=["cases"]),
    partial_update=extend_schema(summary="Edit case", tags=["cases"]),
    update=extend_schema(exclude=True),
    destroy=extend_schema(exclude=True)
)
class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.visible_to(self.request.user)

    def get_permissions(self):
        if self.action == "create":
            return [HasPerm("case_create")]
        if self.action in ("partial_update", "workflow"):
            return [HasPerm("case_edit")]
        return [HasPerm("base")]

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def perform_create(self, serializer):
        if self.request.user.roles.filter(name__in=("base", "complainant", "cadet")).exists():
            complainants = [self.request.user]
        serializer.save(created_by=self.request.user, status=CaseStatus.CREATED, complainants=complainants)

    @extend_schema(
        methods=["GET"],
        summary="Get workflow users with their roles",
        tags=["cases"],
        responses={
            200: {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "roles": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["id", "first_name", "last_name", "roles"]
                }
            }
        },
        examples=[
            OpenApiExample(
                "Workflow Users Example",
                value=[
                    {
                        "id": 3,
                        "first_name": "Ali",
                        "last_name": "Ahmadi",
                        "roles": ["detective", "forensic"]
                    },
                    {
                        "id": 7,
                        "first_name": "Sara",
                        "last_name": "Karimi",
                        "roles": ["admin"]
                    }
                ],
                response_only=True,
            )
        ],
    )
    @extend_schema(
        methods=["POST"],
        summary="Push case to next step in workflow",
        tags=["cases"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "verdict": {
                        "type": "string",
                        "enum": ["pass", "fail"],
                        "description": "Verdict of validation/approval of case by user."
                    }
                },
                "required": []
            }
        },
        responses={
            200: {},
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },
                "required": ["error"]
            },
            403: {},
            406: {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            },
        },
        examples=[
            OpenApiExample(
                "Pass Verdict Example",
                value={"verdict": "pass"},
                request_only=True,
            ),
            OpenApiExample(
                "Fail Verdict Example",
                value={"verdict": "fail"},
                request_only=True,
            ),
        ],
    )
    @action(detail=True, methods=["GET", "POST"], url_path="workflow")
    def workflow(self, request, pk=None):
        case = self.get_object()
        if request.method == "GET":
            users = (
                case.workflow_history
                .select_related("recipient")
                .prefetch_related("recipient__roles")
                .values_list("recipient", flat=True)
                .distinct()
            )

            user_qs = (
                User.objects
                .filter(id__in=users)
                .prefetch_related("roles")
            )

            result = []

            for user in user_qs:
                result.append({
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "roles": [role.name for role in user.roles.all()]
                })

            return Response(result, status=status.HTTP_200_OK)
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
            return Response({"error": "Invalid verdict."}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"error": "Invalid verdict."}, status=status.HTTP_400_BAD_REQUEST)

        elif case.status in (CaseStatus.CANCELLED, CaseStatus.CLOSED):
            return Response({"error": "Case is cancelled and cannot be updated"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"message": "Case is already open."}, status=status.HTTP_406_NOT_ACCEPTABLE)


@extend_schema(
    summary="Get cases needing workflow-action by user",
    tags=["cases"],
    responses={200: UserWorkflowCaseSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([has_perm_helper("case_edit")])
def get_user_workflow_cases(request):
    user = request.user

    latest_history_ids = (
        WorkflowHistory.objects
        .values("case")
        .annotate(last_id=Max("id"))
        .values_list("last_id", flat=True)
    )

    latest_histories = (
        WorkflowHistory.objects
        .filter(id__in=latest_history_ids, recipient=user)
        .exclude(case__status=CaseStatus.CLOSED)
        .select_related("case")
    )

    results = [
        {
            "case_id": history.case.id,
            "message": history.message,
        }
        for history in latest_histories
    ]

    ser = UserWorkflowCaseSerializer(results, many=True)
    return Response(ser.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Get number of solved cases",
    tags=["stats"],
    responses=OpenApiResponse(
        response={
            "type": "object",
            "properties": {
                "count": {"type": "integer"}
            },
            "required": ["count"],
        },
        description="Number of solved cases",
    )
)
@api_view(["GET"])
@permission_classes([has_perm_helper("base")])
def num_solved(request):
    count = Case.objects.filter(status="solved").count()
    return Response({"count": count})


@extend_schema(
    summary="Get number of active cases",
    tags=["stats"],
    responses=OpenApiResponse(
        response={
            "type": "object",
            "properties": {
                "count": {"type": "integer"}
            },
            "required": ["count"],
        },
        description="Number of active cases",
    )
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
    tags=["cases"]
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
