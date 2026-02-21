from django.db import models
from accounts.models import User

class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rewards")
    unique_code = models.CharField(max_length=64, unique=True)
    amount = models.PositiveIntegerField()
    claimed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.amount}"