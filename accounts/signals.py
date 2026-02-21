from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from .models import Permission, Role

DEFAULT_PERMS = {
    "case_create": "Create Case",
    "case_edit": "Edit Case",
    "case_delete": "Delete Case",
    "case_read": "Read Case",
    "evidence_create": "Create Evidence",
    "evidence_read": "Read Evidence",
    "can_investigate": "بازجویی/تحقیق",
    "can_approve_arrest": "تأیید دستگیری",
    "can_give_reward": "ثبت/پرداخت پاداش",
}

DEFAULT_ROLES = {
    "admin": ["admin"],
    "chief_police": [],
    "captain": [],
    "sergeant": [],
    "detective": [],
    "police_officer": [],
    "patrol_officer": [],
    "cadet": [],
    "complainant": ["case_create"],
    "witness": [],
    "suspect": [],
    "criminal": [],
    "judge": [],
    "forensic": [],
    "base": [],
}

@receiver(post_migrate, sender=apps.get_app_config("accounts"))
def create_default_perms(sender, **kwargs):
    Permission.objects.bulk_create(
        [Permission(codename=k, name=v) for k, v in DEFAULT_PERMS.items()],
        ignore_conflicts=True,
    )

@receiver(post_migrate, sender=apps.get_app_config("accounts"))
def create_default_roles(sender, **kwargs):
    Role.objects.bulk_create(
        [
            Role(name=k, permissions=v) for k, v in DEFAULT_ROLES.items()
        ]
    )