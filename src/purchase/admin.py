from django.contrib import admin
from .models import PurchaseOrderMaster, PurchaseOrderDetail, PurchaseMaster, PurchaseDetail, PurchasePaymentDetail, PurchaseAdditionalCharge
# Register your models here.
# class PurchaseMasterAdmin(admin.ModelAdmin):
#      list_display =('id','purchase_no','purchase_type','supplier','bill_no','grand_total','pay_type','created_date_ad')
admin.site.register(PurchaseOrderDetail)
admin.site.register(PurchaseOrderMaster)
admin.site.register(PurchaseMaster)
admin.site.register(PurchaseDetail)
admin.site.register(PurchasePaymentDetail)
admin.site.register(PurchaseAdditionalCharge)
