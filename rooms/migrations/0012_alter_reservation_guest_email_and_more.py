# Generated by Django 5.1.3 on 2024-11-16 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0011_rename_available_today_rooms_is_ready'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='guest_email',
            field=models.EmailField(blank=True, default=None, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='guest_last_name',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='tx_ref',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
