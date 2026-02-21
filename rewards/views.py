from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from .models import Reward
from .serializers import ClaimSerializer, RewardSerializer


class ClaimAPI(generics.GenericAPIView):
    serializer_class = ClaimSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Claim reward by unique code", tags=["Rewards"])
    def post(self, request):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        reward = ser.validated_data["code"]
        reward.user = request.user
        reward.claimed = True
        reward.save()
        return Response(RewardSerializer(reward).data)


class HistoryAPI(generics.ListAPIView):
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="User claimed rewards", tags=["Rewards"])
    def get_queryset(self):
        return self.request.user.rewards.filter(claimed=True)
