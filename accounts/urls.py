from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("users/", views.user_list, name="user-list"),
    path("preferences/", views.user_preferences, name="preferences"),
    path("stats/num_employees", views.num_employees, name="num-employees"),
]
