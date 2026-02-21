from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("users/", views.user_list, name="user-list"),
    path("users/<int:pk>/roles/", views.edit_roles, name="edit-roles"),
]