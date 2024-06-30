# Generated by Django 4.2.4 on 2024-06-30 12:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UserManagement', '0017_user_age_user_school'),
        ('CompanyManagement', '0008_remove_position_company_delete_application_and_more'),
        ('PositionManagement', '0008_application_offer_alter_offer_application'),
        ('TweetManagement', '0003_rename_content_tweet_text_content_and_more'),
        ('NotificationCenter', '0002_notification_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='CompanyManagement.company'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='message',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='UserManagement.message'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='position',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='PositionManagement.position'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='tweet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='TweetManagement.tweet'),
        ),
    ]
