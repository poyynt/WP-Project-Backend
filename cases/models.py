import random

from django.db import models, transaction
from django.db.models import Q

from accounts.models import User


class CrimeLevel(models.IntegerChoices):
    LEVEL_3 = 3, "Level 3"
    LEVEL_2 = 2, "Level 2"
    LEVEL_1 = 1, "Level 1"
    CRITICAL = 0, "Critical"


class CaseStatus(models.TextChoices):
    OPEN = "open", "Open"
    CANCELLED = "cancelled", "Cancelled"
    CLOSED = "closed", "Closed"
    PENDING_APPROVAL = "pending_approval", "Pending Approval"  # cadet stage
    PENDING_VERIFICATION = "pending_verification", "Pending Verification"  # officer stage
    CREATED = "created", "Created"


class CaseQuerySet(models.QuerySet):
    def visible_to(self, user):
        if user.is_superuser or user.roles.filter(permissions__codename="case_read").exists():
            return self.all()

        return self.filter(
            Q(created_by=user)
        ).distinct()


class Case(models.Model):
    objects = CaseQuerySet.as_manager()

    title = models.CharField(max_length=255)
    description = models.TextField()
    level = models.IntegerField(choices=CrimeLevel.choices, default=CrimeLevel.LEVEL_3)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_cases")
    status = models.CharField(max_length=50, choices=CaseStatus.choices, default=CaseStatus.CREATED)
    complainants = models.ManyToManyField(User, related_name="complaints")

    def __str__(self):
        return self.title

    def get_case_approver(self):
        history = self.workflow_history.filter(recipient__roles__name="cadet").first()
        if history:
            return history.recipient
        else:
            cadet_users = User.objects.filter(roles__name="cadet")
            if not cadet_users.exists():
                raise RuntimeError("No cadet user exists to handle case")
            return random.choice(cadet_users)

    def send_to_cadet(self):
        with transaction.atomic():
            cadet = self.get_case_approver()
            self.status = CaseStatus.PENDING_APPROVAL
            self.save()
            WorkflowHistory.objects.create(case=self, recipient=cadet)

    def send_to_officer(self, request_user):
        with transaction.atomic():
            boss = request_user.reporting_to
            self.status = CaseStatus.PENDING_VERIFICATION
            self.save()
            WorkflowHistory.objects.create(case=self, recipient=boss)

    def reject_case_to_cadet(self, error_message):
        with transaction.atomic():
            cadet = self.get_case_approver()
            self.status = CaseStatus.PENDING_APPROVAL
            self.save()
            WorkflowHistory.objects.create(case=self, recipient=cadet, message=error_message)

    def reject_case_to_creator(self, error_message):
        with transaction.atomic():
            self.status = CaseStatus.CREATED
            self.save()
            WorkflowHistory.objects.create(case=self, recipient=self.created_by, message=error_message)

    def open_case(self):
        self.status = CaseStatus.OPEN
        self.save()

    def cancel_case(self):
        with transaction.atomic():
            self.status = CaseStatus.CANCELLED
            self.save()
            WorkflowHistory.objects.create(case=self, recipient=self.created_by)


class WorkflowHistory(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="workflow_history")
    recipient = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    message = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.case.title} - {self.recipient} - {self.message}"
