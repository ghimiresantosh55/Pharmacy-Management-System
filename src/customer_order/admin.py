from django.contrib import admin
from .models import OrderMaster, OrderDetail

# Register your models here.
admin.site.register(OrderDetail)
admin.site.register(OrderMaster)

