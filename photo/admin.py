from django.contrib import admin
from photo.models import ServicePhotoModel


class ServicePhotoAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['service_photo_file']}),
        (None, {'fields': ['service_photo']}),
        (None, {'fields': ['service_photo_cover']}),
        (None, {'fields': ['photo_expiration_date']}),
    ]
    list_display = ('service_photo_file', 'service_photo', 'service_photo_cover', 'photo_expiration_date', 'photo_updated_at', 'photo_updated_by', 'photo_published', 'photo_author',)
    list_filter = ['service_photo']
    search_fields = ['service_photo_file', 'service_photo']

admin.site.register(ServicePhotoModel, ServicePhotoAdmin)
