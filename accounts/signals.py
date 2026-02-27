from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

DEFAULT_PERMS = {
    "case_create": "Create Case",
    "case_edit": "Edit Case",
    "case_approve": "Approve Case",
    "case_verify": "Verify Case",
    "case_delete": "Delete Case",
    "case_read": "Read Case",
    "evidence_create": "Create Evidence",
    "evidence_read": "Read Evidence",
    "investigation_submit": "Submit investigation score",
    "base": "Base Permission for all users",
    "admin": "Administrator permission"
}

DEFAULT_ROLES = {
    "admin": ["admin"],
    "chief_police": ["case_verify", "case_read", "case_edit", "case_approve"],
    "captain": ["case_verify", "case_read", "case_edit", "case_approve"],
    "sergeant": ["investigation_submit"],
    "detective": ["investigation_submit"],
    "police_officer": ["case_verify", "case_read", "case_edit"],
    "patrol_officer": ["case_verify", "case_read", "case_edit"],
    "cadet": ["case_read", "case_approve", "case_edit"],
    "complainant": ["case_create", "case_edit"],
    "witness": [],
    "suspect": [],
    "criminal": [],
    "judge": ["case_read", "case_edit", "evidence_read"],
    "forensic": ["evidence_create", "evidence_read"],
    "base": ["base"],
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