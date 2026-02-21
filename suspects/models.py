from django.db import models
from cases.models import Case
from accounts.models import User

class SuspectStatus(models.TextChoices):
    UNDER_INTERROGATION = "under_interrogation", "Under Interrogation"
    AWAITING_CAPTAIN_VERDICT = "awaiting_captain_verdict", "Awaiting Captain Verdict"
    AWAITING_CHIEF_VERDICT = "awaiting_chief_verdict", "Awaiting Chief Verdict"
    GUILTY = "guilty", "Guilty"
    NOT_GUILTY = "not_guilty", "Not Guilty"

class Suspect(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="suspects")
    national_id = models.CharField(max_length=10)
    full_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=SuspectStatus.choices, default=SuspectStatus.UNDER_INTERROGATION)
    wanted_level = models.CharField(max_length=20, default="normal")  # normal, high

    def __str__(self):
        return self.full_name

class Investigation(models.Model):
    suspect = models.ForeignKey(Suspect, on_delete=models.CASCADE, related_name="investigations")
    investigator = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)