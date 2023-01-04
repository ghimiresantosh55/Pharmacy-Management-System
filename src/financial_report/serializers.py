# rest_framework
from typing import SupportsRound
from rest_framework import serializers
from decimal import Decimal
from src.core_app.models import FiscalSessionAD, FiscalSessionBS
from src.supplier.models import Supplier
from src.party_payment.models import BasicPartyPayment, BasicPartyPaymentDetail
# Models from purchase app
from src.purchase.models import PurchaseOrderMaster, PurchaseOrderDetail
from src.purchase.models import PurchaseMaster, PurchaseDetail, PurchasePaymentDetail, PurchaseAdditionalCharge
from src.sale.models import SaleMaster, SaleDetail, SalePaymentDetail
from src.credit_management.models import CreditClearance
from src.customer_order.models import OrderMaster, OrderDetail
# Models form party payment app 
"""-------------------------serializer for purchase order -----------------------------------------------------------"""


# purchase order serializers
class ReportPurchaseOrderMasterSerializer(serializers.ModelSerializer):
    supplier_first_name = serializers.ReadOnlyField(source='supplier.first_name', allow_null=True)
    supplier_middle_name = serializers.ReadOnlyField(source='supplier.middle_name', allow_null=True)
    supplier_last_name = serializers.ReadOnlyField(source='supplier.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    order_type_display = serializers.ReadOnlyField(source='get_order_type_display', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = "__all__"

    def to_representation(self, instance):
        my_fields = {'supplier_first_name', 'created_by_user_name', 'supplier_middle_name',
                     'supplier_last_name', 'discount_scheme_name', 'ref_purchase_order_no'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class ReportPurchaseOrderDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = PurchaseOrderDetail
        fields = "__all__"

    def to_representation(self, instance):
        my_fields = {'ref_purchase_order_detail', 'item_name', 'item_category_name'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


# purchase order detail serializers for Read Only view
class DetailPurchaseOrderDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = PurchaseOrderDetail
        exclude = ['purchase_order']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'ref_purchase_order_detail'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


# purchase order master serializers for Write Only view
class SummaryPurchaseOrderMasterSerializer(serializers.ModelSerializer):
    purchase_order_details = DetailPurchaseOrderDetailSerializer(many=True)
    supplier_first_name = serializers.ReadOnlyField(source='supplier.first_name', allow_null=True)
    supplier_middle_name = serializers.ReadOnlyField(source='supplier.middle_name', allow_null=True)
    supplier_last_name = serializers.ReadOnlyField(source='supplier.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    order_type = serializers.ReadOnlyField(source='get_order_type_display', allow_null=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = "__all__"

    def to_representation(self, instance):
        my_fields = {'supplier_first_name', 'created_by_user_name', 'supplier_middle_name',
                     'supplier_last_name', 'discount_scheme_name', 'ref_purchase_order_no', 'order_type'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


"""-------------------------serializer for purchase  -----------------------------------------------------------"""
class ItemwisePurchaseReportSerializer(serializers.ModelSerializer):
    supplier_first_name = serializers.ReadOnlyField(source='purchase.supplier.first_name', allow_null=True)
    supplier_last_name = serializers.ReadOnlyField(source='purchase.supplier.last_name', allow_null=True)
    purchase_no = serializers.ReadOnlyField(source='purchase.purchase_no', allow_null=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    class Meta:
        model = PurchaseDetail
        exclude= ['created_date_ad','created_date_bs','created_by','item_category']


class ReportPurchaseMasterSerializer(serializers.ModelSerializer):
    supplier_first_name = serializers.ReadOnlyField(source='supplier.first_name', allow_null=True)
    supplier_middle_name = serializers.ReadOnlyField(source='supplier.middle_name', allow_null=True)
    supplier_last_name = serializers.ReadOnlyField(source='supplier.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    ref_purchase_no = serializers.ReadOnlyField(source='ref_purchase.purchase_no', allow_null=True)
    purchase_type_display = serializers.ReadOnlyField(source='get_purchase_type_display', allow_null=True)
    pay_type_display =serializers.ReadOnlyField(source='get_pay_type_display', allow_null=True)


    class Meta:
        model = PurchaseMaster
        fields = "__all__"

    def to_representation(self, instance):
        my_fields = {'supplier_first_name', 'created_by_user_name', 'supplier_middle_name',
                     'supplier_last_name', 'discount_scheme_name', 'ref_purchase_order_no', 'ref_purchase'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class ReportPurchaseDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = PurchaseDetail
        fields = "__all__"

    def to_representation(self, instance):
        my_fields = {'ref_purchase_order_detail', 'item_name', 'item_category_name',
                     'ref_purchase_detail'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class ReportPurchasePaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)

    class Meta:
        model = PurchasePaymentDetail
        fields = "__all__"


class ReportPurchaseAdditionalChargeSerializer(serializers.ModelSerializer):
    charge_type_name = serializers.ReadOnlyField(source='charge_type.name', allow_null=True)

    class Meta:
        model = PurchaseAdditionalCharge
        fields = "__all__"


# serializer for Summary report of Purchase
class DetailPurchasePaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)

    class Meta:
        model = PurchasePaymentDetail
        exclude = ['purchase_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class DetailPurchaseAdditionalChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseAdditionalCharge
        exclude = ['purchase_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class DetailPurchaseDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = PurchaseDetail
        exclude = ['purchase']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'expiry_date_ad', 'ref_purchase_order_detail', 'ref_purchase_detail'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data



# purchase master serializer for write_only views
class SummaryPurchaseMasterSerializer(serializers.ModelSerializer):
    purchase_details = DetailPurchaseDetailSerializer(many=True)
    payment_details = DetailPurchasePaymentDetailSerializer(many=True)
    additional_charges = DetailPurchaseAdditionalChargeSerializer(many=True)
    supplier_first_name = serializers.ReadOnlyField(source='supplier.first_name', allow_null=True)
    supplier_middle_name = serializers.ReadOnlyField(source='supplier.middle_name', allow_null=True)
    supplier_last_name = serializers.ReadOnlyField(source='supplier.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    ref_purchase = serializers.ReadOnlyField(source='ref_purchase.purchase_no', allow_null=True)
    purchase_type_display = serializers.ReadOnlyField(source='get_purchase_type_display', allow_null=True)
    pay_type_display = serializers.ReadOnlyField(source='get_pay_type_display', allow_null=True)

    class Meta:
        model = PurchaseMaster
        fields = "__all__"
        read_only_fields = ['purchase_type_display','pay_type_display','created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'discount_scheme', 'bill_no', 'due_date_ad', 'ref_purchase', 'ref_purchase_order',
                     'additional_charges'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


# serializer for provide all PurchaseMaster and PurchaseDetail summary
class StockAdjustmentSummarySerializer(serializers.ModelSerializer):
    purchase_details = DetailPurchaseDetailSerializer(many=True)
    supplier_first_name = serializers.ReadOnlyField(source='supplier.first_name', allow_null=True)
    supplier_last_name = serializers.ReadOnlyField(source='supplier.last_name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    purchase_type_display = serializers.ReadOnlyField(source='get_purchase_type_display', allow_null=True)
    pay_type_display = serializers.ReadOnlyField(source='get_pay_type_display', allow_null=True)

    class Meta:
        model = PurchaseMaster
        fields = "__all__"
        read_only_fields = ['purchase_type_display', 'pay_type_display', 'created_by', 'created_date_ad',
                            'created_date_bs']
    

"""-------------------------serializer for Sale  -----------------------------------------------------------"""


class ReportSaleMasterSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_sale_master = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    sale_type_display = serializers.ReadOnlyField(source='get_sale_type_display', allow_null=True)
    pay_type_display = serializers.ReadOnlyField(source='get_pay_type_display', allow_null=True)

    class Meta:
        model = SaleMaster
        fields = "__all__"
        read_only_fields = ['sale_type_display','created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'customer_first_name', 'created_by_user_name', 'customer_middle_name',
                     'customer_last_name', 'discount_scheme_name', 'ref_sale_master'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class ReportSaleDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = SaleDetail
        fields = "__all__"

    def to_representation(self, instance):
        my_fields = {'ref_sale_detail', 'item_name', 'item_category_name',
                     'ref_purchase_detail'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class ReportSalePaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)

    class Meta:
        model = SalePaymentDetail
        fields = "__all__"


# serializer for summary report of sale
class DetailSalePaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)
    class Meta:
        model = SalePaymentDetail
        exclude = ['sale_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class DetailSaleDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = SaleDetail
        exclude = ['sale_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'expiry_date_ad', 'ref_purchase_order_detail', 'ref_purchase_detail'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class SummarySaleMasterSerializer(serializers.ModelSerializer):
    sale_details = DetailSaleDetailSerializer(many=True)
    payment_details = DetailSalePaymentDetailSerializer(many=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_sale_master = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    sale_type_display = serializers.ReadOnlyField(source='get_sale_type_display', allow_null=True)

    class Meta:
        model = SaleMaster
        fields = "__all__"
        read_only_fields= ['sale_type_display','created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'customer_first_name', 'created_by_user_name', 'customer_middle_name',
                     'customer_last_name', 'discount_scheme_name', 'ref_sale_master'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


"""_______________________ serializer for Credit Sale Report _______________________________________________"""

class SaleCreditReportSerializer(serializers.ModelSerializer):
    sale_id = serializers.ReadOnlyField(source='id')
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    paid_amount = serializers.SerializerMethodField()
    due_amount = serializers.SerializerMethodField()

    class Meta:
        model = SaleMaster
        fields = ['sale_id', 'sale_no', 'customer', 'customer_first_name', 'customer_middle_name',
                  'customer_last_name',
                  'grand_total', 'paid_amount', 'due_amount', 'created_date_ad', 'created_date_bs',
                  'created_by', 'created_by_user_name', 'remarks']

    def get_paid_amount(self, instance):
        paid_amount = sum(CreditClearance.objects.filter(sale_master=instance.id)
                          .values_list('total_amount', flat=True))
        return paid_amount

    def get_due_amount(self, instance):
        paid_amount = self.get_paid_amount(instance)
        due_amount = instance.grand_total - paid_amount
        return due_amount


"""_________________________________serializers for customer order Report___________________________________________"""


class CustomerOrderMasterReportSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)

    class Meta:
        model = OrderMaster
        fields = "__all__"
        read_only_fields = ['status_display', 'created_by', 'created_date_ad', 'created_date_bs']


class CustomerOrderDetailReportSerializer(serializers.ModelSerializer):
    order_no = serializers.ReadOnlyField(source='order.order_no', allow_null=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item.item_category.name', allow_null=True)

    class Meta:
        model = OrderDetail
        fields = "__all__"


class CustomerOrderDetailSummaryReportSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item.item_category.name', allow_null=True)

    class Meta:
        model = OrderDetail
        exclude = ['order']


class CustomerOrderSummarySerializer(serializers.ModelSerializer):
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    order_details = CustomerOrderDetailSummaryReportSerializer(many=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)

    class Meta:
        model = OrderMaster
        fields = "__all__"
        read_only_fields = ['status_display','created_by', 'created_date_ad', 'created_date_bs']


"""_________________________________serializers for party Report___________________________________________"""

class ReportBasicPartyPaymentSerializer(serializers.ModelSerializer):
    supplier_first_name = serializers.ReadOnlyField(source='supplier.first_name', allow_null=True)
    supplier_middle_name = serializers.ReadOnlyField(source='supplier.middle_name', allow_null=True)
    supplier_last_name = serializers.ReadOnlyField(source='supplier.last_name', allow_null=True)
    payment_type_display = serializers.ReadOnlyField(source='get_payment_type_display', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    fiscal_session_ad_full = serializers.ReadOnlyField(source='fiscal_session_ad.session_full', allow_null=True)
    fiscal_session_bs_full = serializers.ReadOnlyField(source='fiscal_session_bs.session_full', allow_null=True)
    fiscal_session_ad_short = serializers.ReadOnlyField(source='fiscal_session_ad.session_short', allow_null=True)
    fiscal_session_bs_short = serializers.ReadOnlyField(source='fiscal_session_bs.session_short', allow_null=True)

    class Meta:
        model = BasicPartyPayment
        fields = "__all__"
        read_only_fields = ['payment_type_display','created_by', 'created_date_ad', 'created_date_bs']


class ReportBasicPartyPaymentDetailSerializer(serializers.ModelSerializer):
    supplier_id = serializers.ReadOnlyField(source='basic_party_payment.supplier.id', allow_null='True')
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    basic_party_payment_supplier_first_name = serializers.ReadOnlyField(source='basic_party_payment.supplier.first_name', allow_null=True)
    basic_party_payment_supplier_middle_name = serializers.ReadOnlyField(source='basic_party_payment.supplier.middle_name', allow_null=True)
    basic_party_payment_supplier_last_name = serializers.ReadOnlyField(source='basic_party_payment.supplier.last_name', allow_null=True)
    
    class Meta:
        model = BasicPartyPaymentDetail
        fields = "__all__"



class DetailBasicPartyPaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
   

    class Meta:
        model = BasicPartyPaymentDetail
        exclude = ['basic_party_payment']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class SummaryBasicPartyPaymentSerializer(serializers.ModelSerializer):
    basic_party_payment_details = DetailBasicPartyPaymentDetailSerializer(many=True)
    supplier_first_name = serializers.ReadOnlyField(source= 'supplier.first_name', allow_null= True)
    supplier_middle_name =  serializers.ReadOnlyField(source= 'supplier.middle_name', allow_null= True)
    supplier_last_name =  serializers.ReadOnlyField(source= 'supplier.last_name', allow_null= True)
    payment_type_display = serializers.ReadOnlyField(source='get_payment_type_display', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    fiscal_session_ad_full = serializers.ReadOnlyField(source='fiscal_session_ad.session_full', allow_null=True)
    fiscal_session_bs_full = serializers.ReadOnlyField(source='fiscal_session_bs.session_full', allow_null=True)
    fiscal_session_ad_short = serializers.ReadOnlyField(source='fiscal_session_ad.session_short', allow_null=True)
    fiscal_session_bs_short = serializers.ReadOnlyField(source='fiscal_session_bs.session_short', allow_null=True)
    class Meta:
        model = BasicPartyPayment
        fields = "__all__"
        read_only_fields= ['payment_type_display','created_by', 'created_date_ad', 'created_date_bs']


    def to_representation(self, instance):
        my_fields = {'supplier_first_name', 'created_by_user_name', 'supplier_middle_name',
                     'supplier_last_name'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


"""_________________________________serializers for suppilers Report___________________________________________"""


class GetSupplierSerializer(serializers.ModelSerializer):
    country_name =serializers.ReadOnlyField(source='country.name', allow_null=True)
    class Meta:
        model = Supplier
        exclude = ['created_date_ad','created_date_bs','created_by','active','image','country']


class GetFiscalSessionADSerializer(serializers.ModelSerializer):
    # country_name =serializers.ReadOnlyField(source='country.name', allow_null=True)
    class Meta:
        model = FiscalSessionAD
        exclude = ['created_date_ad','created_date_bs','created_by']


class GetFiscalSessionBSSerializer(serializers.ModelSerializer):
    # country_name =serializers.ReadOnlyField(source='country.name', allow_null=True)
    class Meta:
        model = FiscalSessionBS
        exclude = ['created_date_ad','created_date_bs','created_by']


