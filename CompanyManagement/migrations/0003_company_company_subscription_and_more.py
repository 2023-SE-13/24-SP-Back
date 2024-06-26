# Generated by Django 4.2.4 on 2024-06-26 02:46

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyManagement', '0002_alter_company_company_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='company_subscription',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_id',
            field=models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]