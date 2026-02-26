from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model

from .models import Role, UserPref
from .serializers import RegisterSerializer, UserSerializer, RoleSerializer, UserPrefSerializer
from common.permissions import has_perm_helper

User = get_user_model()


@extend_schema(
    summary="Register new user",
    request=RegisterSerializer,
    responses={201: OpenApiResponse(description="User created")},
    tags=["auth"]
)
@api_view(["POST"])
@permission_classes([])
@authentication_classes([])
def register(request):
    ser = RegisterSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    user = ser.save()
    return Response(UserSerializer(user).data, status=201)


@extend_schema(
    summary="Current user profile",
    responses={200: UserSerializer},
    tags=["auth"]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response(UserSerializer(request.user).data)


@extend_schema(
    summary="List all users (admin only)",
    responses={200: UserSerializer(many=True)},
    tags=["auth"]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, has_perm_helper("admin")])
def user_list(request):
    """
    Get a list of all users.
    Only accessible to users with 'admin' permission.
    """
    return Response(UserSerializer(User.objects.all(), many=True).data)


@extend_schema(
    summary="Get number of police employees",
    tags=["stats"],
    responses=OpenApiResponse(
        response={
            "type": "object",
            "properties": {
                "count": {"type": "integer"}
            },
            "required": ["count"],
        },
        description="Number of police employees",
    )
)
@api_view(["GET"])
@permission_classes([has_perm_helper("base")])
def num_employees(request):
    count = User.objects.exclude(roles__name="base").count()
    return Response({"count": count})


@extend_schema(
    summary="Get or update current user's preferences",
    request=UserPrefSerializer(many=True),
    responses={200: UserPrefSerializer(many=True)},
    tags=["account"]
)
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def user_preferences(request):
    """
    GET: Return all preferences for the current user.
    PATCH: Update existing preferences or create new ones.
    """
    if request.method == "GET":
        prefs = UserPref.objects.filter(user=request.user)
        ser = UserPrefSerializer(prefs, many=True)
        return Response(ser.data)

    data = request.data
    if not isinstance(data, list):
        return Response({"detail": "Expected a list of preferences"}, status=400)

    for item in data:
        UserPref.objects.update_or_create(
            user=request.user,
            key=item.get("key"),
            defaults={"value": item.get("value")}
        )

    return Response(status=status.HTTP_200_OK)


@extend_schema(
    summary="Get or update a user's roles (admin only)",
    responses={200: RoleSerializer(many=True)},
    tags=["auth"],
    request={
        "application/json": {
            "type": "array",
            "items": {"type": "integer"},
            "description": "List of role IDs to assign to the user"
        }
    }
)
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated, has_perm_helper("admin")])
def update_user_roles(request, user_id):
    """
    GET: Get a list of the provided user's roles.
    PATCH: Replace a user's roles with the provided list of role IDs.
    Only users with 'admin' role can perform this action.
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)

    if request.method == "GET":
        return Response(RoleSerializer(user.roles, many=True).data)

    roles = Role.objects.filter(id__in=request.data)

    user.roles.set(roles)
    user.save()

    return Response(UserSerializer(user).data, status=200)


@extend_schema(
    summary="List all roles",
    responses={200: RoleSerializer(many=True)},
    tags=["auth"]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, has_perm_helper("admin")])
def role_list(request):
    """
    Return all available roles.
    Only accessible to users with 'admin' permission.
    """
    roles = Role.objects.all()
    return Response(RoleSerializer(roles, many=True).data)
