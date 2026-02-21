from django.contrib import admin

from accounts.models import User, Role, Permission

# Register your models here.

# admin.site.register(User)
admin.site.register(Permission)
# admin.site.register(Role)