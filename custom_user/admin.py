from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['username']}),
        (None,               {'fields': ['email']}),
        (None,               {'fields': ['is_professional']}),
        (None,               {'fields': ['photo_bookmark']}),
    ]
    list_display = ('username', 'email', 'is_professional')
    list_filter = ['is_professional']
    search_fields = ['username', 'email']


admin.site.register(CustomUser, CustomUserAdmin)

