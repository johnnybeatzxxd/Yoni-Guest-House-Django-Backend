# Generated by Django 5.1.3 on 2024-11-05 13:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0003_reservation_room_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='room_type',
        ),
    ]