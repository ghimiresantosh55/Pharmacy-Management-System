from django.contrib import admin
from .models import CustomGroup, CustomPermission, PermissionCategory
from django.contrib.auth.models import Group

class CustomPermissionAdmin(admin.ModelAdmin):
    model = CustomPermission
    search_fields = ('code_name',)
    list_filter = ('category',)


admin.site.unregister(Group)
admin.site.register(CustomGroup)
admin.site.register(CustomPermission, CustomPermissionAdmin)
admin.site.register(PermissionCategory)