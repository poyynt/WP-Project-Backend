from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CaseViewSet, num_solved, num_active

router = DefaultRouter()
router.register(r"cases", CaseViewSet, basename="case")

urlpatterns = [
    path("", include(router.urls)),
    path("stats/num_solved", num_solved, name="num-solved"),
    path("stats/num_active", num_active, name="num-active"),
]