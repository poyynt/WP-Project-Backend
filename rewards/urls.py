from django.urls import path
from .views import ClaimAPI, HistoryAPI

urlpatterns = [
    path('claim/', ClaimAPI.as_view(), name='claim-reward'),  # Endpoint for claiming a reward
    path('history/', HistoryAPI.as_view(), name='reward-history'),  # Endpoint for getting user rewards history
]