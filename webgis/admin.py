from django.contrib import admin

# Register your models here.
from webgis.models.proposal import Proposal

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display  = ['author', 'district_name', 'problem_type', 'status', 'created_at']
    list_filter   = ['status', 'problem_type']
    search_fields = ['author__username', 'district_name', 'solution']
    readonly_fields = ['author', 'created_at']