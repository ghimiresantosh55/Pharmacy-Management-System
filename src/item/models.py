# Django
from django.core.exceptions import ValidationError
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files import File
from pims import settings
# User-defined models (import)
from src.core_app.models import NowTimestampAndUserModel
from django.core.validators import MinValueValidator
from decimal import Decimal

# import for log
from simple_history import register
from log_app.models import LogBase

def upload_path_item(instance, filename):
    return '/'.join(['item_image', filename])


def validate_image(image):
    file_size = image.size
    limit_byte_size = settings.MAX_UPLOAD_SIZE
    if file_size > limit_byte_size:
        # converting into kb
        f = limit_byte_size / 1024
        # converting into MB
        f = f / 1024
        raise ValidationError("Max size of file is %s MB" % f)

class PackingType(NowTimestampAndUserModel):
    name = models.CharField(max_length=50, unique= True,
                            help_text=" name can be max. of 50 characters")
    short_name = models.CharField(max_length=5, unique= True,
                            help_text=" short name can be max. of 5 characters")
    unit = models.BooleanField(default=False, help_text="By default unit=False")
    active = models.BooleanField(default=True, help_text="By default active=True")

    

    def __str__(self):
        return "id {} : {}".format(self.id, self.name)

register(PackingType, app="log_app", table_name="item_packing_type_log", custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class Unit(NowTimestampAndUserModel):
    name = models.CharField(max_length=50, unique=True,\
                            help_text="Unit name can be max. of 50 characters and must be unique")
    short_form = models.CharField(max_length=20,unique=True,\
                            help_text="short_form can be max. of 20 characters and must be unique")
    display_order = models.IntegerField(default=0, blank= True, null= True, help_text="Display order for ordering, default=0,blank= True, null= True")
    active = models.BooleanField(default=True, help_text="By default active=True")

    def __str__(self):
        return "id {} : {}".format(self.id, self.name)

register(Unit, app="log_app", table_name="item_Unit_log", custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class GenericName(NowTimestampAndUserModel):
    name = models.CharField(max_length=150, unique=True,
                            help_text="Generic name should be max. of 150 characters")
    active = models.BooleanField(default=True, help_text="By default active=True")

    def __str__(self):
        return "id {} : {}".format(self.id, self.name)

register(GenericName, app="log_app", table_name="item_genericname_log", custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class Manufacturer(NowTimestampAndUserModel):
    name = models.CharField(max_length=100, unique=True,
                            help_text="Manufacturer name should be max. of 100 characters")
    active = models.BooleanField(default=True, help_text="By default active=True")

    def __str__(self):
        return "id {} : {}".format(self.id, self.name)

register(Manufacturer, app="log_app", table_name="item_manufacturer_log", custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class ItemCategory(NowTimestampAndUserModel):
    name = models.CharField(max_length=100, unique=True,
                            help_text="Category name can be max. of 100 characters")
    code = models.CharField(max_length=10, unique=True, blank=True,
                            help_text="Item code can be max. of 10 characters")
    display_order = models.IntegerField(default=0,blank= True, null= True, help_text="Display order for ordering, default=0 and blank= True, null= True")
    active = models.BooleanField(default=True, help_text="By default active=True")

    def __str__(self):
        return "id {} : {}".format(self.id, self.name)


register(ItemCategory, app="log_app", table_name="item_itemcategory_log", custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class Item(NowTimestampAndUserModel):
    ITEM_TYPE = (
        (1, "INVENTORY"),
        (2, "SALE"),
        (3, "BOTH")
    )
    name = models.CharField(max_length=100, unique=True,
                            help_text="Item name should be max. of 100 characters")
    code = models.CharField(max_length=10, unique=True, blank=True,
                            help_text="Item code should be max. of 10 characters")
    item_category = models.ForeignKey(ItemCategory, on_delete=models.PROTECT)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    generic_name = models.ForeignKey(GenericName, on_delete=models.PROTECT)
    item_type = models.PositiveIntegerField(choices=ITEM_TYPE, default= 3,
                                            help_text="Item type like 1=INVENTORY, 2=SALE, 3=BOTH and default = BOTH")
    stock_alert_qty = models.IntegerField(default=1, help_text="Quantity for alert/warning")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null= True, blank= True, help_text=" blank=True, null= True")
    
    location = models.CharField(max_length=10, blank= True, null=True,
                                help_text="Physical location of item, max length can be of 10 characters and blank= True, null= True")
    basic_info = models.CharField(max_length=50, blank=True, null=True,
                                  help_text="Basic info can be max. of 50 characters")
    taxable = models.BooleanField(default=True, help_text="Check if item is taxable, default=True")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                   help_text="Tax rate if item is taxable, default=0.0 and can be upto 100.00")
    discountable = models.BooleanField(default=True,
                                       help_text="Check if item is discountable, default=True")
    expirable = models.BooleanField(default=True,
                                    help_text="Check if item is expirable, default=True")
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                        help_text="Max value purchase_cost can be upto 9999999999.99")
    sale_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                    help_text="Max value sale_cost can be upto 9999999999.99")
    image = models.ImageField(upload_to="item", validators=[validate_image], blank=True)
    cc_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, validators=[MinValueValidator(Decimal('0.00'))],
                                    help_text="Check if the item is free purchase or not, default=0.0")
    active = models.BooleanField(default=True, help_text="By default active=True")

    def __str__(self):
        return "id {}".format(self.id)

    def save(self, *args, **kwargs):
        if self.image is True:
            img = Image.open(self.image).convert('RGB')
            im_io = BytesIO()
            img.save(im_io, format="webp")
            new_image = File(im_io, name="%s.webp"%self.image.name.split('.')[0],)
            self.image = new_image
        super().save(*args, **kwargs)



register(Item, app="log_app", table_name="item_item_log", custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PackingTypeDetail(NowTimestampAndUserModel):
    item = models.ForeignKey(Item, on_delete=models.PROTECT, db_index= True, related_name="packing_type_details")
    packing_type = models.ForeignKey(PackingType, on_delete=models.PROTECT, related_name="packing_types")
    pack_qty = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], help_text="Value can't be negative")
    active = models.BooleanField(default=True, help_text="By default active=True")

    def __str__(self):
        return "id {}".format(self.id)

register(PackingTypeDetail, app="log_app", table_name="item_packing_type_detail_log", custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])