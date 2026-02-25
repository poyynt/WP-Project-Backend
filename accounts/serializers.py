from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role, Permission, UserPref

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "codename", "name"]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "national_id",
            "phone",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            password = validated_data.pop("password")
            user = User(**validated_data)
            user.set_password(password)
            user.save()

            default_role = Role.objects.get(name="base")
            user.roles.set([default_role])

            return user

class UserPrefSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPref
        fields = ["key", "value"]


class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "national_id",
            "phone",
            "roles",
        ]
