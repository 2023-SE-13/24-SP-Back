# Generated by Django 4.2.4 on 2024-06-28 01:42

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('CompanyManagement', '0005_merge_20240628_0910'),
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('position_id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('position_name', models.CharField(max_length=255)),
                ('position_description', models.CharField(max_length=255)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('education_requirement', models.CharField(blank=True, max_length=255, null=True)),
                ('salary', models.CharField(blank=True, max_length=255, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CompanyManagement.company')),
            ],
            options={
                'db_table': 'Positions',
            },
        ),
    ]