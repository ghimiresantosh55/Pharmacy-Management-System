# Generated by Django 3.2 on 2023-01-04 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('schema_name', models.CharField(max_length=100, unique=True)),
                ('sub_domain', models.CharField(max_length=300, unique=True)),
                ('default', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]
