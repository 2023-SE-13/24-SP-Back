# Generated by Django 4.2.4 on 2024-07-01 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PositionManagement', '0008_application_offer_alter_offer_application'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='is_accepted',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
