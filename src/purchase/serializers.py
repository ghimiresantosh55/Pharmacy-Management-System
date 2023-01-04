# rest_framework
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db.models import fields
from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone
from rest_framework.fields import ReadOnlyField
from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_ad, get_fiscal_year_code_bs
from src.core_app.models import AdditionalChargeType, DiscountScheme, PaymentMode, FiscalSessionAD, FiscalSessionBS

from src.item.models import ItemCategory, PackingTypeDetail, Item
from src.item.serializers import PackingTypeDetailSerializer
from src.supplier.models import Supplier
# Models from purchase app
from .models import PurchaseOrderMaster, PurchaseOrderDetail,\
            PurchaseMaster, PurchaseDetail, PurchasePaymentDetail, PurchaseAdditionalCharge


from src.core_app.models import OrganizationRule
from src.custom_lib.functions import current_user
import decimal
decimal.getcontext().rounding=decimal.ROUND_HALF_UP

# purchase order master serializers for read only view
class PurchaseOrderMasterSerializer(serializers.ModelSerializer):
    supplier_first_name = serializers.ReadOnlyField(source='supplier.first_name', allow_null=True)
    supplier_middle_name = serializers.ReadOnlyField(source='supplier.middle_name', allow_null=True)
    supplier_last_name = serializers.ReadOnlyField(source='supplier.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    order_type_display = serializers.ReadOnlyField(source='get_order_type_display', allow_null=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = "__all__"
        read_only_fields = ['order_type_display', 'created_by', 'created_date_ad', 'created_date_bs']


# purchase order detail serializers for read only view
class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    packing_type_name = serializers.ReadOnlyField(source="packing_type.name", allow_null=True)

    class Meta:
        model = PurchaseOrderDetail
        fields = "__all__"
        read_only_fields = ['item_name', 'item_category_name', 'created_by', 'created_date_ad', 'created_date_bs']


class GetPackingTypeDetailSerializer(serializers.ModelSerializer):
    packing_type_name = serializers.ReadOnlyField(source="packing_type.name", allow_null=True)
    item_name = serializers.ReadOnlyField(source="item.name", allow_null=True)
   
    class Meta:
        model =PackingTypeDetail
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# purchase order detail serializers for Read Only view
class GetPurchaseOrderDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    packing_type_name = serializers.ReadOnlyField(source='packing_type.name', allow_null=True)
    packing_type_detail_item_unit_name = serializers.ReadOnlyField(source='item.unit.name', allow_null=True)
    item_unit_short_form = serializers.ReadOnlyField(source='item.unit.short_form', allow_null=True)
    order_no = serializers.ReadOnlyField(source='purchase_order.order_no')
    expirable = serializers.ReadOnlyField(source='item.expirable')
    
    packing_type_details_itemwise = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderDetail
        exclude = ['purchase_order']
        read_only_fields = ['created_date_ad','created_by','created_date_bs']


    def to_representation(self, instance):
        my_fields = {'packing_type_detail_item_unit_name','item_unit_short_form'}
                     
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data

    def get_packing_type_details_itemwise(self, purchase_detail):
        # print(purchase_detail.item.id)
        try:
            packing_type_details_itemwise = PackingTypeDetail.objects.filter(item=purchase_detail.item.id)
            # print(packing_type_details_itemwise)
            packing_serializer = GetPackingTypeDetailSerializer(packing_type_details_itemwise, many=True)
            # print(packing_serializer.data)
            return packing_serializer.data
        except:
                return None
    

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


# Purchase order for get-orders view
class GetPurchaseOrderMasterSerializer(serializers.ModelSerializer):
    purchase_order_details = GetPurchaseOrderDetailSerializer(many=True)
    supplier_first_name = serializers.ReadOnlyField(source='supplier.first_name', allow_null=True)
    supplier_middle_name = serializers.ReadOnlyField(source='supplier.middle_name', allow_null=True)
    supplier_last_name = serializers.ReadOnlyField(source='supplier.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)
    order_type_display = serializers.ReadOnlyField(source='get_order_type_display', allow_null=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = "__all__"
        read_only_fields = ['supplier_first_name', 'order_type_display', 'created_by', 'created_date_ad',
                            'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'ref_purchase_order', 'supplier_first_name', 'created_by_user_name', 'supplier_middle_name',
                     'supplier_last_name', 'discount_scheme_name', 'ref_purchase_order_no'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


# purchase order detail serializers for Write Only view
class SavePurchaseOrderDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    order_no = serializers.ReadOnlyField(source='purchase_order.order_no')

    class Meta:
        model = PurchaseOrderDetail
        exclude = ['purchase_order']
        read_only_fields = ['created_by','created_date_ad', 'created_date_bs']

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


# purchase order master nested serializers for Write Only view
class SavePurchaseOrderMasterSerializer(serializers.ModelSerializer):
    purchase_order_details = SavePurchaseOrderDetailSerializer(many=True)
    supplier_first_name = serializers.ReadOnlyField(source='supplier.first_name', allow_null=True)
    supplier_middle_name = serializers.ReadOnlyField(source='supplier.middle_name', allow_null=True)
    supplier_last_name = serializers.ReadOnlyField(source='supplier.last_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    ref_purchase_order_no = serializers.ReadOnlyField(source='ref_purchase_order.order_no', allow_null=True)

    class Meta:
        model = PurchaseOrderMaster
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'ref_purchase_order'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data

    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        date_now = timezone.now()
        purchase_order_details = validated_data.pop('purchase_order_details')
        order_master = PurchaseOrderMaster.objects.create(**validated_data, created_date_ad=date_now)
        for purchase_order_detail in purchase_order_details:
            PurchaseOrderDetail.objects.create(
                **purchase_order_detail,
                purchase_order=order_master, created_by=validated_data['created_by'], created_date_ad=date_now
            )
        return order_master

    def validate(self, data):

        quantize_places = Decimal(10) ** -2
        # initialize variables to check
        sub_total = Decimal('0.00')
        total_discount = Decimal('0.00')
        total_discountable_amount = Decimal('0.00')
        total_taxable_amount = Decimal('0.00')
        total_nontaxable_amount = Decimal('0.00')
        total_tax = Decimal('0.00')
        grand_total = Decimal('0.00')
        purchase_order_details = data['purchase_order_details']
        for purchase_order in purchase_order_details:

            purchase_order_detail = {}
            key_values = zip(purchase_order.keys(), purchase_order.values())
            for key, values in key_values:
                purchase_order_detail[key] = values


            # Validation for ref_purchase_order_detail  quantity should not be greater than order_qty
            if "ref_purchase_order_detail" in purchase_order_detail:
                if purchase_order_detail['ref_purchase_order_detail'] is not None:
                    # print(purchase_order_detail)
                    # print(purchase_order)
                    reference_qty = purchase_order_detail['ref_purchase_order_detail'].qty
                    # print( purchase_order_detail['ref_purchase_order_detail'].qty) # approved qty
                    # print(purchase_order_detail['qty']) # order qty
                    if reference_qty < purchase_order_detail['qty']: # 
                        raise serializers.ValidationError({ f'item {purchase_order_detail["item"].name}': f' Approved quantity :{purchase_order_detail["qty"]} should less than or equal to order quantity:{reference_qty} '})


            # validation for amount values less than or equal to 0 "Zero"
            if purchase_order_detail['tax_rate'] < 0 or purchase_order_detail['discount_rate'] < 0 or \
                    purchase_order_detail['sale_cost'] < 0:
                raise serializers.ValidationError({
                    f'item {purchase_order_detail["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
                                                                  ' cannot be less than 0'})

            if purchase_order_detail['purchase_cost'] <= 0 or purchase_order_detail['qty'] <= 0:
                raise serializers.ValidationError({
                    f'item {purchase_order_detail["item"].name}': 'values in fields, purchase_cost and quantity cannot be less than'
                                                                  ' or equals to 0'})
            if purchase_order_detail['discount_rate'] > 100:
                raise serializers.ValidationError(
                    {f'item {purchase_order_detail["item"].name}': 'Discount rate can not be greater than 100.'})

            # validation for gross_amount
            gross_amount = purchase_order_detail['purchase_cost'] * purchase_order_detail['qty']
            gross_amount = gross_amount.quantize(quantize_places)
            if gross_amount != purchase_order_detail['gross_amount']:
                raise serializers.ValidationError(
                    {
                        f'item {purchase_order_detail["item"].name}': f'gross_amount calculation not valid, should be {gross_amount}'})
            sub_total = sub_total + gross_amount

            # validation for discount amount
            if purchase_order_detail['discountable'] is True:
                total_discountable_amount = total_discountable_amount + purchase_order_detail['gross_amount']
                discount_rate = (purchase_order_detail['discount_amount'] *
                                 Decimal('100')) / (purchase_order_detail['purchase_cost'] *
                                                    purchase_order_detail['qty'])
                discount_rate = discount_rate.quantize(quantize_places)
                if discount_rate != purchase_order_detail['discount_rate']:
                    raise serializers.ValidationError(
                        {
                            f'item {purchase_order_detail["item"].name}': f'discount_rate calculation not valid : should be {discount_rate}'})
                total_discount = total_discount + purchase_order_detail['discount_amount']
            elif purchase_order_detail['discountable'] is False and purchase_order_detail['discount_amount'] > 0:
                raise serializers.ValidationError({f'item {purchase_order_detail["item"].name}':
                                                       f'discount_amount {purchase_order_detail["discount_amount"]} can not be '
                                                       f'given to item with discountable = False'})


            # validation for tax amount
            probable_taxable_amount = gross_amount - purchase_order_detail['discount_amount']
            if purchase_order_detail['taxable'] is True:
                total_taxable_amount = total_taxable_amount + probable_taxable_amount
                tax_amount = purchase_order_detail['tax_rate'] * probable_taxable_amount / Decimal('100')
                tax_amount = tax_amount.quantize(quantize_places)
                if tax_amount != purchase_order_detail['tax_amount']:
                    raise serializers.ValidationError({f'item {purchase_order_detail["item"].name}':
                                                           f'tax_amount calculation not valid : should be {tax_amount}'})
                total_tax = total_tax + tax_amount
            elif purchase_order_detail['taxable'] is False:
                total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

            # validation for net_amount
            net_amount = (gross_amount - ((
                                           purchase_order_detail['discount_amount']) )) + \
                         ((gross_amount - (
                                           purchase_order_detail['discount_amount'])) *
                          purchase_order_detail['tax_rate'] / Decimal('100'))
            
            net_amount = net_amount.quantize(quantize_places)
            if net_amount != purchase_order_detail['net_amount']:
                raise serializers.ValidationError(
                    {
                        f'item {purchase_order_detail["item"].name}': f'net_amount calculation not valid : should be {net_amount}'})
            grand_total = grand_total + net_amount

        # validation for total_discountable_amount
        if total_discountable_amount != data['total_discountable_amount']:
            raise serializers.ValidationError(
                {'total_discountable_amount':
                     f'total_discountable_amount calculation {data["total_discountable_amount"]} not valid: should be {total_discountable_amount}'}
            )

        # validation for discount rate
        # calculated_total_discount_amount = (data['total_discountable_amount'] * data['discount_rate']) / Decimal(
        #     '100.00')
        # calculated_total_discount_amount = calculated_total_discount_amount.quantize(quantize_places)
        # if calculated_total_discount_amount != data['total_discount']:
        #     raise serializers.ValidationError(
        #         'total_discount got {} not valid: expected {}'.format(data['total_discount'],
        #                                                               calculated_total_discount_amount)
        #     )

        # validation for total_taxable_amount
        if total_taxable_amount != data['total_taxable_amount']:
            raise serializers.ValidationError(
                'total_taxable_amount calculation {} not valid: should be {}'.format(data['total_taxable_amount'],
                                                                                     total_taxable_amount)
            )

        # validation for total_nontaxable_amount
        if total_nontaxable_amount != data['total_non_taxable_amount']:
            raise serializers.ValidationError(
                'total_non_taxable_amount calculation {} not valid: should be {}'.format(
                    data['total_non_taxable_amount'],
                    total_nontaxable_amount)
            )

        # check subtotal , total discount , total tax and grand total
        if sub_total != data['sub_total']:
            raise serializers.ValidationError(
                'sub_total calculation not valid: should be {}'.format(sub_total)
            )
        
        # validation for total_discount 
        if total_discount != data['total_discount']:
            raise serializers.ValidationError(
                'total_discount calculation {} not valid: should be {}'.format(data['total_discount'], total_discount)
            )

        # validation for total_tax
        if total_tax != data['total_tax']:
            raise serializers.ValidationError(
                'total_tax calculation {} not valid: should be {}'.format(data['total_tax'], total_tax)
            )

        # validation for grand_total
        if grand_total != data['grand_total']:
            raise serializers.ValidationError(
                'grand_total calculation {} not valid: should be {}'.format(data['grand_total'], grand_total)
            )

        
        return data


class PurchaseAdditionalChargeSerializer(serializers.ModelSerializer):
    charge_type_name = serializers.ReadOnlyField(source='charge_type.name')
    class Meta:
        model = PurchaseAdditionalCharge
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

# purchase master serializer for read_only views
class PurchaseMasterSerializer(serializers.ModelSerializer):
    additional_charges = PurchaseAdditionalChargeSerializer(many=True)
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


# purchase detail serializer for read_only views
class PurchaseDetailSerializer(serializers.ModelSerializer):
    purchase_no = serializers.ReadOnlyField(source='purchase.purchase_no')
    item_name = serializers.ReadOnlyField(source='item.name')
    unit_name = serializers.ReadOnlyField(source='item.unit.name')
    unit_short_form = serializers.ReadOnlyField(source='item.unit.short_form')
    item_category_name = serializers.ReadOnlyField(source='item_category.name')
    packing_type_name = serializers.ReadOnlyField(source="packing_type.name", allow_null=True)
    supplier_first_name = serializers.ReadOnlyField(source='purchase.supplier.first_name', allow_null=True)
    supplier_last_name = serializers.ReadOnlyField(source='purchase.supplier.last_name', allow_null=True)
    supplier = serializers.ReadOnlyField(source='purchase.supplier.id', allow_null=True)


    class Meta:
        model = PurchaseDetail
        fields = "__all__"


class PurchasePaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name')

    class Meta:
        model = PurchasePaymentDetail
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']



# payment detail serializer of write only views
class SavePaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasePaymentDetail
        exclude = ['purchase_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# purchase additional charge serializer of write only views
class SavePurchaseAdditionalChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseAdditionalCharge
        exclude = ['purchase_master']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# purchase detail serializer for write_only views
class SavePurchaseDetailSerializer(serializers.ModelSerializer):
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


# nested serializer for purchase master with purchase detail, payment detail and
# additional charges for write_only views
class SavePurchaseMasterSerializer(serializers.ModelSerializer):
    purchase_details = SavePurchaseDetailSerializer(many=True)
    payment_details = SavePaymentDetailSerializer(many=True)
    additional_charges = SavePurchaseAdditionalChargeSerializer(many=True)
    unit_name =  serializers.ReadOnlyField(source='item.unit.name', allow_null=True)
    unit_short_form = serializers.ReadOnlyField(source='item.unit.short_form', allow_null=True)
    supplier_first_name = serializers.ReadOnlyField(source='supplier.first_name')
    supplier_last_name = serializers.ReadOnlyField(source='supplier.last_name')
    code_name = serializers.ReadOnlyField(source='item.code')
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')

    class Meta:
        model = PurchaseMaster
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs','fiscal_session_ad','fiscal_session_bs']

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

    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        # print(validated_data)

        date_now = timezone.now()
        purchase_details = validated_data.pop('purchase_details')
        payment_details = validated_data.pop('payment_details')
        additional_charges = validated_data.pop('additional_charges')

        # set fiscal year for purchase master
        # get current fiscal year and compare it to FiscalSessionAD and FiscalSessionBS
        current_fiscal_session_short_ad = get_fiscal_year_code_ad()
        current_fiscal_session_short_bs = get_fiscal_year_code_bs()
        try:
            fiscal_session_ad = FiscalSessionAD.objects.get(session_short=current_fiscal_session_short_ad)
            fiscal_session_bs = FiscalSessionBS.objects.get(session_short=current_fiscal_session_short_bs)         
        except:
            raise serializers.ValidationError("fiscal session does not match")
        
        purchase_master = PurchaseMaster.objects.create(**validated_data, created_date_ad=date_now,
         fiscal_session_ad=fiscal_session_ad, fiscal_session_bs=fiscal_session_bs)

            
        for purchase_detail in purchase_details:
            PurchaseDetail.objects.create(**purchase_detail, purchase=purchase_master,
                                          created_by=validated_data['created_by'], created_date_ad=date_now)
        for payment_detail in payment_details:
            PurchasePaymentDetail.objects.create(**payment_detail, purchase_master=purchase_master,
                                                 created_by=validated_data['created_by'], created_date_ad=date_now)

        for additional_charge in additional_charges:
            PurchaseAdditionalCharge.objects.create(**additional_charge, purchase_master=purchase_master,
                                                    created_by=validated_data['created_by'], created_date_ad=date_now)
        return purchase_master

    def validate(self, data):
        quantize_places = Decimal(10) ** -2
        # initialize variables to check
        sub_total = Decimal('0.00')
        total_discount = Decimal('0.00')
        total_discountable_amount = Decimal('0.00')
        total_taxable_amount = Decimal('0.00')
        total_nontaxable_amount = Decimal('0.00')
        total_tax = Decimal('0.00')
        net_amount = Decimal('0.00')
        grand_total = Decimal('0.00')
        purchase_details = data['purchase_details']
        print("purchase_details_object :",purchase_details )

        for purchase in purchase_details:
            # purchase_order_detail = {}
            
            purchase_detail = {}
            key_values = zip(purchase.keys(), purchase.values())
            # key_values_order = zip(purchase_order.keys(), purchase_order.values())
            for key, values in key_values:
                purchase_detail[key] = values

            # if "ref_purchase" in purchase_master:
            #     if purchase_master['ref_purchase'] is not None:
            #         ref_pay_type = purchase_master['ref_purchase'].pay_type

         
    
            # validation for amount values less than or equal to 0 "Zero"
            if purchase_detail['tax_rate'] < 0 or purchase_detail['discount_rate'] < 0 or \
                    purchase_detail['sale_cost'] < 0:
                raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
                                                            ' cannot be less than 0'})

            if purchase_detail['purchase_cost'] <= 0 or purchase_detail['qty'] <= 0:
                raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, purchase_cost and quantity cannot be less than'
                                                            ' or equals to 0'})
            if purchase_detail['discount_rate'] > 100:
                raise serializers.ValidationError(
                    {f'item {purchase_detail["item"].name}': 'Discount rate can not be greater than 100.'})

            # validation for gross_amount
            gross_amount = purchase_detail['purchase_cost'] * purchase_detail['qty']
            gross_amount = gross_amount.quantize(quantize_places)
            if gross_amount != purchase_detail['gross_amount']:
                raise serializers.ValidationError(
                    {
                        f'item {purchase_detail["item"].name}': f'gross_amount calculation not valid : should be {gross_amount}'})
            if purchase_detail['free_purchase'] is False:
                sub_total = sub_total + gross_amount

                # validation for discount amount
            if purchase_detail['discountable'] is True and purchase_detail['free_purchase'] is False:
                total_discountable_amount = total_discountable_amount + purchase_detail['gross_amount']
                discount_rate = (purchase_detail['discount_amount'] *
                                 Decimal('100')) / (purchase_detail['purchase_cost'] *
                                                    purchase_detail['qty'])
                discount_rate = discount_rate.quantize(quantize_places)
                # if discount_rate != purchase_detail['discount_rate']:
                #     raise serializers.ValidationError(
                #         {
                #             f'item {purchase_detail["item"].name}': f'discount_rate calculation not valid : should be {discount_rate}'})
                total_discount = total_discount + purchase_detail['discount_amount']
            elif purchase_detail['discountable'] is False and purchase_detail['discount_amount'] > 0:
                raise serializers.ValidationError({f'item {purchase_detail["item"].name}':
                                                       f'discount_amount {purchase_detail["discount_amount"]} can not be '
                                                       f'given to item with discountable = False'})


            # validation for tax amount
            probable_taxable_amount = gross_amount - purchase_detail['discount_amount']
            if purchase_detail['taxable'] is True and purchase_detail['free_purchase'] is False:
                total_taxable_amount = total_taxable_amount + probable_taxable_amount
                tax_amount = purchase_detail['tax_rate'] * probable_taxable_amount / Decimal('100')
                tax_amount = tax_amount.quantize(quantize_places)
                if tax_amount != purchase_detail['tax_amount']:
                    raise serializers.ValidationError(
                        {f'item {purchase_detail["item"].name}':f'tax_amount calculation not valid : should be {tax_amount}'})
                total_tax = total_tax + tax_amount
            elif purchase_detail['taxable'] is False and purchase_detail['free_purchase'] is False:
                total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

            # validation for net_amount
            net_amount = (gross_amount - ((
                                           purchase_detail['discount_amount']) )) + \
                         ((gross_amount - (
                                           purchase_detail['discount_amount'])) *
                          purchase_detail['tax_rate'] / Decimal('100'))
                          
            net_amount = net_amount.quantize(quantize_places)
            if net_amount != purchase_detail['net_amount']:
                raise serializers.ValidationError({f'item {purchase_detail["item"].name}':
                    'net_amount calculation not valid : should be {}'.format(net_amount)})
            if purchase_detail['free_purchase'] is False:
                grand_total = grand_total + net_amount

        # validation for purchase in CREDIT with no supplier
        if data['pay_type'] == 2 and data['supplier'] == '':
            raise serializers.ValidationError('Cannot perform purchase in CREDIT with no supplier')

        # calculating additional charge
        try:
            data['additional_charges']
        except KeyError:
            raise serializers.ValidationError(
                {'additional_charges': 'Provide additional_charge key'}
            )
        additional_charges = data['additional_charges']
        add_charge = Decimal('0.00')
        for additional_charge in additional_charges:
            add_charge = add_charge + additional_charge['amount']

        # validation for total_discountable_amount
        if total_discountable_amount != data['total_discountable_amount']:
            raise serializers.ValidationError(
                'total_discountable_amount calculation {} not valid: should be {}'.format(
                    data['total_discountable_amount'], total_discountable_amount)
            )

        # validation for discount rate
        # calculated_total_discount_amount = (data['total_discountable_amount'] * data['discount_rate']) / Decimal(
        #     '100.00')
        # calculated_total_discount_amount = calculated_total_discount_amount.quantize(quantize_places)
        # if calculated_total_discount_amount != data['total_discount']:
        #     raise serializers.ValidationError(
        #         'total_discount got {} not valid: expected {}'.format(data['total_discount'],
        #                                                               calculated_total_discount_amount)
        #     )

        # validation for total_taxable_amount
        if total_taxable_amount != data['total_taxable_amount']:
            raise serializers.ValidationError(
                'total_taxable_amount calculation {} not valid: should be {}'.format(data['total_taxable_amount'],
                                                                                     total_taxable_amount)
            )

        # validation for total_nontaxable_amount
        if total_nontaxable_amount != data['total_non_taxable_amount']:
            raise serializers.ValidationError(
                'total_non_taxable_amount calculation {} not valid: should be {}'.format(
                    data['total_non_taxable_amount'],
                    total_nontaxable_amount)
            )

        # check subtotal , total discount , total tax and grand total
        if sub_total != data['sub_total']:
            raise serializers.ValidationError(
                'sub_total calculation not valid: should be {}'.format(sub_total)
            )

        if total_discount != data['total_discount']:
            raise serializers.ValidationError(
                'total_discount calculation {} not valid: should be {}'.format(data['total_discount'],
                                                                               total_discount)
            )
        if total_tax != data['total_tax']:
            raise serializers.ValidationError(
                'total_tax calculation {} not valid: should be {}'.format(data['total_tax'], total_tax)
            )

        grand_total = grand_total + add_charge

            #check where is there  oranizaiantion rule or not
        try:
                organization_rule = OrganizationRule.objects.first()
        except:
            raise ValueError("Object not found, Create Organization Rule")

        if organization_rule.round_off_purchase is True:
            grand_total = grand_total.quantize(Decimal("0")); 
            if grand_total != data['grand_total']:
                raise serializers.ValidationError(
                    'grand_total calculation {} not valid: should be {}'.format(data['grand_total'], grand_total)
                )

        # validation of payment details
        try:
            data['payment_details']
        except KeyError:
            raise serializers.ValidationError(
                {'payment_details': 'Provide payment details'}
            )
        try:
            data['pay_type']
        except KeyError:
            raise serializers.ValidationError(
                {'pay_type': 'please provide pay_type key'}
            )
        payment_details = data['payment_details']
        total_payment = Decimal('0.00')

        for payment_detail in payment_details:
            total_payment = total_payment + payment_detail['amount']
        if data['pay_type'] == 1:
            if total_payment != data['grand_total']:
                raise serializers.ValidationError(
                    {'amount': 'sum of amount {} should be equal to grand_total {} in pay_type CASH'.format(
                        total_payment, data['grand_total'])}
                )
        elif data['pay_type'] == 2 or data['pay_type'] == 3:
            if total_payment > data['grand_total']:
                raise serializers.ValidationError(
                    {
                        'amount': 'Cannot process purchase CREDIT with total paid amount greater than {}'.format(
                            data['grand_total'])}
                )
        return data


"""************************** Serializers for Get Views *****************************************"""
class GetPackingTypeDetailSerializer(serializers.ModelSerializer):
    packing_type_name =serializers.ReadOnlyField(source='packing_type.name', allow_null=True)
    class Meta:
        model = PackingTypeDetail
        exclude = ['created_date_ad','created_date_bs','active','created_by','item']
        


class GetSupplierSerializer(serializers.ModelSerializer):
    # country_name =serializers.ReadOnlyField(source='country.name', allow_null=True)
    class Meta:
        model = Supplier
        exclude = ['created_date_ad','created_date_bs','created_by','active','tax_reg_system','pan_vat_no','image']


class GetItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        exclude = ['created_date_ad','created_date_bs','created_by','active','display_order']


class GetDiscountSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountScheme
        exclude = ['created_date_ad','created_date_bs','created_by','active']


class GetAdditionalChargeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalChargeType
        exclude = ['created_date_ad','created_date_bs','created_by','active'] 


class GetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        exclude = ['created_date_ad','created_date_bs','created_by','active','location',
        'stock_alert_qty','basic_info','image']     


class GetPaymentModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        exclude = ['created_date_ad','created_date_bs','created_by','active','remarks']   



      
      
  