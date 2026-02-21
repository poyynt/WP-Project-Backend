from django.apps import AppConfig
from django.db.models.signals import post_migrate

from accounts.signals import create_default_perms, create_default_roles


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        post_migrate.connect(create_default_perms, sender=self)
        post_migrate.connect(create_default_roles, sender=self)
