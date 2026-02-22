from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SuspectViewSet

router = DefaultRouter()
router.register("", SuspectViewSet)

urlpatterns = [
    path("", include(router.urls)),
]