# Generated by Django 2.1.9 on 2021-06-08 09:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20210607_2026'),
    ]

    operations = [
        migrations.RenameField(
            model_name='p2ptransfer',
            old_name='receipient',
            new_name='recipient',
        ),
    ]
