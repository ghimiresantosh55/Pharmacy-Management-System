from rest_framework import serializers
from src.party_payment.models import BasicPartyPayment, BasicPartyPaymentDetail
from src.financial_report.serializers import DetailBasicPartyPaymentDetailSerializer


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
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    basic_party_payment_supplier_first_name = serializers.ReadOnlyField(source='basic_party_payment.supplier.first_name', allow_null=True)
    basic_party_payment_supplier_middle_name = serializers.ReadOnlyField(source='basic_party_payment.supplier.middle_name', allow_null=True)
    basic_party_payment_supplier_last_name = serializers.ReadOnlyField(source='basic_party_payment.supplier.last_name', allow_null=True)
    
    class Meta:
        model = BasicPartyPaymentDetail
        fields = "__all__"



class SummaryBasicPartyPaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
   

    class Meta:
        model = BasicPartyPaymentDetail
        exclude = ['basic_party_payment']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class DetailBasicPartyPaymentSerializer(serializers.ModelSerializer):
    payment_type = serializers.ReadOnlyField(source="")
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