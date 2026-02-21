from rest_framework.permissions import BasePermission


class HasPerm(BasePermission):
    """
    usage: permission_classes = [HasPerm('can_edit_case')]
    """

    def __init__(self, codename):
        self.codename = codename

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
                request.user.roles.filter(permissions__codename=self.codename).exists()
                or
                request.user.roles.filter(name="admin").exists()
        )


class DynamicRole(BasePermission):
    """
    usage: permission_classes = [DynamicRole("can_edit_case", "can_approve_evidence")]
    """

    def __init__(self, *codenames):
        self.codenames = codenames

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
                user.roles.filter(permissions__codename__in=self.codenames).exists()
                or user.roles.filter(name="admin").exists()
        )
