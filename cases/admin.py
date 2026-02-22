from django.contrib import admin

from cases.models import Complainant, Case

# Register your models here.
admin.site.register(Case)
admin.site.register(Complainant)