from django.contrib import admin

# Register your models here.
from .models import Customer


class CustomerAdminModel(admin.ModelAdmin):
    model = Customer
    search_fields = ['first_name', 'last_name']
    ordering = ['id', 'first_name']
    list_display = ['id', 'first_name', 'last_name', 'active']

admin.site.register(Customer, CustomerAdminModel)
