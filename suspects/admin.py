from django.contrib import admin

from suspects.models import Suspect, Investigation

# Register your models here.
admin.site.register(Suspect)
admin.site.register(Investigation)