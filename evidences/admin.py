from django.contrib import admin

from evidences.models import Evidence, EvidenceFile

# Register your models here.

admin.site.register(Evidence)
admin.site.register(EvidenceFile)