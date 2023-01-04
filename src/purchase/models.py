# third-party
import nepali_datetime
# Django
from django.db import models
# User-defined models (import)
from src.core_app.models import NowTimestampAndUserModel
from src.supplier.models import Supplier
from src.item.models import Item, ItemCategory, PackingType, PackingTypeDetail
from src.core_app.models import PaymentMode, DiscountScheme, AdditionalChargeType, FiscalSessionBS, FiscalSessionAD
from django.core.validators import MinValueValidator
from decimal import Decimal
# import for log
from log_app.models import LogBase
from simple_history import register
from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_ad, get_fiscal_year_code_bs

class PurchaseOrderMaster(NowTimestampAndUserModel):
    PURCHASE_ORDER_TYPE = (
        (1, "ORDER"),
        (2, "CANCELLED"),
        (3, "APPROVED")
    )

    order_no = models.CharField(max_length=20, unique=True,
                                help_text="Order no. should be max. of 20 characters")
    order_type = models.PositiveIntegerField(choices=PURCHASE_ORDER_TYPE,
                                             help_text="Order type like Order, approved, cancelled")
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                    help_text="Sub total can have max value upto=9999999999.99 and default=0.0")
    discount_scheme = models.ForeignKey(DiscountScheme, on_delete=models.PROTECT, blank=True, null=True)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                         help_text="Total discount can have max value upto=9999999999.99 and default=0.0")
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                        help_text="Discount rate if discountable, max_value=100.00 and default=0.0")
    total_discountable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                    help_text="Total discountable amount can have max_value upto=9999999999.99 and min value=0.0")
    total_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                               help_text="Total taxable amount can have max value upto=9999999999.99 default=0.0")
    total_non_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                   help_text="Total nontaxable amount can have max value upto=9999999999.99 and default=0.0")
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                    help_text="Total tax can have max value upto=9999999999.99 and default=0.0")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                      help_text="Grand total can have max value upto=9999999999.99 and default=0.0")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT,
                                 help_text="Supplier")
    remarks = models.CharField(max_length=100, blank=True,
                               help_text="Remarks should be max. of 100 characters")
    ref_purchase_order = models.OneToOneField('self', on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return "id {} : {}".format(self.id, self.order_no)


register(PurchaseOrderMaster, app="log_app", table_name="purchase_purchaseordermaster_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PurchaseOrderDetail(NowTimestampAndUserModel):
    purchase_order = models.ForeignKey('PurchaseOrderMaster',
                                       related_name="purchase_order_details", on_delete=models.PROTECT)
                                       
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    item_category = models.ForeignKey(ItemCategory, on_delete=models.PROTECT)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    sale_cost = models.DecimalField(max_digits=12, decimal_places=2)
    qty = models.DecimalField(max_digits=12, decimal_places=2, help_text="Order quantity")
    pack_qty = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
                            
    packing_type = models.ForeignKey(PackingType, on_delete=models.PROTECT)
    packing_type_detail =  models.ForeignKey(PackingTypeDetail, on_delete=models.PROTECT)
    taxable = models.BooleanField(default=True, help_text="Check if item is taxable")
    tax_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                   help_text="Tax rate if item is taxable")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    discountable = models.BooleanField(default=True, help_text="Check if item is discountable")
    discount_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                        help_text="Discount rate if item is discountable")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    ref_purchase_order_detail = models.ForeignKey('self', on_delete=models.PROTECT, blank=True,
                                                  null=True)

    def __str__(self):
        return "id {} : {}".format(self.id, self.purchase_order)


register(PurchaseOrderDetail, app="log_app", table_name="purchase_purchaseorderdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])

class PurchaseMaster(NowTimestampAndUserModel):
    PURCHASE_TYPE = (
        (1, "PURCHASE"),
        (2, "RETURN"),
        (3, "OPENING-STOCK"),
        (4, "STOCK-ADDITION"),
        (5, "STOCK-SUBTRACTION")
    )

    PAY_TYPE = (
        (1, "CASH"),
        (2, "CREDIT"),
        (3, "PARTIAL")
    )

    purchase_no = models.CharField(max_length=20, unique=True,
                                   help_text="Purchase no. should be max. of 10 characters")
    purchase_type = models.PositiveIntegerField(choices=PURCHASE_TYPE,
                                                help_text="Purchase type like 1= Purchase, 2 = Return, "
                                                          "3 = Opening stock, 4 = stock-addition, 5 = stock-subtraction")
    pay_type = models.PositiveIntegerField(choices=PAY_TYPE,
                                           help_text="Pay type like CASH, CREDIT or PARTIAL")
    sub_total = models.DecimalField(max_digits=12, decimal_places=2,
                                    help_text="Sub total can be max upto 9999999999.99")
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                         help_text="Total discount can be max upto 9999999999.99")
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                        help_text="Discount rate if  discountable, default=0.0 and max_value=100.00")
    discount_scheme = models.ForeignKey(DiscountScheme, on_delete=models.PROTECT, blank=True, null=True)
    total_discountable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                    help_text="Total discountable amount can be max upto 9999999999.99")
    total_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                               help_text="Total taxable amount can be max upto 9999999999.99")
    total_non_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                   help_text="Total nontaxable amount can be max upto 9999999999.99")
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                    help_text="Total tax can be max upto 9999999999.99")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                      help_text="Grand total can be max upto 9999999999.99")
    round_off_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                      help_text="Round off Amount can be max upto 9999999999.99")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT,null=True, help_text="Supplier null=True")

    bill_no = models.CharField(max_length=20, help_text="Bill no.", blank=True)
    bill_date_ad = models.DateField(max_length=10, help_text="Bill Date AD", blank=True, null=True)
    bill_date_bs = models.CharField(max_length=10, help_text="Bill Date BS", blank=True)
    chalan_no = models.CharField(max_length=15, help_text="Chalan no.", blank=True)
    due_date_ad = models.DateField(max_length=10, help_text="Due Date AD", blank=True, null=True)
    due_date_bs = models.CharField(max_length=10, help_text="Due Date BS", blank=True)
    fiscal_session_ad = models.ForeignKey(FiscalSessionAD, on_delete=models.PROTECT)
    fiscal_session_bs = models.ForeignKey(FiscalSessionBS, on_delete=models.PROTECT)                                        
    remarks = models.CharField(max_length=100, blank=True,
                               help_text="Remarks can be max. of 100 characters")
    ref_purchase = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    ref_purchase_order = models.ForeignKey('PurchaseOrderMaster', on_delete=models.PROTECT,
                                           blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.bill_date_ad is not None:
            date_bs_bill = nepali_datetime.date.from_datetime_date(self.bill_date_ad)
            self.bill_date_bs = date_bs_bill
        if self.due_date_ad is not None:
            date_bs_due = nepali_datetime.date.from_datetime_date(self.due_date_ad)
            self.due_date_bs = date_bs_due
        
       
        super().save(*args, **kwargs)

    def __str__(self):
        return "id {} : {}".format(self.id, self.purchase_no)


register(PurchaseMaster, app="log_app", table_name="purchase_purchasemaster_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PurchaseDetail(NowTimestampAndUserModel):
    purchase = models.ForeignKey(PurchaseMaster, default=False, related_name="purchase_details",
                                 on_delete=models.PROTECT)
    item = models.ForeignKey(Item, default=False, on_delete=models.PROTECT)
    item_category = models.ForeignKey(ItemCategory, default=False, on_delete=models.PROTECT)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                            help_text="purchase_cost can be max value upto 9999999999.99 and default=0.0")
    sale_cost = models.DecimalField(max_digits=12, decimal_places=2,
                            help_text="sale_cost can be max value upto 9999999999.99 and default=0.0")
    qty = models.DecimalField(max_digits=12, decimal_places=2,
                            help_text="Purchase quantity can be max value upto 9999999999.99 and default=0.0")
    pack_qty = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    free_purchase = models.BooleanField(default= False, help_text="default = false")                    
    packing_type = models.ForeignKey(PackingType, on_delete=models.PROTECT)
    packing_type_detail =  models.ForeignKey(PackingTypeDetail, on_delete=models.PROTECT)
    taxable = models.BooleanField(default=True, help_text="Check if item is taxable")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                            help_text="Tax rate if item is taxable, max value=100.00 and default=0.0")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                            help_text="Tax amount can be max value upto 9999999999.99 and default=0.0")
    discountable = models.BooleanField(default=True, help_text="Check if item is discountable")
    expirable = models.BooleanField(default=False, help_text="Check if item is Expirable, default=False")
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                            help_text="Discount rate if item is discountable, default=0.0 and max_value=100.00")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                            help_text="Discount_amount can be max upto 9999999999.99 and default=0.0")
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2,
                             help_text="Gross amount can be max upto 9999999999.99 and default=0.0")
    net_amount = models.DecimalField(max_digits=12, decimal_places=2,
                            help_text="Net amount can be max upto 9999999999.99 and default=0.0")
    expiry_date_ad = models.DateField(max_length=10, help_text="Expiry Date AD", null=True, blank=True)
    expiry_date_bs = models.CharField(max_length=10, help_text="Expiry Date BS", blank=True)
    batch_no = models.CharField(max_length=20, help_text="Batch no. max length 20")
    ref_purchase_order_detail = models.ForeignKey('PurchaseOrderDetail', on_delete=models.PROTECT,
                                                  blank=True, null=True)
    cc_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, validators=[MinValueValidator(Decimal('0.00'))],
                                    help_text="Check if the item is free purchase or not, default=0.0")
    cc_amount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, validators=[MinValueValidator(Decimal('0.00'))],
                                    help_text="Check if the item is free purchase or not, default=0.0")
    ref_purchase_detail = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.expiry_date_ad is not None:
            date_bs = nepali_datetime.date.from_datetime_date(self.expiry_date_ad)
            self.expiry_date_bs = date_bs
        super().save(*args, **kwargs)

    def __str__(self):
        return "id {}: {}".format(self.id, self.purchase.purchase_no)

register(PurchaseDetail, app="log_app", table_name="purchase_purchasedetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PurchasePaymentDetail(NowTimestampAndUserModel):
    purchase_master = models.ForeignKey(PurchaseMaster, on_delete=models.PROTECT, related_name="payment_details")
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                            help_text="Amount can have max value upto 9999999999.99 and min=0.0")
    remarks = models.CharField(max_length=50, blank=True,
                            help_text="Remarks can have max upto 50 characters")

    def __str__(self):
        return f"{self.id}"


register(PurchasePaymentDetail, app="log_app", table_name="purchase_purchasepaymentdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PurchaseAdditionalCharge(NowTimestampAndUserModel):
    charge_type = models.ForeignKey(AdditionalChargeType, on_delete=models.PROTECT)
    purchase_master = models.ForeignKey(PurchaseMaster, on_delete=models.PROTECT, related_name="additional_charges")
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                            help_text="Amount can have max value upto 9999999999.99 and min=0.0")
    remarks = models.CharField(max_length=50, blank=True,
                            help_text="Remarks can have max upto 50 characters")

    def __str__(self):
        return "id {} purchase {} charge {}".format(self.id, self.purchase_master.purchase_no, self.charge_type.name)


register(PurchaseAdditionalCharge, app="log_app", table_name="purchase_purchaseadditionalcharge_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])