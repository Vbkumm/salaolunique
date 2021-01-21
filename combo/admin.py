from django.contrib import admin
from combo.models import ComboModel
# Register your models here.


class ComboAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['combo_tittle']}),
        (None,               {'fields': ['combo_description']}),
        (None,               {'fields': ['combo_service']}),
        (None,               {'fields': ['combo_views']}),
        ('Date information', {'fields': ['combo_expiration_date'], 'classes': ['collapse']}),
    ]
    list_display = ('combo_tittle', 'combo_active', 'combo_updated_at', 'combo_updated_by', 'combo_published', 'combo_author',)
    list_filter = ['combo_active']
    search_fields = ['combo_tittle', 'combo_active']


admin.site.register(ComboModel, ComboAdmin)


