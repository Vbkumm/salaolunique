from django.contrib import admin
from price.models import PriceModel


class PriceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['price_service']}),
        (None,               {'fields': ['price_combo']}),
        (None,               {'fields': ['price_value']}),
        (None,               {'fields': ['old_price_value']}),
        (None,               {'fields': ['price_active']}),
    ]
    list_display = ('price_service','price_combo', 'price_value', 'price_active', 'price_updated_at', 'price_updated_by', 'price_published', 'price_user', )
    list_filter = ['price_value']
    search_fields = ['price', 'price_value']


admin.site.register(PriceModel, PriceAdmin)
