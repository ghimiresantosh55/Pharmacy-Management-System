# Generated by Django 3.2 on 2023-01-04 07:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdvancedDeposit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('advanced_deposit_type', models.PositiveIntegerField(choices=[(1, 'DEPOSIT'), (2, 'DEPOSIT-RETURN')], help_text='Advanced Deposit type like 1= Deposit, 2 = Return')),
                ('deposit_no', models.CharField(help_text='max deposit_no should not be greater than 13', max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, help_text='Maximum value upto 99999999999.99', max_digits=12)),
                ('remarks', models.CharField(blank=True, max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AdvancedDepositPaymentDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_ad', models.DateTimeField()),
                ('created_date_bs', models.CharField(max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, help_text='Maximum value upto 99999999999.99', max_digits=12)),
                ('remarks', models.CharField(blank=True, help_text='remarks can be upto 50 characters', max_length=50)),
                ('advanced_deposit', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='advanced_deposit_payment_details', to='advance_deposit.advanceddeposit')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
