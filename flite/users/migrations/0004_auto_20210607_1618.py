# Generated by Django 2.1.9 on 2021-06-07 15:18

from django.db import migrations, models
import flite.users.utils


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210603_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='reference',
            field=models.CharField(default=flite.users.utils.generate_ref, max_length=200),
        ),
    ]
