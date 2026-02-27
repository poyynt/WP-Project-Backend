from django.contrib import admin

from cases.models import Case, WorkflowHistory

# Register your models here.
admin.site.register(Case)
admin.site.register(WorkflowHistory)