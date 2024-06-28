# Generated by Django 4.2.4 on 2024-06-28 02:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('CompanyManagement', '0006_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('application_id', models.UUIDField(auto_created=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
                ('result', models.CharField(blank=True, max_length=255, null=True)),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CompanyManagement.position')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'applications',
            },
        ),
    ]