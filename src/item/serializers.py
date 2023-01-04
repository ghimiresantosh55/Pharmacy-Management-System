from django.db import models
from django.db.models import fields
from rest_framework import serializers
# imported model here
from .models import Unit, Manufacturer, GenericName, ItemCategory, Item, PackingType, PackingTypeDetail
from src.custom_lib.functions import current_user
from django.utils import timezone


class PackingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model =  PackingType
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']
    
    def create(self, validated_data):
        date_now = timezone.now()
        print(date_now)
        validated_data['created_by'] = current_user.get_created_by(self.context)
        packing_type = PackingType.objects.create(**validated_data, created_date_ad=date_now)
        return  packing_type 

   
class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        unit = Unit.objects.create(**validated_data, created_date_ad=date_now)
        return unit


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']
        
    def create(self, validated_data):
        print(validated_data)
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        manufacturer = Manufacturer.objects.create(**validated_data, created_date_ad=date_now)
        return manufacturer


class GenericNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericName
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']
    
    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        generic_name = GenericName.objects.create(**validated_data, created_date_ad=date_now)
        return generic_name


class SaveItemPackingTypeDetailSerializer(serializers.ModelSerializer):
    packing_type_name = serializers.ReadOnlyField(source="packing_type.name", allow_null=True)
    class Meta:
        model = PackingTypeDetail
        exclude = ['item','packing_type','pack_qty','active']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class ItemSerializer(serializers.ModelSerializer):
    # packing_type_details =  SaveItemPackingTypeDetailSerializer(many=True)
    item_category_name = serializers.ReadOnlyField(source="item_category.name", allow_null=True)
    item_type_display = serializers.ReadOnlyField(source="get_item_type_display", allow_null=True)
    manufacturer_name = serializers.ReadOnlyField(source="manufacturer.name", allow_null=True)
    generic_name_name = serializers.ReadOnlyField(source="generic_name.name", allow_null=True)
    unit_name = serializers.ReadOnlyField(source="unit.name", allow_null=True)
    unit_short_form  =  serializers.ReadOnlyField(source="unit.short_form", allow_null=True)
     
    class Meta:
        model = Item
        fields = "__all__"
        read_only_fields = ['item_type_display', 'created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'item_category', 'unit_name','unit_short_form','image',
                     'item_category_name'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


    def create(self, validated_data):
        print(validated_data)
        if validated_data['code'] == "":
            item_count = Item.objects.count()
            max_id = str(item_count + 1)
            unique_id = "ITM-" + max_id.zfill(6)
            validated_data['code'] = unique_id
       
        date_now = timezone.now()
        # if validated_data['packing_type_details'] == [] or validated_data['packing_type_details'] is None:
        #     validated_data.pop('packing_type_details')
            # pack_qty= 1
            # active = True
        # validated_data['created_by'] = current_user.get_created_by(self.context)
        # packing_type = PackingType.objects.get(pk=1)
        pack_qty= 1
        active = True
        validated_data['created_by'] = current_user.get_created_by(self.context)
        
        item = Item.objects.create(**validated_data, created_date_ad=date_now)
        PackingTypeDetail.objects.create(item=item, pack_qty=pack_qty, packing_type_id=1, active = active, created_date_ad=date_now, created_by=current_user.get_created_by(self.context)).save()
        return item


class ItemCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ItemCategory
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


    def create(self, validated_data):
        # empty field for display order
        if validated_data['display_order'] == '':
            validated_data['display_order'] = None
        if validated_data['code'] == "" or validated_data['code'] is None:
            item_count = ItemCategory.objects.count()
            max_id = str(item_count + 1)
            unique_id = "ITC-" + max_id.zfill(6)
            validated_data['code'] = unique_id
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        item_category = ItemCategory.objects.create(**validated_data, created_date_ad=date_now)
        return item_category


class PackingTypeDetailSerializer(serializers.ModelSerializer):
    packing_type_name = serializers.ReadOnlyField(source="packing_type.name", allow_null=True)
    item_name = serializers.ReadOnlyField(source="item.name", allow_null=True)
    code_name = serializers.ReadOnlyField(source="item.code")
    unit_name =  serializers.ReadOnlyField(source='item.unit.name', allow_null=True)
    unit_short_form = serializers.ReadOnlyField(source='item.unit.short_form', allow_null=True)
    class Meta:
        model =  PackingTypeDetail
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']
    
    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        packing_type_details = PackingTypeDetail.objects.create(**validated_data, created_date_ad=date_now)
        return  packing_type_details

    def to_representation(self, instance):
        my_fields = { 'unit_name','unit_short_form'}
                     
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


"""************************** Serializers for Get Views *****************************************"""
class GetItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model =  ItemCategory
        exclude = ['created_date_ad','created_date_bs','created_by','active','display_order']


class GetPackingTypeDetailSerializer(serializers.ModelSerializer):
    packing_type_name =serializers.ReadOnlyField(source='packing_type.name', allow_null=True)
    class Meta:
        model = PackingTypeDetail
        exclude = ['created_date_ad','created_date_bs','active','created_by']



class GetManufactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        exclude = ['created_date_ad','created_date_bs','active','created_by']


class GetManufactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        exclude = ['created_date_ad','created_date_bs','active','created_by']


class GetGenericNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericName
        exclude = ['created_date_ad','created_date_bs','active','created_by']


class GetUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        exclude = ['created_date_ad','created_date_bs','active','created_by','display_order']



# class GenericNameReadOnlyModelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GenericName
#         exclude = ['active',]
#         fields = [
#             'id',
#             'name',
#             # 'item_type',
#             # 'code',
#             # 'generic_name',
#             # 'manufacturer',
#             # 'stock_alert_qty',
#             # 'unit',
#             # 'taxable ',
#             # 'tax_rate',
#             # 'discountable',
#             # 'expirable',
#             # 'purchase_cost',
#             # 'sale_cost'
            
#         ]
#         read_only_fields = fields