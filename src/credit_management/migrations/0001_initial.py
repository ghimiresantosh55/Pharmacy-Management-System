# Generated by Django 3.2 on 2023-01-04 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CreditClearance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('payment_type', models.PositiveIntegerField(choices=[(1, 'PAYMENT'), (2, 'REFUND')], default=1, help_text='Where 1 = PAYMENT, 2 = REFUND, default=1')),
                ('receipt_no', models.CharField(help_text='receipt_no can be upto 20 characters', max_length=20)),
                ('total_amount', models.DecimalField(decimal_places=2, help_text='max_value upto 9999999999.99, min_value=0.0', max_digits=12)),
                ('remarks', models.CharField(blank=True, help_text='Remarks can have max of 50 characters, blank=True', max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CreditPaymentDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, help_text='max_value upto 9999999999.99', max_digits=12)),
                ('remarks', models.CharField(blank=True, help_text='Remarks can have max of 50 characters, blank=True', max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
