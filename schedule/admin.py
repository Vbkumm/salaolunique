from django.contrib import admin
from .models import ScheduleModel

# Register your models here.


class ScheduleAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['schedule_service']}),
        (None,               {'fields': ['schedule_costumer']}),
        (None,               {'fields': ['schedule_date']}),
        (None,               {'fields': ['schedule_hour']}),
        (None,               {'fields': ['schedule_professional']}),
        (None,               {'fields': ['schedule_description']}),
        (None,               {'fields': ['schedule_service_done']}),
        (None,               {'fields': ['schedule_service_paid']}),
    ]
    list_display = ('schedule_service','schedule_costumer', 'schedule_date', 'schedule_hour', 'schedule_professional', 'schedule_updated_at', 'schedule_updated_by', 'schedule_published', 'schedule_author', )
    list_filter = ['schedule_service']
    search_fields = ['schedule_service', 'schedule_costumer']


admin.site.register(ScheduleModel, ScheduleAdmin)