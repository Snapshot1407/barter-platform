# Generated by Django 5.0.6 on 2025-07-08 07:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0002_ad_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ad',
            name='status',
        ),
    ]
