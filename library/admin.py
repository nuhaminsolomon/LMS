from django.contrib import admin

from library.models import CustomUser

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass
    # list_display = ['name']
    # search_fields = ['name']