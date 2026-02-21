from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, RoleSerializer
from common.permissions import HasPerm


User = get_user_model()

@extend_schema(
    summary="Register new user",
    request=RegisterSerializer,
    responses={201: OpenApiResponse(description="User created")},
    tags=["Auth"]
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    ser = RegisterSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    user = ser.save()
    return Response(UserSerializer(user).data, status=201)

@extend_schema(
    summary="Current user profile",
    responses={200: UserSerializer},
    tags=["Auth"]
)
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == "GET":
        return Response(UserSerializer(request.user).data)
    ser = UserSerializer(request.user, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    ser.save()
    return Response(ser.data)

@extend_schema(
    summary="List users",
    responses={200: UserSerializer(many=True)},
    tags=["Auth"]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, HasPerm("user_read")])
def user_list(request):
    return Response(UserSerializer(User.objects.all(), many=True).data)

@extend_schema(
    summary="Edit user roles",
    request=RoleSerializer(many=True),
    responses={200: UserSerializer},
    tags=["Auth"]
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated, HasPerm("user_edit")])
def edit_roles(request, pk):
    user = User.objects.get(pk=pk)
    ser = RoleSerializer(data=request.data, many=True)
    ser.is_valid(raise_exception=True)
    user.roles.set([r["id"] for r in ser.validated_data])
    return Response(UserSerializer(user).data)