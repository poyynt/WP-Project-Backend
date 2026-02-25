from django.contrib.auth.models import AbstractUser
from django.db import models

class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)  # snake_case
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True)

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return self.name

class User(AbstractUser):
    national_id = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=15)
    roles = models.ManyToManyField(Role, blank=True)
    reporting_to = models.ForeignKey('self', on_delete=models.deletion.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({', '.join([role.name for role in self.roles.all()])})" + (f" reporting to {self.reporting_to.first_name} {self.reporting_to.last_name}" if self.reporting_to else "")


class UserPref(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="preferences")
    key = models.CharField(max_length=255)
    value = models.TextField()