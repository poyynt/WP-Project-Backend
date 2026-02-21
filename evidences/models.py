from django.core.exceptions import ValidationError
from django.db import models
from cases.models import Case
from accounts.models import User

class EvidenceType(models.TextChoices):
    TESTIMONY = "testimony", "Testimony"
    MEDICAL = "medical", "Medical"
    VEHICLE = "vehicle", "Vehicle"
    ID = "id", "ID Document"
    OTHER = "other", "Other"

class Evidence(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="evidences")
    type = models.CharField(max_length=20, choices=EvidenceType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.type})"

class EvidenceFile(models.Model):
    evidence = models.ForeignKey(
        Evidence,
        on_delete=models.CASCADE,
        related_name="files"
    )
    file = models.FileField(upload_to="evidences/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.evidence.title}"