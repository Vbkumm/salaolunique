from django.contrib import admin
from service.models import ServiceModel, ServiceCategoryModel, ProfessionalServicesSkillModel
# Register your models here.


class ServiceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['service_tittle']}),
        (None,               {'fields': ['service_category']}),
        (None,               {'fields': ['service_author']}),
        (None,               {'fields': ['service_updated_by']}),
        (None,               {'fields': ['service_active']}),
        (None,               {'fields': ['service_views']}),
        ]
    list_display = ('service_tittle', 'service_category', 'service_updated_at', 'service_published', 'service_updated_by', 'service_author',)
    list_filter = ['service_category']
    search_fields = ['service_tittle', 'service_category']


admin.site.register(ServiceModel, ServiceAdmin)


class CategoryServiceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['category_service']}),
        (None,               {'fields': ['professional_category']}),
        (None,               {'fields': ['category_service_author']}),
        (None,               {'fields': ['category_service_updated_by']}),
    ]
    list_display = ('category_service', 'professional_category', 'category_service_updated_at', 'category_service_published', 'category_service_updated_by', 'category_service_author',)
    list_filter = ['professional_category']
    search_fields = ['category_service', 'professional_category']


admin.site.register(ServiceCategoryModel, CategoryServiceAdmin)

admin.site.register(ProfessionalServicesSkillModel, admin.ModelAdmin)
