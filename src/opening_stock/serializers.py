from django.db import models
from rest_framework import fields, serializers
from decimal import Decimal
from django.utils import timezone

# custom models
from src.purchase.models import PurchaseMaster, PurchaseDetail
from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_ad, get_fiscal_year_code_bs
from src.core_app.models import  FiscalSessionAD, FiscalSessionBS

# custom lib
from src.custom_lib.functions.validators import purchase_opening_stock_qty_patch_validator
from src.custom_lib.functions import current_user


class OpeningStockSerializer(serializers.ModelSerializer):
    pay_type_display = serializers.ReadOnlyField(source='get_pay_type_display', allow_null=True)
    purchase_type_display = serializers.ReadOnlyField(source='get_purchase_type_display', allow_null=True)
    supplier_first_name = serializers.ReadOnlyField(source='supplier.first_name', allow_null=True)
    discount_scheme_name = serializers.ReadOnlyField(source='discount_scheme.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    created_by_first_name = serializers.ReadOnlyField(source='created_by.first_name', allow_null=True)
    
    class Meta:
        model = PurchaseMaster
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class OpeningStockDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    packing_type_name = serializers.ReadOnlyField(source='packing_type.name', allow_null=True)
    class Meta:
        model = PurchaseDetail
        fields = "__all__"
        
class OpeningStockSummarySerializer(serializers.ModelSerializer):
    purchase_details = OpeningStockDetailSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    class Meta:
        model = PurchaseMaster
        fields = "__all__"


class SavePurchaseOpenigStockDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = PurchaseDetail
        exclude = ['purchase']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

class SaveOpeningStockSerializer(serializers.ModelSerializer):
    purchase_details = SavePurchaseOpenigStockDetailSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    class Meta:
        model = PurchaseMaster
        fields = "__all__"   
        read_only_fields = ['fiscal_session_ad','fiscal_session_bs','created_by', 'created_date_ad', 'created_date_bs']
    
    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        date_now = timezone.now()
        purchase_details = validated_data.pop('purchase_details')
        #validation if data is not send
        if not purchase_details:
            raise serializers.ValidationError("Please provide value") 

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
        fiscal_session_ad= fiscal_session_ad, fiscal_session_bs= fiscal_session_bs)
        for purchase_detail in purchase_details:
            PurchaseDetail.objects.create(**purchase_detail, purchase=purchase_master,
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
        grand_total = Decimal('0.00')
        purchase_details = data['purchase_details']
        for purchase in purchase_details:
            purchase_detail = {}
            key_values = zip(purchase.keys(), purchase.values())
            for key, values in key_values:
                purchase_detail[key] = values
            # validation for amount values less than or equal to 0 "Zero"
            if purchase_detail['tax_rate'] < 0 or purchase_detail['discount_rate'] < 0 or \
                    purchase_detail['sale_cost'] < 0:
                raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
                                                            ' cannot be less than 0'})

            if purchase_detail['purchase_cost'] < 0:
                 raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, purchase_cost cannot be less than 0'})
            if purchase_detail['qty'] <= 0:
                raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, quantity cannot be less than'
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
            sub_total = sub_total + gross_amount

            # validation for discount amount
            if purchase_detail['discountable'] is True:
                total_discountable_amount = total_discountable_amount + purchase_detail['gross_amount']
                discount_rate = (purchase_detail['discount_amount'] *
                                 Decimal('100')) / (purchase_detail['purchase_cost'] *
                                                    purchase_detail['qty'])
                discount_rate = discount_rate.quantize(quantize_places)
                if discount_rate != purchase_detail['discount_rate']:
                    raise serializers.ValidationError(
                        {
                            f'item {purchase_detail["item"].name}': f'discount_rate calculation not valid : should be {discount_rate}'})
                total_discount = total_discount + purchase_detail['discount_amount']
            elif purchase_detail['discountable'] is False and purchase_detail['discount_amount'] > 0:
                raise serializers.ValidationError({f'item {purchase_detail["item"].name}':
                                                       f'discount_amount {purchase_detail["discount_amount"]} can not be '
                                                       f'given to item with discountable = False'})

            # validation for tax amount
            probable_taxable_amount = gross_amount - purchase_detail['discount_amount']
            if purchase_detail['taxable'] is True:
                total_taxable_amount = total_taxable_amount + probable_taxable_amount
                tax_amount = purchase_detail['tax_rate'] * probable_taxable_amount / Decimal('100')
                tax_amount = tax_amount.quantize(quantize_places)
                if tax_amount != purchase_detail['tax_amount']:
                    raise serializers.ValidationError(
                        {f'item {purchase_detail["item"].name}':f'tax_amount calculation not valid : should be {tax_amount}'})
                total_tax = total_tax + tax_amount
            elif purchase_detail['taxable'] is False:
                total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

            # validation for net_amount
            net_amount = (gross_amount - ((purchase_detail['purchase_cost'] *
                                           purchase_detail['qty'] *
                                           purchase_detail['discount_rate']) / Decimal('100'))) + \
                         ((gross_amount - (purchase_detail['purchase_cost'] *
                                           purchase_detail['qty'] *
                                           purchase_detail['discount_rate']) / Decimal('100')) *
                          purchase_detail['tax_rate'] / Decimal('100'))
            net_amount = net_amount.quantize(quantize_places)
            if net_amount != purchase_detail['net_amount']:
                raise serializers.ValidationError({f'item {purchase_detail["item"].name}':
                    'net_amount calculation not valid : should be {}'.format(net_amount)})
            grand_total = grand_total + net_amount

        # validation for purchase in CREDIT with no supplier
        if data['pay_type'] == 2 and data['supplier'] == '':
            raise serializers.ValidationError('Cannot perform purchase in CREDIT with no supplier')


        # validation for total_discountable_amount
        if total_discountable_amount != data['total_discountable_amount']:
            raise serializers.ValidationError(
                'total_discountable_amount calculation {} not valid: should be {}'.format(
                    data['total_discountable_amount'], total_discountable_amount)
            )

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

        # grand_total = grand_total + add_charge
        if grand_total != data['grand_total']:
            raise serializers.ValidationError(
                'grand_total calculation {} not valid: should be {}'.format(data['grand_total'], grand_total)
            )
        
        return data

class UpdateOpeningStockSerializer(serializers.ModelSerializer):
    purchase_details = SavePurchaseOpenigStockDetailSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    class Meta:
        model = PurchaseMaster
        fields = "__all__"   
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def update(self, instance, validated_data):
        purchase_details_data = validated_data.pop('purchase_details')

        purchase_details = (instance.purchase_details).all()
        purchase_details = list(purchase_details)

        # children data in purchase_details must be equal
        if len(purchase_details)!= len(purchase_details_data):
            raise serializers.ValidationError("To perform patch operation you must call all purcahse detail")

        instance.sub_total = validated_data.get('sub_total',instance.sub_total)
        instance.total_discount = validated_data.get('total_discount',instance.total_discount)
        instance.discount_rate = validated_data.get('discount_rate',instance.discount_rate)
        instance.discount_scheme = validated_data.get('discount_scheme',instance.discount_scheme)
        instance.total_discountable_amount = validated_data.get('total_discountable_amount',instance.total_discountable_amount)
        instance.total_taxable_amount = validated_data.get('total_taxable_amount',instance.total_taxable_amount)
        instance.total_non_taxable_amount = validated_data.get('total_non_taxable_amount',instance.total_non_taxable_amount)
        instance.total_tax = validated_data.get('total_tax',instance.total_tax)
        instance.grand_total = validated_data.get('grand_total',instance.grand_total)
        instance.remarks = validated_data.get('remarks',instance.remarks)
        
        for purchase_detail_data in purchase_details_data:
            purchase_detail = purchase_details.pop(0)
            # checking of quantity while performing patch operation
            purchase_opening_stock_qty_patch_validator(purchase_detail.id,purchase_detail_data['qty'])
            purchase_detail.id = purchase_detail_data.get('id',purchase_detail.id)
            purchase_detail.item = purchase_detail_data.get('item',purchase_detail.item)
            purchase_detail.item_category = purchase_detail_data.get('item_category',purchase_detail.item_category)
            purchase_detail.purchase_cost = purchase_detail_data.get('purchase_cost',purchase_detail.purchase_cost)
            purchase_detail.sale_cost = purchase_detail_data.get('sale_cost',purchase_detail.sale_cost)
            purchase_detail.qty = purchase_detail_data.get('qty',purchase_detail.qty)
            purchase_detail.taxable = purchase_detail_data.get('taxable',purchase_detail.taxable)
            purchase_detail.tax_rate = purchase_detail_data.get('tax_rate',purchase_detail.tax_rate)
            purchase_detail.tax_amount = purchase_detail_data.get('tax_amount',purchase_detail.tax_amount)
            purchase_detail.discountable = purchase_detail_data.get('discountable',purchase_detail.discountable)
            purchase_detail.expirable = purchase_detail_data.get('expirable',purchase_detail.expirable)
            purchase_detail.discount_rate = purchase_detail_data.get('discount_rate',purchase_detail.discount_rate)
            purchase_detail.discount_amount = purchase_detail_data.get('discount_amount',purchase_detail.discount_amount)
            purchase_detail.gross_amount = purchase_detail_data.get('gross_amount',purchase_detail.gross_amount)
            purchase_detail.net_amount = purchase_detail_data.get('net_amount',purchase_detail.net_amount)
            purchase_detail.expiry_date_ad = purchase_detail_data.get('expiry_date_ad',purchase_detail.expiry_date_ad)
            purchase_detail.expiry_date_bs = purchase_detail_data.get('expiry_date_bs',purchase_detail.expiry_date_bs)
            purchase_detail.batch_no = purchase_detail_data.get('batch_no',purchase_detail.batch_no)
            purchase_detail.save()
        
        instance.save()
        return instance

    def validate(self, data):
        # changing into decimal form with 2 digit after point 
        quantize_places = Decimal(10) ** -2
        # initialize variables to check
        sub_total = Decimal('0.00')
        total_discount = Decimal('0.00')
        total_discountable_amount = Decimal('0.00')
        total_taxable_amount = Decimal('0.00')
        total_nontaxable_amount = Decimal('0.00')
        total_tax = Decimal('0.00')
        grand_total = Decimal('0.00')
        purchase_details = data['purchase_details']
        for purchase in purchase_details:
            purchase_detail = {}
            key_values = zip(purchase.keys(), purchase.values())
            for key, values in key_values:
                purchase_detail[key] = values

            # tax_rate, discount and sale_cost cannot be less than  0 but can be 0
            if purchase_detail['tax_rate'] < 0 or purchase_detail['discount_rate'] < 0 or \
                    purchase_detail['sale_cost'] < 0:
                raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
                                                            ' cannot be less than 0'})
            
            # purchase cost can be 0 but cannot be less than 0
            if purchase_detail['purchase_cost'] < 0:
                 raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, purchase_cost cannot be less than 0'})

            # qty cannot be less than or is equal to 0. Must have atleast 1 qty.
            if purchase_detail['qty'] <= 0:
                raise serializers.ValidationError({
                    f'item {purchase_detail["item"].name}': 'values in fields, quantity cannot be less than'
                                                            ' or equals to 0'})
            
            # discount_rate cannot be greater than 100
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
            sub_total = sub_total + gross_amount

            # validation for discount amount
            if purchase_detail['discountable'] is True:
                total_discountable_amount = total_discountable_amount + purchase_detail['gross_amount']
                discount_rate = (purchase_detail['discount_amount'] *
                                 Decimal('100')) / (purchase_detail['purchase_cost'] *
                                                    purchase_detail['qty'])
                discount_rate = discount_rate.quantize(quantize_places)
                if discount_rate != purchase_detail['discount_rate']:
                    raise serializers.ValidationError(
                        {
                            f'item {purchase_detail["item"].name}': f'discount_rate calculation not valid : should be {discount_rate}'})
                total_discount = total_discount + purchase_detail['discount_amount']
            elif purchase_detail['discountable'] is False and purchase_detail['discount_amount'] > 0:
                raise serializers.ValidationError({f'item {purchase_detail["item"].name}':
                                                       f'discount_amount {purchase_detail["discount_amount"]} can not be '
                                                       f'given to item with discountable = False'})

            # validation for tax amount
            probable_taxable_amount = gross_amount - purchase_detail['discount_amount']
            if purchase_detail['taxable'] is True:
                total_taxable_amount = total_taxable_amount + probable_taxable_amount
                tax_amount = purchase_detail['tax_rate'] * probable_taxable_amount / Decimal('100')
                tax_amount = tax_amount.quantize(quantize_places)
                if tax_amount != purchase_detail['tax_amount']:
                    raise serializers.ValidationError(
                        {f'item {purchase_detail["item"].name}':f'tax_amount calculation not valid : should be {tax_amount}'})
                total_tax = total_tax + tax_amount
            elif purchase_detail['taxable'] is False:
                total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

            # validation for net_amount
            net_amount = (gross_amount - ((purchase_detail['purchase_cost'] *
                                           purchase_detail['qty'] *
                                           purchase_detail['discount_rate']) / Decimal('100'))) + \
                         ((gross_amount - (purchase_detail['purchase_cost'] *
                                           purchase_detail['qty'] *
                                           purchase_detail['discount_rate']) / Decimal('100')) *
                          purchase_detail['tax_rate'] / Decimal('100'))
            net_amount = net_amount.quantize(quantize_places)
            if net_amount != purchase_detail['net_amount']:
                raise serializers.ValidationError({f'item {purchase_detail["item"].name}':
                    'net_amount calculation not valid : should be {}'.format(net_amount)})
            grand_total = grand_total + net_amount

        # validation for total_discountable_amount
        if total_discountable_amount != data['total_discountable_amount']:
            raise serializers.ValidationError(
                'total_discountable_amount calculation {} not valid: should be {}'.format(
                    data['total_discountable_amount'], total_discountable_amount)
            )

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
        
        # validation of discount
        if total_discount != data['total_discount']:
            raise serializers.ValidationError(
                'total_discount calculation {} not valid: should be {}'.format(data['total_discount'],
                                                                               total_discount)
            )

        # validation of tax
        if total_tax != data['total_tax']:
            raise serializers.ValidationError(
                'total_tax calculation {} not valid: should be {}'.format(data['total_tax'], total_tax)
            )

        # grand_total = grand_total + add_charge
        if grand_total != data['grand_total']:
            raise serializers.ValidationError(
                'grand_total calculation {} not valid: should be {}'.format(data['grand_total'], grand_total)
            )
        
        # for validation of purchase_type 
        if data['purchase_type'] !=3:
            raise serializers.ValidationError('purcahse_type must be 3')
        
        return data

    
