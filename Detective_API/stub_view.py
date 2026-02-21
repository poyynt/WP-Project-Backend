from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView

from rest_framework.permissions import BasePermission, IsAuthenticated


class IsAuthenticatedAndInGroup(BasePermission):
    """
    Custom permission that checks if the user is authenticated and belongs to a specific group.
    """

    def __init__(self, group_name: str):
        self.group_name = group_name

    def has_permission(self, request, view):
        # First check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Then check if the user is in the specified group
        if request.user.groups.filter(name=self.group_name).exists():
            return True

        return False

class StubView(APIView):
    """
    Just a stub endpoint for testing
    """
    # permission_required = ["stub.stub"]
    permission_classes = (lambda : IsAuthenticatedAndInGroup("stub_reader"),)


    def get(self, request):
        stub_data = [{"name": "stub data 1"}, {"name": request.user.groups.filter(name="stub_reader").exists()}]
        return JsonResponse(stub_data, safe=False)
