# importing of function
from src.custom_lib.functions import current_user
from rest_framework import serializers
from src.party_payment.models import BasicPartyPayment, BasicPartyPaymentDetail, PartyPayment,PartyPaymentDetail
from src.custom_lib.functions.current_user import get_created_by
from src.purchase.models import PurchaseMaster
from django.utils import timezone
from src.custom_lib.functions import current_user
from django.utils import timezone
from src.custom_lib.functions.current_user import get_created_by
from rest_framework.response import Response
from rest_framework import serializers,  status
from src.custom_lib.functions.fiscal_year import get_fiscal_year_code_ad, get_fiscal_year_code_bs
from src.core_app.models import FiscalSessionAD, FiscalSessionBS


class PartyPaymentMasterSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    payment_type_display= serializers.ReadOnlyField(source='get_payment_type_display', allow_null=True)
    purchase_no = serializers.ReadOnlyField(source='purchase_master.purchase_no', allow_null=True)
    # purchase_master =
    class Meta:
        model = PartyPayment
        fields = "__all__"


class PartyPaymentDetailSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    # party_clearance_aa = serializers.ReadOnlyField(source='party_clearance.receipt_no')
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)
    # sale_master = serializers.ReadOnlyField(source='credit_clearance_master.creditclearancedetail.sale_master.id',
    #                                         allow_null=True)

    class Meta:
        model = PartyPaymentDetail
        fields = '__all__'
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')


"""_________________________________save credit payment details_________________________________________________"""


class SavePartyPaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name')

    class Meta:
        model = PartyPaymentDetail
        exclude = ['party_payment']
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')


class SavePartyPaymentSerializer(serializers.ModelSerializer):
    party_payment_details = SavePartyPaymentDetailSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    purchase_no = serializers.ReadOnlyField(source='purchase_master.purchase_no', allow_null=True)
    payment_type_display = serializers.ReadOnlyField(source='get_payment_type_display', allow_null=True)
    class Meta:
        model = PartyPayment
        fields = "__all__"
        read_only_fields = ( 'created_date_ad', 'created_date_bs', 'created_by')


    def create(self, validated_data):
        date_now = timezone.now()
        party_payment_details = validated_data.pop('party_payment_details')

        validated_data['created_by'] = get_created_by(self.context)

        party_clearance = PartyPayment.objects.create(**validated_data, created_date_ad=date_now)
        for party_payment_detail in party_payment_details:
            PartyPaymentDetail.objects.create(**party_payment_detail, party_clearance=party_clearance,
                                              created_by=validated_data['created_by'], created_date_ad=date_now)

        return party_clearance


"""_______________________ serializer for Credit Sale Report _______________________________________________"""


class PurchaseCreditSerializer(serializers.ModelSerializer):
    purchase_id = serializers.ReadOnlyField(source='id')
    purchase_number = serializers.ReadOnlyField(source='purchase_no', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    supplier_first_name = serializers.ReadOnlyField(source='supplier.first_name', allow_null=True)
    supplier_last_name = serializers.ReadOnlyField(source='supplier.last_name', allow_null=True)
    total_amount = serializers.ReadOnlyField(source='grand_total')
    paid_amount = serializers.SerializerMethodField()
    due_amount = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseMaster
        fields = ['purchase_id','purchase_number', 'supplier_first_name', 'supplier_last_name','created_by_user_name','customer_first_name', 'customer_middle_name',
                  'customer_last_name', 'total_amount',
                  'paid_amount', 'due_amount', 'purchase_no', 'supplier', 'created_date_ad', 'created_date_bs',
                  'created_by', 'remarks']

    def get_paid_amount(self, instance):
        paid_amount = sum(PartyPayment.objects.filter(purchase_master=instance.id)
                          .values_list('total_amount', flat=True))
        return paid_amount

    def get_due_amount(self, instance):
        paid_amount = self.get_paid_amount(instance)
        due_amount = instance.grand_total - paid_amount
        return due_amount


class BasicPartyPaymentDetailSerializer(serializers.ModelSerializer):
    supplier_name = serializers.ReadOnlyField(source='basic_party_payment.supplier.first_name')
    supplier_id = serializers.ReadOnlyField(source='basic_party_payment.supplier.id')
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name')
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    payment_date_ad = serializers.ReadOnlyField(source='basic_party_payment.payment_date_ad', allow_null=True)
    payment_date_bs = serializers.ReadOnlyField(source='basic_party_payment.payment_date_bs', allow_null=True)
    recipt_no = serializers.ReadOnlyField(source='basic_party_payment.receipt_no', allow_null=True)
    class Meta:
        model = BasicPartyPaymentDetail
        fields = "__all__"
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')

        
class SaveBasicPartyPaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name')
    class Meta:
        model = BasicPartyPaymentDetail
        exclude = ['basic_party_payment']
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')

class SaveBasicPartyPaymentSerializer(serializers.ModelSerializer):
    basic_party_payment_details = SaveBasicPartyPaymentDetailSerializer(many=True)
    payment_type_display = serializers.ReadOnlyField(source='get_payment_type_display', allow_null=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.first_name')
    class Meta:
        model = BasicPartyPayment
        fields = "__all__"
        read_only_fields = ('fiscal_session_ad','fiscal_session_bs','created_date_ad', 'created_date_bs', 'created_by')

    def create(self, validated_data):
        date_now = timezone.now()
        basic_party_payment_details = validated_data.pop('basic_party_payment_details')
        validated_data['created_by'] = get_created_by(self.context)

        current_fiscal_session_short_ad = get_fiscal_year_code_ad()
        current_fiscal_session_short_bs = get_fiscal_year_code_bs()
        try:
            fiscal_session_ad = FiscalSessionAD.objects.get(session_short=current_fiscal_session_short_ad)
            fiscal_session_bs = FiscalSessionBS.objects.get(session_short=current_fiscal_session_short_bs)         
        except:
            raise serializers.ValidationError("fiscal session does not match")

        basic_party_payment = BasicPartyPayment.objects.create(**validated_data, created_date_ad=date_now,
         fiscal_session_ad= fiscal_session_ad, fiscal_session_bs= fiscal_session_bs)

        for basic_party_payment_detail in basic_party_payment_details:
            BasicPartyPaymentDetail.objects.create(**basic_party_payment_detail, basic_party_payment=basic_party_payment,
                                              created_by=validated_data['created_by'], created_date_ad=date_now)            
        return  basic_party_payment
