from django.contrib import admin
from testimony.models import TestimonyModel, TestimonyDeletedModel


class TestimonyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['testimony_title']}),
        (None,               {'fields': ['testimony_user']}),
        (None,               {'fields': ['testimony_updated_by']}),
        (None,               {'fields': ['testimony_description']}),
        (None,               {'fields': ['testimony_active']}),
        (None,               {'fields': ['testimony_service']}),
        (None,               {'fields': ['testimony_professional']}),
        (None,               {'fields': ['testimony_bride']}),
        (None,               {'fields': ['testimony_photo']}),
        (None,               {'fields': ['testimony_rating']}),
        ]
    list_display = ('testimony_title', 'testimony_user', 'testimony_published', 'testimony_updated_at', 'testimony_active')
    list_filter = ['testimony_active']
    search_fields = ['testimony_title', 'testimony_user']


admin.site.register(TestimonyModel, TestimonyAdmin)


class TestimonyDeletedAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['testimony_deleted_title']}),
        (None,               {'fields': ['testimony_deleted_user']}),
        (None,               {'fields': ['testimony_deleted_description']}),
        (None,               {'fields': ['testimony_deleted_rating']}),
        ]
    list_display = ('testimony_deleted_title', 'testimony_deleted_user', 'testimony_deleted_date', 'testimony_deleted_rating',)
    list_filter = ['testimony_deleted_user']
    search_fields = ['testimony_deleted_title', 'testimony_deleted_user']


admin.site.register(TestimonyDeletedModel, TestimonyDeletedAdmin)

