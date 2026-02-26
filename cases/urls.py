from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CaseViewSet, num_solved, num_active, most_wanted, case_workflow, get_user_workflow_cases

router = DefaultRouter()
router.register("", CaseViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("stats/num_solved", num_solved, name="num-solved"),
    path("stats/num_active", num_active, name="num-active"),
    path("most_wanted", most_wanted, name="most-wanted"),
    path("<int:case_id>/workflow", case_workflow, name="case-workflow"),
    path("my_workflow", get_user_workflow_cases, name="my-workflow"),
]
