# Generated by Django 4.2.4 on 2024-06-27 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserManagement', '0003_merge_20240627_0907'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='resume',
            field=models.FileField(blank=True, null=True, upload_to='resources/resumes/'),
        ),
    ]