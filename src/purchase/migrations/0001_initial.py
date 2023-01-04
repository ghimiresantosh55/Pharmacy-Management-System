# Generated by Django 3.2 on 2023-01-04 07:30

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseAdditionalCharge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, help_text='Amount can have max value upto 9999999999.99 and min=0.0', max_digits=12)),
                ('remarks', models.CharField(blank=True, help_text='Remarks can have max upto 50 characters', max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PurchaseDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('purchase_cost', models.DecimalField(decimal_places=2, default=0.0, help_text='purchase_cost can be max value upto 9999999999.99 and default=0.0', max_digits=12)),
                ('sale_cost', models.DecimalField(decimal_places=2, help_text='sale_cost can be max value upto 9999999999.99 and default=0.0', max_digits=12)),
                ('qty', models.DecimalField(decimal_places=2, help_text='Purchase quantity can be max value upto 9999999999.99 and default=0.0', max_digits=12)),
                ('pack_qty', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('free_purchase', models.BooleanField(default=False, help_text='default = false')),
                ('taxable', models.BooleanField(default=True, help_text='Check if item is taxable')),
                ('tax_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Tax rate if item is taxable, max value=100.00 and default=0.0', max_digits=5)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Tax amount can be max value upto 9999999999.99 and default=0.0', max_digits=12)),
                ('discountable', models.BooleanField(default=True, help_text='Check if item is discountable')),
                ('expirable', models.BooleanField(default=False, help_text='Check if item is Expirable, default=False')),
                ('discount_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Discount rate if item is discountable, default=0.0 and max_value=100.00', max_digits=5)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Discount_amount can be max upto 9999999999.99 and default=0.0', max_digits=12)),
                ('gross_amount', models.DecimalField(decimal_places=2, help_text='Gross amount can be max upto 9999999999.99 and default=0.0', max_digits=12)),
                ('net_amount', models.DecimalField(decimal_places=2, help_text='Net amount can be max upto 9999999999.99 and default=0.0', max_digits=12)),
                ('expiry_date_ad', models.DateField(blank=True, help_text='Expiry Date AD', max_length=10, null=True)),
                ('expiry_date_bs', models.CharField(blank=True, help_text='Expiry Date BS', max_length=10)),
                ('batch_no', models.CharField(help_text='Batch no. max length 20', max_length=20)),
                ('cc_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Check if the item is free purchase or not, default=0.0', max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('cc_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Check if the item is free purchase or not, default=0.0', max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PurchaseMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('purchase_no', models.CharField(help_text='Purchase no. should be max. of 10 characters', max_length=20, unique=True)),
                ('purchase_type', models.PositiveIntegerField(choices=[(1, 'PURCHASE'), (2, 'RETURN'), (3, 'OPENING-STOCK'), (4, 'STOCK-ADDITION'), (5, 'STOCK-SUBTRACTION')], help_text='Purchase type like 1= Purchase, 2 = Return, 3 = Opening stock, 4 = stock-addition, 5 = stock-subtraction')),
                ('pay_type', models.PositiveIntegerField(choices=[(1, 'CASH'), (2, 'CREDIT'), (3, 'PARTIAL')], help_text='Pay type like CASH, CREDIT or PARTIAL')),
                ('sub_total', models.DecimalField(decimal_places=2, help_text='Sub total can be max upto 9999999999.99', max_digits=12)),
                ('total_discount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total discount can be max upto 9999999999.99', max_digits=12)),
                ('discount_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Discount rate if  discountable, default=0.0 and max_value=100.00', max_digits=5)),
                ('total_discountable_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total discountable amount can be max upto 9999999999.99', max_digits=12)),
                ('total_taxable_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total taxable amount can be max upto 9999999999.99', max_digits=12)),
                ('total_non_taxable_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total nontaxable amount can be max upto 9999999999.99', max_digits=12)),
                ('total_tax', models.DecimalField(decimal_places=2, default=0.0, help_text='Total tax can be max upto 9999999999.99', max_digits=12)),
                ('grand_total', models.DecimalField(decimal_places=2, default=0.0, help_text='Grand total can be max upto 9999999999.99', max_digits=12)),
                ('round_off_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Round off Amount can be max upto 9999999999.99', max_digits=12)),
                ('bill_no', models.CharField(blank=True, help_text='Bill no.', max_length=20)),
                ('bill_date_ad', models.DateField(blank=True, help_text='Bill Date AD', max_length=10, null=True)),
                ('bill_date_bs', models.CharField(blank=True, help_text='Bill Date BS', max_length=10)),
                ('chalan_no', models.CharField(blank=True, help_text='Chalan no.', max_length=15)),
                ('due_date_ad', models.DateField(blank=True, help_text='Due Date AD', max_length=10, null=True)),
                ('due_date_bs', models.CharField(blank=True, help_text='Due Date BS', max_length=10)),
                ('remarks', models.CharField(blank=True, help_text='Remarks can be max. of 100 characters', max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PurchaseOrderDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('purchase_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('sale_cost', models.DecimalField(decimal_places=2, max_digits=12)),
                ('qty', models.DecimalField(decimal_places=2, help_text='Order quantity', max_digits=12)),
                ('pack_qty', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('taxable', models.BooleanField(default=True, help_text='Check if item is taxable')),
                ('tax_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Tax rate if item is taxable', max_digits=12)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('discountable', models.BooleanField(default=True, help_text='Check if item is discountable')),
                ('discount_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Discount rate if item is discountable', max_digits=12)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('gross_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('net_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PurchaseOrderMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('order_no', models.CharField(help_text='Order no. should be max. of 20 characters', max_length=20, unique=True)),
                ('order_type', models.PositiveIntegerField(choices=[(1, 'ORDER'), (2, 'CANCELLED'), (3, 'APPROVED')], help_text='Order type like Order, approved, cancelled')),
                ('sub_total', models.DecimalField(decimal_places=2, default=0.0, help_text='Sub total can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('total_discount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total discount can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('discount_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='Discount rate if discountable, max_value=100.00 and default=0.0', max_digits=5)),
                ('total_discountable_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total discountable amount can have max_value upto=9999999999.99 and min value=0.0', max_digits=12)),
                ('total_taxable_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total taxable amount can have max value upto=9999999999.99 default=0.0', max_digits=12)),
                ('total_non_taxable_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Total nontaxable amount can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('total_tax', models.DecimalField(decimal_places=2, default=0.0, help_text='Total tax can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('grand_total', models.DecimalField(decimal_places=2, default=0.0, help_text='Grand total can have max value upto=9999999999.99 and default=0.0', max_digits=12)),
                ('remarks', models.CharField(blank=True, help_text='Remarks should be max. of 100 characters', max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PurchasePaymentDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, help_text='Amount can have max value upto 9999999999.99 and min=0.0', max_digits=12)),
                ('remarks', models.CharField(blank=True, help_text='Remarks can have max upto 50 characters', max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
