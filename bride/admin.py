from django.contrib import admin
from bride.models import BrideModel

# Register your models here.


class BrideAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['bride_category']}),
        (None,               {'fields': ['bride_name']}),
        (None,               {'fields': ['bride_user']}),
        (None,               {'fields': ['bride_active']}),
        ('Date information', {'fields': ['bride_party_date'], 'classes': ['collapse']}),
    ]
    list_display = ('bride_name', 'bride_category', 'bride_user', 'bride_active', 'bride_updated_at', 'bride_updated_by', 'bride_published', 'bride_register_user',)
    list_filter = ['bride_category']
    search_fields = ['bride_name', 'bride_user']


admin.site.register(BrideModel, BrideAdmin)