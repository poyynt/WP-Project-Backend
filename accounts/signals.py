from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

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

# @receiver(post_migrate, sender=apps.get_app_config("accounts"))
def create_default_perms(**kwargs):
    from .models import Permission
    Permission.objects.bulk_create(
        [Permission(codename=k, name=v) for k, v in DEFAULT_PERMS.items()],
        ignore_conflicts=True,
    )

# @receiver(post_migrate, sender=apps.get_app_config("accounts"))
def create_default_roles(**kwargs):
    from .models import Role, Permission

    for role_name, perm_codes in DEFAULT_ROLES.items():
        role, _ = Role.objects.get_or_create(name=role_name)

        if perm_codes:
            perms = Permission.objects.filter(codename__in=perm_codes)
            role.permissions.set(perms)