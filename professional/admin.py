from django.contrib import admin
from professional.models import ProfessionalModel, ProfessionalCategoryModel

# Register your models here.


class ProfessionalAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['professional_name']}),
        (None,               {'fields': ['professional_category']}),
        (None,               {'fields': ['professional_active']}),
        ('Date information', {'fields': ['professional_start_date']}),
    ]
    list_display = ('professional_name', 'professional_start_date', 'professional_updated_at', 'professional_updated_by', 'professional_published', 'professional_author')
    list_filter = ['professional_start_date']
    search_fields = ['professional_name']


admin.site.register(ProfessionalModel, ProfessionalAdmin)


class CategoryProfessionalAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['category_professional']}),
    ]
    list_display = ('category_professional', 'category_professional_updated_at', 'category_professional_updated_by', 'category_professional_author', 'category_professional_published',)
    list_filter = ['category_professional_updated_at']
    search_fields = ['category_professional']

admin.site.register(ProfessionalCategoryModel, CategoryProfessionalAdmin)
