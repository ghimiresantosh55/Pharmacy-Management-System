from django.db import models
from rest_framework import fields, serializers
# importing of models 
from .models import FiscalSessionBS, FiscalSessionAD,OrganizationRule, OrganizationSetup, Country, Province, District, AppAccessLog
from .models import Bank, BankDeposit, PaymentMode, DiscountScheme, AdditionalChargeType, Store
from src.item.models import Item

# importing of function
from src.custom_lib.functions import current_user
from src.custom_lib.functions.fiscal_year import  get_fiscal_year_code_bs
from src.custom_lib.functions.fiscal_year import  get_fiscal_year_code_ad
from src.custom_lib.functions.fiscal_year import  get_full_fiscal_year_code_ad
from src.custom_lib.functions.fiscal_year import get_full_fiscal_year_code_bs
bs_year_code = get_fiscal_year_code_bs()
ad_year_code = get_fiscal_year_code_ad()
full_ad_year_code = get_full_fiscal_year_code_ad()
full_bs_year_code = get_full_fiscal_year_code_bs()
from django.utils import timezone


class CountrySerializer(serializers.ModelSerializer):
    # serializers.ReadOnlyField is only used for displaying the data with the help of FK. It is uneditable (only readable). 
    # allow_null=True means if no data then null value is passed.
    created_by_first_name =serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name =serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name =serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name =serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)

    class Meta:
        model = Country
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by'] 

    def create(self, validated_data):
        # provide current time
        date_now = timezone.now()
        # providing the id of current login user
        validated_data['created_by'] = current_user.get_created_by(self.context)
        # after getting all validated data, it is posted in DB
        country = Country.objects.create(**validated_data, created_date_ad=date_now)
        return country


class ProvinceSerializer(serializers.ModelSerializer):
    created_by_first_name =serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name =serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name =serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name =serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)

    class Meta:
        model = Province
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']
    
    def create(self, validated_data):
        # provide current time
        date_now = timezone.now()
        # providing the id of current login user
        validated_data['created_by'] = current_user.get_created_by(self.context)
        # after getting all validated data, it is posted in DB
        province = Province.objects.create(**validated_data, created_date_ad=date_now)
        return province


class DistrictSerializer(serializers.ModelSerializer):
    created_by_first_name =serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name =serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name =serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name =serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)
    province_name = serializers.ReadOnlyField(source='province.name',allow_null=True)

    class Meta:
        model = District
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']
    
    def create(self, validated_data):
        # provide current time
        date_now = timezone.now()
        # providing the id of current login user
        validated_data['created_by'] = current_user.get_created_by(self.context)
        # after getting all validated data, it is posted in DB
        district = District.objects.create(**validated_data, created_date_ad=date_now)
        return district


class OrganizationRuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationRule
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


    def to_representation(self, instance):
        my_fields = {'phone_no_1', 'mobile_no','pan_no','owner_name','email','website_url'}
                     
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data

    def create(self, validated_data):
        # provide current time
        date_now = timezone.now()
        # providing the id of current login user
        validated_data['created_by'] = current_user.get_created_by(self.context)
        # after getting all validated data, it is posted in DB
        organization_rule = OrganizationRule.objects.create(**validated_data, created_date_ad=date_now)
        return organization_rule


class OrganizationSetupSerializer(serializers.ModelSerializer):
    country_name = serializers.ReadOnlyField(source='country.name',allow_null=True)

    class Meta:
        model = OrganizationSetup
        fields = "__all__"
        # read_only_fields are the fields from same model. Fields mentioned here can't be editable.
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        organization_setup = OrganizationSetup.objects.create(**validated_data, created_date_ad=date_now)
        return organization_setup


class BankSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bank
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        # provide current time
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        bank = Bank.objects.create(**validated_data, created_date_ad=date_now)
        return bank


class BankDepositSerializer(serializers.ModelSerializer):
    bank_name = serializers.ReadOnlyField(source='bank.name', allow_null=True)

    class Meta:
        model = BankDeposit
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        bank_deposit = BankDeposit.objects.create(**validated_data, created_date_ad=date_now)
        return bank_deposit


class PaymentModeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentMode
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        payment_mode = PaymentMode.objects.create(**validated_data, created_date_ad=date_now)
        return payment_mode


class DiscountSchemeSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiscountScheme
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        discount_scheme = DiscountScheme.objects.create(**validated_data, created_date_ad=date_now)
        return discount_scheme


class AdditionalChargeTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdditionalChargeType
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        charge_type = AdditionalChargeType.objects.create(**validated_data, created_date_ad=date_now)
        return charge_type


class AppAccessLogSerializer(serializers.ModelSerializer):
    created_by_first_name =serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name =serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name =serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name =serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)
    device_type_display= serializers.ReadOnlyField(source="get_device_type_display", allow_null=True)
    app_type_display = serializers.ReadOnlyField(source="get_app_type_display", allow_null=True)

    class Meta:
        model = AppAccessLog
        fields = "__all__"
       

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        if validated_data['code'] == "":
            store_count = Store.objects.count()
            max_id = str(store_count + 1)
            unique_id = "ST-" + max_id.zfill(4)
            validated_data['code'] = unique_id
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        store = Store.objects.create(**validated_data, created_date_ad=date_now)
        return store


class FiscalSessionADSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalSessionAD
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        if validated_data['session_short'] == "":
            unique_id = ad_year_code
            validated_data['session_short'] = unique_id

        if validated_data['session_full'] == "":
            unique_id = full_ad_year_code
            validated_data['session_full'] = unique_id
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        fiscal_session_ad = FiscalSessionAD.objects.create(**validated_data, created_date_ad=date_now)
        return  fiscal_session_ad
   

class FiscalSessionBSSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalSessionBS
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        if validated_data['session_short'] == "":
            unique_id = bs_year_code
            validated_data['session_short'] = unique_id
        if validated_data['session_full'] =="":
            unique_id = full_bs_year_code
            validated_data['session_full'] = unique_id
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        fiscal_session_bs = FiscalSessionBS.objects.create(**validated_data, created_date_ad=date_now)
        return  fiscal_session_bs