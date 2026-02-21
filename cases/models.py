from django.db import models
from accounts.models import User

class CrimeLevel(models.IntegerChoices):
    LEVEL_3 = 3, "Level 3"
    LEVEL_2 = 2, "Level 2"
    LEVEL_1 = 1, "Level 1"
    CRITICAL = 0, "Critical"

class Case(models.Model):
    title = models.CharField(max_length=255)
    level = models.IntegerField(choices=CrimeLevel.choices, default=CrimeLevel.LEVEL_3)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_cases")
    status = models.CharField(max_length=50, default="open")

    def __str__(self):
        return self.title

class Complainant(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="complainants")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ("case", "user")