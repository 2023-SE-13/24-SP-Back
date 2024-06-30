# Generated by Django 4.2.4 on 2024-06-30 09:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PositionManagement', '0007_alter_offer_application'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='offer',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='PositionManagement.offer'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='application',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='PositionManagement.application'),
        ),
    ]
