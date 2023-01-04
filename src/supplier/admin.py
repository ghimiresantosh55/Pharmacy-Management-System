from django.contrib import admin

# Register your models here.
from .models import Supplier


class SupplierAdminModel(admin.ModelAdmin):
    model = Supplier
    search_fields = ['first_name', 'last_name']
    ordering = ['id', 'first_name']
    list_display = ['id', 'first_name', 'last_name', 'pan_vat_no',
                    'phone_no', 'email_id']


admin.site.register(Supplier, SupplierAdminModel)