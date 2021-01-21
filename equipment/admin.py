from django.contrib import admin
from .models import EquipmentModel, ServiceEquipmentModel
# Register your models here.


class EquipmentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['equipment_tittle']}),
        (None,               {'fields': ['equipment_description']}),
        (None,               {'fields': ['equipment_quantity']}),
        (None,               {'fields': ['equipment_active']}),
        (None,               {'fields': ['equipment_author']}),
        (None,               {'fields': ['equipment_updated_at']}),
        (None,               {'fields': ['equipment_updated_by']}),
        (None,               {'fields': ['equipment_published']}),
        ]
    list_display = ('equipment_tittle', 'equipment_quantity', 'equipment_updated_at', 'equipment_updated_by', 'equipment_published', 'equipment_author',)
    list_filter = ['equipment_active']
    search_fields = ['equipment_tittle', 'equipment_active']


admin.site.register(EquipmentModel, EquipmentAdmin)


