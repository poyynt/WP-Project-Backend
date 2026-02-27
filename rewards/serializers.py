from rest_framework import serializers
from .models import Reward
from accounts.models import User  # Assuming the User model is in the `accounts` app

# Serializer for Reward model
class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['id', 'user', 'unique_code', 'amount', 'claimed', 'created_at']

# Serializer for handling claims (incoming data)
class ClaimSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=64)  # The unique reward code