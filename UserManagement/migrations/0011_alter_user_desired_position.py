# Generated by Django 4.2.4 on 2024-06-30 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PositionManagement', '0002_position_hr'),
        ('UserManagement', '0010_user_cur_position_user_years_of_service_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='desired_position',
            field=models.ManyToManyField(blank=True, to='PositionManagement.positiontag'),
        ),
    ]
