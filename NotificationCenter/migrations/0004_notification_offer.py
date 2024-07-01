# Generated by Django 4.2.4 on 2024-07-01 02:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PositionManagement', '0008_application_offer_alter_offer_application'),
        ('NotificationCenter', '0003_alter_notification_company_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='offer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='PositionManagement.offer'),
        ),
    ]