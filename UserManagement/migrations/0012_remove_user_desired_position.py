# Generated by Django 4.2.4 on 2024-06-30 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserManagement', '0011_alter_user_desired_position'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='desired_position',
        ),
    ]